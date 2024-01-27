<!---
NOTE: AUTO-GENERATED FILE
to edit this file, instead edit its template at: ./github/scripts/templates/README.md.j2
-->
<div align="center">


## Containers

_An opinionated collection of container images_

</div>

<div align="center">

![GitHub Repo stars](https://img.shields.io/github/stars/LilDrunkenSmurf/containers?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/LilDrunkenSmurf/containers?style=for-the-badge)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/LilDrunkenSmurf/containers/release-scheduled.yaml?style=for-the-badge&label=Scheduled%20Release)

</div>

Welcome to my container images, if looking for a container start by [browsing the GitHub Packages page for this repo's packages](https://github.com/LilDrunkenSmurf?tab=packages&repo_name=containers).

Please note that this repo is *heavily* copied (or plaguarized) from [onedr0p's container repo](https://github.com/onedr0p/containers)

## Mission statement

The goal of this project is to support [semantically versioned](https://semver.org/), [rootless](https://rootlesscontaine.rs/), and [multiple architecture](https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/) containers for various applications.

We also try to adhere to a [KISS principle](https://en.wikipedia.org/wiki/KISS_principle), logging to stdout, [one process per container](https://testdriven.io/tips/59de3279-4a2d-4556-9cd0-b444249ed31e/), no [s6-overlay](https://github.com/just-containers/s6-overlay) and all images are built on top of [Alpine](https://hub.docker.com/_/alpine) or [Ubuntu](https://hub.docker.com/_/ubuntu).

## Tag immutability

The containers built here do not use immutable tags, as least not in the more common way you have seen from [linuxserver.io](https://fleet.linuxserver.io/) or [Bitnami](https://bitnami.com/stacks/containers).

We do take a similar approach but instead of appending a `-ls69` or `-r420` prefix to the tag we instead insist on pinning to the sha256 digest of the image, while this is not as pretty it is just as functional in making the images immutable.

| Container                                          | Immutable |
|----------------------------------------------------|-----------|
| `ghcr.io/lildrunkensmurf/sonarr:rolling`                   | ❌         |
| `ghcr.io/lildrunkensmurf/sonarr:3.0.8.1507`                | ❌         |
| `ghcr.io/lildrunkensmurf/sonarr:rolling@sha256:8053...`    | ✅         |
| `ghcr.io/lildrunkensmurf/sonarr:3.0.8.1507@sha256:8053...` | ✅         |

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

Container | Channel | Image | Latest Tags
--- | --- | --- | ---
[actions-runner](https://github.com/LilDrunkenSmurf/containers/pkgs/container/actions-runner) | stable | ghcr.io/LilDrunkenSmurf/actions-runner |![2](https://img.shields.io/badge/2-blue?style=flat-square) ![2.312](https://img.shields.io/badge/2.312-blue?style=flat-square) ![2.312.0](https://img.shields.io/badge/2.312.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[bazarr](https://github.com/LilDrunkenSmurf/containers/pkgs/container/bazarr) | stable | ghcr.io/LilDrunkenSmurf/bazarr |![1](https://img.shields.io/badge/1-blue?style=flat-square) ![1.4](https://img.shields.io/badge/1.4-blue?style=flat-square) ![1.4.0](https://img.shields.io/badge/1.4.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[bitwarden-cli](https://github.com/LilDrunkenSmurf/containers/pkgs/container/bitwarden-cli) | stable | ghcr.io/LilDrunkenSmurf/bitwarden-cli |![2024.1.0](https://img.shields.io/badge/2024.1.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[feedcord](https://github.com/LilDrunkenSmurf/containers/pkgs/container/feedcord) | stable | ghcr.io/LilDrunkenSmurf/feedcord |![1.3.0](https://img.shields.io/badge/1.3.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[free-game-notifier](https://github.com/LilDrunkenSmurf/containers/pkgs/container/free-game-notifier) | stable | ghcr.io/LilDrunkenSmurf/free-game-notifier |![latest](https://img.shields.io/badge/latest-green?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[home-assistant](https://github.com/LilDrunkenSmurf/containers/pkgs/container/home-assistant) | stable | ghcr.io/LilDrunkenSmurf/home-assistant |![2024.1.5](https://img.shields.io/badge/2024.1.5-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[par2cmdline-turbo](https://github.com/LilDrunkenSmurf/containers/pkgs/container/par2cmdline-turbo) | stable | ghcr.io/LilDrunkenSmurf/par2cmdline-turbo |![1.1.1](https://img.shields.io/badge/1.1.1-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[plex](https://github.com/LilDrunkenSmurf/containers/pkgs/container/plex) | stable | ghcr.io/LilDrunkenSmurf/plex |![1.32.8.7639-fb6452ebf](https://img.shields.io/badge/1.32.8.7639--fb6452ebf-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[plex-beta](https://github.com/LilDrunkenSmurf/containers/pkgs/container/plex-beta) | beta | ghcr.io/LilDrunkenSmurf/plex-beta |![1.40.0.7775-456fbaf97](https://img.shields.io/badge/1.40.0.7775--456fbaf97-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[prowlarr](https://github.com/LilDrunkenSmurf/containers/pkgs/container/prowlarr) | master | ghcr.io/LilDrunkenSmurf/prowlarr |![1](https://img.shields.io/badge/1-blue?style=flat-square) ![1.12](https://img.shields.io/badge/1.12-blue?style=flat-square) ![1.12.2](https://img.shields.io/badge/1.12.2-blue?style=flat-square) ![1.12.2.4211](https://img.shields.io/badge/1.12.2.4211-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[prowlarr-develop](https://github.com/LilDrunkenSmurf/containers/pkgs/container/prowlarr-develop) | develop | ghcr.io/LilDrunkenSmurf/prowlarr-develop |![1](https://img.shields.io/badge/1-blue?style=flat-square) ![1.12](https://img.shields.io/badge/1.12-blue?style=flat-square) ![1.12.2](https://img.shields.io/badge/1.12.2-blue?style=flat-square) ![1.12.2.4211](https://img.shields.io/badge/1.12.2.4211-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[prowlarr-nightly](https://github.com/LilDrunkenSmurf/containers/pkgs/container/prowlarr-nightly) | nightly | ghcr.io/LilDrunkenSmurf/prowlarr-nightly |![1](https://img.shields.io/badge/1-blue?style=flat-square) ![1.13](https://img.shields.io/badge/1.13-blue?style=flat-square) ![1.13.1](https://img.shields.io/badge/1.13.1-blue?style=flat-square) ![1.13.1.4243](https://img.shields.io/badge/1.13.1.4243-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[qbittorrent](https://github.com/LilDrunkenSmurf/containers/pkgs/container/qbittorrent) | stable | ghcr.io/LilDrunkenSmurf/qbittorrent |![4](https://img.shields.io/badge/4-blue?style=flat-square) ![4.6](https://img.shields.io/badge/4.6-blue?style=flat-square) ![4.6.3](https://img.shields.io/badge/4.6.3-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[qbittorrent-beta](https://github.com/LilDrunkenSmurf/containers/pkgs/container/qbittorrent-beta) | beta | ghcr.io/LilDrunkenSmurf/qbittorrent-beta |![4](https://img.shields.io/badge/4-blue?style=flat-square) ![4.6](https://img.shields.io/badge/4.6-blue?style=flat-square) ![4.6.3](https://img.shields.io/badge/4.6.3-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[radarr](https://github.com/LilDrunkenSmurf/containers/pkgs/container/radarr) | master | ghcr.io/LilDrunkenSmurf/radarr |![5](https://img.shields.io/badge/5-blue?style=flat-square) ![5.2](https://img.shields.io/badge/5.2-blue?style=flat-square) ![5.2.6](https://img.shields.io/badge/5.2.6-blue?style=flat-square) ![5.2.6.8376](https://img.shields.io/badge/5.2.6.8376-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[radarr-develop](https://github.com/LilDrunkenSmurf/containers/pkgs/container/radarr-develop) | develop | ghcr.io/LilDrunkenSmurf/radarr-develop |![5](https://img.shields.io/badge/5-blue?style=flat-square) ![5.3](https://img.shields.io/badge/5.3-blue?style=flat-square) ![5.3.2](https://img.shields.io/badge/5.3.2-blue?style=flat-square) ![5.3.2.8504](https://img.shields.io/badge/5.3.2.8504-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[radarr-nightly](https://github.com/LilDrunkenSmurf/containers/pkgs/container/radarr-nightly) | nightly | ghcr.io/LilDrunkenSmurf/radarr-nightly |![5](https://img.shields.io/badge/5-blue?style=flat-square) ![5.3](https://img.shields.io/badge/5.3-blue?style=flat-square) ![5.3.3](https://img.shields.io/badge/5.3.3-blue?style=flat-square) ![5.3.3.8533](https://img.shields.io/badge/5.3.3.8533-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[readarr-develop](https://github.com/LilDrunkenSmurf/containers/pkgs/container/readarr-develop) | develop | ghcr.io/LilDrunkenSmurf/readarr-develop |![0](https://img.shields.io/badge/0-blue?style=flat-square) ![0.3](https://img.shields.io/badge/0.3-blue?style=flat-square) ![0.3.15](https://img.shields.io/badge/0.3.15-blue?style=flat-square) ![0.3.15.2376](https://img.shields.io/badge/0.3.15.2376-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[readarr-nightly](https://github.com/LilDrunkenSmurf/containers/pkgs/container/readarr-nightly) | nightly | ghcr.io/LilDrunkenSmurf/readarr-nightly |![0](https://img.shields.io/badge/0-blue?style=flat-square) ![0.3](https://img.shields.io/badge/0.3-blue?style=flat-square) ![0.3.17](https://img.shields.io/badge/0.3.17-blue?style=flat-square) ![0.3.17.2409](https://img.shields.io/badge/0.3.17.2409-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[sabnzbd](https://github.com/LilDrunkenSmurf/containers/pkgs/container/sabnzbd) | stable | ghcr.io/LilDrunkenSmurf/sabnzbd |![4](https://img.shields.io/badge/4-blue?style=flat-square) ![4.2](https://img.shields.io/badge/4.2-blue?style=flat-square) ![4.2.1](https://img.shields.io/badge/4.2.1-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[smartctl_exporter](https://github.com/LilDrunkenSmurf/containers/pkgs/container/smartctl_exporter) | stable | ghcr.io/LilDrunkenSmurf/smartctl_exporter |![0](https://img.shields.io/badge/0-blue?style=flat-square) ![0.11](https://img.shields.io/badge/0.11-blue?style=flat-square) ![0.11.0](https://img.shields.io/badge/0.11.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[sonarr](https://github.com/LilDrunkenSmurf/containers/pkgs/container/sonarr) | main | ghcr.io/LilDrunkenSmurf/sonarr |![4](https://img.shields.io/badge/4-blue?style=flat-square) ![4.0](https://img.shields.io/badge/4.0-blue?style=flat-square) ![4.0.1](https://img.shields.io/badge/4.0.1-blue?style=flat-square) ![4.0.1.929](https://img.shields.io/badge/4.0.1.929-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[sonarr-develop](https://github.com/LilDrunkenSmurf/containers/pkgs/container/sonarr-develop) | develop | ghcr.io/LilDrunkenSmurf/sonarr-develop |![4](https://img.shields.io/badge/4-blue?style=flat-square) ![4.0](https://img.shields.io/badge/4.0-blue?style=flat-square) ![4.0.1](https://img.shields.io/badge/4.0.1-blue?style=flat-square) ![4.0.1.1014](https://img.shields.io/badge/4.0.1.1014-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[tautulli](https://github.com/LilDrunkenSmurf/containers/pkgs/container/tautulli) | master | ghcr.io/LilDrunkenSmurf/tautulli |![2](https://img.shields.io/badge/2-blue?style=flat-square) ![2.13](https://img.shields.io/badge/2.13-blue?style=flat-square) ![2.13.4](https://img.shields.io/badge/2.13.4-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[tf-runner-bitwarden](https://github.com/LilDrunkenSmurf/containers/pkgs/container/tf-runner-bitwarden) | stable | ghcr.io/LilDrunkenSmurf/tf-runner-bitwarden |![0.15.1](https://img.shields.io/badge/0.15.1-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[theme-park](https://github.com/LilDrunkenSmurf/containers/pkgs/container/theme-park) | stable | ghcr.io/LilDrunkenSmurf/theme-park |![1](https://img.shields.io/badge/1-blue?style=flat-square) ![1.15](https://img.shields.io/badge/1.15-blue?style=flat-square) ![1.15.1](https://img.shields.io/badge/1.15.1-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)
[volsync](https://github.com/LilDrunkenSmurf/containers/pkgs/container/volsync) | stable | ghcr.io/LilDrunkenSmurf/volsync |![0](https://img.shields.io/badge/0-blue?style=flat-square) ![0.8](https://img.shields.io/badge/0.8-blue?style=flat-square) ![0.8.0](https://img.shields.io/badge/0.8.0-blue?style=flat-square) ![rolling](https://img.shields.io/badge/rolling-blue?style=flat-square)


## Contributing

1. Install [Docker](https://docs.docker.com/get-docker/), [Taskfile](https://taskfile.dev/) & [Cuelang](https://cuelang.org/)
2. Get familiar with the structure of the repositroy
3. Find a similar application in the apps directory
4. Copy & Paste an application and update the directory name
5. Update `metadata.json`, `Dockerfile`, `ci/latest.sh`, `ci/goss.yaml` and make it suit the application build
6. Include any additional files if required
7. Use Taskfile to build and test your image

    ```ruby
    task APP=radarr CHANNEL=main test
    ```

### Automated tags

Here's an example of how tags are created in the GitHub workflows, be careful with `metadata.json` as it does affect the outcome of how the tags will be created when the application is built.

| Application | Channel   | Stable  | Base    | Generated Tag               |
|-------------|-----------|---------|---------|-----------------------------|
| `ubuntu`    | `jammy`   | `true`  | `true`  | `ubuntu:rolling`            |
| `ubuntu`    | `jammy`   | `true`  | `true`  | `ubuntu:jammy-20231211.1`   |
| `alpine`    | `3.19`    | `true`  | `true`  | `alpine:rolling`            |
| `alpine`    | `3.10`    | `true`  | `true`  | `alpine:3.19.0`             |
| `radarr`    | `develop` | `false` | `false` | `radarr-develop:5.2.6.8376` |
| `radarr`    | `develop` | `false` | `false` | `radarr-develop:rolling`    |
| `radarr`    | `main`    | `true`  | `false` | `radarr:5.2.6.8376`         |
| `radarr`    | `main`    | `true`  | `false` | `radarr:rolling`            |

## Deprecations

Containers here can be **deprecated** at any point, this could be for any reason described below.

1. The upstream application is **no longer actively developed**
2. The upstream application has an **official upstream container** that follows closely to the mission statement described here
3. The upstream application has been **replaced with a better alternative**
4. The **maintenance burden** of keeping the container here **is too bothersome**

**Note**: Deprecated containers will remained published to this repo for 6 months after which they will be pruned.
## Credits

A lot of inspiration and ideas are thanks to the hard work of [onedr0p](https://github.com/onedr0p), [hotio.dev](https://hotio.dev/) and [linuxserver.io](https://www.linuxserver.io/) contributors.