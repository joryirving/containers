from __future__ import annotations

import logging
import os
import signal
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from hoymiles_modbus.client import HoymilesModbusTCP
from prometheus_client import Counter, Gauge, start_http_server


@dataclass(frozen=True)
class Config:
    dtu_host: str
    dtu_port: int
    dtu_unit_id: int
    scrape_interval_seconds: int
    listen_port: int
    log_level: int
    expected_inverter_serials: tuple[str, ...]


HOYMILES_PV_POWER_WATTS = Gauge(
    "hoymiles_pv_power_watts",
    "Current plant PV power in watts.",
)
HOYMILES_TODAY_PRODUCTION_WH = Gauge(
    "hoymiles_today_production_watt_hours",
    "Plant production today in watt-hours.",
)
HOYMILES_TOTAL_PRODUCTION_WH = Gauge(
    "hoymiles_total_production_watt_hours",
    "Plant total production in watt-hours.",
)
HOYMILES_PLANT_ALARM_FLAG = Gauge(
    "hoymiles_plant_alarm_flag",
    "1 if at least one inverter reports an alarm, 0 otherwise.",
)
HOYMILES_INVERTERS_REPORTED = Gauge(
    "hoymiles_inverters_reported",
    "Number of unique inverter serials in the most recent successful scrape.",
)
HOYMILES_INVERTER_PORTS_REPORTED = Gauge(
    "hoymiles_inverter_ports_reported",
    "Number of inverter port records in the most recent successful scrape.",
)
HOYMILES_DTU_INFO = Gauge(
    "hoymiles_dtu_info",
    "Static DTU metadata as labels (always 1).",
    ["dtu_serial", "dtu_host", "dtu_port", "dtu_unit_id"],
)
HOYMILES_INVERTER_EXPECTED_INFO = Gauge(
    "hoymiles_inverter_expected_info",
    "Configured expected inverters as labels (always 1).",
    ["inverter_serial"],
)
HOYMILES_INVERTER_EXPECTED_ONLINE = Gauge(
    "hoymiles_inverter_expected_online",
    "Configured expected inverter online status (1 online, 0 offline/missing).",
    ["inverter_serial"],
)

HOYMILES_INVERTER_PV_POWER_WATTS = Gauge(
    "hoymiles_inverter_pv_power_watts",
    "Current inverter PV power in watts.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_TODAY_PRODUCTION_WH = Gauge(
    "hoymiles_inverter_today_production_watt_hours",
    "Inverter production today in watt-hours.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_TOTAL_PRODUCTION_WH = Gauge(
    "hoymiles_inverter_total_production_watt_hours",
    "Inverter total production in watt-hours.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_TEMPERATURE_CELSIUS = Gauge(
    "hoymiles_inverter_temperature_celsius",
    "Current inverter temperature in celsius.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_GRID_VOLTAGE_VOLTS = Gauge(
    "hoymiles_inverter_grid_voltage_volts",
    "Current inverter grid voltage in volts.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_GRID_FREQUENCY_HZ = Gauge(
    "hoymiles_inverter_grid_frequency_hz",
    "Current inverter grid frequency in hertz.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_OPERATING_STATUS = Gauge(
    "hoymiles_inverter_operating_status",
    "Current inverter operating status code.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_ALARM_CODE = Gauge(
    "hoymiles_inverter_alarm_code",
    "Current inverter alarm code.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_ALARM_COUNT = Gauge(
    "hoymiles_inverter_alarm_count",
    "Current inverter alarm count.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_LINK_STATUS = Gauge(
    "hoymiles_inverter_link_status",
    "Current inverter link status (typically 0 or 1).",
    ["inverter_serial"],
)
HOYMILES_INVERTER_DATA_TYPE = Gauge(
    "hoymiles_inverter_data_type",
    "Current inverter data type code from DTU record.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_PORT_COUNT = Gauge(
    "hoymiles_inverter_port_count",
    "Number of port records seen for this inverter in latest successful scrape.",
    ["inverter_serial"],
)
HOYMILES_INVERTER_REGISTERED_INFO = Gauge(
    "hoymiles_inverter_registered_info",
    "Inverters currently reported by DTU as labels (always 1).",
    ["inverter_serial"],
)
HOYMILES_INVERTER_ONLINE = Gauge(
    "hoymiles_inverter_online",
    "Current inverter online status derived from link status (1 online, 0 offline).",
    ["inverter_serial"],
)
HOYMILES_INVERTER_OFFLINE = Gauge(
    "hoymiles_inverter_offline",
    "Current inverter offline status derived from link status (1 offline, 0 online).",
    ["inverter_serial"],
)

