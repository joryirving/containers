# amdgpu-exporter

Small Prometheus exporter for AMDGPU/ROCm telemetry on Kubernetes nodes.

The exporter reads Linux AMDGPU sysfs, hwmon, and DRM client fdinfo files directly. It does not require the ROCm userspace stack inside the image, which keeps the image small and compatible with Talos nodes that already load the AMDGPU kernel driver.

## Endpoint

- `GET /metrics` on port `9494`

## Configuration

| Variable      | Required | Default | Description                       |
| ------------- | -------- | ------- | --------------------------------- |
| `LISTEN_ADDR` | no       | `:9494` | HTTP listen address               |
| `PROC_ROOT`   | no       | `/proc` | Root of the procfs tree to scrape |
| `SYSFS_ROOT`  | no       | `/sys`  | Root of the sysfs tree to scrape  |

For Kubernetes, mount the host `/proc` and `/sys` read-only and set `PROC_ROOT=/host/proc` and `SYSFS_ROOT=/host/sys`. The process must run as root to read other containers' `/proc/<pid>/fdinfo` entries; it drops all capabilities and does not need privilege escalation.

## Metrics

Device discovery and health:

- `amdgpu_gpus_discovered`
- `amdgpu_gpu_info{card,pci_slot,vendor_id,device_id,...}`
- `amdgpu_scrape_success`
- `amdgpu_scrape_failures_total`
- `amdgpu_last_scrape_duration_seconds`

AMDGPU device metrics when exposed by the kernel:

- `amdgpu_gpu_busy_percent`
- `amdgpu_memory_busy_percent`
- `amdgpu_vram_used_bytes`
- `amdgpu_vram_total_bytes`
- `amdgpu_visible_vram_used_bytes`
- `amdgpu_visible_vram_total_bytes`
- `amdgpu_gtt_used_bytes`
- `amdgpu_gtt_total_bytes`
- `amdgpu_pcie_replay_total (counter)`

HWMON metrics when exposed by the kernel:

- `amdgpu_temperature_celsius{sensor=...}`
- `amdgpu_power_watts{sensor=...,type=...}`
- `amdgpu_fan_rpm{sensor=...}`
- `amdgpu_clock_hertz{sensor=...}`
- `amdgpu_voltage_volts{sensor=...}`

Per-DRM-client metrics:

- `amdgpu_drm_client_memory_bytes{card,pci_slot,client_id,pid,process,pod_uid,container_id,region,state}`

`region` is `cpu`, `gtt`, or `vram`; `state` is `total`, `resident`, or `purgeable` when the kernel reports it. The exporter deduplicates multiple file descriptors for the same `(pci_slot, client_id)`. `pod_uid` can be joined to `kube_pod_info.uid` in PromQL to attribute a client to a Kubernetes pod.

## Strix Halo Notes

For bottleneck work on llama.cpp and ComfyUI, start with GPU busy, memory busy, VRAM/GTT allocation, per-client resident GTT, clocks, power, and temperature. Linux AMDGPU sysfs exposes device-wide memory totals; DRM fdinfo provides the per-client breakdown. If Strix Halo exposes richer values through `gpu_metrics` or AMD SMI CPU metrics, those can be added after validating the files available on the Talos node.

## Kubernetes Example

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
    name: amdgpu-exporter
    namespace: monitoring
spec:
    selector:
        matchLabels:
            app.kubernetes.io/name: amdgpu-exporter
    template:
        metadata:
            labels:
                app.kubernetes.io/name: amdgpu-exporter
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
                  image: ghcr.io/joryirving/amdgpu-exporter:rolling
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

The example above is device-only. For per-client mode, add `hostPID: true`, a read-only `/proc` hostPath mounted at `/host/proc`, `PROC_ROOT=/host/proc`, and a pod security context of `runAsUser: 0`, `runAsGroup: 0`, and `runAsNonRoot: false`.

## Local Build

```bash
docker buildx bake -f docker-bake.hcl image-local
```
