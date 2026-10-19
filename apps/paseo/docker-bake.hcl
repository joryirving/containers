target "docker-metadata-action" {}

variable "APP" {
  default = "paseo"
}

variable "VERSION" {
  // renovate: datasource=docker depName=ghcr.io/getpaseo/paseo
  default = "0.12.0"
}

variable "OPENCODE_VERSION" {
  // renovate: datasource=npm depName=@opencode/cli
  default = "2.0.32"
}

variable "MISE_VERSION" {
  // renovate: datasource=github-releases depName=jdx/mise
  default = "v2026.10.15"
}

variable "SOURCE" {
  default = "https://github.com/getpaseo/paseo"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION       = "${VERSION}"
    OPENCODE_VERSION = "${OPENCODE_VERSION}"
    MISE_VERSION  = "${MISE_VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output   = ["type=docker"]
  tags     = ["${APP}:${VERSION}"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
