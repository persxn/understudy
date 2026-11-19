# DevOps: containers and delivery
for: a developer who must now deploy and run their service
leads to: backend engineer who deploys, platform engineer, SRE
status: reviewed 2026-11-19 by independent agent, goals run
sources: the cards (Needs first, Goals); training.linuxfoundation.org CKAD, CKA (rows 6,
  10); developer.hashicorp.com Terraform Associate (row 9)
unverified: hours, levels, goals and planned rows are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | linux-command-line | none | work on a server from a shell | processes, permissions, services | 20 | 3 Build |
| 2 | git | none | work by pull requests | branches, merging, undo | 15 | 3 Build |
| 3 | networking-basics | none | follow a request between machines | DNS, TCP, TLS, HTTP | 25 | 2 Explain |
| 4 | docker | 1, 3 | ship a service as a small, safe image | layers, Compose | 30 | 3 Build |
| 5 | github-actions-ci-cd | 2, 4 | test every change, deploy without stored keys | secrets, OIDC | 25 | 3 Build |
| 6 | kubernetes-core | 3, 4 | run, update, debug a service on a cluster | Deployments, Services, probes | 40 | 3 Build |
| 7 | reliability-and-observability | 3, sql-and-relational, system-design-foundations, caching-and-queues | set targets, alert, survive overload | SLOs, incidents | 30 | 3 Build |
| 8 | cloud-core-services (planned) | 3, 4 | run on one cloud's services | identity, networks | 30 | 3 Build |
| 9 | infrastructure-as-code-with-terraform (planned) | 2, 5, 8 | change infrastructure from reviewed files | plan and apply, state, modules | 25 | 3 Build |
| 10 | kubernetes-internals (planned) | 1, 6 | upgrade and repair a cluster | control plane | 30 | 3 Build |
| 11 | helm-and-gitops (planned) | 2, 6 | release a cluster's services from Git | charts, sync, drift | 20 | 3 Build |
| 12 | configuration-management-with-ansible (planned) | 1 | configure servers from reviewed files | playbooks, idempotence | 15 | 2 Explain |

## Goals
### Ship my service in a container with a pipeline (about 90 h)
Steps: linux-command-line 1-8, 12; git 1-7, 9-10; networking-basics 1, 3-5, 8, 10; docker; github-actions-ci-cd 1-5, 7-14.
Open with: their service in a container from a five-line Dockerfile they wrote, seen as a plain process in the host's `ps` (docker 1-2 in miniature); then broken on purpose: a start command ending in `&` exits at once (a container lives as long as its main process).
Deep: docker 3, 4, 6; github-actions-ci-cd 8, 9, 14.
Order: docker 1-2; linux-command-line 1-4; docker 4; git 1-7; github-actions-ci-cd 1-5; linux-command-line 6, 8; docker 3; github-actions-ci-cd 7-8, 13; linux-command-line 5; docker 5-6, 11; networking-basics 1, 3-5; docker 7, 9; linux-command-line 7, 12; docker 8, 10, 12; github-actions-ci-cd 9-12; git 9-10; networking-basics 8, 10; github-actions-ci-cd 14.
Halfway: "Every pull request is tested on a clean machine; my image rebuilds in a second and stops at once."

### Deploy and debug my service on my team's cluster (about 130 h; 75 with rows 1, 2, 4 held)
Steps: linux-command-line 1-8, 12; git 1-7, 10; networking-basics 1, 3-5, 7-10; docker; github-actions-ci-cd 1-5, 7-11, 13; kubernetes-core 1-10, 12-13.
Open with: their service, imaged by a five-line Dockerfile, as a Deployment of two on a local cluster (docker 2, kubernetes-core 2, in miniature); a deleted pod returns under a new name; then a misspelt tag: `ImagePullBackOff` in `kubectl describe`.
Deep: kubernetes-core 2, 5, 9, 13; docker 3; networking-basics 10.
Order: docker 1-2; kubernetes-core 1-3; linux-command-line 1-4, 6; docker 3-6; networking-basics 1, 3-5; kubernetes-core 4-5; docker 7-8; networking-basics 7-8; linux-command-line 5, 7; kubernetes-core 6-8; git 1-7; github-actions-ci-cd 1-5, 7-8; docker 9-12; kubernetes-core 9-10; linux-command-line 8; github-actions-ci-cd 9-11, 13; networking-basics 9-10; linux-command-line 12; kubernetes-core 12-13; git 10.
Halfway: "I delete my pods and say which loop brings them back, and why a Service has no endpoints."