HOYMILES_INVERTER_PORT_PV_POWER_WATTS = Gauge(
    "hoymiles_inverter_port_pv_power_watts",
    "Current inverter port/channel PV power in watts.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_PV_VOLTAGE_VOLTS = Gauge(
    "hoymiles_inverter_port_pv_voltage_volts",
    "Current inverter port/channel PV voltage in volts.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_PV_CURRENT_AMPS = Gauge(
    "hoymiles_inverter_port_pv_current_amps",
    "Current inverter port/channel PV current in amps.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_TEMPERATURE_CELSIUS = Gauge(
    "hoymiles_inverter_port_temperature_celsius",
    "Current inverter port/channel inverter temperature in celsius.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_GRID_VOLTAGE_VOLTS = Gauge(
    "hoymiles_inverter_port_grid_voltage_volts",
    "Current inverter port/channel grid voltage in volts.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_GRID_FREQUENCY_HZ = Gauge(
    "hoymiles_inverter_port_grid_frequency_hz",
    "Current inverter port/channel grid frequency in hertz.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_TODAY_PRODUCTION_WH = Gauge(
    "hoymiles_inverter_port_today_production_watt_hours",
    "Current inverter port/channel production today in watt-hours.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_TOTAL_PRODUCTION_WH = Gauge(
    "hoymiles_inverter_port_total_production_watt_hours",
    "Current inverter port/channel total production in watt-hours.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_OPERATING_STATUS = Gauge(
    "hoymiles_inverter_port_operating_status",
    "Current inverter port/channel operating status code.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_ALARM_CODE = Gauge(
    "hoymiles_inverter_port_alarm_code",
    "Current inverter port/channel alarm code.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_ALARM_COUNT = Gauge(
    "hoymiles_inverter_port_alarm_count",
    "Current inverter port/channel alarm count.",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_LINK_STATUS = Gauge(
    "hoymiles_inverter_port_link_status",
    "Current inverter port/channel link status (typically 0 or 1).",
    ["inverter_serial", "port"],
)
HOYMILES_INVERTER_PORT_DATA_TYPE = Gauge(
    "hoymiles_inverter_port_data_type",
    "Current inverter port/channel data type code from DTU record.",
    ["inverter_serial", "port"],
)

HOYMILES_SCRAPE_SUCCESS = Gauge(
    "hoymiles_scrape_success",
    "1 if the latest scrape succeeded, 0 otherwise.",
)
HOYMILES_SCRAPE_FAILURES_TOTAL = Counter(
    "hoymiles_scrape_failures_total",
    "Total number of scrape failures.",
)
HOYMILES_LAST_SCRAPE_UNIX_TIME = Gauge(
    "hoymiles_last_scrape_timestamp_seconds",
    "Unix timestamp of the most recent scrape attempt.",
)
HOYMILES_LAST_SCRAPE_DURATION_SECONDS = Gauge(
    "hoymiles_last_scrape_duration_seconds",
    "Duration of the most recent scrape attempt in seconds.",
)


def _env_int(name: str, default: int | None) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        if default is None:
            raise ValueError(f"{name} must be set")
        return default

    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc

    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _env_log_level(name: str, default: str = "INFO") -> int:
    level_name = os.getenv(name, default).upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        raise ValueError(f"{name} must be a valid log level, got {level_name!r}")
    return level


def _env_serial_list(name: str) -> tuple[str, ...]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return ()

    values = [part.strip() for part in raw.split(",") if part.strip()]
    deduped = tuple(dict.fromkeys(values))
    return deduped


def load_config() -> Config:
    dtu_host = os.getenv("DTU_HOST", "").strip()
    if not dtu_host:
        raise ValueError("DTU_HOST must be set")

    return Config(
        dtu_host=dtu_host,
        dtu_port=_env_int("DTU_PORT", 502),
        dtu_unit_id=_env_int("DTU_UNIT_ID", 1),
        scrape_interval_seconds=_env_int("SCRAPE_INTERVAL_SECONDS", 30),
        listen_port=_env_int("LISTEN_PORT", 9099),
        log_level=_env_log_level("LOG_LEVEL", "INFO"),
        expected_inverter_serials=_env_serial_list("EXPECTED_INVERTER_SERIALS"),
    )


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_label(value: Any, default: str = "unknown") -> str:
    text = str(value).strip() if value is not None else ""
    return text if text else default


def _remove_stale_labels(
    previous: set[tuple[str, ...]],
    current: set[tuple[str, ...]],
    gauges: Iterable[Gauge],
) -> None:
    stale = previous - current
    if not stale:
        return

    for labels in stale:
        for gauge in gauges:
            try:
                gauge.remove(*labels)
            except KeyError:
                pass


class HoymilesExporter:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = HoymilesModbusTCP(
            host=config.dtu_host,
            port=config.dtu_port,
            unit_id=config.dtu_unit_id,
        )
        self._known_inverter_labels: set[tuple[str, ...]] = set()
        self._known_port_labels: set[tuple[str, ...]] = set()

    def scrape(self) -> None:
        plant = self._client.plant_data

        HOYMILES_PV_POWER_WATTS.set(_to_float(getattr(plant, "pv_power", 0)))
        HOYMILES_TODAY_PRODUCTION_WH.set(
            _to_float(getattr(plant, "today_production", 0))
        )
        HOYMILES_TOTAL_PRODUCTION_WH.set(
            _to_float(getattr(plant, "total_production", 0))
        )
        HOYMILES_PLANT_ALARM_FLAG.set(
            1.0 if bool(getattr(plant, "alarm_flag", False)) else 0.0
        )

        dtu_serial = _to_label(getattr(plant, "dtu", None))
        HOYMILES_DTU_INFO.labels(
            dtu_serial,
            self._config.dtu_host,
            str(self._config.dtu_port),
            str(self._config.dtu_unit_id),
        ).set(1.0)

        inverter_rollup: dict[str, dict[str, float | None]] = {}
        current_port_labels: set[tuple[str, ...]] = set()
        port_records = 0

        for record in getattr(plant, "inverters", []):
            port_records += 1
            inverter_serial = _to_label(getattr(record, "serial_number", None))
            port = _to_label(getattr(record, "port_number", None), default="0")
            labels = (inverter_serial, port)
            current_port_labels.add(labels)

            pv_power = _to_float(getattr(record, "pv_power", 0))
            today_production = _to_float(getattr(record, "today_production", 0))
            total_production = _to_float(getattr(record, "total_production", 0))
            temperature = (
                _to_float(getattr(record, "temperature", None))
                if hasattr(record, "temperature")
                else None
            )
            pv_voltage = (
                _to_float(getattr(record, "pv_voltage", None))
                if hasattr(record, "pv_voltage")
                else None
            )
            pv_current = (
                _to_float(getattr(record, "pv_current", None))
                if hasattr(record, "pv_current")
                else None
            )
            grid_voltage = (
                _to_float(getattr(record, "grid_voltage", None))
                if hasattr(record, "grid_voltage")
                else None
            )
            grid_frequency = (
                _to_float(getattr(record, "grid_frequency", None))
                if hasattr(record, "grid_frequency")
                else None
            )
            operating_status = (
                _to_float(getattr(record, "operating_status", None))
                if hasattr(record, "operating_status")
                else None
            )
            alarm_code = (
                _to_float(getattr(record, "alarm_code", None))
                if hasattr(record, "alarm_code")
                else None
            )
            alarm_count = (
                _to_float(getattr(record, "alarm_count", None))
                if hasattr(record, "alarm_count")
                else None
            )
            link_status = (
                _to_float(getattr(record, "link_status", None))
                if hasattr(record, "link_status")
                else None
            )
            data_type = (
                _to_float(getattr(record, "data_type", None))
                if hasattr(record, "data_type")
                else None
            )

            HOYMILES_INVERTER_PORT_PV_POWER_WATTS.labels(*labels).set(pv_power)
            HOYMILES_INVERTER_PORT_TODAY_PRODUCTION_WH.labels(*labels).set(
                today_production
            )
            HOYMILES_INVERTER_PORT_TOTAL_PRODUCTION_WH.labels(*labels).set(
                total_production
            )

            if pv_voltage is not None:
                HOYMILES_INVERTER_PORT_PV_VOLTAGE_VOLTS.labels(*labels).set(pv_voltage)
            if pv_current is not None:
                HOYMILES_INVERTER_PORT_PV_CURRENT_AMPS.labels(*labels).set(pv_current)
            if temperature is not None:
                HOYMILES_INVERTER_PORT_TEMPERATURE_CELSIUS.labels(*labels).set(
                    temperature
                )
            if grid_voltage is not None:
                HOYMILES_INVERTER_PORT_GRID_VOLTAGE_VOLTS.labels(*labels).set(
                    grid_voltage
                )
            if grid_frequency is not None:
                HOYMILES_INVERTER_PORT_GRID_FREQUENCY_HZ.labels(*labels).set(
                    grid_frequency
                )
            if operating_status is not None:
                HOYMILES_INVERTER_PORT_OPERATING_STATUS.labels(*labels).set(
                    operating_status
                )
            if alarm_code is not None:
                HOYMILES_INVERTER_PORT_ALARM_CODE.labels(*labels).set(alarm_code)
            if alarm_count is not None:
                HOYMILES_INVERTER_PORT_ALARM_COUNT.labels(*labels).set(alarm_count)
            if link_status is not None:
                HOYMILES_INVERTER_PORT_LINK_STATUS.labels(*labels).set(link_status)
            if data_type is not None:
                HOYMILES_INVERTER_PORT_DATA_TYPE.labels(*labels).set(data_type)

            totals = inverter_rollup.setdefault(
                inverter_serial,
                {
                    "pv_power": 0.0,
                    "today_production": 0.0,
                    "total_production": 0.0,
                    "temperature": None,
                    "grid_voltage": None,
                    "grid_frequency": None,
                    "operating_status": None,
                    "alarm_code": None,
                    "alarm_count": None,
                    "link_status": None,
                    "data_type": None,
                    "port_count": 0.0,
                },
            )
            totals["pv_power"] += pv_power
            totals["today_production"] = max(
                totals["today_production"], today_production
            )
            totals["total_production"] = max(
                totals["total_production"], total_production
            )
            totals["port_count"] += 1
            if temperature is not None:
                prior_temp = totals["temperature"]
                totals["temperature"] = (
                    temperature
                    if prior_temp is None
                    else max(float(prior_temp), temperature)
                )
            if grid_voltage is not None:
                prior_grid_voltage = totals["grid_voltage"]
                totals["grid_voltage"] = (
                    grid_voltage
                    if prior_grid_voltage is None
                    else max(float(prior_grid_voltage), grid_voltage)
                )
            if grid_frequency is not None:
                prior_grid_frequency = totals["grid_frequency"]
                totals["grid_frequency"] = (
                    grid_frequency
                    if prior_grid_frequency is None
                    else max(float(prior_grid_frequency), grid_frequency)
                )
            if operating_status is not None:
                prior_operating_status = totals["operating_status"]
                totals["operating_status"] = (
                    operating_status
                    if prior_operating_status is None
                    else max(float(prior_operating_status), operating_status)
                )
            if alarm_code is not None:
                prior_alarm_code = totals["alarm_code"]
                totals["alarm_code"] = (
                    alarm_code
                    if prior_alarm_code is None
                    else max(float(prior_alarm_code), alarm_code)
                )
            if alarm_count is not None:
                prior_alarm_count = totals["alarm_count"]
                totals["alarm_count"] = (
                    alarm_count
                    if prior_alarm_count is None
                    else max(float(prior_alarm_count), alarm_count)
                )
            if link_status is not None:
                prior_link_status = totals["link_status"]
                totals["link_status"] = (
                    link_status
                    if prior_link_status is None
                    else max(float(prior_link_status), link_status)
                )
            if data_type is not None:
                prior_data_type = totals["data_type"]
                totals["data_type"] = (
                    data_type
                    if prior_data_type is None
                    else max(float(prior_data_type), data_type)
                )

        current_inverter_labels: set[tuple[str, ...]] = set()
        for inverter_serial, totals in inverter_rollup.items():
            labels = (inverter_serial,)
            current_inverter_labels.add(labels)
            HOYMILES_INVERTER_REGISTERED_INFO.labels(*labels).set(1.0)

            inverter_link_status = totals["link_status"]
            inverter_online = (
                1.0
                if inverter_link_status is not None and float(inverter_link_status) > 0
                else 0.0
            )
            HOYMILES_INVERTER_ONLINE.labels(*labels).set(inverter_online)
            HOYMILES_INVERTER_OFFLINE.labels(*labels).set(1.0 - inverter_online)

            HOYMILES_INVERTER_PV_POWER_WATTS.labels(*labels).set(totals["pv_power"])
            HOYMILES_INVERTER_TODAY_PRODUCTION_WH.labels(*labels).set(
                totals["today_production"]
            )
            HOYMILES_INVERTER_TOTAL_PRODUCTION_WH.labels(*labels).set(
                totals["total_production"]
            )
            inverter_temperature = totals["temperature"]
            if inverter_temperature is not None:
                HOYMILES_INVERTER_TEMPERATURE_CELSIUS.labels(*labels).set(
                    float(inverter_temperature)
                )
            inverter_grid_voltage = totals["grid_voltage"]
            if inverter_grid_voltage is not None:
                HOYMILES_INVERTER_GRID_VOLTAGE_VOLTS.labels(*labels).set(
                    float(inverter_grid_voltage)
                )
            inverter_grid_frequency = totals["grid_frequency"]
            if inverter_grid_frequency is not None:
                HOYMILES_INVERTER_GRID_FREQUENCY_HZ.labels(*labels).set(
                    float(inverter_grid_frequency)
                )
            inverter_operating_status = totals["operating_status"]
            if inverter_operating_status is not None:
                HOYMILES_INVERTER_OPERATING_STATUS.labels(*labels).set(
                    float(inverter_operating_status)
                )
            inverter_alarm_code = totals["alarm_code"]
            if inverter_alarm_code is not None:
                HOYMILES_INVERTER_ALARM_CODE.labels(*labels).set(
                    float(inverter_alarm_code)
                )
            inverter_alarm_count = totals["alarm_count"]
            if inverter_alarm_count is not None:
                HOYMILES_INVERTER_ALARM_COUNT.labels(*labels).set(
                    float(inverter_alarm_count)
                )
            if inverter_link_status is not None:
                HOYMILES_INVERTER_LINK_STATUS.labels(*labels).set(
                    float(inverter_link_status)
                )
            inverter_data_type = totals["data_type"]
            if inverter_data_type is not None:
                HOYMILES_INVERTER_DATA_TYPE.labels(*labels).set(
                    float(inverter_data_type)
                )
            HOYMILES_INVERTER_PORT_COUNT.labels(*labels).set(
                float(totals["port_count"])
            )

        for inverter_serial in self._config.expected_inverter_serials:
            HOYMILES_INVERTER_EXPECTED_INFO.labels(inverter_serial).set(1.0)
            observed = inverter_rollup.get(inverter_serial)
            observed_link_status = observed["link_status"] if observed else None
            HOYMILES_INVERTER_EXPECTED_ONLINE.labels(inverter_serial).set(
                1.0
                if observed_link_status is not None and float(observed_link_status) > 0
                else 0.0
            )

        HOYMILES_INVERTERS_REPORTED.set(float(len(current_inverter_labels)))
        HOYMILES_INVERTER_PORTS_REPORTED.set(float(port_records))

        _remove_stale_labels(
            self._known_inverter_labels,
            current_inverter_labels,
            [
                HOYMILES_INVERTER_PV_POWER_WATTS,
                HOYMILES_INVERTER_TODAY_PRODUCTION_WH,
                HOYMILES_INVERTER_TOTAL_PRODUCTION_WH,
                HOYMILES_INVERTER_TEMPERATURE_CELSIUS,
                HOYMILES_INVERTER_GRID_VOLTAGE_VOLTS,
                HOYMILES_INVERTER_GRID_FREQUENCY_HZ,
                HOYMILES_INVERTER_OPERATING_STATUS,
                HOYMILES_INVERTER_ALARM_CODE,
                HOYMILES_INVERTER_ALARM_COUNT,
                HOYMILES_INVERTER_LINK_STATUS,
                HOYMILES_INVERTER_DATA_TYPE,
                HOYMILES_INVERTER_PORT_COUNT,
                HOYMILES_INVERTER_REGISTERED_INFO,
                HOYMILES_INVERTER_ONLINE,
                HOYMILES_INVERTER_OFFLINE,
            ],
        )
        _remove_stale_labels(
            self._known_port_labels,
            current_port_labels,
            [
                HOYMILES_INVERTER_PORT_PV_POWER_WATTS,
                HOYMILES_INVERTER_PORT_PV_VOLTAGE_VOLTS,
                HOYMILES_INVERTER_PORT_PV_CURRENT_AMPS,
                HOYMILES_INVERTER_PORT_TEMPERATURE_CELSIUS,
                HOYMILES_INVERTER_PORT_GRID_VOLTAGE_VOLTS,
                HOYMILES_INVERTER_PORT_GRID_FREQUENCY_HZ,
                HOYMILES_INVERTER_PORT_TODAY_PRODUCTION_WH,
                HOYMILES_INVERTER_PORT_TOTAL_PRODUCTION_WH,
                HOYMILES_INVERTER_PORT_OPERATING_STATUS,
                HOYMILES_INVERTER_PORT_ALARM_CODE,
                HOYMILES_INVERTER_PORT_ALARM_COUNT,
                HOYMILES_INVERTER_PORT_LINK_STATUS,
                HOYMILES_INVERTER_PORT_DATA_TYPE,
            ],
        )

        self._known_inverter_labels = current_inverter_labels
        self._known_port_labels = current_port_labels

    def scrape_once_with_health_metrics(self) -> None:
        started = time.time()
        try:
            self.scrape()
            HOYMILES_SCRAPE_SUCCESS.set(1)
        except Exception:
            HOYMILES_SCRAPE_SUCCESS.set(0)
            HOYMILES_SCRAPE_FAILURES_TOTAL.inc()
            logging.exception("Scrape failed")
        finally:
            duration = time.time() - started
            HOYMILES_LAST_SCRAPE_UNIX_TIME.set(time.time())
            HOYMILES_LAST_SCRAPE_DURATION_SECONDS.set(duration)
            logging.debug("Scrape attempt completed in %.3fs", duration)

    def run(self, stop_event: threading.Event) -> None:
        logging.info(
            "Starting scrape loop: host=%s port=%d unit_id=%d interval=%ds expected_inverters=%d",
            self._config.dtu_host,
            self._config.dtu_port,
            self._config.dtu_unit_id,
            self._config.scrape_interval_seconds,
            len(self._config.expected_inverter_serials),
        )
        while not stop_event.is_set():
            loop_started = time.monotonic()
            self.scrape_once_with_health_metrics()
            elapsed = time.monotonic() - loop_started
            sleep_for = max(0.0, self._config.scrape_interval_seconds - elapsed)
            stop_event.wait(sleep_for)


def main() -> int:
    try:
        config = load_config()
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return 1

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    start_http_server(config.listen_port, addr="0.0.0.0")
    logging.info("Metrics endpoint listening on 0.0.0.0:%d/metrics", config.listen_port)

    exporter = HoymilesExporter(config)
    stop_event = threading.Event()

    def _signal_handler(signum: int, _frame: Any) -> None:
        logging.info("Received signal %d, stopping exporter", signum)
        stop_event.set()

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    exporter.run(stop_event)
    logging.info("Exporter stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
