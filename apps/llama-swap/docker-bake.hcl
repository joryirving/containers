target "docker-metadata-action" {}

variable "APP" {
  default = "llama-swap"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=mostlygeek/llama-swap
  default = "v0.1.5"
}

variable "SOURCE" {
  default = "https://github.com/mostlygeek/llama-swap"
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
    "linux/amd64"
  ]
}
