package main

import (
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync/atomic"
	"time"
)

const namespace = "rocm_smi"

var version = "dev"

var (
	cardNameRe     = regexp.MustCompile(`^card[0-9]+$`)
	hwmonValueRe   = regexp.MustCompile(`^([a-z]+)([0-9]+)(?:_([a-z_]+))?$`)
	scrapeFailures atomic.Uint64
)

type config struct {
	listenAddr string
	sysfsRoot  string
}

type metric struct {
	name   string
	help   string
	type_  string
	labels map[string]string
	value  float64
}

type device struct {
	card    string
	path    string
	pciSlot string
	static  map[string]string
}

func main() {
	cfg := config{
		listenAddr: envDefault("LISTEN_ADDR", ":9494"),
		sysfsRoot:  envDefault("SYSFS_ROOT", "/sys"),
	}

	http.HandleFunc("/metrics", func(w http.ResponseWriter, _ *http.Request) {
		started := time.Now()
		metrics, err := collect(cfg)
		duration := time.Since(started).Seconds()
		if err != nil {
			log.Printf("scrape failed: %v", err)
			scrapeFailures.Add(1)
			metrics = append(metrics, metric{name: "scrape_success", help: "1 if the latest scrape succeeded, 0 otherwise.", type_: "gauge", value: 0})
		} else {
			metrics = append(metrics, metric{name: "scrape_success", help: "1 if the latest scrape succeeded, 0 otherwise.", type_: "gauge", value: 1})
		}
		metrics = append(metrics, metric{name: "scrape_failures_total", help: "Total number of failed scrapes.", type_: "counter", value: float64(scrapeFailures.Load())})
		metrics = append(metrics, metric{name: "last_scrape_duration_seconds", help: "Duration of the latest scrape in seconds.", type_: "gauge", value: duration})

		w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
		writeMetrics(w, metrics)
	})

	log.Printf("listening on %s/metrics with SYSFS_ROOT=%s", cfg.listenAddr, cfg.sysfsRoot)
	log.Fatal(http.ListenAndServe(cfg.listenAddr, nil))
}

func envDefault(name, fallback string) string {
	value := strings.TrimSpace(os.Getenv(name))
	if value == "" {
		return fallback
	}
	return value
}

