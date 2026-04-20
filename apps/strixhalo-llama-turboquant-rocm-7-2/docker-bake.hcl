target "docker-metadata-action" {}

variable "APP" {
  default = "strixhalo-llama-turboquant-rocm-7-2"
}

variable "VERSION" {
  default = "rolling"
}

variable "SOURCE" {
  default = "https://github.com/unixsysdev/llama-turboquant"
}

variable "TURBOQUANT_SOURCE" {
  default = "unixsysdev/llama-turboquant"
}

variable "TURBOQUANT_REF" {
  default = "main"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
    SOURCE = "${SOURCE}"
    TURBOQUANT_SOURCE = "${TURBOQUANT_SOURCE}"
    TURBOQUANT_REF = "${TURBOQUANT_REF}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
  tags = ["${APP}:${VERSION}"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64"
  ]
}