### Run services on a cluster and keep them up (about 170 h)
Steps: linux-command-line 1-8, 12; git 1-7, 10; networking-basics 1, 3-5, 7-10; docker; github-actions-ci-cd 1-5, 7-11, 13; kubernetes-core; reliability-and-observability 1-5, 8-9, 11-12; system-design-foundations 1, 3, 7; sql-and-relational 7.
Open with: their service, imaged by a five-line Dockerfile, as a Deployment of two on a local cluster (docker 2, kubernetes-core 2, in miniature); requests counted as a pod is deleted: what did users see?
Deep: kubernetes-core 2, 9, 13; reliability-and-observability 2, 5; system-design-foundations 3.
Order: docker 1-2; kubernetes-core 1-3; linux-command-line 1-4, 6; docker 3-6; networking-basics 1, 3-5; kubernetes-core 4-5; system-design-foundations 1, 3, 7; reliability-and-observability 1-3; docker 7-8; networking-basics 7-8; linux-command-line 5, 7; kubernetes-core 6-9; reliability-and-observability 8; git 1-7; github-actions-ci-cd 1-5, 7-8; docker 9-12; kubernetes-core 10; reliability-and-observability 9; linux-command-line 8; github-actions-ci-cd 9-11, 13; sql-and-relational 7; kubernetes-core 11; networking-basics 9-10; linux-command-line 12; reliability-and-observability 4-5; kubernetes-core 12-13; reliability-and-observability 11-12; git 10.
Halfway: "My service has an SLO from my own numbers; I can say what a deleted pod cost it."

### Move from developer to platform engineer (about 205 h)
Steps: linux-command-line; git; networking-basics; docker; github-actions-ci-cd; kubernetes-core; reliability-and-observability; system-design-foundations 1, 3-4, 7; caching-and-queues 6, 9; sql-and-relational 7.
Open with: a Linux machine of their own (a local VM or a server reached by `ssh`), their service run from the shell, stopped by `kill` and by `kill -9`: only one lets it clean up (linux-command-line 1, 6).
Deep: linux-command-line 6, 8; docker 4; github-actions-ci-cd 9; kubernetes-core 2, 9.
Order: linux-command-line 1-6, 10, 7-8; docker 1-6; networking-basics 1-5; linux-command-line 9, 11-13, then from no card what an owner of servers meets: a slow server (load, memory, the OOM killer), log rotation, the firewall, a reverse proxy, taking over an undocumented server (survey, then a runbook); docker 7-12; git 1-7; github-actions-ci-cd 1-8; kubernetes-core 1-5; networking-basics 6-10; kubernetes-core 6-10; github-actions-ci-cd 9-14; git 8-14; system-design-foundations 1, 3-4, 7; kubernetes-core 11-13; sql-and-relational 7; caching-and-queues 6, 9; reliability-and-observability 1-12; rows 8 to 11 once written.
Halfway: "From a bare server: my service in a container, tested on each pull request, on a cluster."

## Why this order
A container is a process with its own network: Linux and networking steps come where a container needs them. Git before the pipeline (it runs on pull requests). Reliability judges a running service. Helm and GitOps release to a cluster; Ansible needs only shell and SSH.

## Checkpoint projects
- After 5: each pull request tested, an image per commit. After 6: pipeline-deployed, surviving a killed pod and a bad release. After 7: SLOs, burn-rate alerts, a rehearsed rollback.

## Short on time
Goals' steps are the floor: over budget, less depth, not fewer steps.

## Left out on purpose
- Other CI systems: one pipeline learnt deeply transfers.
