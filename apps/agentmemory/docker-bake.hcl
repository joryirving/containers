target "docker-metadata-action" {}

variable "APP" {
  default = "agentmemory"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=rohitg00/agentmemory
  default = "0.9.32"
}

variable "SOURCE" {
  default = "https://github.com/rohitg00/agentmemory"
}

variable "III_VERSION" {
  // The engine version must move together with the FROM tag in the
  // Dockerfile; the build fails the iii --version guard if they drift.
  // The renovate annotation below uses the same depName as the docker
  // manager resolves for that FROM line, so both are bumped in one PR.
  // On agentmemory package bumps, also check the STATE_VERSION/HTTP_VERSION
  // worker pins in the Dockerfile against the agentmemory release notes.
  // renovate: datasource=docker depName=docker.io/iiidev/iii
  default = "0.25.1"
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