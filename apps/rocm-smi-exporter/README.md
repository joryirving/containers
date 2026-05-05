# rocm-smi-exporter

Small Prometheus exporter for AMDGPU/ROCm telemetry on Kubernetes nodes.

The exporter reads Linux AMDGPU sysfs and hwmon files directly. It does not require the ROCm userspace stack inside the image, which keeps the container rootless, multi-architecture, and compatible with Talos nodes that already load the AMDGPU kernel driver.

## Endpoint

- `GET /metrics` on port `9494`

## Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `LISTEN_ADDR` | no | `:9494` | HTTP listen address |
| `SYSFS_ROOT` | no | `/sys` | Root of the sysfs tree to scrape |

For Kubernetes, mount the host `/sys` read-only and set `SYSFS_ROOT=/host/sys`.

## Metrics

Device discovery and health:

- `rocm_smi_gpus_discovered`
- `rocm_smi_gpu_info{card,pci_slot,vendor_id,device_id,...}`
- `rocm_smi_scrape_success`
- `rocm_smi_scrape_failures_total`
- `rocm_smi_last_scrape_duration_seconds`

AMDGPU device metrics when exposed by the kernel:

- `rocm_smi_gpu_busy_percent`
- `rocm_smi_memory_busy_percent`
- `rocm_smi_vram_used_bytes`
- `rocm_smi_vram_total_bytes`
- `rocm_smi_visible_vram_used_bytes`
- `rocm_smi_visible_vram_total_bytes`
- `rocm_smi_gtt_used_bytes`
- `rocm_smi_gtt_total_bytes`
- `rocm_smi_pcie_replay_count`

HWMON metrics when exposed by the kernel:

- `rocm_smi_temperature_celsius{sensor=...}`
- `rocm_smi_power_watts{type=...}`
- `rocm_smi_fan_rpm{sensor=...}`
- `rocm_smi_clock_hertz{sensor=...}`
- `rocm_smi_voltage_volts{sensor=...}`

## Strix Halo Notes

For bottleneck work on llama.cpp and ComfyUI, start with GPU busy, memory busy, VRAM/GTT allocation, clocks, power, and temperature. Linux AMDGPU sysfs exposes memory utilization as a busy percentage, but not always true memory bandwidth in GB/s. If Strix Halo exposes richer values through `gpu_metrics` or AMD SMI CPU metrics, those can be added after validating the files available on the Talos node.

## Kubernetes Example

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: rocm-smi-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: rocm-smi-exporter
  template:
    metadata:
      labels:
        app.kubernetes.io/name: rocm-smi-exporter
    spec:
      nodeSelector:
        node-role.kubernetes.io/rocm-worker: "true"
      tolerations:
        - key: llm-workload
          operator: Equal
          value: "true"
          effect: NoSchedule
      containers:
        - name: exporter
          image: ghcr.io/joryirving/rocm-smi-exporter:rolling
          env:
            - name: SYSFS_ROOT
              value: /host/sys
          ports:
            - name: metrics
              containerPort: 9494
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
            readOnlyRootFilesystem: true
            runAsGroup: 65534
            runAsNonRoot: true
            runAsUser: 65534
          volumeMounts:
            - name: sys
              mountPath: /host/sys
              readOnly: true
      volumes:
        - name: sys
          hostPath:
            path: /sys
            type: Directory
```

## Local Build

```bash
docker buildx bake -f docker-bake.hcl image-local
```
