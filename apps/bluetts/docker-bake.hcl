target "docker-metadata-action" {}

variable "APP" {
  default = "bluetts"
}

variable "VERSION" {
  // Pinned to the maxmelichov/BlueTTS commit this voice set was tuned against;
  // upstream has a single v1.0.0 tag that predates the tuning-relevant changes.
  // Update manually (and re-tune BLUE_* render envs + regenerate voices-custom/).
  default = "cbe51508f3f05207662bc714ad646da8191861d0"
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
