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

const namespace = "amdgpu"

var version = "dev"

var (
	cardNameRe     = regexp.MustCompile(`^card[0-9]+$`)
	pidNameRe      = regexp.MustCompile(`^[0-9]+$`)
	podUIDRe       = regexp.MustCompile(`pod([0-9a-fA-F]{8}-[0-9a-fA-F-]{27,})`)
	containerIDRe  = regexp.MustCompile(`([0-9a-fA-F]{64})`)
	hwmonValueRe   = regexp.MustCompile(`^([a-z]+)([0-9]+)(?:_([a-z_]+))?$`)
	scrapeFailures atomic.Uint64
)

type config struct {
	listenAddr string
	procRoot   string
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

type drmClient struct {
	pdev        string
	clientID    string
	pid         string
	process     string
	podUID      string
	containerID string
	memory      map[string]map[string]float64
}

func main() {
	cfg := config{
		listenAddr: envDefault("LISTEN_ADDR", ":9494"),
		procRoot:   envDefault("PROC_ROOT", "/proc"),
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

	log.Printf("listening on %s/metrics with SYSFS_ROOT=%s PROC_ROOT=%s", cfg.listenAddr, cfg.sysfsRoot, cfg.procRoot)
	server := &http.Server{
		Addr:              cfg.listenAddr,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Fatal(server.ListenAndServe())
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
		help:   "Build information for amdgpu-exporter. Value is always 1.",
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
		metrics = append(metrics, readSimpleCounter(dev, "pcie_replay_count", "pcie_replay_total", "Total PCIe replay count reported by amdgpu.", 1)...)
		metrics = append(metrics, collectHwmon(dev)...)
	}
	metrics = append(metrics, collectDRMClients(cfg.procRoot, devices)...)

	return metrics, nil
}

func collectDRMClients(procRoot string, devices []device) []metric {
	if strings.TrimSpace(procRoot) == "" {
		return nil
	}

	entries, err := os.ReadDir(procRoot)
	if err != nil {
		return nil
	}

	deviceByPCI := make(map[string]device, len(devices))
	for _, dev := range devices {
		deviceByPCI[dev.pciSlot] = dev
	}

	clients := make(map[string]drmClient)
	for _, entry := range entries {
		if !entry.IsDir() || !pidNameRe.MatchString(entry.Name()) {
			continue
		}

		pid := entry.Name()
		process := readProcValue(procRoot, pid, "comm")
		if process == "" {
			process = "unknown"
		}
		podUID, containerID := readCgroupIdentity(procRoot, pid)

		fdEntries, err := os.ReadDir(filepath.Join(procRoot, pid, "fdinfo"))
		if err != nil {
			continue
		}
		for _, fdEntry := range fdEntries {
			if fdEntry.IsDir() {
				continue
			}
			client, ok := readDRMClient(filepath.Join(procRoot, pid, "fdinfo", fdEntry.Name()))
			if !ok {
				continue
			}
			client.pid = pid
			client.process = process
			client.podUID = podUID
			client.containerID = containerID

			// A process can hold several file descriptors for one DRM client.
			// Deduplicate by device and DRM client ID or the same allocation would
			// be counted once per descriptor.
			key := client.pdev + "\x00" + client.clientID
			if _, exists := clients[key]; !exists {
				clients[key] = client
			}
		}
	}

	keys := make([]string, 0, len(clients))
	for key := range clients {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	metrics := make([]metric, 0, len(keys)*3)
	for _, key := range keys {
		client := clients[key]
		card := "unknown"
		if dev, ok := deviceByPCI[client.pdev]; ok {
			card = dev.card
		}
		labels := map[string]string{
			"card":         card,
			"pci_slot":     client.pdev,
			"client_id":    client.clientID,
			"pid":          client.pid,
			"process":      client.process,
			"pod_uid":      client.podUID,
			"container_id": client.containerID,
		}
		for region, states := range client.memory {
			for state, value := range states {
				clientLabels := cloneLabels(labels)
				clientLabels["region"] = region
				clientLabels["state"] = state
				metrics = append(metrics, metric{
					name:   "drm_client_memory_bytes",
					help:   "AMDGPU DRM client memory by region and accounting state.",
					type_:  "gauge",
					labels: clientLabels,
					value:  value,
				})
			}
		}
	}
	return metrics
}

func readDRMClient(path string) (drmClient, bool) {
	data, err := os.ReadFile(path)
	if err != nil {
		return drmClient{}, false
	}

	client := drmClient{memory: make(map[string]map[string]float64)}
	driver := ""
	for _, line := range strings.Split(string(data), "\n") {
		fields := strings.Fields(line)
		if len(fields) < 2 {
			continue
		}
		key := strings.TrimSuffix(fields[0], ":")
		switch key {
		case "drm-driver":
			driver = fields[1]
		case "drm-client-id":
			client.clientID = fields[1]
		case "drm-pdev":
			client.pdev = fields[1]
		}

		parts := strings.Split(key, "-")
		if len(parts) != 3 || parts[0] != "drm" {
			continue
		}
		state, region := parts[1], parts[2]
		if !drmMemoryState(state) || !drmMemoryRegion(region) {
			continue
		}
		value, ok := parseMemoryBytes(fields[1:])
		if !ok {
			continue
		}
		if client.memory[region] == nil {
			client.memory[region] = make(map[string]float64)
		}
		client.memory[region][state] = value
	}

	if driver != "amdgpu" || client.clientID == "" || client.pdev == "" || len(client.memory) == 0 {
		return drmClient{}, false
	}
	return client, true
}

func drmMemoryState(state string) bool {
	return state == "total" || state == "resident" || state == "purgeable"
}

func drmMemoryRegion(region string) bool {
	return region == "cpu" || region == "gtt" || region == "vram"
}

func parseMemoryBytes(fields []string) (float64, bool) {
	if len(fields) == 0 {
		return 0, false
	}
	value, err := strconv.ParseFloat(fields[0], 64)
	if err != nil {
		return 0, false
	}
	if len(fields) == 1 {
		return value, true
	}
	switch strings.ToLower(fields[1]) {
	case "b", "bytes":
		return value, true
	case "kib":
		return value * 1024, true
	case "mib":
		return value * 1024 * 1024, true
	case "gib":
		return value * 1024 * 1024 * 1024, true
	default:
		return 0, false
	}
}

func readProcValue(procRoot, pid, name string) string {
	value, ok := readTextFile(filepath.Join(procRoot, pid, name))
	if !ok {
		return ""
	}
	return cleanLabel(value)
}

func readCgroupIdentity(procRoot, pid string) (string, string) {
	value, ok := readTextFile(filepath.Join(procRoot, pid, "cgroup"))
	if !ok {
		return "", ""
	}
	path := strings.TrimSpace(value)
	podUID := ""
	if match := podUIDRe.FindStringSubmatch(path); match != nil {
		podUID = match[1]
	}
	containerID := ""
	if match := containerIDRe.FindStringSubmatch(path); match != nil {
		containerID = match[1]
	}
	return podUID, containerID
}

func cloneLabels(labels map[string]string) map[string]string {
	clone := make(map[string]string, len(labels))
	for key, value := range labels {
		clone[key] = value
	}
	return clone
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
	return readSimple(dev, sysfsName, metricName, help, divisor, "gauge")
}

func readSimpleCounter(dev device, sysfsName, metricName, help string, divisor float64) []metric {
	return readSimple(dev, sysfsName, metricName, help, divisor, "counter")
}

func readSimple(dev device, sysfsName, metricName, help string, divisor float64, type_ string) []metric {
	value, ok := readFloatFile(filepath.Join(dev.path, sysfsName), divisor)
	if !ok {
		return nil
	}
	return []metric{{name: metricName, help: help, type_: type_, labels: baseLabels(dev), value: value}}
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
		// Keep the sensor index label: a device exposing power1_average and
		// power2_average must emit distinct series, or the duplicate label
		// sets make the whole exposition invalid.
		labels["type"] = kind
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
