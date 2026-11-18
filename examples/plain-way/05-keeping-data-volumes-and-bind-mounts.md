# Chapter 5: Keeping data: volumes and bind mounts

<!-- contents -->
- [5.2 The container's writable layer](#52-the-containers-writable-layer)
- [5.3 Named volumes](#53-named-volumes)
- [5.4 Putting the SQLite file on a volume](#54-putting-the-sqlite-file-on-a-volume)
- [5.5 Bind mounts for code you are editing](#55-bind-mounts-for-code-you-are-editing)
- [5.11 Practice: break it and fix it, the vanishing guestbook](#511-practice-break-it-and-fix-it-the-vanishing-guestbook)
<!-- /contents -->

In chapter 4 you built `guestbook:1`, ran it, and wrote your first entries into it from the browser. This chapter starts with the morning after, when those entries are gone, and ends with a guestbook whose entries survive anything short of you deleting them on purpose. Everything here was written for Docker Engine 28 on Ubuntu; the commands have not changed in years and work the same on older and newer engines.

## 5.2 The container's writable layer

### The question

Here is what happened. On Friday you ran the guestbook the way chapter 4 taught you:

```text
docker run -d --name guestbook -p 127.0.0.1:8000:8000 guestbook:1
```

You opened `http://127.0.0.1:8000`, signed the book three times ("hello from me", "second entry", "it works"), and smiled. Before you closed the laptop you tidied up, also the way chapter 2 taught you: `docker stop guestbook`, then `docker rm guestbook`. On Monday you typed the same `docker run` line again, opened the page, and the guestbook was empty. Three entries, gone. No error, no warning, nothing in the logs. The app started cleanly, created a fresh empty database, and waited for visitors as if it had never had any.

So the question this section answers is the one you are asking right now: where did the entries live, and why did they not come back? And behind it, a bigger one: when a program inside a container writes a file, where does that file actually go on your disk, and how long does it last?

### The picture

Think of a printed workbook from school, the kind where every pupil gets the same book and writes answers in pencil. The printed pages are the same for every pupil; nobody can change the print. Your pencil marks are yours. Now picture a cleaner, very literal, who is told "throw away this pupil's book". He throws away the book with your pencil marks in it. Tomorrow you get a new copy of the same printed workbook: the print is all there, every page perfect, and not one of your answers.

The image `guestbook:1` is the printed workbook. Every container you start from it gets the same print. The pencil marks are the files the running container writes, like `/app/data/guestbook.db`. `docker rm` is the cleaner.

Where the picture stops being true: in a real workbook your pencil marks sit on the printed page. In Docker the print and the pencil are kept apart, in separate places on disk, and the container only sees them merged together. That separation is exactly the idea of this section, and it is what makes the fix in the next sections possible.

### The idea

Let us build this step by step, starting from what you already know.

**An image is read-only.** In chapter 3 you learned that an image is made of layers, and in chapter 4 you watched each `RUN`, `COPY` and other instruction of your Dockerfile add a layer during `docker build`. Once the image is built, those layers never change. You can start a hundred containers from `guestbook:1` and the image stays byte for byte the same. That is what lets Docker share one copy of the image between all of them.

**But a running program needs to write.** Your Flask app opens `/app/data/guestbook.db` and writes rows to it. Python writes `.pyc` files. Gunicorn may write temporary files. If the image is read-only, where do those writes go?

**New word: the writable layer.** When you run `docker run`, Docker takes the image's read-only layers and puts one more, thin, empty layer on top. This one belongs to that one container alone, and it can be written to. It is called the container's *writable layer* (the Docker documentation also calls it the "container layer"). Every file the container creates, changes or deletes is recorded in this top layer. The layers underneath are not touched.

**How the container sees one filesystem.** Inside the container, `ls /app` shows you one ordinary directory tree. You do not see layers. Docker's storage driver (on Ubuntu today this is `overlay2`, or the containerd image store on newer installs; you do not need to choose) stacks the layers and shows the container a merged view: if a file exists in the writable layer, you see that version; if not, you see the one from the image below. When the container changes a file that came from the image, the file is first copied up into the writable layer and changed there. This is called *copy-on-write*: the copy happens only at the moment of writing. When the container deletes a file that came from the image, the writable layer records a small "this file is gone" marker, and the merged view hides the file. The image still has it.

So when your guestbook first started and found no `/app/data/guestbook.db`, it created one. That file was born in the writable layer of the container named `guestbook`, and it grew there with every entry.

**What `docker stop` does to the writable layer.** Nothing. Stopping a container ends its processes, but the container, as a thing Docker remembers, still exists, and so does its writable layer. You saw in chapter 2 that `docker ps -a` lists stopped containers. If on Monday you had typed `docker start guestbook` instead of `docker rm` plus `docker run`, your three entries would have been there. Stop and start keep the writable layer.

**What `docker rm` does to the writable layer.** It deletes it. Removing a container means removing everything that belonged to that container and only to it, and the writable layer is the main thing that belongs to it. The image's layers stay, because they are shared. Your database file was in the part that was not shared.

**What `docker run` does.** It always creates a *new* container, with a *new*, empty writable layer, even if you give it the same name as one you removed. A name is just a label; the old container and the new one have nothing to do with each other. That is why Monday's guestbook started empty: it was a different container, reading the same print, with blank pencil space.

Let us put this as a rule you will use for the rest of the book: **a container's writable layer lives exactly as long as the container.** Stop and start: kept. Remove: gone. Run again: a new, empty one.

**Why not just never remove containers?** It is tempting. If `docker rm` is the problem, keep the container forever and only `stop` and `start` it. This works for a weekend, and then it breaks in three ways.

First, you cannot upgrade. In chapter 4 you changed `app.py` and built a new image. A container is tied to the image it was created from; to run the new code you must create a new container from the new image, and the new container gets a new writable layer. Your data stays behind in the old one. Every upgrade becomes a data loss.

Second, the data is hard to reach. The writable layer is stored under `/var/lib/docker`, in directories with long generated names, owned by root, managed by Docker. You are not meant to go in there and copy files around, and the layout differs between storage drivers.

Third, the writable layer is slow for this kind of work. Copy-on-write is fine for a few small files. A database that rewrites pages of a file again and again pays extra cost for the layering. Docker's own documentation says to keep write-heavy data out of the writable layer.

**So what is the fix, in one sentence?** Put the data somewhere that does not belong to the container: a place on disk that Docker keeps for you and plugs into the container at `/app/data`, and that outlives any one container. That place is a volume, and it is the whole of the next section. For now the job is to see the problem with your own eyes, so that you believe it, and to learn one command that lets you look into the writable layer.

**New word: `docker diff`.** The command `docker diff NAME` lists what has changed in a container's writable layer compared to its image. Each line starts with a letter: `A` for a file or directory that was added, `C` for one that was changed, `D` for one that was deleted. It is a small command and a very honest one: whatever is in the list will vanish on `docker rm`.

**New word, briefly: `docker exec`.** You need one more tool, which you may have met in chapter 2: `docker exec NAME COMMAND` runs a command inside a container that is already running. We will use it to run `ls` inside the guestbook and see the database file.

We will reproduce Friday and Monday in the code below, but with `alpine:3.22`, the tiny image from chapter 1, first, because it makes the writable layer easy to see with a single text file, and then once with the guestbook itself.

### The code

First, a tiny experiment. Start a container from `alpine:3.22` that just sleeps, so it stays running, and write a file into it.

<!-- code: id=writable-layer-alpine unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker run -d --name scratchpad alpine:3.22 sleep 3600
$ docker exec scratchpad sh -c 'echo "my pencil mark" > /root/note.txt'
$ docker exec scratchpad cat /root/note.txt
my pencil mark
$ docker diff scratchpad
C /root
A /root/note.txt
```

The first command prints a long container id, which you can ignore; you named the container `scratchpad`, so you never need the id. `docker diff` shows that `/root` changed (`C`) and `/root/note.txt` was added (`A`). That file lives in the writable layer of `scratchpad`.

Now stop and start it, and look again.

<!-- code: id=writable-layer-stop-start unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker stop scratchpad
scratchpad
$ docker start scratchpad
scratchpad
$ docker exec scratchpad cat /root/note.txt
my pencil mark
```

Still there. Now remove it and run a new one with the same name.

<!-- code: id=writable-layer-rm unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f scratchpad
scratchpad
$ docker run -d --name scratchpad alpine:3.22 sleep 3600
$ docker exec scratchpad cat /root/note.txt
cat: can't open '/root/note.txt': No such file or directory
$ docker diff scratchpad
$ docker rm -f scratchpad
scratchpad
```

`docker rm -f` stops and removes in one step (you met `-f` in chapter 2). The new `scratchpad` has an empty `docker diff`: nothing has been written yet.

Now the same with the guestbook. Run it, add an entry in the browser at `http://127.0.0.1:8000`, then look.

<!-- code: id=writable-layer-guestbook unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 guestbook:1
$ docker exec guestbook ls -l /app/data
total 12
-rw-r--r-- 1 root root 12288 Nov 18 09:14 guestbook.db
$ docker diff guestbook
C /app
C /app/data
A /app/data/guestbook.db
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 guestbook:1
$ docker exec guestbook ls -l /app/data
total 12
-rw-r--r-- 1 root root 12288 Nov 18 09:16 guestbook.db
```

Look closely at the last listing: there *is* a `guestbook.db`, but its time is two minutes later. It is not your file. It is a brand new, empty database that the app created when the new container started. Open the page: no entries. Your exact Monday morning, reproduced in a minute. (Your sizes and times will differ; `docker diff` may also list a few Python cache files, which is fine.)

Leave this `guestbook` container running; the next section starts from it. If you prefer a clean slate, `docker rm -f guestbook`.

### The trace

| Step | Command | What changed where |
|---|---|---|
| 1 | `docker run -d --name scratchpad alpine:3.22 sleep 3600` | A new container with an empty writable layer; image unchanged |
| 2 | `docker exec scratchpad sh -c 'echo ... > /root/note.txt'` | `note.txt` added to scratchpad's writable layer |
| 3 | `docker stop` then `docker start` | Processes ended and restarted; writable layer kept |
| 4 | `docker rm -f scratchpad` | Container and its writable layer deleted; `note.txt` gone |
| 5 | `docker run ... --name scratchpad ...` again | A different container, new empty writable layer, same name |
| 6 | Guestbook run, entry added | `guestbook.db` added in the guestbook's writable layer |
| 7 | `docker rm -f guestbook`, run again | Old database deleted; app creates a new empty one |

```text
   container "guestbook"                 after docker rm
 +---------------------------+
 | writable layer            |  <-- guestbook.db lives here   (deleted)
 |   A /app/data/guestbook.db|
 +---------------------------+
 | image layers (read-only)  |  <-- shared, unchanged         (kept)
 |   app.py, Flask, Python   |
 +---------------------------+
```

### What goes wrong

**"I only stopped it, and the data is gone."** Check the order of your commands. If you used `docker run --rm` (the flag that removes a container automatically when it stops, from chapter 2), then stopping it also removed it, and the writable layer with it. `--rm` is great for throwaway commands and wrong for anything with data in the writable layer.

**`docker start` says the container does not exist.**

```text
Error response from daemon: No such container: guestbook
```

You removed it earlier. The data went with it. There is no undo for `docker rm`.

**`docker run` says the name is in use.**

```text
docker: Error response from daemon: Conflict. The container name "/guestbook" is already in use by container "...". You have to remove (or rename) that container to be able to reuse that name.
```

The old container still exists, stopped. This is actually good news if it holds data you want: `docker start guestbook` brings it back with the writable layer intact. Before removing it, think about whether there is anything inside you need. Section 5.4 shows how to never be in this position again.

**"I deleted a file inside the container, but the image did not get smaller."** Right: a deletion in the writable layer is only a marker. The file is still in the image layer below. This matters in chapter 9 when we make images smaller.

### Remember

- An image is read-only. Each container adds one thin writable layer on top, its own.
- Files a container writes go into its writable layer, by copy-on-write.
- `docker stop` and `docker start` keep the writable layer. `docker rm` deletes it. `docker run` always makes a new container with an empty one.
- `docker diff NAME` shows what is in the writable layer: whatever it lists will vanish on `docker rm`.
- Never keep data you care about in the writable layer. (Practice 8 of this book.)

**Check yourself**

1. Run `alpine:3.22` with `sleep 3600` as a container named `cy-layer`, create `/tmp/a.txt` in it with `docker exec`, and run `docker diff cy-layer`. Which lines do you see?

<details><summary>Answer</summary>

`docker run -d --name cy-layer alpine:3.22 sleep 3600`, then `docker exec cy-layer touch /tmp/a.txt`, then `docker diff cy-layer`. You see `C /tmp` and `A /tmp/a.txt`. Clean up with `docker rm -f cy-layer`.

</details>

2. In the same container, delete `/etc/motd` (a file that comes from the image) with `docker exec cy-layer rm /etc/motd`. What does `docker diff` show for it, and is the file still in the image?

<details><summary>Answer</summary>

It shows `C /etc` and `D /etc/motd`. The file is still in the image: start a new container from `alpine:3.22` and `cat /etc/motd` works. The deletion is only a marker in this container's writable layer.

</details>

3. A friend says: "I never lose data, I just `docker stop` and `docker start`." Give one everyday reason this plan fails.

<details><summary>Answer</summary>

Upgrading. A new image needs a new container, and a new container has a new, empty writable layer. The data stays behind in the old container, which you will eventually remove.

</details>

## 5.3 Named volumes

### The question

You now know the database died with the container because it lived in the container's writable layer. So the question is: can Docker give you a place to keep files that belongs to *no* container, that you can plug into one container today and a different container tomorrow, and that stays put when you `docker rm`? And if it can, how do you see it, name it, and get rid of it when you really want to?

### The picture

Think of a USB stick. Your laptop can break, be wiped, be replaced; the stick still holds your files. You plug it into one computer, work, unplug it, plug it into another. The computer decides where the stick appears (on Ubuntu, under `/media/you/STICK`), but the files belong to the stick, not to the computer.

A named volume is a USB stick that Docker keeps for you. You give it a name, Docker stores it, and when you start a container you say "plug the stick named `gb-data` in at `/app/data`". Remove the container: the stick is still there. Start a new container: plug it in again.

Where the picture stops being true: a volume is not a separate piece of hardware. It is a directory on your own disk that Docker manages, and it only lasts as long as you leave it. And unlike a stick, removing a volume does not ask "are you sure?", so the one command that deletes it deserves care.

### The idea

**New word: volume.** A *volume* is a storage area that Docker creates and manages, separate from any container's writable layer, which can be mounted into containers. *Mounted* is the next word: to *mount* something at a path means to make its contents appear at that path. If a volume is mounted at `/app/data` inside a container, then everything the container reads or writes under `/app/data` actually goes to the volume. The writable layer does not see those files at all.

**New word: named volume.** A volume you create with a name you choose, such as `gb-data`, is a *named volume*. (There are also *anonymous volumes*, which Docker names with a long random string; we will see in a moment how you get one by accident. You want named ones: a name is how you find your data again.)

**Where a volume lives.** With the default `local` driver, a named volume is a directory on the host under `/var/lib/docker/volumes/NAME/_data`. *Host* is the word for your Ubuntu machine, the one running Docker, as opposed to the containers. A *driver* is the piece of Docker that decides how a volume is stored; `local` means "a directory on this machine", and it is the only one you will need in this book. You can see this path with `docker volume inspect`, but you should not reach into it by hand: it is owned by root and Docker expects to manage it. Treat it like the inside of a database: look, don't edit.

**The commands.** Volumes have their own small family of commands under `docker volume`:

- `docker volume create NAME` makes an empty named volume.
- `docker volume ls` lists volumes.
- `docker volume inspect NAME` prints details as JSON, including `Mountpoint`, the directory on the host.
- `docker volume rm NAME` deletes a volume and everything in it.
- `docker volume prune` deletes anonymous volumes that no container uses; `docker volume prune -a` deletes named ones too. Per practice 4, this book shows prune commands but you do not run them; on a machine with other projects, "unused" can include data you still need.

**Mounting a volume when you run a container.** There are two ways to write it. The short one is `-v`:

```text
-v gb-data:/app/data
```

Read it left to right: the volume named `gb-data`, mounted at `/app/data` inside the container. The colon separates the two. The long one is `--mount`:

```text
--mount type=volume,source=gb-data,target=/app/data
```

It says the same thing in named parts. `type=volume` says it is a volume, `source` is the volume name, `target` is the path in the container. The long form is clearer and fails more loudly when you make a mistake, which is why Docker's documentation prefers it. The short form is everywhere in blog posts and is quicker to type. This book uses `-v` for volumes in commands you type, and shows `--mount` where its stricter checking helps, as you will see with bind mounts in 5.5.

**If the volume does not exist yet.** With `-v gb-data:/app/data`, if there is no volume called `gb-data`, Docker creates it for you. Handy, and also a trap: a typo such as `gb-date` silently creates a second, empty volume, and your app happily starts with no data. Creating volumes explicitly with `docker volume create` first, and checking with `docker volume ls`, keeps you honest.

**The anonymous-volume trap.** If you write only a container path, `-v /app/data`, with no name before it, Docker creates an anonymous volume with a random name. Your data lands there, survives `docker rm`, and you then cannot easily tell which of several random-named volumes holds it. Always give the name.

**What happens to the volume on `docker rm`.** Nothing. `docker rm guestbook` removes the container and its writable layer. A named volume mounted into it is untouched. This is the whole point. (`docker rm -v` also removes *anonymous* volumes that belonged to the container, but never named ones.)

**One volume, many containers.** A volume can be mounted into more than one container, even at the same time. Both see the same files. This is useful for small tools, as in the code below, where a second container reads what the first wrote. For a SQLite database, two running copies of the app writing to the same file at once is asking for trouble; run one at a time.

**Removing a volume removes the data (5.9).** This is short, and it is the most important paragraph in this section. `docker volume rm gb-data` deletes the volume's directory and every file in it. There is no recycle bin, no undo, and no confirmation prompt. Docker refuses only in one case: when a container, running or stopped, still uses the volume. Then you see:

```text
Error response from daemon: remove gb-data: volume is in use - [...]
```

with the container's id in the brackets. That refusal is your last safety net. If you remove the container first and then the volume, nothing stops you. Three habits follow:

1. Before `docker volume rm`, ask "is there anything in here I need?" and, for real data, take a copy first (5.8 shows how to back up a volume).
2. Never run `docker volume prune -a` on a machine where you have data you care about, unless you have read the list of volumes it will delete.
3. In chapter 7 you will meet `docker compose down -v`. The `-v` there means "also remove the volumes". Practice 10 says never do that on data you need, and now you know why.

### The code

Create a volume, look at it, and use it from two short-lived containers in turn. This shows the data surviving the removal of the container that wrote it.

<!-- code: id=volume-create-ls unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker volume create gb-scratch
gb-scratch
$ docker volume ls
DRIVER    VOLUME NAME
local     gb-scratch
$ docker volume inspect gb-scratch
[
    {
        "CreatedAt": "2026-11-18T09:20:11Z",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/gb-scratch/_data",
        "Name": "gb-scratch",
        "Options": null,
        "Scope": "local"
    }
]
```

If you have other volumes from earlier experiments, `docker volume ls` lists them too.

Now write into the volume from one container, remove that container, and read from another.

<!-- code: id=volume-survives-rm unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker run --name writer -v gb-scratch:/stick alpine:3.22 sh -c 'echo "kept on the stick" > /stick/note.txt'
$ docker rm writer
writer
$ docker run --rm --name reader -v gb-scratch:/stick alpine:3.22 cat /stick/note.txt
kept on the stick
```

The `writer` container ran its one command and exited; we removed it. The file did not go with it. The `reader` container, a different container, mounted the same volume at the same path and found the file. Note that `--rm` is safe here: it removes `reader`'s writable layer, but the note lives on the volume.

Now the deletion, on purpose, so you see what it looks like.

<!-- code: id=volume-rm unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker run -d --name holder -v gb-scratch:/stick alpine:3.22 sleep 3600
$ docker volume rm gb-scratch
Error response from daemon: remove gb-scratch: volume is in use - [...]
$ docker rm -f holder
holder
$ docker volume rm gb-scratch
gb-scratch
$ docker run --rm --name reader -v gb-scratch:/stick alpine:3.22 cat /stick/note.txt
cat: can't open '/stick/note.txt': No such file or directory
$ docker volume rm gb-scratch
gb-scratch
```

Read the last three commands slowly. The volume was deleted. Then `-v gb-scratch:/stick` *created a new, empty one* with the same name, and the file was not in it. The final `docker volume rm` cleans up that accidental new volume. (The brackets in the error hold the id of `holder`; yours will differ.)

### The trace

| Step | Command | What changed where |
|---|---|---|
| 1 | `docker volume create gb-scratch` | Empty directory under `/var/lib/docker/volumes/gb-scratch/_data` on the host |
| 2 | `docker run --name writer -v gb-scratch:/stick ...` | `note.txt` written into the volume, not the writable layer |
| 3 | `docker rm writer` | writer's writable layer deleted; volume untouched |
| 4 | `docker run --rm --name reader -v gb-scratch:/stick ...` | New container sees `note.txt` |
| 5 | `docker volume rm` while `holder` uses it | Refused: volume in use |
| 6 | `docker rm -f holder`, `docker volume rm gb-scratch` | Volume and `note.txt` deleted for good |
| 7 | `-v gb-scratch:/stick` again | A new, empty volume with the old name was created |

```text
   host: /var/lib/docker/volumes/gb-scratch/_data/note.txt
                         ^
          mounted at /stick in each container in turn
          |                         |
   +-------------+           +-------------+
   | writer      |  removed  | reader      |
   | /stick ->vol|  ------>  | /stick ->vol|
   +-------------+           +-------------+
```

### What goes wrong

**A typo in the volume name.** You meant `gb-data` and typed `gb-date`. No error: Docker made a new empty volume and the app started with nothing. Check with `docker volume ls`; you will see both names. Remove the wrong one once you are sure it is empty.

**An anonymous volume you did not mean.** `docker volume ls` shows lines like `local     3f9a1c...` with a 64-character name. Something ran with `-v /path` and no name, or an image declared a `VOLUME` (an instruction we do not use in this book). Find which container uses it with `docker ps -a --filter volume=NAME`.

**"volume is in use".** Shown above. A stopped container still counts. Remove the container (after thinking) and try again.

**`docker volume rm` succeeded and you wanted the data.** There is no fix. This is why 5.8 exists, and why the Remember list below has the line it has.

### Remember

- A named volume is storage Docker manages, outside any container. Create with `docker volume create NAME`, list with `docker volume ls`.
- `-v NAME:/path` (or `--mount type=volume,source=NAME,target=/path`) mounts it; files under `/path` go to the volume.
- `docker rm` never removes a named volume. Always name volumes; `-v /path` alone makes an anonymous one.
- `-v` with a name that does not exist silently creates an empty volume.
- `docker volume rm` deletes the data, with no undo. Only "in use" stops it.

**Check yourself**

1. Create a volume `cy-vol`, write the date into `/v/when.txt` from a container named `cy-a` using `alpine:3.22` and `date > /v/when.txt`, remove `cy-a`, and read the file from a container named `cy-b`.

<details><summary>Answer</summary>

```text
docker volume create cy-vol
docker run --name cy-a -v cy-vol:/v alpine:3.22 sh -c 'date > /v/when.txt'
docker rm cy-a
docker run --rm --name cy-b -v cy-vol:/v alpine:3.22 cat /v/when.txt
```

The date prints. Keep `cy-vol` for the next question.

</details>

2. Without looking it up, predict what `docker volume rm cy-vol` prints now, then run it. Then predict what `cat /v/when.txt` in a fresh container with `-v cy-vol:/v` prints.

<details><summary>Answer</summary>

It prints `cy-vol`: no container uses it (`cy-a` was removed, `cy-b` used `--rm`). The `cat` then fails with `No such file or directory`, because `-v cy-vol:/v` created a new empty volume. Remove it again with `docker volume rm cy-vol`.

</details>

3. Run `docker run --rm --name cy-anon -v /data alpine:3.22 true` and then `docker volume ls`. What do you see, and why?

<details><summary>Answer</summary>

If `--rm` is used, Docker removes the anonymous volume along with the container, so you may see nothing new. Without `--rm` (and then `docker rm cy-anon`) a volume with a long random name stays behind. Either way, `-v /data` with no name makes an anonymous volume; always give a name.

</details>

## 5.4 Putting the SQLite file on a volume

### The question

You have the two halves now: the guestbook writes `/app/data/guestbook.db`, and a named volume can keep files across containers. How do you join them so that the guestbook's database goes on the volume, survives `docker rm`, and survives an upgrade to a new image? And which path exactly do you mount: the file, the directory, or all of `/app`?

### The picture

Back to the workbook. The fix is not to make pencil marks stronger; it is to stop writing your answers in the workbook at all. You write them in a separate exercise book that you keep in your bag. Every year you get a new printed workbook (a new image), and you bring the same exercise book (the volume). The trick is to agree on where the exercise book goes: if the teacher says "answers in the green book" and you write in the blue one, you lose them anyway.

Where the picture stops being true: in Docker, the app does not know or care that `/app/data` is a volume. It just opens a path. You make the agreement on its behalf, by mounting the volume at exactly the path the app writes to.

### The idea

**New word: mount path.** The *mount path* (Docker's documentation also says *target* or *destination*) is the path inside the container where the volume appears. Everything hangs on choosing it right. The rule is: **mount the volume at the directory the app writes its data into, and nothing wider.**

For the guestbook that directory is `/app/data`. Look at the three choices:

- `-v gb-data:/app/data` mounts the directory holding the database. The app's code in `/app` still comes from the image, so a new image brings new code, and the data on the volume stays. This is right.
- `-v gb-data:/app` mounts the volume over the whole app directory. The first time, Docker copies the image's `/app` into the empty volume (more on this copying below), so it seems to work. But from then on the code lives on the volume too, and when you build `guestbook:2` with a fix, the container still runs the *old* code from the volume. Wrong: too wide.
- `-v gb-data:/app/data/guestbook.db` tries to mount a volume onto a single file. A volume is a directory, so this does not do what you want: Docker creates a directory named `guestbook.db`, and SQLite fails to open a directory as a database. Wrong: too narrow.

There is a second reason to mount the directory and not the file, specific to SQLite. While it writes, SQLite creates helper files next to the database, such as `guestbook.db-journal` (or `-wal` and `-shm` in another mode). They must be in the same directory as the database. Mount the directory and they are.

**Where does the app's path come from?** From the code. Somewhere in `app.py` there is a line like `DB_PATH = "/app/data/guestbook.db"`. In chapter 6 you will learn to set such paths from outside with environment variables; for now, the path is fixed and you mount to match it. When you meet a new image made by someone else, its documentation tells you its data path (for example, the official PostgreSQL image documents `/var/lib/postgresql/data`). Mounting at a different path than the program uses is the most common volume mistake there is: the volume stays empty and the data keeps going into the writable layer.

**What happens the first time an empty named volume is mounted.** This is a detail that surprises people, so here it is plainly. When you mount an *empty* named volume at a path where the *image* already has files, Docker copies those files from the image into the volume before the container starts. If the volume already has anything in it, Docker copies nothing and the volume's contents win. So:

- If the image has an empty `/app/data` directory, the volume gets nothing copied but inherits that directory's owner and permissions. That matters in 5.6 and 5.7.
- If the image has no `/app/data` at all, Docker creates the directory, owned by root.

This copying happens only for volumes, never for bind mounts (5.5), and only into an empty volume.

**Making the directory in the Dockerfile.** It is good practice for the image to contain the data directory, so the mount point exists and has the owner you expect. If your chapter 4 Dockerfile does not create `/app/data`, add one line after `WORKDIR /app`:

```text
RUN mkdir -p /app/data
```

`mkdir -p` creates the directory and does not complain if it already exists. We will build this as `guestbook:2`, keeping `guestbook:1` untouched, so you can compare. Tags are cheap; reusing a tag for a different build hides what changed. (In 5.7 this same line grows a `chown`, when the app stops running as root.)

**What does not change.** The app, the port, `-p 127.0.0.1:8000:8000`, the container name. Only one flag is added to `docker run`. That is the beauty of mounts: the program needs no change.

**The upgrade, the real test.** The proof that you got it right is not that the entries survive `docker rm`. It is that they survive running a *new image*. We will remove the container, start one from a different tag with the same volume, and find the entries.

**How to check what is mounted.** `docker inspect NAME` prints everything Docker knows about a container. With a *format* you can pick out one part: `docker inspect -f '{{ json .Mounts }}' guestbook` prints the list of mounts as JSON. The `{{ ... }}` is Go template syntax, the language Docker uses for `-f`; you only need to copy this one line. If `.Mounts` is `[]`, nothing is mounted and your data is in the writable layer.

### The code

The Dockerfile, as chapter 4 left it, with the one new line marked. Your requirements and file names may differ a little; keep yours and add only the `RUN mkdir` line.

```text
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN mkdir -p /app/data          # new in chapter 5
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

Build it, create the volume, and run with the volume mounted.

<!-- code: id=guestbook-volume-run unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker build -t guestbook:2 .
...
 => naming to docker.io/library/guestbook:2
$ docker rm -f guestbook
guestbook
$ docker volume create gb-data
gb-data
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2
$ docker inspect -f '{{ json .Mounts }}' guestbook
[{"Type":"volume","Name":"gb-data","Source":"/var/lib/docker/volumes/gb-data/_data","Destination":"/app/data","Driver":"local","Mode":"z","RW":true,"Propagation":""}]
```

(The `docker rm -f guestbook` is there in case the container from 5.2 is still around; if it is not, you see `No such container`, which is fine. The `Mode` field may be empty on your machine.)

Now open `http://127.0.0.1:8000` and sign the book twice. Then do Friday and Monday again.

<!-- code: id=guestbook-volume-survives unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2
$ docker run --rm --name gb-peek -v gb-data:/data alpine:3.22 ls -l /data
total 12
-rw-r--r--    1 root     root         12288 Nov 18 09:41 guestbook.db
$ docker diff guestbook
```

Refresh the page: both entries are there. `gb-peek` is a throwaway `alpine` container that mounts the same volume to show you the file without going through the app. And `docker diff guestbook` is now empty (or lists only Python cache files): the database is no longer in the writable layer at all.

The upgrade test. Pretend `guestbook:1` is the new version (any other image of the app will do) and run it with the same volume:

<!-- code: id=guestbook-volume-upgrade unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:1
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2
```

At each step the page shows the same entries. Different images, different containers, one volume. Leave the last `guestbook` running.

### The trace

| Step | Command | What changed where |
|---|---|---|
| 1 | `docker build -t guestbook:2 .` | New image with an empty `/app/data` directory |
| 2 | `docker volume create gb-data` | Empty volume on the host |
| 3 | `docker run ... -v gb-data:/app/data guestbook:2` | Volume mounted at `/app/data`; app creates `guestbook.db` on the volume |
| 4 | Two entries signed in the browser | Rows written to `guestbook.db` on the volume |
| 5 | `docker rm -f guestbook` | Writable layer deleted; volume untouched |
| 6 | Run again, then with `guestbook:1`, then `guestbook:2` | Each new container mounts the same volume; entries shown every time |

```text
   image guestbook:2 (read-only)       volume gb-data (on host)
   /app/app.py  /app/templates ...     guestbook.db
            \                            /
             \                          /
          container "guestbook" sees:
          /app/app.py        <- from image
          /app/data/         <- the volume, mounted here
          /app/data/guestbook.db
```

### What goes wrong

**The entries still vanish.** Run `docker inspect -f '{{ json .Mounts }}' guestbook`. If it prints `[]`, you forgot `-v`. If it shows a `Destination` other than `/app/data`, for example `/data`, the volume is mounted at a path the app never uses, and `docker diff guestbook` shows `A /app/data/guestbook.db` in the writable layer. Fix the target path.

**`sqlite3.OperationalError: unable to open database file`.** In the logs (`docker logs guestbook`), this has two common causes. You mounted at the file path, so `guestbook.db` is a directory: check with the `gb-peek` command above, which shows `drwxr-xr-x ... guestbook.db`. Or the app cannot write to the directory, the permissions problem of 5.6 and 5.7.

**The new code does not show up after a rebuild.** You mounted too wide, at `/app`, and the old code was copied into the volume the first time. Mount at `/app/data`. To clean up the wrong volume you will have to copy the database out first; Practice task 6 in 5.11 walks through it.

**`docker run` says the port is already allocated.** An old `guestbook` from earlier is still running, or another container publishes 8000. You met this in chapter 4 (4.11): stop it, or check `docker ps`.

### Remember

- Mount the volume at the directory the app writes to: `-v gb-data:/app/data`. Not the file, not all of `/app`.
- Code comes from the image, data comes from the volume: then a new image upgrades the code and keeps the data.
- An empty named volume gets the image's files at that path copied in, the first time only.
- Create the data directory in the Dockerfile: `RUN mkdir -p /app/data`.
- Check with `docker inspect -f '{{ json .Mounts }}' NAME` and `docker diff NAME`.

**Check yourself**

1. Without the browser, prove the database is on the volume: show its size with an `alpine:3.22` container named `cy-peek`, sign the book once more, and show it again.

<details><summary>Answer</summary>

`docker run --rm --name cy-peek -v gb-data:/data alpine:3.22 ls -l /data` before and after. The size may stay at a multiple of 4096 for small changes; the time changes. You can also look for a `-journal` file appearing for an instant during writes.

</details>

2. Run the guestbook as `cy-wrong` on port 8001 with `-v gb-data:/data` instead of `/app/data`. Sign the book. What does `docker diff cy-wrong` show, and what do you see on port 8000's guestbook?

<details><summary>Answer</summary>

`docker run -d --name cy-wrong -p 127.0.0.1:8001:8000 -v gb-data:/data guestbook:2`. `docker diff cy-wrong` shows `A /app/data/guestbook.db`: the new entry is in the writable layer, and the page on 8001 started empty. The guestbook on 8000 does not see that entry. Remove it with `docker rm -f cy-wrong`; the entry goes with it.

</details>

3. Why is `-v gb-data:/app` worse than `-v gb-data:/app/data`, even though both keep the data?

<details><summary>Answer</summary>

With `/app` the code is copied into the volume the first time and then kept there, so rebuilding the image no longer changes the code that runs. With `/app/data`, code comes from the image and data from the volume.

</details>

## 5.5 Bind mounts for code you are editing

### The question

The data is safe now. But a new annoyance has appeared. Every time you change one line of `app.py`, say the page title, you must run `docker build`, remove the container, and run it again. That is fine for a release and tiring for the twentieth small change of an afternoon. Could the container simply see the files in your project folder, as they are right now, so that you save in your editor and the running app picks it up? And if the container can write into your folder, what happens to the files it writes?

### The picture

A volume was a USB stick that Docker keeps. A bind mount is more like a window cut through a wall. On one side is your project folder in your home directory; on the other side, inside the container, is `/app`. Through the window, both sides see the very same things. Put a new sheet on your desk, and the container sees it at once. The container moves something, and it has moved on your desk too.

Where the picture stops being true: a window shows only what is on your side. Whatever was in the container's `/app` before, from the image, is hidden behind the wall while the window is open. And things the container puts on your desk come stamped with the container's name for "who did this", which, unless you say otherwise, is root.

### The idea

**New word: bind mount.** A *bind mount* makes a directory (or a file) that already exists on the host appear at a path inside the container. Unlike a volume, Docker does not create or manage it: it is your directory, wherever you choose, and Docker just passes it through. There is no copying in either direction; the container reads and writes the host's files directly.

**Writing it.** The long form, which this book uses for bind mounts:

```text
--mount type=bind,source="$(pwd)",target=/app
```

`type=bind` says it is a bind mount. `source` is the host path, and it must be absolute (start with `/`); `"$(pwd)"` is the shell asking `pwd` for the current directory and pasting it in, quoted in case the path has spaces. `target` is the path in the container. The short form is `-v "$(pwd)":/app`. Docker tells the two apart by the left side: a name like `gb-data` is a volume, a path starting with `/` is a bind mount.

**Why this book uses `--mount` for bind mounts.** Because of one difference that bites beginners. If the host path does not exist, `-v` quietly creates it, as an empty directory owned by root, and mounts that. Your app starts against an empty folder and you wonder where your code went. `--mount` refuses instead:

```text
docker: Error response from daemon: invalid mount config for type "bind": bind source path does not exist: /home/you/guestbok
```

A loud error beats a quiet empty folder.

**A mount hides what was there.** This is the rule behind 5.10's "a mount that hides files". When anything is mounted at a path, the files the image had at that path are hidden for as long as the mount is there. They are not deleted; the image still has them; the container just cannot see them. With a bind mount there is no copying to soften it (the copy-into-empty-volume rule of 5.4 is for volumes only). So `--mount type=bind,source="$(pwd)",target=/app` means `/app` inside shows *exactly* your project folder, and nothing of the image's `/app`. For code that you are editing, that is what you want. But it is why you never bind-mount an empty or wrong folder over a path the app needs.

**Mounts can nest.** You can bind-mount your project at `/app` and still mount the `gb-data` volume at `/app/data`. The deeper mount wins at its path. So your code comes from your folder, live, and the database still lives on the volume, not in your project folder. That keeps the database out of your Git repository, too.

**Getting the app to reload.** Seeing the new file is half of it; the running Python process loaded `app.py` when it started and will not read it again by itself. Gunicorn has a flag for development, `--reload`, which watches the code files and restarts its workers when they change. Anything you write after the image name in `docker run` replaces the image's `CMD` (you saw this in chapter 4), so we can start the same image with a development command, without changing the Dockerfile:

```text
guestbook:2 gunicorn --reload -b 0.0.0.0:8000 app:app
```

Use `--reload` only while developing. The image's own `CMD`, without it, is what you run for real.

**New word: UID.** On Linux every user has a number, the *user id* or *UID*. Files record the UID of their owner, not a name; `ls -l` looks the number up and prints a name. Root is always UID 0. You, the first user created on an Ubuntu machine, are usually UID 1000; `id -u` prints yours. The same goes for groups and the *GID*.

**Files owned by root after a mount (5.6).** Unless an image says otherwise, the process in a container runs as root, UID 0. That is true of `guestbook:2`: chapter 4's Dockerfile has no `USER` line. A container's root is still UID 0, and a bind mount passes files straight through to the host. So any file the container creates in your bind-mounted folder is owned on your host by UID 0, root. In the guestbook this happens without you asking: when gunicorn imports `app.py`, Python writes a compiled copy into `__pycache__/` next to it. Run `ls -l` in your project afterwards and you find a `__pycache__` directory owned by root, which you cannot delete or edit without `sudo`. Git may complain about it, your editor may fail to save over a root-owned file, and `rm -rf __pycache__` says `Permission denied`.

**Two ways out for development.** First: tell Docker to run the container's process as you, with `--user "$(id -u):$(id -g)"`. Then the files it creates in your folder are yours. Second, for a file that is already root-owned: remove it from inside a container, where you are root, for example `docker run --rm --name gb-clean --mount type=bind,source="$(pwd)",target=/work alpine:3.22 rm -rf /work/__pycache__`. (`sudo rm` works too, but it is a habit worth not forming: one typo with `sudo rm -rf` costs much more than one with plain `rm`.)

**But `--user` bumps into the volume.** If you run as UID 1000, the app now needs to write to `/app/data` on the `gb-data` volume, and that directory was created as root (by `mkdir` in the Dockerfile, run as root, and copied onto the empty volume). UID 1000 cannot write there, and SQLite fails with `unable to open database file` or `attempt to write a readonly database`. The real fix is not a flag for development; it is that the app should not run as root at all, in development or in production. Section 5.7 does it properly: create a user in the Dockerfile, give it `/app/data` with `chown`, and switch to it with the `USER` instruction (practice 11). Then the volume gets the right owner from the image, and `--user` is not needed. Until you reach 5.7, for the exercises here, use `--user` only with the `alpine` examples, and accept the root-owned `__pycache__` when running the guestbook, cleaning it up as shown.

**Volume or bind mount?** Volumes for data the app owns: databases, uploads. Docker manages them, they survive containers, they do not depend on where your home directory is. Bind mounts for files *you* own and edit on the host: your code during development, a config file you want the container to read. Practice 8 says data goes on a named volume; a bind mount is for code you are editing.

### The code

Go to your guestbook project folder (the one with the Dockerfile and `app.py` from chapter 4). Run the guestbook with your code bind-mounted and the database on the volume.

<!-- code: id=bind-mount-dev unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ cd ~/guestbook
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook-dev -p 127.0.0.1:8000:8000 --mount type=bind,source="$(pwd)",target=/app -v gb-data:/app/data guestbook:2 gunicorn --reload -b 0.0.0.0:8000 app:app
$ docker inspect -f '{{ json .Mounts }}' guestbook-dev
[{"Type":"bind","Source":"/home/you/guestbook","Destination":"/app","Mode":"","RW":true,"Propagation":"rprivate"},{"Type":"volume","Name":"gb-data","Source":"/var/lib/docker/volumes/gb-data/_data","Destination":"/app/data","Driver":"local","Mode":"z","RW":true,"Propagation":""}]
```

Now change the page title in `app.py` or a template, save, and refresh the page. The new title appears in a second or two, and the entries are still there. Watch it happen in the logs:

<!-- code: id=bind-mount-reload-logs unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker logs guestbook-dev
[2026-11-18 10:02:11 +0000] [1] [INFO] Starting gunicorn 23.0.0
[2026-11-18 10:02:11 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2026-11-18 10:02:11 +0000] [7] [INFO] Booting worker with pid: 7
[2026-11-18 10:03:40 +0000] [7] [INFO] Worker reloading: /app/app.py modified
[2026-11-18 10:03:40 +0000] [9] [INFO] Booting worker with pid: 9
```

(Your gunicorn version and the pids will differ.) Now the root-owned files.

<!-- code: id=bind-mount-root-owned unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ ls -ld __pycache__
drwxr-xr-x 2 root root 4096 Nov 18 10:02 __pycache__
$ rm -rf __pycache__
rm: cannot remove '__pycache__/app.cpython-313.pyc': Permission denied
$ docker rm -f guestbook-dev
guestbook-dev
$ docker run --rm --name gb-clean --mount type=bind,source="$(pwd)",target=/work alpine:3.22 rm -rf /work/__pycache__
$ ls -ld __pycache__
ls: cannot access '__pycache__': No such file or directory
```

And the `--user` flag, shown with `alpine` so nothing else is involved:

<!-- code: id=bind-mount-user unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ mkdir -p ~/mount-test && cd ~/mount-test
$ docker run --rm --name as-root --mount type=bind,source="$(pwd)",target=/out alpine:3.22 touch /out/by-root.txt
$ docker run --rm --name as-me --user "$(id -u):$(id -g)" --mount type=bind,source="$(pwd)",target=/out alpine:3.22 touch /out/by-me.txt
$ ls -l
total 0
-rw-r--r-- 1 you  you  0 Nov 18 10:10 by-me.txt
-rw-r--r-- 1 root root 0 Nov 18 10:10 by-root.txt
```

Clean up the root-owned file the same way as before, then remove the folder: `docker run --rm --name gb-clean --mount type=bind,source="$(pwd)",target=/work alpine:3.22 rm /work/by-root.txt`, then `cd ~ && rm -r ~/mount-test`. Start the normal guestbook again: `docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2`.

### The trace

| Step | Command | What changed where |
|---|---|---|
| 1 | `docker run ... --mount type=bind,source="$(pwd)",target=/app -v gb-data:/app/data ...` | `/app` shows your folder; `/app/data` shows the volume; image's `/app` hidden |
| 2 | Edit and save `app.py` on the host | Same file changes inside the container at once; gunicorn reloads |
| 3 | Gunicorn imports the app | `__pycache__/` created in your folder, owned by root (UID 0) |
| 4 | `rm -rf __pycache__` as you | Refused: not your file |
| 5 | `docker run ... alpine:3.22 rm -rf /work/__pycache__` | Removed from inside a container running as root |
| 6 | `--user "$(id -u):$(id -g)"` | New files in the bind mount owned by you |

```text
   host                                  container "guestbook-dev"
   /home/you/guestbook/  <== bind ==>    /app/            (image's /app hidden)
      app.py                                app.py
      __pycache__/ (root!)                  __pycache__/
   /var/lib/docker/volumes/gb-data/_data  <== volume ==>  /app/data/
      guestbook.db                                          guestbook.db
```

### What goes wrong

**`bind source path does not exist`.** Shown above: you ran from the wrong directory or misspelled the path. `pwd` and `ls` tell you where you are. With `-v` instead of `--mount`, the same mistake gives no error, an empty `/app`, and in the logs:

```text
Failed to find attribute 'app' in 'app'.
```

or `ModuleNotFoundError: No module named 'app'`, because the code is hidden behind an empty mount. Then remove the root-owned empty directory that `-v` created.

**The change does not show.** Either the app was not started with `--reload` (check `docker logs`), or you are editing a file in a different folder than the one mounted (check `Source` in `docker inspect -f '{{ json .Mounts }}'`).

**`Permission denied` on the host.** Root-owned files from the container. Remove them from a container, or prevent them with `--user`.

**`attempt to write a readonly database` or `unable to open database file`** after adding `--user`. The volume's `/app/data` is owned by root. Do not fix it with `chmod 777`; 5.7 fixes it with `USER`.

### Remember

- A bind mount shows a host directory inside the container, live, in both directions. Use `--mount type=bind,source="$(pwd)",target=/app`.
- `--mount` errors on a missing host path; `-v` silently creates an empty root-owned one.
- Any mount hides what the image had at that path.
- Bind mounts for code you edit, named volumes for data. They nest: code at `/app`, volume at `/app/data`.
- A container running as root creates root-owned files in your folder. `--user "$(id -u):$(id -g)"` for quick runs; `USER` in the Dockerfile (5.7) for the real fix.

**Check yourself**

1. In an empty folder `~/cy-bind`, run an `alpine:3.22` container named `cy-bind` with that folder bind-mounted at `/w`, which writes `hello` into `/w/hi.txt`. Who owns `hi.txt` on the host?

<details><summary>Answer</summary>

`docker run --rm --name cy-bind --mount type=bind,source="$(pwd)",target=/w alpine:3.22 sh -c 'echo hello > /w/hi.txt'`. `ls -l` shows owner `root`. Remove it from a container as shown in The code.

</details>

2. Do the same with `--user "$(id -u):$(id -g)"`. Who owns it now? Then try writing to `/` instead of `/w` in that container. What happens and why?

<details><summary>Answer</summary>

You own it. Writing to `/hi.txt` fails with `Permission denied`: the container's `/` belongs to root, and the process is now UID 1000, not root.

</details>

3. Run `docker run --rm --name cy-hide --mount type=bind,source="$HOME/cy-bind",target=/etc alpine:3.22 ls /etc`. What do you see, and where did alpine's `/etc` go?

<details><summary>Answer</summary>

Only the files from `~/cy-bind`. Alpine's `/etc` is hidden by the mount, not deleted; a container without the mount sees it as usual. (Some programs fail badly with `/etc` hidden; that is the danger of mounting over a path the image needs.)

</details>

## 5.11 Practice: break it and fix it, the vanishing guestbook

### The question

You know three places a file can live: a container's writable layer, a named volume, a bind-mounted host folder. Can you tell, from the outside, which one a given file is in? And when the guestbook loses its entries, refuses to start, or shows the wrong code, can you find which of the three is to blame and fix it, without guessing and without deleting anything you need?

### The picture

A detective at a missing-property case does not search the whole city. She asks: where was it kept, who had the key, and who was last in the room? For a missing file you ask the same three things: which place held it (writable layer, volume, bind mount), which user owned it (root or you), and which command touched it last (`rm`, `volume rm`, a new `run`).

Where the picture stops being true: a detective cannot rewind. You often can, because you can always start a fresh throwaway `alpine:3.22` container, mount the suspect volume or folder, and look, without touching the app.

### The idea

This section adds no new commands. It collects the mistakes of 5.10 so you can recognise them by their symptoms, then gives you eight tasks. The first ones repeat what you did; the middle ones hand you something broken to fix; the last ones ask you to build a small procedure yourself.

**The three questions, as commands.** For any container, three commands answer almost every data question:

- `docker inspect -f '{{ json .Mounts }}' NAME`: which mounts, from where, to where. `[]` means no mounts: everything is in the writable layer.
- `docker diff NAME`: what is in the writable layer. If your data file appears here with `A`, it is not on a volume, and it will vanish on `docker rm`.
- `docker run --rm --name peek -v VOLUME:/data alpine:3.22 ls -l /data`: what is on a volume, and who owns it, without the app.

**The mistakes of 5.10, by symptom.**

*Data gone.* Four usual causes. No `-v` at all (Mounts is `[]`). The wrong target path, so the volume is mounted where the app never writes (`docker diff` shows the database). A typo in the volume name, so a new empty volume was created (`docker volume ls` shows two similar names). Or the volume was really deleted, by `docker volume rm`, `docker volume prune`, or later `docker compose down -v`; then there is nothing to recover unless you made a backup (5.8).

*Permission denied.* On the host, about files a container created in a bind mount: they are root's. Inside the container, from SQLite (`unable to open database file`, `attempt to write a readonly database`): the process runs as a user who does not own `/app/data` on the volume. The fix for the first is to remove the files from a container and use `--user` next time; for the second, 5.7's `USER` with a `chown` in the Dockerfile. Never `chmod 777`: it makes the problem disappear by letting everyone write everything.

*A mount that hides files.* Something is mounted over a path where the image had files the app needs. Symptoms: `ModuleNotFoundError`, `Failed to find attribute 'app' in 'app'`, a missing template, or "my rebuild changed nothing". Check `Destination` in the Mounts output. Bind mounts hide completely. A volume mounted too wide (at `/app`) hides newer code behind the old copy it took the first time.

**Rules for the practice.** Name every container. Remove only what you made. Before any `docker volume rm`, look inside the volume. Use `-p 127.0.0.1:8000:8000` (or 8001 when two run at once). For each task, try it before opening the answer.

### The code

A quick setup that the tasks assume: the `gb-data` volume holds your entries and a guestbook is running from `guestbook:2`.

<!-- code: id=practice-setup unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f guestbook
guestbook
$ docker volume ls --filter name=gb-data
DRIVER    VOLUME NAME
local     gb-data
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2
$ docker run --rm --name peek -v gb-data:/data alpine:3.22 ls -l /data
total 12
-rw-r--r--    1 root     root         12288 Nov 18 09:41 guestbook.db
```

**Task 1 (do it again).** Remove the `guestbook` container and run it again with the same volume. Show that the entries survive, using the browser and `docker diff`.

<details><summary>Answer</summary>

`docker rm -f guestbook`, then the same `docker run` as in the setup. The page shows the entries. `docker diff guestbook` does not list `guestbook.db`, because the file is on the volume.

</details>

**Task 2 (do it again).** Create a volume `practice-notes`. From a container named `p-write` using `alpine:3.22`, write three lines into `/n/notes.txt`. Remove `p-write`. Read the file from a container named `p-read`. Then remove the volume and prove it is gone.

<details><summary>Answer</summary>

```text
docker volume create practice-notes
docker run --name p-write -v practice-notes:/n alpine:3.22 sh -c 'printf "one\ntwo\nthree\n" > /n/notes.txt'
docker rm p-write
docker run --rm --name p-read -v practice-notes:/n alpine:3.22 cat /n/notes.txt
docker volume rm practice-notes
docker volume ls --filter name=practice-notes
```

The last command prints only the header line. Do not run `p-read` again before checking: `-v practice-notes:/n` would create a new empty volume.

</details>

**Task 3 (read the clues).** A friend runs this and says the entries disappear every time he upgrades:

```text
docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/data guestbook:2
```

Without running his command, say what is wrong, which command would prove it, and the fix.

<details><summary>Answer</summary>

The volume is mounted at `/data`, but the app writes to `/app/data`. `docker diff guestbook` would show `A /app/data/guestbook.db` in the writable layer, and `docker run --rm --name peek -v gb-data:/data alpine:3.22 ls /data` shows the volume empty. Fix: `-v gb-data:/app/data`.

</details>

**Task 4 (find and fix).** Run this broken setup, and get the guestbook working with the entries from `gb-data`, without deleting anything you have not checked first:

<!-- code: id=practice-task4-broken unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-dta:/app/data guestbook:2
```

<details><summary>Answer</summary>

The page is empty. `docker volume ls` shows both `gb-data` and `gb-dta`: the typo created a new volume. Fix:

```text
docker rm -f guestbook
docker run --rm --name peek -v gb-dta:/data alpine:3.22 ls -l /data
docker volume rm gb-dta
docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data:/app/data guestbook:2
```

Look inside `gb-dta` before removing it: if someone signed the book in the meantime, those entries are in it.

</details>

**Task 5 (find and fix).** In your project folder, run:

<!-- code: id=practice-task5-broken unrun="needs Docker Hub images, not reachable on this machine" -->
```console
$ docker rm -f guestbook
guestbook
$ docker run -d --name guestbook-dev -p 127.0.0.1:8000:8000 -v "$(pwd)/src":/app -v gb-data:/app/data guestbook:2 gunicorn --reload -b 0.0.0.0:8000 app:app
$ docker logs guestbook-dev
...
ModuleNotFoundError: No module named 'app'
```

Explain the error, the extra thing it left on your disk, and the fix.

<details><summary>Answer</summary>

There is no `src` folder in the project, so `-v` created an empty `src/` owned by root on the host and mounted it over `/app`, hiding the image's code. Gunicorn cannot find `app`. Fix: `docker rm -f guestbook-dev`, remove the empty root-owned folder from a container (`docker run --rm --name gb-clean --mount type=bind,source="$(pwd)",target=/work alpine:3.22 rmdir /work/src`), and run again with `--mount type=bind,source="$(pwd)",target=/app`, which would have refused the missing path with `bind source path does not exist`.

</details>

**Task 6 (find and fix, harder).** Someone ran the guestbook for a month with `-v gb-old:/app`, too wide. Now new code does not show up. Move the database onto a correct volume `gb-data2`, mounted at `/app/data`, without losing entries. You may only use `alpine:3.22` containers and the guestbook image.

<details><summary>Answer</summary>

Stop the app so the database is not being written, then copy the file between two volumes with one throwaway container that mounts both:

```text
docker rm -f guestbook
docker volume create gb-data2
docker run --rm --name gb-move -v gb-old:/from -v gb-data2:/to alpine:3.22 cp -a /from/data/guestbook.db /to/
docker run --rm --name peek -v gb-data2:/data alpine:3.22 ls -l /data
docker run -d --name guestbook -p 127.0.0.1:8000:8000 -v gb-data2:/app/data guestbook:2
```

Check the entries in the browser. Only then, and only if you are sure, remove `gb-old`. (`cp -a` keeps owner and times.) This is a small version of 5.8's backup.

</details>

**Task 7 (build it).** Write the commands to check, for any container name, the three questions: what is mounted where, what is in its writable layer, and who owns the files on its data volume. Try them on `guestbook` and on a container `p-bare` run from `guestbook:2` with no `-v` at all, on port 8001. What differs?

<details><summary>Answer</summary>

```text
docker inspect -f '{{ json .Mounts }}' guestbook
docker diff guestbook
docker run --rm --name peek -v gb-data:/data alpine:3.22 ls -l /data
docker run -d --name p-bare -p 127.0.0.1:8001:8000 guestbook:2
docker inspect -f '{{ json .Mounts }}' p-bare
docker diff p-bare
```

For `p-bare`, Mounts is `[]` and `docker diff` lists `A /app/data/guestbook.db`: its entries will vanish on `docker rm`. Remove it with `docker rm -f p-bare`.

</details>

**Task 8 (build it).** Set up a development run that: bind-mounts your project at `/app` with `--mount`, keeps the database on `gb-data`, reloads on save, and leaves no root-owned files in your project folder. You will hit one error on the way. Name it, say which section fixes it for good, and get as close as you can with what this chapter taught.

<details><summary>Answer</summary>

Running with `--user "$(id -u):$(id -g)"` keeps your folder clean, but the app then cannot write to `/app/data` on the volume, which is owned by root: `attempt to write a readonly database` or `unable to open database file`. Section 5.7 fixes it for good with a non-root `USER` and a `chown` of `/app/data` in the Dockerfile. With this chapter alone, the closest is to run as root and avoid the compiled files with Python's own switch: add `-e PYTHONDONTWRITEBYTECODE=1` (an environment variable; chapter 6 explains `-e`):

```text
docker run -d --name guestbook-dev -p 127.0.0.1:8000:8000 -e PYTHONDONTWRITEBYTECODE=1 --mount type=bind,source="$(pwd)",target=/app -v gb-data:/app/data guestbook:2 gunicorn --reload -b 0.0.0.0:8000 app:app
```

Then `ls -l` shows no new root-owned files after you sign the book and save a change.

</details>

### The trace

A trace of Task 4, the typo, the most common of the eight:

| Step | Command | What changed where |
|---|---|---|
| 1 | `docker run ... -v gb-dta:/app/data ...` | New empty volume `gb-dta` created; app makes an empty database on it |
| 2 | Page shows no entries | `gb-data` untouched, still holds them |
| 3 | `docker volume ls` | Two volumes listed: the clue |
| 4 | `docker rm -f guestbook`, peek into `gb-dta` | Container gone; you check `gb-dta` holds nothing needed |
| 5 | `docker volume rm gb-dta` | Wrong volume deleted |
| 6 | Run with `-v gb-data:/app/data` | Entries back |

```text
   symptom              first command                         usual cause
   entries gone   ->    docker inspect -f '{{json .Mounts}}'  no -v, wrong target, typo
   permission     ->    ls -l  /  peek with alpine            root-owned files, user mismatch
   code missing   ->    Destination in Mounts                 a mount hiding the image's files
```

### What goes wrong

**Running out of patience and pruning.** When the volume list looks messy, `docker volume prune` is tempting. On current Docker it removes only unused anonymous volumes, but with `-a` it deletes every volume no container uses, which, after you removed the containers, includes `gb-data`. Read `docker volume ls`, peek into each volume you are unsure about, and remove by name.

**Fixing permissions with `chmod 777` or `sudo`.** It hides the real problem, which is which user writes where, and it stays in your project or volume long after you forgot why. Clean up from a container; fix ownership in the Dockerfile (5.7).

**Copying a database while the app writes to it.** In Task 6 the app is stopped first. Copying a SQLite file in the middle of a write can give a copy that will not open. Stop, copy, check, start.

### Remember

- Three questions for lost data: which place, which user, which command.
- `docker inspect -f '{{ json .Mounts }}'`, `docker diff`, and an `alpine:3.22` peek container answer them.
- Before deleting a volume, look inside it. Remove by name, never by prune.
- Typos in volume names and missing bind paths fail silently with `-v`; `docker volume ls` and `--mount` catch them.
- Permission problems are about UIDs; the lasting fix is `USER` in 5.7.

**Check yourself**

1. Which single command tells you whether a container's data will survive `docker rm`, and what output means "no"?

<details><summary>Answer</summary>

`docker diff NAME`. If it lists the data file (for the guestbook, `A /app/data/guestbook.db`), the data is in the writable layer and will not survive. (`docker inspect -f '{{ json .Mounts }}' NAME` printing `[]` says the same from the other side.)

</details>

2. Clean up everything this chapter's practice created, and nothing else. List the commands, and say which one you ran last and why.

<details><summary>Answer</summary>

Remove the practice containers by name (`docker rm -f p-bare guestbook-dev`, ignoring "No such container"), then the practice volumes after peeking into each: `docker volume rm gb-old` (if you made it for Task 6). Keep `gb-data` (or `gb-data2`) and the running `guestbook`: they hold your real entries and chapter 6 uses them. The volume removal comes last, after the peek, because it is the only step with no undo.

</details>

