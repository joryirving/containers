target "docker-metadata-action" {}

variable "APP" {
  default = "it-tools"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=sharevb/it-tools
  default = "v2025.12.7"
}

variable "SOURCE" {
  default = "https://github.com/sharevb/it-tools"
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