func collect(cfg config) ([]metric, error) {
	devices, err := discoverDevices(cfg.sysfsRoot)
	if err != nil {
		return nil, err
	}

	metrics := []metric{{
		name:  "gpus_discovered",
		help:  "Number of AMDGPU DRM card devices discovered under sysfs.",
		type_: "gauge",
		value: float64(len(devices)),
	}, {
		name:   "build_info",
		help:   "Build information for rocm-smi-exporter. Value is always 1.",
		type_:  "gauge",
		labels: map[string]string{"version": version},
		value:  1,
	}}

	for _, dev := range devices {
		labels := map[string]string{"card": dev.card, "pci_slot": dev.pciSlot}
		for key, value := range dev.static {
			if value != "" {
				labels[key] = value
			}
		}
		metrics = append(metrics, metric{name: "gpu_info", help: "Static AMDGPU device information. Value is always 1.", type_: "gauge", labels: labels, value: 1})

		metrics = append(metrics, readSimpleGauge(dev, "gpu_busy_percent", "gpu_busy_percent", "Current GPU busy percentage.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_busy_percent", "memory_busy_percent", "Current memory busy percentage.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_vram_used", "vram_used_bytes", "Currently used VRAM bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_vram_total", "vram_total_bytes", "Total available VRAM bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_vis_vram_used", "visible_vram_used_bytes", "Currently used visible VRAM bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_vis_vram_total", "visible_vram_total_bytes", "Total visible VRAM bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_gtt_used", "gtt_used_bytes", "Currently used GTT bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "mem_info_gtt_total", "gtt_total_bytes", "Total GTT bytes.", 1)...)
		metrics = append(metrics, readSimpleGauge(dev, "pcie_replay_count", "pcie_replay_count", "Total PCIe replay count reported by amdgpu.", 1)...)
		metrics = append(metrics, collectHwmon(dev)...)
	}

	return metrics, nil
}

func discoverDevices(sysfsRoot string) ([]device, error) {
	entries, err := os.ReadDir(filepath.Join(sysfsRoot, "class", "drm"))
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, err
	}

	devices := make([]device, 0)
	for _, entry := range entries {
		if !cardNameRe.MatchString(entry.Name()) {
			continue
		}
		devPath := filepath.Join(sysfsRoot, "class", "drm", entry.Name(), "device")
		vendor, ok := readTextFile(filepath.Join(devPath, "vendor"))
		if !ok || !strings.EqualFold(strings.TrimSpace(vendor), "0x1002") {
			continue
		}

		pciSlot := filepath.Base(resolvePath(devPath))
		devices = append(devices, device{
			card:    entry.Name(),
			path:    devPath,
			pciSlot: pciSlot,
			static: map[string]string{
				"vendor_id":           cleanLabel(vendor),
				"device_id":           readStatic(devPath, "device"),
				"subsystem_vendor_id": readStatic(devPath, "subsystem_vendor"),
				"subsystem_device_id": readStatic(devPath, "subsystem_device"),
				"revision_id":         readStatic(devPath, "revision"),
				"product_name":        readStatic(devPath, "product_name"),
				"unique_id":           readStatic(devPath, "unique_id"),
			},
		})
	}

	sort.Slice(devices, func(i, j int) bool { return devices[i].card < devices[j].card })
	return devices, nil
}

func resolvePath(path string) string {
	resolved, err := filepath.EvalSymlinks(path)
	if err != nil {
		return path
	}
	return resolved
}

func readStatic(dir, name string) string {
	value, ok := readTextFile(filepath.Join(dir, name))
	if !ok {
		return ""
	}
	return cleanLabel(value)
}

func cleanLabel(value string) string {
	return strings.Join(strings.Fields(strings.TrimSpace(value)), " ")
}

func readSimpleGauge(dev device, sysfsName, metricName, help string, divisor float64) []metric {
	value, ok := readFloatFile(filepath.Join(dev.path, sysfsName), divisor)
	if !ok {
		return nil
	}
	return []metric{{name: metricName, help: help, type_: "gauge", labels: baseLabels(dev), value: value}}
}

func collectHwmon(dev device) []metric {
	hwmonDirs, err := filepath.Glob(filepath.Join(dev.path, "hwmon", "hwmon*"))
	if err != nil {
		return nil
	}
	sort.Strings(hwmonDirs)

	var metrics []metric
	for _, hwmonDir := range hwmonDirs {
		_ = filepath.WalkDir(hwmonDir, func(path string, d fs.DirEntry, err error) error {
			if err != nil || d.IsDir() {
				return nil
			}
			match := hwmonValueRe.FindStringSubmatch(d.Name())
			if match == nil {
				return nil
			}
			kind := match[3]
			if kind == "" {
				kind = "input"
			}
			if kind != "input" && kind != "average" && kind != "cap" && kind != "cap_min" && kind != "cap_max" {
				return nil
			}

			prefix, index := match[1], match[2]
			name, help, labels, divisor, ok := hwmonMetric(dev, hwmonDir, prefix, index, kind)
			if !ok {
				return nil
			}

			value, ok := readFloatFile(path, divisor)
			if !ok {
				return nil
			}
			metrics = append(metrics, metric{name: name, help: help, type_: "gauge", labels: labels, value: value})
			return nil
		})
	}
	return metrics
}

func hwmonMetric(dev device, hwmonDir, prefix, index, kind string) (string, string, map[string]string, float64, bool) {
	labels := baseLabels(dev)
	labels["sensor"] = index
	if label, ok := readTextFile(filepath.Join(hwmonDir, prefix+index+"_label")); ok {
		labels["sensor"] = cleanLabel(label)
	}

	switch prefix {
	case "temp":
		return "temperature_celsius", "AMDGPU temperature sensor value in celsius.", labels, 1000, true
	case "power":
		labels["type"] = kind
		delete(labels, "sensor")
		return "power_watts", "AMDGPU power sensor value in watts.", labels, 1000000, true
	case "fan":
		return "fan_rpm", "AMDGPU fan speed in RPM.", labels, 1, kind == "input"
	case "pwm":
		return "fan_pwm", "AMDGPU fan PWM value.", labels, 1, kind == "input"
	case "freq":
		return "clock_hertz", "AMDGPU clock sensor value in hertz.", labels, 1, kind == "input"
	case "in":
		return "voltage_volts", "AMDGPU voltage sensor value in volts.", labels, 1000, kind == "input"
	default:
		return "", "", nil, 1, false
	}
}

func baseLabels(dev device) map[string]string {
	return map[string]string{"card": dev.card, "pci_slot": dev.pciSlot}
}

func readTextFile(path string) (string, bool) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", false
	}
	return string(data), true
}

func readFloatFile(path string, divisor float64) (float64, bool) {
	data, ok := readTextFile(path)
	if !ok {
		return 0, false
	}
	value, err := strconv.ParseFloat(strings.TrimSpace(data), 64)
	if err != nil {
		return 0, false
	}
	return value / divisor, true
}

func writeMetrics(w http.ResponseWriter, metrics []metric) {
	seen := map[string]bool{}
	sort.SliceStable(metrics, func(i, j int) bool { return metrics[i].name < metrics[j].name })
	for _, m := range metrics {
		fullName := namespace + "_" + m.name
		if !seen[fullName] {
			fmt.Fprintf(w, "# HELP %s %s\n", fullName, m.help)
			fmt.Fprintf(w, "# TYPE %s %s\n", fullName, m.type_)
			seen[fullName] = true
		}
		fmt.Fprintf(w, "%s%s %s\n", fullName, formatLabels(m.labels), strconv.FormatFloat(m.value, 'g', -1, 64))
	}
}

func formatLabels(labels map[string]string) string {
	if len(labels) == 0 {
		return ""
	}
	keys := make([]string, 0, len(labels))
	for key := range labels {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	parts := make([]string, 0, len(keys))
	for _, key := range keys {
		parts = append(parts, fmt.Sprintf(`%s="%s"`, key, escapeLabel(labels[key])))
	}
	return "{" + strings.Join(parts, ",") + "}"
}

func escapeLabel(value string) string {
	value = strings.ReplaceAll(value, `\`, `\\`)
	value = strings.ReplaceAll(value, "\n", `\n`)
	value = strings.ReplaceAll(value, `"`, `\"`)
	return value
}
