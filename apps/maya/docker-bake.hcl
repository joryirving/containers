target "docker-metadata-action" {}

variable "APP" {
  default = "maya"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=mw00/project-Maya
  default = "1.1.84"
}

variable "SOURCE" {
  default = "https://github.com/mw00/project-Maya"
}

variable "CUDA_ARCHITECTURES" {
  default = "86"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    CUDA_ARCHITECTURES = "${CUDA_ARCHITECTURES}"
    VERSION = "${VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
  tags = ["${APP}:${VERSION}-cuda13"]
}

target "image-all" {
  inherits = ["image"]
  platforms = ["linux/amd64"]
}
