variable "REGISTRY" {
  default = "ghcr.io"
}

variable "REPOSITORY" {
  default = "joryirving"
}

variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["vllm-openvino"]
}

target "vllm-openvino" {
  context = "."
  dockerfile = "Dockerfile"
  platforms = ["linux/amd64"]
  tags = [
    "${REGISTRY}/${REPOSITORY}/vllm-openvino:${TAG}",
  ]
  cache-from = ["type=gha"]
  cache-to = ["type=gha,mode=max"]
}
