target "docker-metadata-action" {}

variable "APP" {
  default = "bluetts"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=maxmelichov/BlueTTS
  default = "3.0.1"
}

variable "SOURCE_SHA" {
  // The maxmelichov/BlueTTS commit the voice set was tuned against: 15 commits
  // past V3.0.1, adding the voice-export machinery the shipped voice JSONs were
  // produced with. Re-pin to the release tag's commit when renovate bumps
  // VERSION past it (and re-tune BLUE_* render envs / regenerate voices-custom/
  // if the bundle moves too).
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
    SOURCE_SHA = "${SOURCE_SHA}"
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
