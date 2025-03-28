target "docker-metadata-action" {}

variable "VERSION" {
  // renovate: datasource=github-releases depName=CorentinTh/it-tools versioning=regex:^(v?(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)-(?<revision>.*))$
  default = "2024.10.22-7ca5933"
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
    "org.opencontainers.image.source" = "https://github.com/CorentinTh/it-tools"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
