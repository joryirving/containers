# hoymiles-exporter

Small Prometheus exporter for a Hoymiles DTU-Pro/DTU-Pro-S over Modbus TCP (`hoymiles_modbus`).

This exporter is independent of Home Assistant, MQTT, and InfluxDB.

## Exposed endpoint

- `GET /metrics`

## Configuration

All configuration is done via environment variables.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `DTU_HOST` | yes | none | DTU hostname or IP (for example: `solar.internal`) |
| `DTU_PORT` | no | `502` | Modbus TCP port |
| `DTU_UNIT_ID` | no | `1` | Modbus unit/slave ID |
| `SCRAPE_INTERVAL_SECONDS` | no | `30` | Poll interval for DTU reads |
| `LISTEN_PORT` | no | `9099` | HTTP listen port for exporter |
| `LOG_LEVEL` | no | `INFO` | Python log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Metrics

Installation-level gauges:

- `hoymiles_pv_power_watts`
- `hoymiles_today_production_watt_hours`
- `hoymiles_total_production_watt_hours`

Per-inverter gauges (label: `inverter_serial`):

- `hoymiles_inverter_pv_power_watts`
- `hoymiles_inverter_today_production_watt_hours`
- `hoymiles_inverter_total_production_watt_hours`

Per-port/channel gauges (labels: `inverter_serial`, `port`):

- `hoymiles_inverter_port_pv_power_watts`
- `hoymiles_inverter_port_pv_voltage_volts`
- `hoymiles_inverter_port_pv_current_amps`

Exporter health metrics:

- `hoymiles_scrape_success` (`1` on latest success, `0` on latest failure)
- `hoymiles_scrape_failures_total` (counter)
- `hoymiles_last_scrape_timestamp_seconds` (unix timestamp)

On scrape failure, the exporter keeps the last good metric values and updates only the exporter health metrics.

## Example PromQL

- Current plant production:
  - `hoymiles_pv_power_watts`
- Plant production today in kWh:
  - `hoymiles_today_production_watt_hours / 1000`
- Per-inverter live power:
  - `sum by (inverter_serial) (hoymiles_inverter_pv_power_watts)`
- Per-port live power for one inverter:
  - `hoymiles_inverter_port_pv_power_watts{inverter_serial="112233445566"}`
- Scrape failure rate over 15m:
  - `rate(hoymiles_scrape_failures_total[15m])`
- Alert candidate for stale scrapes (no scrape in 2 intervals):
  - `time() - hoymiles_last_scrape_timestamp_seconds > (2 * 30)`

## Local run

```bash
cd apps/hoymiles-exporter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DTU_HOST=solar.internal python exporter.py
```

## Container build

```bash
docker buildx bake -f docker-bake.hcl image-local
```
