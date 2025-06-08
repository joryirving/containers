target "docker-metadata-action" {}

variable "APP" {
  default = "readarr"
}

variable "VERSION" {
  // renovate: datasource=custom.servarr-develop depName=readarr versioning=loose
  default = "0.4.17.2801"
}

variable "SOURCE" {
  default = "https://github.com/Readarr/Readarr"
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
