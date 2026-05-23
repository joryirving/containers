target "docker-metadata-action" {}

variable "APP" {
  default = "agentmemory"
}

variable "VERSION" {
  default = "0.9.21"
}

variable "SOURCE" {
  default = "https://github.com/rohitg00/agentmemory"
}

variable "III_VERSION" {
  // renovate: datasource=docker depName=docker.io/iiidev/iii
  default = "0.12.0"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
    AGENTMEMORY_VERSION = "${VERSION}"
    III_VERSION = "${III_VERSION}"
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
    "linux/amd64",
    "linux/arm64"
  ]
}