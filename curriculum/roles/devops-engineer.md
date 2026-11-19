# devops-engineer: junior to mid-level DevOps or platform engineer (0 to 3 years)
status: reviewed 2026-11-19 by independent agent, sources reopened
sources: read 2026-11-19: handbook.gitlab.com SRE family (Associate, mid); CKA domains; Terraform Associate
  objectives; adverts (posted): unnamed Junior Platform 2026-05-04 (institutedata), Bayer Junior
  DevOps 01-20, Kforce DevOps II 08-07, Sitecore Platform 05-12, Career Team (removed 10-05), commercetools SRE
  (closed), Greenhouse Platform, unnamed (recruitee, joindevops); 3 reopened 11-19; Miratech Junior added
unverified: 9 adverts (4 closed); essential 5+ of 9, desirable 3-4; git: judgement (CI and Terraform
  run from Git); levels, hours, interview checks

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| linux-command-line | 3 Build | essential | troubleshooting (5 of 9, GitLab) | down service diagnosed |
| python-core | 3 Build | essential | scripting, Python or Bash (9 of 9) | tested automation script |
| git | 3 Build | essential | Git (4 of 9; Miratech), GitOps (3) | changes only by reviewed PR |
| networking-basics | 2 Explain | essential | DNS, VPCs (6 of 9, GitLab) | failing request traced |
| docker | 3 Build | essential | containers (5 of 9) | small non-root image |
| github-actions-ci-cd | 3 Build | essential | CI/CD (9 of 9) | PRs tested, OIDC deploy, rollback |
| kubernetes-core | 3 Build | essential | Kubernetes (8 of 9, CKA) | crashing pod fixed |
| cloud-core-services (planned) | 3 Build | essential | a cloud (9 of 9; most AWS), IAM (7) | least-privilege roles |
| infrastructure-as-code-with-terraform (planned) | 3 Build | essential | Terraform (9 of 9) | remote state, modules, drift |
| reliability-and-observability | 3 Build | essential | monitoring (9 of 9), on-call (5) | alert, dashboard, postmortem |
| helm-and-gitops (planned) | 2 Explain | desirable | GitOps (3 of 9), Helm (2) | chart synced from Git |
| configuration-management-with-ansible (planned) | 1 Use | specialist | Ansible (2 of 9, GitLab) | idempotent playbook |
| kubernetes-internals (planned) | 2 Explain | specialist | clusters (1 of 9, CKA) | upgrade done |
| sql-and-relational | 1 Use | specialist | managed databases (2 of 9) | backup restored |

## Order and time
Table order; reliability-and-observability takes only the steps of its needs it uses (DevOps map,
goal 3), the rest `later:`. Essential 280 h, desirable 20 h.

## Interview checks
- A down service found aloud (linux-command-line).
- Why a name does not resolve (networking-basics).
- A pod that will not start (kubernetes-core; CKA troubleshooting 30%).
- `plan` replaces a resource: state, locking, drift (infrastructure-as-code-with-terraform).
- An incident handled, its root cause (reliability-and-observability; GitLab RCA).

## Capstone
The learner's service on a cloud: Terraform-built, pipeline-deployed by OIDC, SLO alert, runbook. Finish: from
an empty account, `apply` and one merge serve it over HTTPS; a script kills a pod (recovers), ships a bad release (rolled back), stops it (alert fires); `destroy` leaves nothing.

## Overlap
SRE: nearly all. backend-engineer: git, docker, CI, reliability.
