target "docker-metadata-action" {}

variable "APP" {
  default = "token-enhancer"
}

variable "VERSION" {
  // renovate: datasource=git-commit depName=https://github.com/Boof-Pack/token-enhancer
  default = "v1.0.0
}

variable "SOURCE" {
  default = "https://github.com/Boof-Pack/token-enhancer"
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
