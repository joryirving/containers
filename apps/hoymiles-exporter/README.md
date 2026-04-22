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
| `EXPECTED_INVERTER_SERIALS` | no | empty | Comma-separated inverter serials expected to be online (for offline detection metrics) |

`EXPECTED_INVERTER_SERIALS` is optional. Offline/online detection works from DTU-reported inverter link status without hardcoding when the DTU includes all registered inverters in Modbus data.

## Metrics

Installation-level gauges:

- `hoymiles_dtu_info{dtu_serial,dtu_host,dtu_port,dtu_unit_id}`
- `hoymiles_inverter_expected_info{inverter_serial}`
- `hoymiles_inverter_expected_online{inverter_serial}`
- `hoymiles_pv_power_watts`
- `hoymiles_today_production_watt_hours`
- `hoymiles_total_production_watt_hours`
- `hoymiles_plant_alarm_flag`
- `hoymiles_inverters_reported`
- `hoymiles_inverter_ports_reported`

Per-inverter gauges (label: `inverter_serial`):

- `hoymiles_inverter_pv_power_watts`
- `hoymiles_inverter_today_production_watt_hours`
- `hoymiles_inverter_total_production_watt_hours`
- `hoymiles_inverter_temperature_celsius`
- `hoymiles_inverter_grid_voltage_volts`
- `hoymiles_inverter_grid_frequency_hz`
- `hoymiles_inverter_operating_status`
- `hoymiles_inverter_alarm_code`
- `hoymiles_inverter_alarm_count`
- `hoymiles_inverter_link_status`
- `hoymiles_inverter_registered_info`
- `hoymiles_inverter_online`
- `hoymiles_inverter_offline`
- `hoymiles_inverter_data_type`
- `hoymiles_inverter_port_count`

Per-port/channel gauges (labels: `inverter_serial`, `port`):

- `hoymiles_inverter_port_pv_power_watts`
- `hoymiles_inverter_port_pv_voltage_volts`
- `hoymiles_inverter_port_pv_current_amps`
- `hoymiles_inverter_port_temperature_celsius`
- `hoymiles_inverter_port_grid_voltage_volts`
- `hoymiles_inverter_port_grid_frequency_hz`
- `hoymiles_inverter_port_today_production_watt_hours`
- `hoymiles_inverter_port_total_production_watt_hours`
- `hoymiles_inverter_port_operating_status`
- `hoymiles_inverter_port_alarm_code`
- `hoymiles_inverter_port_alarm_count`
- `hoymiles_inverter_port_link_status`
- `hoymiles_inverter_port_data_type`

Exporter health metrics:

- `hoymiles_scrape_success` (`1` on latest success, `0` on latest failure)
- `hoymiles_scrape_failures_total` (counter)
- `hoymiles_last_scrape_timestamp_seconds` (unix timestamp)
- `hoymiles_last_scrape_duration_seconds` (duration of latest scrape)

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
- Per-inverter temperature:
  - `hoymiles_inverter_temperature_celsius`
- Per-port temperature for one inverter:
  - `hoymiles_inverter_port_temperature_celsius{inverter_serial="112233445566"}`
- Inverters reporting alarms right now:
  - `hoymiles_inverter_alarm_code > 0`
- Link status by inverter:
  - `hoymiles_inverter_link_status`
- Expected inverters that are currently offline or missing:
  - `hoymiles_inverter_expected_online == 0`
- DTU-reported inverters currently offline (no hardcoded list needed):
  - `hoymiles_inverter_offline == 1`
- How many inverter ports are currently reported:
  - `hoymiles_inverter_ports_reported`
- Scrape failure rate over 15m:
  - `rate(hoymiles_scrape_failures_total[15m])`
- Alert candidate for stale scrapes (no scrape in 2 intervals):
  - `time() - hoymiles_last_scrape_timestamp_seconds > (2 * 30)`

## Recording Rules

Example rule group you can paste into your Prometheus rules config:

```yaml
groups:
  - name: hoymiles-exporter
    interval: 30s
    rules:
      - record: hoymiles:site:pv_power_watts
        expr: hoymiles_pv_power_watts

      - record: hoymiles:site:scrape_age_seconds
        expr: time() - hoymiles_last_scrape_timestamp_seconds

      - record: hoymiles:site:last_scrape_duration_seconds
        expr: hoymiles_last_scrape_duration_seconds

      - record: hoymiles:site:scrape_healthy
        expr: (hoymiles_scrape_success == 1)

      - record: hoymiles:inverter:online
        expr: max by (inverter_serial) (hoymiles_inverter_online)

      - record: hoymiles:inverter:offline
        expr: max by (inverter_serial) (hoymiles_inverter_offline)

      - record: hoymiles:inverter:expected_online
        expr: max by (inverter_serial) (hoymiles_inverter_expected_online)

      - record: hoymiles:inverter:expected_offline
        expr: clamp_min(hoymiles_inverter_expected_info - hoymiles_inverter_expected_online, 0)

      - record: hoymiles:inverter:temperature_celsius
        expr: max by (inverter_serial) (hoymiles_inverter_temperature_celsius)
```

With `EXPECTED_INVERTER_SERIALS` configured, `hoymiles:inverter:expected_offline == 1` means an expected inverter is either not reporting or reporting `link_status=0`.

## Alerting Rules

Example alert rules you can pair with the recordings above:

```yaml
groups:
  - name: hoymiles-exporter-alerts
    rules:
      - alert: HoymilesExporterScrapeFailing
        expr: hoymiles:site:scrape_healthy == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Hoymiles exporter scrape is failing
          description: hoymiles-exporter has not completed a successful scrape for 5 minutes.

      - alert: HoymilesExporterScrapeStale
        expr: hoymiles:site:scrape_age_seconds > 120
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Hoymiles exporter data is stale
          description: Last scrape timestamp is older than 120 seconds for over 10 minutes.

      - alert: HoymilesExpectedInverterOffline
        expr: hoymiles:inverter:expected_offline == 1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: Expected Hoymiles inverter is offline
          description: Expected inverter {{ $labels.inverter_serial }} is offline or missing.
```

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
