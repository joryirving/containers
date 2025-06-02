target "docker-metadata-action" {}

variable "APP" {
  default = "free-game-notifier"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=j6nca/free-game-notifier
  default = "1.6.0"
}

variable "SOURCE" {
  default = "https://github.com/j6nca/free-game-notifier"
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
