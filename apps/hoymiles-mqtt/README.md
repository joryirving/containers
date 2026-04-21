# hoymiles-mqtt

Publishes Hoymiles DTU data to MQTT for Home Assistant discovery.

## Quick Start

Example local run:

```bash
docker run --rm \
  -e MQTT_BROKER=192.168.1.10 \
  -e DTU_HOST=192.168.1.20 \
  -e LOG_TO_CONSOLE=true \
  ghcr.io/joryirving/hoymiles-mqtt:rolling
```

## Configuration

Required environment variables:

| Config | Description | Default |
|--------|-------------|---------|
| MQTT_BROKER | Hostname or IP address of the MQTT broker | |
| DTU_HOST | Hostname or IP address of the Hoymiles DTU | |

Optional environment variables:

| Config | Description | Default |
|--------|-------------|---------|
| MQTT_PORT | MQTT broker port | `1883` |
| MQTT_USER | MQTT username | |
| MQTT_PASSWORD | MQTT password | |
| MQTT_TLS | Enable TLS for MQTT connection | `false` |
| MQTT_TLS_INSECURE | Skip MQTT TLS certificate verification | `false` |
| DTU_PORT | DTU Modbus TCP port | `502` |
| MODBUS_UNIT_ID | DTU Modbus unit ID | `1` |
| QUERY_PERIOD | Polling interval in seconds | `60` |
| EXPIRE_AFTER | Mark entities unavailable after this many seconds | `0` |
| COMM_TIMEOUT | Modbus request timeout in seconds | `3` |
| COMM_RETRIES | Modbus retries per request | `3` |
| COMM_RECONNECT_DELAY | Initial reconnect delay in seconds | `0` |
| COMM_RECONNECT_DELAY_MAX | Maximum reconnect delay in seconds | `300` |
| LOG_LEVEL | Python log level | `WARNING` |
| LOG_TO_CONSOLE | Enable console logging | `false` |

## Kubernetes Notes

This container does not expose an inbound service. The pod only needs outbound access to:

- the Hoymiles DTU on TCP `502`
- your MQTT broker on its configured port

For troubleshooting, set `LOG_TO_CONSOLE=true` and optionally `LOG_LEVEL=DEBUG`.

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hoymiles-mqtt
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hoymiles-mqtt
  template:
    metadata:
      labels:
        app: hoymiles-mqtt
    spec:
      containers:
        - name: hoymiles-mqtt
          image: ghcr.io/joryirving/hoymiles-mqtt:rolling
          securityContext:
            runAsNonRoot: true
            runAsUser: 65534
            runAsGroup: 65534
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
          env:
            - name: MQTT_BROKER
              value: mqtt.default.svc
            - name: DTU_HOST
              value: 192.168.1.20
            - name: LOG_TO_CONSOLE
              value: "true"
```
