target "docker-metadata-action" {}

variable "APP" {
  default = "courier-opencode"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=misospace/courier
  default = "0.1.12"
}

variable "SOURCE" {
  default = "https://github.com/misospace/courier"
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
  platforms = ["linux/amd64"]
}
