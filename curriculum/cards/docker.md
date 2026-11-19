# docker: Docker for people who will ship their own services in containers
kind: tool
aliases: containers, dockerfile, docker compose
needs: linux-command-line, networking-basics
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: docs.docker.com: get-started concepts (order), best practices, Dockerfile reference, build cache
  (mtime ignored), secrets, volumes (an empty one is filled), networking, port publishing,
  Compose startup order, CLI (prune, down, rm, run); OWASP Docker Security Cheat Sheet. Run here (daemon in /tmp,
  FROM scratch, host Node): every Show
unverified: step 12's push and the UFW bypass (not run); base images were stand-ins built from the host's files

## Promise
Package your own application as a small, safe image, run it with its database under Compose, debug a container that will not start or stop, and know where its data lives.

## The one idea
An image is a read-only stack of file-system layers plus metadata (command, environment, user); a container is an ordinary process on the host's kernel, started from that stack with a thin writable layer on top. Picture: tracing paper over a printed book; the container writes only on its sheet. Where it breaks: there is no machine: when the main process exits, the container stops.

## In production
- CI builds, tags, scans and pushes the image; Kubernetes runs it as non-root with limits.
- Compose runs the development stack; data lives in volumes or a managed database.

## Teaching order
1. Images and containers: `docker run` (`-it`, `-d`, `--rm`, `--name`; words after the image replace `CMD`), `docker ps -a`, `stop`, `rm`; `docker top` (a host process), `docker image inspect`.
2. A Dockerfile line by line: `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `USER`, `CMD`; `docker build -t app:dev .` and the build context it sends.
3. Starting and stopping: exec form `CMD ["app"]` against shell form `CMD app` (`/bin/sh -c`); PID 1 and SIGTERM; `docker stop`, then SIGKILL; a handler or `--init`; `ENTRYPOINT` with `CMD` as its arguments, `exec "$@"`.
4. Layers and the build cache: `docker history`; a changed layer rebuilds all after it; manifest and lockfile, install, then source; `apt-get update && apt-get install` in one `RUN`; `.dockerignore`.
5. Multi-stage builds: `FROM ... AS build`, `COPY --from=build`; compilers stay behind; sizes in `docker image ls`.
6. Data: the writable layer (`docker diff`) dies with `docker rm`; named volumes (`-v dbdata:/path`), anonymous volumes, bind mounts (`-v "$PWD":/app`) for code in development; `docker volume ls`.
7. Networking: `-p 8080:80` (every host address, past UFW's rules) against `-p 127.0.0.1:8080:80`; `EXPOSE`; listen on `0.0.0.0` inside; `docker network create` gives containers each other's names, the default bridge does not.
8. Configuration and secrets: `-e`, `--env-file`; `ENV` reaches every container, `ARG` only `docker history`; a file deleted in a later layer stays in the earlier one; `RUN --mount=type=secret`, `docker build --secret`.
9. Compose for a real stack: `compose.yaml` with app and database, `ports`, `environment`, `volumes`, service names as host names; `healthcheck`, `depends_on: condition: service_healthy`; `up -d`, `logs -f`, `exec`, `down`.
10. Debugging: `docker logs`, `docker exec -it c sh` (minimal images: none), `docker inspect` (`State.ExitCode`, `OOMKilled`); exit 125 (Docker's own), 126, 127 (command not in the image), 137, 143: 128 + signal (linux-command-line 6).
11. Production images: non-root `USER`, a base pinned by tag and `@sha256:` digest, `HEALTHCHECK`, `--restart unless-stopped`, `-m`, `--cap-drop ALL`, `--read-only`, a CI scanner; never `--privileged` or the Docker socket inside.
12. Tags and registries: `name:tag`, `latest`; tags move, digests do not; `docker tag`, `docker login`, `docker push`; the commit hash as tag.

## State and danger
- [1,6] Images, writable layers and volumes sit under the daemon's "Docker Root Dir" (`docker info`), in a virtual machine on macOS and Windows; its socket, and so the `docker` group, is root on the host.
- [6,9] `docker compose down -v` deletes the stack's named volumes: the database is gone. Safe: plain `down`; a database dump first.
- [6] `docker volume prune -a` deletes every unused named volume: every removed stack's data; without `-a`, anonymous ones only. Safe: `docker volume ls` first.
- [1,4] `docker system prune -a --volumes` removes stopped containers, unused images, networks and build cache, anonymous volumes; named volumes survive (run here). Safe: `docker system df`, then prune one kind.
- [1,3] `docker rm -f` sends SIGKILL: no clean shutdown (`-v` adds anonymous volumes only). Safe: `docker stop` first.
- [6] A bind mount hands over the host path (`-v /:/host`: all of it). Safe: the narrowest path, `:ro`.
- [8,12] A secret in any layer ships with every pull. Safe: secret mounts; rotate a leaked one.

## Step notes
### 1
Need: It runs on my machine; why does `docker run -d` print an ID and then `docker ps` show nothing?
Show: `docker run -d ubuntu` (`CMD` `bash`, no terminal); `docker ps`: empty; `docker ps -a`: `Exited (0) 1
second ago`; `-dit` keeps it `Up` (here `dash` in a `FROM scratch` image). `docker top`: a plain host process.
Explain: A container lives as long as its main process; a shell with no terminal reads end of input and exits 0,
as does a start command that backgrounds the server.
Try: predict: `docker ps -a` after `docker run -d <their image> echo hi`; fix: a start script ending in `&`, until
the container is still `Up` a minute later.
### 2
Need: Why does `docker build` sit on "transferring context" when I copy one small app?
Show: `COPY . .` in a folder with 350 MB of `.git` and `node_modules`: `transferring context: 350.09MB`, about
14 s, the image 350 MB bigger. A `.dockerignore` naming both: `transferring context: 112B`, about 1 s (run twice).
Explain: `docker build .` sends the whole folder, minus `.dockerignore`, to the daemon; `COPY . .` puts all of it
in a layer.
Try: build: their `.dockerignore`, done when the context is under 1 MB with no `.git` or `.env`; explain: each
Dockerfile line as "adds a layer" or "sets metadata", against `docker history`.
### 3
Need: Why does `docker stop` hang ten seconds and my shutdown code never run?
Show: a Node server, no SIGTERM handler. Exec form `CMD ["node","server.js"]`: stop 10.2 s, exit 137, as shell
form under `dash` (`sh -c` PID 1, node its child). A `process.on("SIGTERM")` handler: 0.1 s, exit 0; `--init`:
0.1 s, 143. `bash` as `/bin/sh` `exec`s a one-command shell form. An entrypoint script without `exec "$@"`:
10.1 s despite the handler.
Explain: `docker stop` signals PID 1 only, then SIGKILL; the kernel drops signals PID 1 has no handler for, and a
shell in front passes none on.
Try: predict: their image's stop time and exit code, then time it; fix: [3,10] their Dockerfile until stop takes
under a second, their cleanup line in `docker logs`.
### 4
Need: I changed one line of code; why does every build reinstall all my dependencies?
Show: a 20 s stand-in install (theirs: `npm ci`). `COPY . .` first: a source edit rebuilds in 21 s; lockfile,
install, source: under 0.5 s, three steps `CACHED`. Surprises: unedited, the first order still took 21 s every
time: `docker build . | tee build.log` wrote into the context (`*.log` in `.dockerignore`: 0.3 s); `touch` kept
the cache, `chmod` lost it.
Explain: A step's cache key is its text plus the copied files' content and metadata, never their modification
time; the first miss rebuilds that layer and all after it.
Try: predict: which steps print `CACHED` after a lockfile edit, then check with `--progress=plain`; fix: [4]
their Dockerfile until a source edit rebuilds in seconds.
### 5
Need: My image is 800 MB; does the compiler have to ship with it?
Show: their language's build image as one stage against a slim final stage, in `docker image ls`. Here (no Hub)
a static C program on a stand-in toolchain image (the host's gcc): one stage 187 MB; `FROM scratch` plus `COPY
--from=build /app /app`: 1.14 MB, where `gcc` gives exit 127. Real build images are larger still.
Explain: Only the last stage becomes the image; earlier ones are reached only by `COPY --from`.
Try: build: their app multi-stage, done when `docker image ls` shows the drop; decide: `scratch`, distroless or
slim, from what each lacks (shell, CA certificates, libc).
### 6
Need: I recreated the database container and the data is gone; where was it?
Show: `docker run --name w1 <image> sh -c 'echo hello > /notes.txt'`; `docker diff w1`: `A /notes.txt`. A new
`docker run`: no file; `docker cp w1:/notes.txt -` still finds it; after `docker rm w1`, gone. With `-v
notes:/data`, one `--rm` container writes, the next reads it.
Explain: Writes land in that container's writable layer, deleted with it; a volume is a directory outside every
container, mounted in, so it outlives `rm`.
Try: predict: which of `rm -v`, `volume prune`, `volume prune -a`, `down`, `down -v`, `system prune -a
--volumes` deletes their named volume, then run each on a throwaway stack (here: `prune -a`, `down -v`); fix: [6]
a database lost with its container.
### 7
Need: curl inside the container works; why does the published port reset the connection?
Show: Node on `127.0.0.1:3000`, `-p 18080:3000`: `curl: (56) Recv failure: Connection reset by peer`; inside,
`ok`; on `0.0.0.0`, `ok`. Default bridge, `db`: `Name or service not known` (Node: `ENOTFOUND`); a `docker
network create` network:
`db2 -> 172.18.0.2`, from Docker's DNS at `127.0.0.11`.
Explain: `-p` forwards to the container's interface, never its loopback; only a user-defined network has the DNS
that knows container names.
Try: predict: what a phone on their Wi-Fi gets from `-p 8080:80` and `-p 127.0.0.1:8080:80`; fix: [7] two
containers that cannot resolve each other's names.
### 8
Need: I delete `.npmrc` in the next `RUN`; is my token gone?
Show: `COPY api_key.txt`, then `RUN ... rm`: no file in the container. `docker save`, unpacked: one layer holds
`app/api_key.txt` and the key, the next `app/.wh.api_key.txt`. `--build-arg NPM_TOKEN=...`: `docker history
--no-trunc` shows it. `RUN --mount=type=secret`: absent from history, image and `docker save`.
Explain: Layers only add; a deletion is a whiteout marker, so every pull carries the earlier layer; a secret mount
exists only during its `RUN`.
Try: build: their private install with a secret mount, done when `docker save` holds no token; explain: why a
pushed leak needs rotation.
### 9
Need: Compose started the database first; why does my app crash with `ECONNREFUSED`?
Show: a database listening 5 s after start, an app connecting once. `depends_on: [db]`: `app failed:
ECONNREFUSED`, then `db listening`. With a `healthcheck` and `condition: service_healthy`: `db listening`, then
`app got ready after` a few ms (theirs: `pg_isready` or similar).
Explain: Compose orders starts; started means the process exists, not that it listens; a health check gives
a state to wait for.
Try: fix: [9] their stack until `up` from nothing works ten times running; predict: their rows after `down`,
`up`, and after `down -v`, `up`.
### 10
Need: It just says `Exited (137)`; where do I start?
Show: exits made on purpose: unknown flag 125; `/nope` as command 127; a directory 126; `-m 64m` around a program
touching 10 MB at a time: 137 after 60 MB, `OOMKilled` `true`. Node under `-m 512m`: its own `JavaScript heap
out of memory`, exit 139 here, `OOMKilled` `false`.
Explain: Above 128 is 128 plus the killing signal (137 KILL, 143 TERM); `OOMKilled` says the kernel sent that KILL
for the limit.
Try: predict: their app's exit and `OOMKilled` under `-m 32m`; explain: three dead containers' causes from
`inspect` and `logs` alone.
### 11
Need: The scanner says "runs as root"; what breaks when I add `USER`?
Show: `USER 1000`, `-v data:/data`, no `/data` in the image: `/data/x: Permission denied`. With `COPY
--chown=1000:1000 data/ /data/` a new volume takes that owner: written; so did `data`, left empty by the failed
write. A volume first filled as root: denied (run here).
Explain: An empty volume is filled with the image directory's files and owner when mounted; once it holds data,
it keeps its own.
Try: apply: non-root `USER`, `--cap-drop ALL`, `--read-only` with a `tmpfs`, a restart policy (Compose
`restart:`), done when it serves and `inspect` shows each; decide: the OWASP rules it still breaks.
### 12
Need: I pushed `latest`; why is the server running last week's build?
Show: `docker build -t app .` (v1), then `-t app:v2` from new code: `docker run app` prints `v1`; `latest` is only
the tag a build without one got. `docker tag app:v2 app:latest` moves it: both tags on one ID.
Explain: A tag is a name the next build or push can move; a digest names exact bytes: deploy a commit tag or a
digest.
Try: apply: CI tags with the commit hash, done when the server's `docker inspect` shows it; predict: what a
server holding `app:latest` runs after a push, before and after `docker pull`.

## Believable numbers
- [3,4] `docker stop` waits 10 s before SIGKILL unless `-t`; a cached build step under 0.5 s, a
  missed one its full time (Docker 29 here, 2026-11).
- [2,5] A context of a few hundred MB costs about 10 s a build; a static binary alone in `scratch` is about 1 MB,
  its toolchain image hundreds (run here).

## Go deep, leave for later
- Deep steps: 3, 4, 6 (PID 1 and signals, layers and the build cache, where data lives: the three things that decide whether a container that runs also stops cleanly, rebuilds in seconds and keeps its data).
- Later: rootless mode, seccomp profiles, multi-platform builds.

## Never omit
- Each stack taken down and up, data checked.
- [8] No secret in a Dockerfile, an `ENV`, a build argument or the build context.
- Look up when planned: Docker, Compose and BuildKit versions, the learner's base image and digest, log rotation, the registry.

## Wrong beliefs
- [1] "A container is a small virtual machine" (a process on the host's kernel; no boot, no init).
- [1,6] "Stopping a container loses its data" (`stop` keeps the writable layer; `rm` loses it, a volume survives both).
- [3] "Exec form makes `docker stop` clean" (only with a SIGTERM handler or `--init`: PID 1 ignores unhandled signals; Node: 10 s, 137).
- [7] "`EXPOSE` opens the port" (it records it; `-p` publishes).
- [8] "Deleting the secret in a later step removes it" (the earlier layer keeps it: `docker save` recovers it, run here).
- [9] "`depends_on` waits for the database to be ready" (only to start, unless `condition: service_healthy`).
- [12] "`latest` is the newest image" (just the default tag; here it named an older build).

## Failures to diagnose
- [3,10] `docker stop` waits out its timeout, exit 137: shell-form `CMD`, or a PID 1 that ignores SIGTERM.
- [10,11] Exit 137 with `OOMKilled: true`: the memory limit was reached.
- [7] `Connection reset by peer` on the published port: the app listens on the container's own `127.0.0.1`.
- [7,9] A container cannot resolve another's name: they share no user-defined network.
- [6,11] `Permission denied` writing to a volume as a non-root user: its directory belongs to root.
- [4] Every code change reinstalls all dependencies: `COPY . .` comes before the install.

## Practice and project
Guided: on the learner's own app. On your own: fix a slow, large, root-running Dockerfile. Project: the learner's service and database: multi-stage Dockerfile, non-root, pinned base, health check, Compose stack; finish line: a source change rebuilds only the last layers, `docker stop` ends cleanly at once, data survives `down` and `up`, `docker history` shows no secret, the image size justified.

## Mastery ladder
- Use: run, inspect and clean up a stack's containers, images and volumes, its data kept.
- Explain: draw your image's layers and say which a one-line source change rebuilds, and why.
- Build: the project.
- Design: choose base, user, stages, health check and data placement for a stated service, defended against OWASP's rules.

## Words to own
[1] image, container, Docker daemon; [2] Dockerfile, base image, build context; [3] exec form, shell form, PID 1, entrypoint;
[4] layer, build cache; [5] multi-stage build; [6] writable layer, volume, bind mount; [7] port publishing, bridge network;
[8] build secret; [9] Compose, health status; [10] OOM kill; [11] digest, attack surface, non-root user; [12] tag, registry
