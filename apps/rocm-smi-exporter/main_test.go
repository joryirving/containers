package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCollectFromSysfsFixture(t *testing.T) {
	root := t.TempDir()
	devicePath := filepath.Join(root, "class", "drm", "card0", "device")
	hwmonPath := filepath.Join(devicePath, "hwmon", "hwmon0")
	if err := os.MkdirAll(hwmonPath, 0o755); err != nil {
		t.Fatal(err)
	}

	writeFixture(t, devicePath, "vendor", "0x1002\n")
	writeFixture(t, devicePath, "device", "0x150e\n")
	writeFixture(t, devicePath, "gpu_busy_percent", "91\n")
	writeFixture(t, devicePath, "mem_busy_percent", "84\n")
	writeFixture(t, devicePath, "mem_info_vram_used", "1073741824\n")
	writeFixture(t, hwmonPath, "temp1_label", "edge\n")
	writeFixture(t, hwmonPath, "temp1_input", "65500\n")
	writeFixture(t, hwmonPath, "power1_average", "120000000\n")
	writeFixture(t, hwmonPath, "freq1_label", "sclk\n")
	writeFixture(t, hwmonPath, "freq1_input", "2900000000\n")

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}

	assertMetricValue(t, metrics, "gpus_discovered", 1)
	assertMetricValue(t, metrics, "gpu_busy_percent", 91)
	assertMetricValue(t, metrics, "memory_busy_percent", 84)
	assertMetricValue(t, metrics, "vram_used_bytes", 1073741824)
	assertMetricValue(t, metrics, "temperature_celsius", 65.5)
	assertMetricValue(t, metrics, "power_watts", 120)
	assertMetricValue(t, metrics, "clock_hertz", 2900000000)
}

func writeFixture(t *testing.T, dir, name, value string) {
	t.Helper()
	if err := os.WriteFile(filepath.Join(dir, name), []byte(value), 0o644); err != nil {
		t.Fatal(err)
	}
}

func assertMetricValue(t *testing.T, metrics []metric, name string, value float64) {
	t.Helper()
	for _, metric := range metrics {
		if metric.name == name && metric.value == value {
			return
		}
	}
	t.Fatalf("metric %s=%v not found in %#v", name, value, metrics)
}
