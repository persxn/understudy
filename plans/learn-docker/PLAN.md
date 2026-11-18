# Learn Docker
for: a beginner on Ubuntu who uses a terminal a little and has written a small Python program, but has never used containers
run: console
state: docker
timeout: 120
check: docker version
check: docker ps

<!-- The book's image set, fixed in 1.6 and reused with exactly these tags in every chapter (download size first,
size on disk after; rough, x86_64):
  hello-world:latest    about 10 KB,  20 KB   (1.2 only; the one image with no other tag worth pinning)
  alpine:3.22           about 4 MB,   9 MB    (small commands, shells, networks, volumes)
  python:3.13-slim      about 45 MB,  130 MB  (the guestbook and every Dockerfile)
  registry:3            about 10 MB,  25 MB   (chapter 10 only: a local registry to push to)
About 60 MB downloaded for the whole book. No full python, postgres, mysql or nginx image is pulled; no section
uses --pull always. The running example is the guestbook: a small Flask app that keeps its entries in a SQLite
file, carried from 1.10 to the last chapter. -->

## Part I · Containers

### 1 Getting Docker running
1.1 Installing Docker Engine on Ubuntu from Docker's own repository | teaches: docker-engine, docker-apt-repository, snap-docker-pitfall
1.2 Your first container: hello-world | short | teaches: hello-world, docker-run | fig
1.3 Permission denied: the docker group | teaches: docker-socket, docker-group
1.4 What just happened: client, daemon and registry | teaches: docker-client, docker-daemon, registry | fig
1.5 Images and containers | teaches: image, container | fig
1.6 The book's image set: pulling only what you need | teaches: docker-pull, image-tag, image-size
1.7 Logging in to Docker Hub and the pull limit | short | teaches: docker-login, pull-limit
1.8 Day-one errors: cannot connect, daemon not running, no space left | teaches: cannot-connect-daemon, docker-info, disk-full
1.9 A container is not a virtual machine | teaches: shared-kernel, vm-comparison | fig | level: 2
1.10 Meet the guestbook, the app you will carry through the book | story
1.11 Practice: break it and fix it, a locked socket and a stopped daemon | practice | level: 3

### 2 Running containers
2.1 Giving a container a command | short | teaches: run-command
2.2 An interactive shell with -it | short | teaches: interactive-tty
2.3 Listing containers with docker ps | short | teaches: docker-ps
2.4 Naming your containers | short | teaches: container-name
2.5 Running in the background and reading logs | teaches: detached-run, docker-logs
2.6 Stopping, starting and removing | teaches: docker-stop, docker-start, docker-rm, run-rm
2.7 The life of a container | teaches: container-lifecycle, exit-code | fig
2.8 Getting into a running container with docker exec | short | teaches: docker-exec
2.9 Looking closer: inspect and stats | teaches: docker-inspect, docker-stats | level: 2
2.10 When it goes wrong: a name already in use, a container that exits at once | teaches: name-conflict, exits-at-once
2.11 Practice: break it and fix it, a container that will not stay up | practice | level: 3

### 3 Images
3.1 Where images come from: registries, repositories and tags | teaches: repository-name, official-image | fig
3.2 Why a book never uses latest | short | teaches: latest-tag-pitfall
3.3 Listing and removing images | short | teaches: docker-images, docker-rmi
3.4 Layers, and how images share them | teaches: image-layer, layer-sharing, docker-history | fig | level: 2
3.5 How much disk Docker uses | short | teaches: docker-system-df
3.6 Digests: naming one exact image | teaches: image-digest | level: 2
3.7 Images for other machines and "exec format error" | teaches: image-platform, exec-format-error
3.8 Cleaning up only what you made | teaches: dangling-image, prune-danger
3.9 When it goes wrong: access denied, too many requests, manifest unknown | teaches: pull-errors, rate-limit-error
3.10 Practice: break it and fix it, a pull that fails | practice | level: 3

## Part II · Your own app in a container

### 4 The guestbook's first Dockerfile
4.1 From an app on your laptop to an image | story
4.2 A Dockerfile line by line | teaches: dockerfile, from-instruction, workdir-instruction, copy-instruction, run-instruction
4.3 Keeping things out of the image with .dockerignore | short | teaches: dockerignore
4.4 Copy the requirements first: the build cache | teaches: build-cache, layer-order | fig
4.5 Building and tagging the guestbook | short | teaches: docker-build, build-tag
4.6 CMD in exec form | short | teaches: cmd-instruction, exec-form
4.7 Listening on 0.0.0.0 inside the container | teaches: listen-all-interfaces | fig
4.8 Publishing a port on 127.0.0.1 only | short | teaches: port-publish, localhost-publish
4.9 Logs that show up at once: PYTHONUNBUFFERED | short | teaches: env-instruction, pythonunbuffered
4.10 A real web server: gunicorn instead of flask run | teaches: gunicorn
4.11 When it goes wrong: connection refused, port already allocated, a failed build | teaches: connection-refused, port-allocated, build-errors
4.12 Practice: break it and fix it, the guestbook will not answer | practice | level: 3

### 5 Keeping data: volumes and bind mounts
5.1 Where did the guestbook's entries go? | story
5.2 The container's writable layer | teaches: writable-layer | fig
5.3 Named volumes | teaches: named-volume, docker-volume | fig
5.4 Putting the SQLite file on a volume | teaches: volume-mount-path | needs: dockerfile
5.5 Bind mounts for code you are editing | teaches: bind-mount | fig
5.6 Files owned by root after a mount | teaches: container-uid, root-owned-files
5.7 Running the app as a user that is not root | teaches: user-instruction | level: 2
5.8 Backing up and restoring a volume | teaches: volume-backup | level: 2
5.9 Removing a volume removes the data | short | teaches: volume-rm
5.10 When it goes wrong: data gone, permission denied, a mount that hides files | teaches: mount-hides-files
5.11 Practice: break it and fix it, the vanishing guestbook | practice | level: 3

