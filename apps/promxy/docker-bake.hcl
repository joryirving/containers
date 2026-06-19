target "docker-metadata-action" {}

variable "APP" {
  default = "promxy"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=jacksontj/promxy
  default = "v0.0.94"
}

variable "SOURCE" {
  default = "https://github.com/jacksontj/promxy"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
    SOURCE = "${SOURCE}"
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
