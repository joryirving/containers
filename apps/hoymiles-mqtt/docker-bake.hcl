target "docker-metadata-action" {}

variable "APP" {
  default = "hoymiles-mqtt"
}

variable "VERSION" {
  // renovate: datasource=pypi depName=hoymiles-mqtt
  default = "0.11.0"
}

variable "SOURCE" {
  default = "https://github.com/wasilukm/hoymiles-mqtt"
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
