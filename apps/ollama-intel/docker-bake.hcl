target "docker-metadata-action" {}

variable "APP" {
  default = "ollama-intel"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=ollama/ollama
  default = "0.5.4"
}

variable "SOURCE" {
  default = "https://github.com/joryirving/containers"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
  tags = ["${APP}:${VERSION}", "${APP}:latest"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64"
  ]
  # Note: Only amd64 is supported for Intel GPU acceleration
}