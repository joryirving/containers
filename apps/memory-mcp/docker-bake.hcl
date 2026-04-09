target "docker-metadata-action" {}

variable "APP" {
  default = "memory-mcp"
}

variable "VERSION" {
  // renovate: datasource=npm depName=@modelcontextprotocol/server-memory
  default = "0.6.3"
}

variable "SOURCE" {
  default = "https://github.com/modelcontextprotocol/servers"
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
