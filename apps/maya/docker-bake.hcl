target "docker-metadata-action" {}

variable "APP" {
  default = "maya"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=mw00/project-Maya
  default = "1.1.67"
}

variable "SOURCE" {
  default = "https://github.com/mw00/project-Maya"
}

variable "MAYA_COMMIT" {
  default = "81b68a6c1da6aebeecf83f6f9ca33878258ef968"
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
    MAYA_COMMIT = "${MAYA_COMMIT}"
    CUDA_ARCHITECTURES = "${CUDA_ARCHITECTURES}"
    VERSION = "${VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
    "com.joryirving.maya.source-revision" = "${MAYA_COMMIT}"
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
