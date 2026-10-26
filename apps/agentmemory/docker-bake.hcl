target "docker-metadata-action" {}

variable "APP" {
  default = "agentmemory"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=rohitg00/agentmemory
  default = "0.9.31"
}

variable "SOURCE" {
  default = "https://github.com/rohitg00/agentmemory"
}

variable "III_VERSION" {
  // Pinned manually, no renovate annotation: agentmemory 0.9.31 upgrades its
  // runtime to iii 0.25.0 with Worker Compose, and the engine version must
  // move together with the agentmemory package. Sync this pin (plus the
  // FROM digest and the STATE_VERSION/HTTP_VERSION worker pins in the
  // Dockerfile) from the agentmemory release notes on every agentmemory bump.
  default = "0.25.0"
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