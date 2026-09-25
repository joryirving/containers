target "docker-metadata-action" {}

variable "APP" {
  default = "opencode"
}

variable "VERSION" {
  // renovate: datasource=npm depName=@opencode/cli
  default = "2.0.17"
}

variable "SOURCE" {
  default = "https://github.com/anomalyco/opencode"
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
  tags = ["${APP}:${VERSION}"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
