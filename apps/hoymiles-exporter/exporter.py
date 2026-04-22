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

        inverter_rollup: dict[str, dict[str, float]] = {}
        current_port_labels: set[tuple[str, ...]] = set()

        for record in getattr(plant, "inverters", []):
            inverter_serial = _to_label(getattr(record, "serial_number", None))
            port = _to_label(getattr(record, "port_number", None), default="0")
            labels = (inverter_serial, port)
            current_port_labels.add(labels)

            pv_power = _to_float(getattr(record, "pv_power", 0))
            today_production = _to_float(getattr(record, "today_production", 0))
            total_production = _to_float(getattr(record, "total_production", 0))

            HOYMILES_INVERTER_PORT_PV_POWER_WATTS.labels(*labels).set(pv_power)

            if hasattr(record, "pv_voltage"):
                HOYMILES_INVERTER_PORT_PV_VOLTAGE_VOLTS.labels(*labels).set(
                    _to_float(getattr(record, "pv_voltage", 0))
                )
            if hasattr(record, "pv_current"):
                HOYMILES_INVERTER_PORT_PV_CURRENT_AMPS.labels(*labels).set(
                    _to_float(getattr(record, "pv_current", 0))
                )

            totals = inverter_rollup.setdefault(
                inverter_serial,
                {
                    "pv_power": 0.0,
                    "today_production": 0.0,
                    "total_production": 0.0,
                },
            )
            totals["pv_power"] += pv_power
            totals["today_production"] = max(
                totals["today_production"], today_production
            )
            totals["total_production"] = max(
                totals["total_production"], total_production
            )

        current_inverter_labels: set[tuple[str, ...]] = set()
        for inverter_serial, totals in inverter_rollup.items():
            labels = (inverter_serial,)
            current_inverter_labels.add(labels)
            HOYMILES_INVERTER_PV_POWER_WATTS.labels(*labels).set(totals["pv_power"])
            HOYMILES_INVERTER_TODAY_PRODUCTION_WH.labels(*labels).set(
                totals["today_production"]
            )
            HOYMILES_INVERTER_TOTAL_PRODUCTION_WH.labels(*labels).set(
                totals["total_production"]
            )

        _remove_stale_labels(
            self._known_inverter_labels,
            current_inverter_labels,
            [
                HOYMILES_INVERTER_PV_POWER_WATTS,
                HOYMILES_INVERTER_TODAY_PRODUCTION_WH,
                HOYMILES_INVERTER_TOTAL_PRODUCTION_WH,
            ],
        )
        _remove_stale_labels(
            self._known_port_labels,
            current_port_labels,
            [
                HOYMILES_INVERTER_PORT_PV_POWER_WATTS,
                HOYMILES_INVERTER_PORT_PV_VOLTAGE_VOLTS,
                HOYMILES_INVERTER_PORT_PV_CURRENT_AMPS,
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
            HOYMILES_LAST_SCRAPE_UNIX_TIME.set(time.time())
            logging.debug("Scrape attempt completed in %.3fs", time.time() - started)

    def run(self, stop_event: threading.Event) -> None:
        logging.info(
            "Starting scrape loop: host=%s port=%d unit_id=%d interval=%ds",
            self._config.dtu_host,
            self._config.dtu_port,
            self._config.dtu_unit_id,
            self._config.scrape_interval_seconds,
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
