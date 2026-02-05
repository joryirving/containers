# Ollama with Intel GPU Support

This image provides Ollama with Intel GPU acceleration support for running LLMs on Intel integrated graphics and discrete GPUs.

## Features

- Official Ollama binary with Intel GPU acceleration
- Pre-configured for Intel Xe Graphics and Arc GPUs
- Optimized for running large language models with GPU acceleration
- Includes necessary Intel GPU runtime libraries
- Non-root execution for security

## Building

```bash
# Build the image
./build-ollama-intel.sh

# Build and push to registry
./build-ollama-intel.sh latest --push
```

## Environment Variables

The image comes pre-configured with:

- `OLLAMA_HOST=0.0.0.0` - Listen on all interfaces
- `OLLAMA_INTEL_GPU=true` - Enable Intel GPU acceleration
- `OLLAMA_NUM_GPU=999` - Use all available GPU memory
- `OLLAMA_CONTEXT_LENGTH=65536` - Large context window for specialized models
- `ZES_ENABLE_SYSMAN=1` - Enable Intel GPU system management
- `no_proxy=localhost,127.0.0.1` - Bypass proxy for local connections

## Usage

```bash
# Run with GPU access
docker run -d --device=/dev/dri --gpus=all \
  -v ollama-models:/models \
  -p 11434:11434 \
  joryirving/ollama-intel:latest
```

## Kubernetes Deployment

For Kubernetes deployment, you'll need to ensure:

1. Intel GPU plugin is installed on your nodes
2. Proper device access is configured
3. GPU resources are requested/limited appropriately

Example deployment configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: llm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: joryirving/ollama-intel:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        # Additional environment variables are pre-configured
        volumeMounts:
        - name: models
          mountPath: /models
        securityContext:
          privileged: true  # May be required for GPU access
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ollama-models
      # GPU resource configuration as needed
```

## Supported Hardware

- Intel Arc A-series graphics cards
- Intel Xe integrated graphics (11th gen and newer)
- Intel Data Center GPU Max series (experimental)

## Troubleshooting

### GPU Not Detected

If the GPU is not being detected:

1. Ensure Intel GPU drivers are properly installed on the host
2. Verify that the container has access to `/dev/dri` device
3. Check that the Intel GPU plugin is properly configured in Kubernetes

### Performance Issues

For optimal performance:

1. Ensure adequate GPU memory allocation
2. Use appropriate context lengths for your models
3. Monitor GPU utilization with `intel_gpu_top` or similar tools

### Common Error Messages

- `failed to initialize Intel GPU`: Check driver installation and device access
- `context length exceeded`: Adjust OLLAMA_CONTEXT_LENGTH as needed
- `out of memory`: Increase GPU memory limits or reduce context size