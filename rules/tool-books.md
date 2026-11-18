# Books about a tool

Read when planning or writing a book about a command-line tool (Docker, Git, a shell). How to shape and write its chapters is in `rules/writers-guide.md`; this file holds only what the runner and the machine need.

## Header lines, above the first chapter

```text
run: console               the sessions are typed at a terminal
state: docker              only if sessions make things in Docker (containers, images, volumes, networks)
timeout: 120               seconds allowed for each session; a marker's own timeout= still wins
check: docker version      repeatable: must succeed on this machine before a chapter is written
mask: REGEX                repeatable: text that changes every run, ignored when output is compared
```

`python3 scripts/us_plan.py check <book>` refuses a `run:` or `state:` value it does not know.

## Planning, beyond the writer's guide

- **Chapter 1 sets the machine up:** installing the tool on the learner's system from the maker's own package source, and the day-one problems (permissions, such as the `docker` group and logging in again; the service not running; the network).
- **One small set of images or downloads, fixed in chapter 1** with their tags and rough sizes, reused all book. Prefer small ones (`-slim`, `-alpine`); never `latest`.

## For `state: docker`

- Nothing made in Docker carries from chapter to chapter: each chapter makes what it uses. Name every container (`--name`), and never quote an id in prose.
- Clean-up commands that touch more than the book made (`docker system prune`, `docker rm $(docker ps -aq)`) are shown as `mode=fragment`, never run.
- Publish ports on this machine only: `-p 127.0.0.1:8080:80`.
- To type into a program inside a container (`docker run -it`, `docker exec -it`) give the marker `stdin="..." wait=1`; to stop a foreground container, `stdin="^C" wait=3 exit=130`. Ctrl-C only stops a program that handles it: start such containers with `--init`.
- A session that cannot run on this machine gets `unrun="short plain reason"`. The reading page prints the note for it; write no "not run" sentence in the prose.
