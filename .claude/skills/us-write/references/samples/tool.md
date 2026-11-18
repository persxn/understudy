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