### 6 Configuration and networks
6.1 Settings from outside: -e and --env-file | teaches: env-var, env-file
6.2 Keeping .env out of Git and out of the image | short | teaches: secrets-out-of-git | needs: dockerignore
6.3 Container networks | teaches: bridge-network, user-network | fig
6.4 Containers find each other by name | teaches: container-dns | needs: container-name
6.5 localhost inside a container is not your laptop | teaches: localhost-in-container | fig
6.6 Reaching a service on your own machine | teaches: host-gateway | level: 2
6.7 A port clash with something already on your laptop | short | teaches: port-clash | needs: port-allocated
6.8 Restart policies | short | teaches: restart-policy
6.9 When it goes wrong: a name that does not resolve, refused between containers | teaches: network-debugging
6.10 Practice: break it and fix it, two containers that cannot talk | practice | level: 3

### 7 Docker Compose
7.1 Many docker run lines become one file | story
7.2 compose.yaml: services, build, image, ports | teaches: compose-file, compose-service | fig
7.3 docker compose with a space, and no version: key | short | teaches: compose-v2, version-key-obsolete
7.4 up, ps, logs and down | teaches: compose-up, compose-ps, compose-logs, compose-down
7.5 docker compose config: what Compose understood | short | teaches: compose-config
7.6 Service names are host names | teaches: service-name-dns | needs: container-dns
7.7 Volumes in Compose, and why down -v deletes your data | teaches: compose-volumes, down-v-warning | needs: named-volume
7.8 Settings and .env in Compose | teaches: compose-environment, compose-interpolation | needs: env-file
7.9 Start order and health checks | teaches: depends-on, healthcheck | level: 2
7.10 Seeing code changes at once with watch | teaches: compose-watch | needs: bind-mount | level: 2
7.11 When it goes wrong: the Compose errors a beginner meets | teaches: compose-errors
7.12 Practice: break it and fix it, the guestbook stack | practice | level: 3

## Part III · Working like a team

### 8 Finding what is wrong
8.1 A method: read, reproduce, narrow down | teaches: debug-method
8.2 Reading logs well: follow, tail and since | short | teaches: logs-follow | needs: docker-logs
8.3 Exit codes 137 and 143, and running out of memory | teaches: signal-exit-codes, oom-killed | needs: exit-code | level: 2
8.4 A shell inside an image that will not start | teaches: entrypoint-override
8.5 Watching what Docker does with docker events | short | teaches: docker-events | level: 2
8.6 Seeing a whole build: plain progress and no cache | teaches: build-progress-plain, no-cache | needs: build-cache
8.7 Asking inspect exactly what you need | teaches: inspect-format | needs: docker-inspect | level: 2
8.8 Asking for help: docker info and a small example that fails | short | teaches: minimal-repro
8.9 Practice: break it and fix it, five broken containers | practice | level: 3

### 9 Better images
9.1 slim or alpine: what you gain and what breaks | teaches: slim-vs-alpine
9.2 Multi-stage builds | teaches: multi-stage-build | fig
9.3 ENTRYPOINT and CMD together | teaches: entrypoint-instruction, entrypoint-cmd-pair | needs: cmd-instruction | level: 2
9.4 Build arguments and environment variables | teaches: build-arg | needs: env-instruction | level: 2
9.5 A cache for pip downloads | teaches: cache-mount | level: 2
9.6 HEALTHCHECK in the Dockerfile | short | teaches: dockerfile-healthcheck | needs: healthcheck
9.7 Labels that describe an image | short | teaches: image-label
9.8 docker init: a generated starting point, read critically | teaches: docker-init
9.9 Checking an image for known security problems | teaches: image-scan | level: 2
9.10 Practice: break it and fix it, a slow and heavy build | practice | level: 3

### 10 Sharing images
10.1 Naming an image for a registry | short | teaches: registry-tag | needs: image-tag
10.2 Pushing to Docker Hub | teaches: docker-push | needs: docker-login
10.3 Version tags a teammate can trust | teaches: version-tags | level: 2
10.4 A registry of your own for practice | teaches: local-registry | level: 2
10.5 Building for another architecture with buildx | teaches: buildx-platform | needs: image-platform | level: 2
10.6 Moving an image without a registry: save and load | short | teaches: docker-save-load
10.7 Building and pushing from GitHub Actions | teaches: ci-image-build | level: 2
10.8 When it goes wrong: denied, unauthorized, the wrong architecture | teaches: push-errors
10.9 Practice: break it and fix it, a teammate cannot run your image | practice | level: 3

### 11 Safe defaults for running it for real
11.1 What changes between your laptop and a server | story
11.2 Limits on memory and CPU | teaches: resource-limits | needs: oom-killed
11.3 Read-only containers and tmpfs | teaches: read-only-rootfs, tmpfs-mount | level: 2
11.4 Dropping capabilities | teaches: cap-drop | level: 2
11.5 Secrets in Compose | teaches: compose-secrets | needs: secrets-out-of-git | level: 2
11.6 Logs that do not fill the disk | short | teaches: log-rotation
11.7 The docker group is as good as root | teaches: docker-group-root | needs: docker-group | level: 4
11.8 Updating a running service with Compose | teaches: compose-update | needs: compose-up
11.9 Choosing defaults for a team | teaches: team-defaults | level: 4
11.10 Practice: the guestbook made safe, explained to a teammate | practice | level: 5
