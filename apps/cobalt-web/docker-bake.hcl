target "docker-metadata-action" {}

variable "APP" {
  default = "cobalt-web"
}

variable "VERSION" {
  default = "11.7.1"
}

variable "SOURCE_REF" {
  default = "a636575b09de1fc55d9b8cd98cac88f5f2f16b42"
}

variable "SOURCE" {
  default = "https://github.com/imputnet/cobalt"
}

variable "WEB_DEFAULT_API" {
  default = "https://cobalt.jory.dev"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    SOURCE_REF      = "${SOURCE_REF}"
    WEB_DEFAULT_API = "${WEB_DEFAULT_API}"
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
