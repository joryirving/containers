package main

import (
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
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

// TestPowerSensorsStayDistinct is the regression for the review finding:
// a device exposing two power sensors of the same kind must emit two
// distinct series (sensor label retained), and the rendered exposition
// must contain no duplicate label sets — which Prometheus would reject.
func TestPowerSensorsStayDistinct(t *testing.T) {
	root := t.TempDir()
	devicePath := filepath.Join(root, "class", "drm", "card0", "device")
	hwmonPath := filepath.Join(devicePath, "hwmon", "hwmon0")
	if err := os.MkdirAll(hwmonPath, 0o755); err != nil {
		t.Fatal(err)
	}
	writeFixture(t, devicePath, "vendor", "0x1002\n")
	writeFixture(t, hwmonPath, "power1_average", "120000000\n")
	writeFixture(t, hwmonPath, "power2_average", "45000000\n")

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}

	var powerSeries []metric
	for _, m := range metrics {
		if m.name == "power_watts" {
			powerSeries = append(powerSeries, m)
		}
	}
	if len(powerSeries) != 2 {
		t.Fatalf("want 2 power_watts series, got %d: %#v", len(powerSeries), powerSeries)
	}
	if powerSeries[0].labels["sensor"] == powerSeries[1].labels["sensor"] {
		t.Fatalf("power series must carry distinct sensor labels, both got %q", powerSeries[0].labels["sensor"])
	}

	assertNoDuplicateSeries(t, renderExposition(t, metrics))
}

// TestVendorFilterSkipsNonAMD: a non-AMD card (vendor 0x10de) must not
// be discovered.
func TestVendorFilterSkipsNonAMD(t *testing.T) {
	root := t.TempDir()
	amd := filepath.Join(root, "class", "drm", "card0", "device")
	nvidia := filepath.Join(root, "class", "drm", "card1", "device")
	for _, d := range []string{amd, nvidia} {
		if err := os.MkdirAll(d, 0o755); err != nil {
			t.Fatal(err)
		}
	}
	writeFixture(t, amd, "vendor", "0x1002\n")
	writeFixture(t, nvidia, "vendor", "0x10de\n")

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}
	assertMetricValue(t, metrics, "gpus_discovered", 1)
	for _, m := range metrics {
		if m.labels["card"] == "card1" {
			t.Fatalf("non-AMD card1 must not emit metrics, got %#v", m)
		}
	}
}

// TestMissingFilesSkipPerMetric: an absent sysfs attribute skips that
// one metric; the rest of the device still reports.
func TestMissingFilesSkipPerMetric(t *testing.T) {
	root := t.TempDir()
	devicePath := filepath.Join(root, "class", "drm", "card0", "device")
	if err := os.MkdirAll(devicePath, 0o755); err != nil {
		t.Fatal(err)
	}
	writeFixture(t, devicePath, "vendor", "0x1002\n")
	writeFixture(t, devicePath, "mem_info_vram_used", "42\n")
	// no gpu_busy_percent, no hwmon

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}
	assertMetricValue(t, metrics, "vram_used_bytes", 42)
	for _, m := range metrics {
		if m.name == "gpu_busy_percent" {
			t.Fatalf("missing attribute must skip the metric, got %#v", m)
		}
	}
}

// TestMultiGPU: two AMD cards report side by side with distinct card labels.
func TestMultiGPU(t *testing.T) {
	root := t.TempDir()
	for _, card := range []string{"card0", "card1"} {
		devicePath := filepath.Join(root, "class", "drm", card, "device")
		if err := os.MkdirAll(devicePath, 0o755); err != nil {
			t.Fatal(err)
		}
		writeFixture(t, devicePath, "vendor", "0x1002\n")
		writeFixture(t, devicePath, "gpu_busy_percent", "7\n")
	}

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}
	assertMetricValue(t, metrics, "gpus_discovered", 2)
	cards := map[string]bool{}
	for _, m := range metrics {
		if m.name == "gpu_busy_percent" {
			cards[m.labels["card"]] = true
		}
	}
	if !cards["card0"] || !cards["card1"] {
		t.Fatalf("want gpu_busy_percent for both cards, got %v", cards)
	}
	assertNoDuplicateSeries(t, renderExposition(t, metrics))
}

// TestExpositionOutput pins the rendered text format: HELP/TYPE emitted
// once per metric, pcie replay exposed as a counter named _total.
func TestExpositionOutput(t *testing.T) {
	root := t.TempDir()
	devicePath := filepath.Join(root, "class", "drm", "card0", "device")
	if err := os.MkdirAll(devicePath, 0o755); err != nil {
		t.Fatal(err)
	}
	writeFixture(t, devicePath, "vendor", "0x1002\n")
	writeFixture(t, devicePath, "pcie_replay_count", "5\n")

	metrics, err := collect(config{sysfsRoot: root})
	if err != nil {
		t.Fatal(err)
	}
	body := renderExposition(t, metrics)

	if !strings.Contains(body, "# TYPE rocm_smi_pcie_replay_total counter") {
		t.Fatalf("pcie replay must be a counter named _total; got:\n%s", body)
	}
	if !strings.Contains(body, "rocm_smi_pcie_replay_total{") {
		t.Fatalf("pcie replay sample line missing; got:\n%s", body)
	}
	if strings.Count(body, "# TYPE rocm_smi_gpu_info gauge") != 1 {
		t.Fatalf("HELP/TYPE must be emitted exactly once per metric; got:\n%s", body)
	}
	assertNoDuplicateSeries(t, body)
}

// renderExposition runs writeMetrics through an httptest recorder and
// returns the body, so tests assert on the real exposition text.
func renderExposition(t *testing.T, metrics []metric) string {
	t.Helper()
	rec := httptest.NewRecorder()
	writeMetrics(rec, metrics)
	return rec.Body.String()
}

// assertNoDuplicateSeries fails if two sample lines share the same
// name+label-set, which makes the exposition invalid to Prometheus.
func assertNoDuplicateSeries(t *testing.T, body string) {
	t.Helper()
	seen := map[string]bool{}
	for _, line := range strings.Split(body, "\n") {
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		idx := strings.LastIndex(line, " ")
		if idx < 0 {
			continue
		}
		series := line[:idx]
		if seen[series] {
			t.Fatalf("duplicate series %q in exposition:\n%s", series, body)
		}
		seen[series] = true
	}
}
