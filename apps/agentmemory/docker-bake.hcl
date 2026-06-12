target "docker-metadata-action" {}

variable "APP" {
  default = "agentmemory"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=rohitg00/agentmemory
  default = "0.9.27"
}

variable "SOURCE" {
  default = "https://github.com/rohitg00/agentmemory"
}

variable "III_VERSION" {
  // renovate: datasource=docker depName=docker.io/iiidev/iii
  // Pinned: agentmemory 0.9.21 ships a docker-compose pinning iii 0.11.2.
  // iii >=0.11.6 changes the worker model agentmemory hasn't adopted -> EPIPE
  // reconnect loops and empty search after save. Renovate is constrained to
  // <0.11.6 in .renovaterc.json5; bump only when agentmemory itself moves.
  default = "0.11.2"
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