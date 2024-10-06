<!---
NOTE: AUTO-GENERATED FILE
to edit this file, instead edit its template at: ./github/scripts/templates/README.md.j2
-->
<div align="center">


## Containers

_An opinionated collection of container images_

</div>

<div align="center">

![GitHub Repo stars](https://img.shields.io/github/stars/joryirving/containers?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/joryirving/containers?style=for-the-badge)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/joryirving/containers/release-scheduled.yaml?style=for-the-badge&label=Scheduled%20Release)

</div>

Welcome to container images, if looking for a container start by [browsing the GitHub Packages page for this repo's packages](https://github.com/joryirving?tab=packages&repo_name=containers). Please also check out the inspiration repo from [onedr0p](https://github.com/onedr0p/containers).

## Mission statement

The goal of this project is to support [semantically versioned](https://semver.org/), [rootless](https://rootlesscontaine.rs/), and [multiple architecture](https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/) containers for various applications.

I try to adhere to a [KISS principle](https://en.wikipedia.org/wiki/KISS_principle), logging to stdout, [one process per container](https://testdriven.io/tips/59de3279-4a2d-4556-9cd0-b444249ed31e/), no [s6-overlay](https://github.com/just-containers/s6-overlay) and all images are built on top of [Alpine](https://hub.docker.com/_/alpine) or [Ubuntu](https://hub.docker.com/_/ubuntu).

## Rootless

To run these containers as non-root make sure you update your configuration to the user and group you want.

### Docker compose

```yaml
networks:
  sonarr:
    name: sonarr
    external: true
services:
  sonarr:
    image: ghcr.io/joryirving/sonarr:3.0.8.1507
    container_name: sonarr
    user: 65534:65534
    # ...
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sonarr
# ...
spec:
  # ...
  template:
    # ...
    spec:
      # ...
      securityContext:
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534
        fsGroupChangePolicy: OnRootMismatch
# ...
```

## Tag immutability

The containers built here do not use immutable tags, as least not in the more common way you have seen from [linuxserver.io](https://fleet.linuxserver.io/) or [Bitnami](https://bitnami.com/stacks/containers).

We do take a similar approach but instead of appending a `-ls69` or `-r420` prefix to the tag we instead insist on pinning to the sha256 digest of the image, while this is not as pretty it is just as functional in making the images immutable.

| Container                                          | Immutable |
|----------------------------------------------------|-----------|
| `ghcr.io/joryirving/sonarr:rolling`                   | ❌         |
| `ghcr.io/joryirving/sonarr:3.0.8.1507`                | ❌         |
| `ghcr.io/joryirving/sonarr:rolling@sha256:8053...`    | ✅         |
| `ghcr.io/joryirving/sonarr:3.0.8.1507@sha256:8053...` | ✅         |

_If pinning an image to the sha256 digest, tools like [Renovate](https://github.com/renovatebot/renovate) support updating the container on a digest or application version change._

## Passing arguments to a application

Some applications do not support defining configuration via environment variables and instead only allow certain config to be set in the command line arguments for the app. To circumvent this, for applications that have an `entrypoint.sh` read below.

1. First read the Kubernetes docs on [defining command and arguments for a Container](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/).
2. Look up the documentation for the application and find a argument you would like to set.
3. Set the argument in the `args` section, be sure to include `entrypoint.sh` as the first arg and any application specific arguments thereafter.

    ```yaml
    args:
      - /entrypoint.sh
      - --port
      - "8080"
    ```

## Configuration volume

For applications that need to have persistent configuration data the config volume is hardcoded to `/config` inside the container. This is not able to be changed in most cases.

## Available Images

Each Image will be built with a `rolling` tag, along with tags specific to it's version. Available Images Below

Container | Channel | Image
--- | --- | ---
[actions-runner](https://github.com/joryirving/containers/pkgs/container/actions-runner) | stable | ghcr.io/joryirving/actions-runner
[bazarr](https://github.com/joryirving/containers/pkgs/container/bazarr) | stable | ghcr.io/joryirving/bazarr
[free-game-notifier](https://github.com/joryirving/containers/pkgs/container/free-game-notifier) | stable | ghcr.io/joryirving/free-game-notifier
[home-assistant](https://github.com/joryirving/containers/pkgs/container/home-assistant) | stable | ghcr.io/joryirving/home-assistant
[par2cmdline-turbo](https://github.com/joryirving/containers/pkgs/container/par2cmdline-turbo) | stable | ghcr.io/joryirving/par2cmdline-turbo
[plex](https://github.com/joryirving/containers/pkgs/container/plex) | stable | ghcr.io/joryirving/plex
[plex-beta](https://github.com/joryirving/containers/pkgs/container/plex-beta) | beta | ghcr.io/joryirving/plex-beta
[prowlarr](https://github.com/joryirving/containers/pkgs/container/prowlarr) | master | ghcr.io/joryirving/prowlarr
[prowlarr-develop](https://github.com/joryirving/containers/pkgs/container/prowlarr-develop) | develop | ghcr.io/joryirving/prowlarr-develop
[prowlarr-nightly](https://github.com/joryirving/containers/pkgs/container/prowlarr-nightly) | nightly | ghcr.io/joryirving/prowlarr-nightly
[qbittorrent](https://github.com/joryirving/containers/pkgs/container/qbittorrent) | stable | ghcr.io/joryirving/qbittorrent
[qbittorrent-beta](https://github.com/joryirving/containers/pkgs/container/qbittorrent-beta) | beta | ghcr.io/joryirving/qbittorrent-beta
[radarr](https://github.com/joryirving/containers/pkgs/container/radarr) | master | ghcr.io/joryirving/radarr
[radarr-develop](https://github.com/joryirving/containers/pkgs/container/radarr-develop) | develop | ghcr.io/joryirving/radarr-develop
[radarr-nightly](https://github.com/joryirving/containers/pkgs/container/radarr-nightly) | nightly | ghcr.io/joryirving/radarr-nightly
[readarr-develop](https://github.com/joryirving/containers/pkgs/container/readarr-develop) | develop | ghcr.io/joryirving/readarr-develop
[readarr-nightly](https://github.com/joryirving/containers/pkgs/container/readarr-nightly) | nightly | ghcr.io/joryirving/readarr-nightly
[redlib](https://github.com/joryirving/containers/pkgs/container/redlib) | stable | ghcr.io/joryirving/redlib
[sabnzbd](https://github.com/joryirving/containers/pkgs/container/sabnzbd) | stable | ghcr.io/joryirving/sabnzbd
[smartctl_exporter](https://github.com/joryirving/containers/pkgs/container/smartctl_exporter) | stable | ghcr.io/joryirving/smartctl_exporter
[sonarr](https://github.com/joryirving/containers/pkgs/container/sonarr) | main | ghcr.io/joryirving/sonarr
[sonarr-develop](https://github.com/joryirving/containers/pkgs/container/sonarr-develop) | develop | ghcr.io/joryirving/sonarr-develop
[tf-runner-bitwarden](https://github.com/joryirving/containers/pkgs/container/tf-runner-bitwarden) | stable | ghcr.io/joryirving/tf-runner-bitwarden
[theme-park](https://github.com/joryirving/containers/pkgs/container/theme-park) | stable | ghcr.io/joryirving/theme-park
[volsync](https://github.com/joryirving/containers/pkgs/container/volsync) | stable | ghcr.io/joryirving/volsync


## Deprecations

Containers here can be **deprecated** at any point, this could be for any reason described below.

1. The upstream application is **no longer actively developed**
2. The upstream application has an **official upstream container** that follows closely to the mission statement described here
3. The upstream application has been **replaced with a better alternative**
4. The **maintenance burden** of keeping the container here **is too bothersome**

**Note**: Deprecated containers will remained published to this repo for 6 months after which they will be pruned.

## Credits

A lot of inspiration and ideas are thanks to the hard work of [onedr0p](https://github.com/onedr0p), [hotio.dev](https://hotio.dev/) and [linuxserver.io](https://www.linuxserver.io/) contributors.