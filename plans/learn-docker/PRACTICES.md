# Docker practices worth teaching

Sources read 2026-11-18 as reading material only:
- [Build] Docker docs, "Building best practices", docs.docker.com/build/building/best-practices/
- [Install] Docker docs, "Install Docker Engine on Ubuntu" and "Linux post-installation steps", docs.docker.com/engine/install/
- [Compose] Docker docs, Compose file reference, docs.docker.com/reference/compose-file/
- [Hub] Docker docs, "Docker Hub pull usage and limits", docs.docker.com/docker-hub/usage/pulls/

A beginner's habits, from chapter 1:
1. Install from Docker's own apt repository, not the snap; add yourself to the `docker` group and log in again. From chapter 1. [Install]
2. Log in to Docker Hub: anonymous pulls are limited to 100 per 6 hours per address, shared by everyone behind it. From chapter 1. [Hub]
3. Name an exact tag (`python:3.13-slim`), never `latest`. From chapter 1. [Build]
4. Name your containers; remove only what you made; show prune commands, do not run them. From chapter 2.
5. Keep a `.dockerignore`; copy the requirements file and install before copying the code. From chapter 4. [Build]
6. Write `CMD` in exec form: `CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]`. From chapter 4. [Build]
7. Inside, listen on 0.0.0.0; outside, publish on 127.0.0.1: `-p 127.0.0.1:8000:8000`. From chapter 4.
8. Keep data on a named volume, never in the container. From chapter 5.
9. Keep `.env` out of Git and out of the image. From chapter 6. [Compose]
10. Write `compose.yaml` without a `version:` key; type `docker compose`, with a space; check with `docker compose config`; never `down -v` on data you need. From chapter 7. [Compose]

Hardening habits, later:
11. Run as a user that is not root (`USER`). From chapter 5. [Build]
12. Use multi-stage builds so build tools stay out of the final image. From chapter 9. [Build]
13. Set memory limits, rotate logs, drop capabilities, use read-only containers where the app allows. From chapter 11.
