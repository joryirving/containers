target "docker-metadata-action" {}

variable "APP" {
  default = "mission-control"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=builderz-labs/mission-control
  default = "v1.3.0"
}

variable "SOURCE" {
  default = "https://github.com/builderz-labs/mission-control"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = VERSION
    SOURCE = SOURCE
  }
  labels = {
    "org.opencontainers.image.source" = SOURCE
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
