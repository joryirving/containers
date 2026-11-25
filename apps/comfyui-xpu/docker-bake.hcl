target "docker-metadata-action" {}

variable "APP" {
  default = "comfyui-xpu"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=comfyanonymous/ComfyUI
  default = "0.45.0"
}

variable "SOURCE" {
  default = "https://github.com/comfyanonymous/ComfyUI"
}

variable "XPU_TARGET" {
  // ptl-h: Intel Panther Lake Xe3 iGPU. Changing this requires rebuilding the
  // omni_xpu_kernel wheel; the artifact is AOT-locked to one target.
  default = "ptl-h"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    XPU_TARGET = "${XPU_TARGET}"
    VERSION = "${VERSION}"
    COMFYUI_VERSION = "${VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
  tags = ["${APP}:${VERSION}-xpu"]
}

target "image-all" {
  inherits = ["image"]
  platforms = ["linux/amd64"]
}
