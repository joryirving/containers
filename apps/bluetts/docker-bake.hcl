target "docker-metadata-action" {}

variable "APP" {
  default = "bluetts"
}

variable "VERSION" {
  // Held at the upstream release the voice set was tuned against; bumped only
  // for major upstream changes worth re-tuning against (renovate deliberately
  // does not track this — every patch release would otherwise churn the pin).
  default = "3.0.1"
}

variable "BLUEV3_REVISION" {
  // Bundle revision on huggingface.co/notmax123/BlueV3-onnx (voice JSONs must match it).
  default = "39c4843019442bbf67e3980242549504b8583f2c"
}

variable "SOURCE" {
  default = "https://github.com/maxmelichov/BlueTTS"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
    BLUEV3_REVISION = "${BLUEV3_REVISION}"
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
