# kubernetes-core: Kubernetes for people who will deploy, run and debug their own services
kind: tool
aliases: kubernetes, k8s, kubectl
needs: docker, networking-basics
status: reviewed 2026-11-19 by independent agent, every Show's source reopened
sources: kubernetes.io/docs: concepts (contents, objects, pod lifecycle and termination, hooks, replicaset,
  deployment, DNS, ingress, configmap, secret, resources, probes, persistent volumes, RBAC); tasks (assign
  memory, configure probes, debug pods, services, running pods, force-delete); kubectl auth can-i; blog
  2026-01-29 (ingress-nginx); CKAD domains
unverified: nothing run (no cluster): each Show is from the page named; judgement: the `preStop` pause

## Promise
Deploy, expose, configure, update and debug your own service on a cluster from files in Git, naming what each part of the cluster did.

## The one idea
You write down the state you want; control loops compare it with what runs and act on the difference. Picture: a thermostat. Where it breaks: many loops, each a little behind: the cluster converges, rarely matches.

## In production
- A managed cluster; teams own namespaces; a pipeline (github-actions-ci-cd) applies manifests from Git, images tagged by commit.

## Teaching order
1. A pod by hand: `kubectl config current-context`; `kubectl run`, then a manifest (`apiVersion`, `kind`, `metadata`, `spec`) and `kubectl apply -f`; `status` in `get -o yaml`; `describe`, `logs`; deleted, it stays gone.
2. A Deployment and the reconcile loop: Deployment, ReplicaSet, pods (`ownerReferences`); a deleted pod replaced with a new name and IP.
3. One `kubectl apply` traced: the API server stores it in etcd; controllers create pod objects; the scheduler filters, scores, binds; the kubelet has the runtime pull and start; `kubectl get events`.
4. Labels and selectors: `spec.selector.matchLabels` matching the template's labels; `get pods -l app=web`; a relabelled pod leaves its ReplicaSet, which makes another; the selector is immutable.
5. Services and cluster DNS: ClusterIP, `port` and `targetPort`, EndpointSlices of ready pods; `web`, `web.prod.svc.cluster.local`; NodePort, LoadBalancer; `kubectl port-forward`.
6. Traffic in: Ingress (inert without an ingress controller; API frozen) or the recommended Gateway API (GatewayClass, Gateway, HTTPRoute), whichever the cluster runs; TLS ended at the edge from a Secret.
7. ConfigMaps and Secrets as `env` (`valueFrom`, `envFrom`) or files in a volume; env is read at start (`kubectl rollout restart`), files update eventually.
8. Requests and limits (`250m` cpu, `256Mi`): the scheduler sums requests, never real use, against a node's allocatable; at the CPU limit, throttling; over the memory limit the kernel may kill (`OOMKilled`); over its memory request on a short node, eviction.
9. Probes and shutdown: failing liveness restarts the container; failing readiness (all its life) removes it from EndpointSlices; a startup probe holds both; `httpGet`, `exec`; on delete, SIGTERM races the EndpointSlice update: `preStop` pause, drain, exit before `terminationGracePeriodSeconds` (docker 3).
10. Rolling updates: a new image tag in `spec.template` makes a new ReplicaSet; `maxSurge`, `maxUnavailable`; `rollout status`, `history`, `undo`; `ProgressDeadlineExceeded`; the undo then made in Git, or the next apply re-breaks it.
11. Storage: `emptyDir` dies with the pod; a PersistentVolumeClaim, its volume made by a StorageClass; access modes; reclaim policy `Retain` or `Delete`; a StatefulSet when each replica needs its own name (`db-0`) and claim (`volumeClaimTemplates`).
12. Namespaces and access: RBAC Role and RoleBinding, ClusterRole, additive, no deny; ServiceAccounts for pods; `kubectl auth can-i create deployments -n team-a`.
13. Debugging drill: `get pods` (STATUS, RESTARTS), `describe` (Events), `logs --previous`, `exec`, `kubectl debug -it POD --image=busybox --target=app` for a shell-less image; each failure below made and repaired.

## State and danger
- [1,3] State lives in etcd; Git holds its only safe copy. `kubectl edit` drifts; the next apply undoes it. Safe: edit the file, `kubectl diff`, apply.
- [1,12] `~/.kube/config` holds contexts; the wrong one changes the wrong cluster. Safe: check `current-context`; `--context` in scripts.
- [12] `kubectl delete namespace` deletes all in it, no undo. Safe: confirm the context, list first (`get all` omits ConfigMaps, Secrets, claims).
- [11] Deleting a claim whose volume's reclaim policy is `Delete` (dynamic volumes take their StorageClass's) deletes the data once no pod uses it. Safe: `kubectl get pv`, patch to `Retain`, a tested backup.
- [9,11] `delete pod --force --grace-period=0` on a StatefulSet pod may start a twin of one still running. Safe: plain delete, and wait.
- [7] A Secret manifest in Git is a leak. Safe: the team's secret store.

## Step notes
### 1
Need: I can `docker run` my image; why a pod, and what happens when it dies?
Show: on their local cluster (their image pushed, or loaded into it: kind, minikube and k3d differ, look up),
`kubectl run web --image=<their image>`, `get pod web -o wide` (a node, an IP),
`delete pod web`, `get pods`: gone for good; most expect a restart (Pod Lifecycle: "never rescheduled", only
"replaced").
Explain: A pod is one run of your containers on one node, recorded as an object; with no owner, nothing makes
another.
Try: predict: `get pods` a minute after the delete; fix: [1,13] their pod's manifest with a misspelt tag
(`ImagePullBackOff`), done when it runs.
### 2
Need: If a deleted pod stays dead, how does anything stay up?
Show: `replicas: 3`; `kubectl get pods -o wide -w` beside `delete pod <one>`: in seconds a pod with a new name
and IP, the old name never back; its `ownerReferences` names a ReplicaSet, which creates pods "to reach the
desired number".
Explain: You stored "three of these"; a controller counts its pods and creates or deletes until they match: a
replacement is new, never moved.
Try: predict: pods after `scale --replicas=5`, then after deleting three at once; explain: why deleting pods
never stops the app.
### 3
Need: `kubectl apply` said `configured`; why is the old version still serving?
Show: a new tag applied, then at once `get pods`: old pods, new ones `ContainerCreating`; `get events --watch`:
`Scheduled` (`default-scheduler`), `Pulling`, `Pulled`, `Created`, `Started` (`kubelet`), after apply returned
(Working with Objects: "a record of intent"; Debug Running Pods).
Explain: apply stores desired state in etcd through the API server and returns; controllers, scheduler and
kubelet act later.
Try: predict: the events and who reports each; explain: which component has not acted when a pod stays
`Pending`, and at `ContainerCreating`.
### 4
Need: I relabelled a pod to debug it; why are there four now?
Show: `kubectl label pod <one> app=debug --overwrite` under three replicas: `get pods -l app=web` lists three,
one new; the old one runs on, uncounted (ReplicaSet: relabelled pods "will be replaced automatically").
Explain: A controller owns what its selector matches, not what it made; a pod that stops matching leaves the count.
Try: fix: a Deployment whose `matchLabels` and template labels differ, until accepted; predict: `apply` of a
changed selector on a live Deployment.
### 5
Need: The pods run and the Service exists; why does every request fail?
Show: a Service selecting `app: wbe`: `kubectl get endpointslices -l kubernetes.io/service-name=web`: `ENDPOINTS
<none>`, yet `web` resolves to its cluster IP. Fix the selector: pod IPs appear, pods untouched (Debug Services:
"a typo"; DNS for Services).
Explain: A Service is a fixed name and virtual IP; a controller writes the ready pods its selector matches into
EndpointSlices; nodes forward to them.
Try: fix: [4,5,13] their Service with no endpoints, done when every ready pod is listed; predict: `port` and
`targetPort` swapped.
### 6
Need: I created an Ingress for my host name; why does nothing answer?
Show: an Ingress on a cluster with no controller: listed, no address, no answer; with a controller an address
comes, often `<pending>` first (Ingress: "Only creating an Ingress resource has no effect").
Explain: Ingress and Gateway objects are rules; a controller reads them and configures a real proxy at the edge.
Try: apply: their host routed to their Service by their cluster's controller, done when `curl -H 'Host: ...'`
answers; decide: Ingress or Gateway API.
### 7
Need: I applied the new ConfigMap; why does the app still use the old setting?
Show: a ConfigMap as `env` and as a mounted file, a value changed: `kubectl exec <pod> -- printenv LOG_LEVEL`
stays old, the file changes later, no rollout starts; `rollout restart` brings it (ConfigMaps: env needs "a pod
restart"; Deployments: rollouts follow `.spec.template`).
Explain: env is copied in at start, a mounted file refreshed later by the kubelet; neither tells the app, and the
Deployment did not change.
Try: predict: env, file and `subPath` file a minute after a change; decide: how their pipeline rolls out
config.
### 8
Need: The node is nearly idle; why is my pod `Pending`, and why does another keep dying?
Show: the docs' manifests. Request `1000Gi`: `Pending` for ever, `FailedScheduling`, `Insufficient memory`. A 100Mi limit around 250M: `OOMKilled`, `exitCode: 137`, RESTARTS climbing, `Back-off
restarting failed container` (Assign Memory Resources; Resource Management).
Explain: The scheduler adds requests, never real use, against each node's allocatable; the kernel enforces memory
limits by killing, CPU limits by throttling.
Try: explain: why `memory: 400m` asks for 0.4 bytes; decide: their requests and limits from measured use.
### 9
Need: Both my probes call `/health`, which checks the database; what happens when it blips?
Show: three replicas, database scaled to 0. In readiness: `Running`, READY `0/1`, RESTARTS 0, no endpoints; back
with the database. In liveness: `Liveness probe failed`, `will be restarted`, RESTARTS climbing everywhere
(Configure Probes; Probes: liveness "can lead to cascading failures", readiness checks back-ends).
Explain: Readiness decides traffic, never restarts; liveness restarts the container, which helps only a stuck
container.
Try: build: requests looped through `rollout restart`, errors counted, then again with a `preStop` pause, done
when those errors are gone (endpoints go "at the same time" as shutdown starts: Pod Termination); fix: [9]
liveness killing a slow starter.
### 10
Need: The new version is broken; will Kubernetes roll it back?
Show: `kubectl set image deployment/web web=<image>:<typo>`; `rollout status`: `Waiting for rollout to finish: 1
out of 3 new replicas have been updated...`; one pod `ImagePullBackOff`, three old serving; past the deadline,
`error: deployment "web" exceeded its progress deadline`, exit 1, nothing else; `rollout undo` (Deployments).
Explain: A new ReplicaSet grows as the old shrinks, only as new pods become ready; stuck, it waits and reports.
Try: predict: pods mid-rollout from their `maxSurge`, `maxUnavailable`; fix: [9,10] a stuck rollout undone and
fixed in Git.
### 11
Need: If I delete the claim, is the database's data gone?
Show: `kubectl delete pvc data` while a pod uses it: `Status: Terminating`, `Finalizers:
[kubernetes.io/pvc-protection]`; once the pod goes, the claim goes, and under reclaim policy `Delete` the data
too (Persistent Volumes).
Explain: A claim asks, a StorageClass makes a volume, and its reclaim policy decides what a deleted claim does.
Try: predict: RECLAIM POLICY in their `get pv`; apply: a two-replica StatefulSet, done when `db-0` keeps its data
after `delete pod db-0`.
### 12
Need: My pod calls the API and gets `Forbidden`; who is it, and what may it do?
Show: `kubectl auth can-i list pods --as=system:serviceaccount:team-a:default -n team-a`: `no`; a Role for `get`,
`list` pods bound to it: `yes`; `-n team-b`: `no` (RBAC: "purely additive"; kubectl auth can-i).
Explain: Each request acts as a user or service account, allowed only what a bound Role lists, in its
namespace; nothing denies.
Try: apply: their app's ServiceAccount with only what it uses (`auth can-i --list --as=...`); predict: whether a
ClusterRole bound by a RoleBinding reaches other namespaces.
### 13
Need: It says `CrashLoopBackOff` and `kubectl logs` is empty; where is the reason?
Show: a container exiting 1 at once: RESTARTS slow down as the kubelet waits 10 s, 20 s, 40 s, up to 300 s, reset
after 10 minutes up (defaults; a node may set a lower cap); `logs` shows the new attempt, `logs --previous` the crash; `kubectl debug --target` for
no shell (Pod Lifecycle; Debug Running Pods).
Explain: CrashLoopBackOff is the wait between restarts, not a cause; that is in the previous logs and events.
Try: predict: RESTARTS after 5 minutes, from the back-off; fix: [8,13] `Pending` made on purpose, repaired from
`describe` alone.

## Believable numbers
- [9] `terminationGracePeriodSeconds` is 30 s by default: SIGTERM, then SIGKILL 30 s later (Pod Termination,
  2026-11).
- [13] Restart back-off 10 s doubling to 300 s, reset after 10 minutes running; so a crash loop shows RESTARTS 4
  after 5 minutes (10 + 20 + 40 + 80 s; the fifth near 310 s) (Pod Lifecycle defaults, 2026-11; nodes may cap lower).

## Go deep, leave for later
- Deep steps: 2, 5, 9, 13 (the reconcile loop, how traffic finds pods through selectors, EndpointSlices and readiness, and reading events and logs: where using a cluster turns into understanding it).
- Later: Jobs, CronJobs, init and sidecar containers, Helm, Kustomize, autoscaling, quotas, NetworkPolicy, `securityContext`, operators, GitOps.

## Never omit
- Break something in every step; say which loop repairs it, or why none does.
- Look up when planned: the cluster's version, edge controller (ingress-nginx is retired), StorageClasses, registry,
  how images reach a local cluster, the node's restart back-off cap.

## Wrong beliefs
- [2] "Kubernetes moves my pod to a healthy node" (never; a controller makes a new pod).
- [3] "`kubectl apply` starts the containers" (it stores desired state; loops act after).
- [5] "A Service is a load-balancer program" (a virtual IP; each node's kube-proxy, or a replacement, forwards to ready endpoints).
- [7] "Secrets are encrypted" (unencrypted in etcd unless encryption at rest is configured; whoever may create a pod in the namespace can read them).
- [8] "A CPU limit kills a busy container" (it throttles; over the memory limit it may be killed).
- [9] "Liveness should check the database" (a database outage then restarts every pod, repairing nothing).
- [10] "A failed rollout rolls itself back" (it only reports `ProgressDeadlineExceeded`).
- [11] "`ReadWriteOnce` means one pod" (one node; `ReadWriteOncePod` is one pod).

## Failures to diagnose
- [8,13] `Pending`, event `FailedScheduling`: no node has the requested cpu or memory.
- [1,13] `ImagePullBackOff`: wrong name or tag, never pushed, or no `imagePullSecrets` for a private registry.
- [9,13] `CrashLoopBackOff`: the container keeps exiting, or liveness kills a slow starter; `logs --previous`.
- [8] `OOMKilled`, restarts climbing: the memory limit is below real use.
- [4,5,13] A Service with no endpoints: its selector matches no pod's labels, or no pod is ready.
- [9,10] A rollout stuck: new pods never ready; old ones serve until `rollout undo`.
- [9] Errors at every rollout: the app exits on SIGTERM while traffic still arrives.

## Practice and project
Guided: the learner's image. Alone: predict a manifest's events, then check. Project: the learner's service and database deployed from their repository; finish line: a pod killed mid-traffic unnoticed, a bad image undone, every failure above repaired, all recreated in a fresh namespace from Git.

## Mastery ladder
- Use: deploy, expose and update an image from manifests.
- Explain: trace one `kubectl apply` to a serving pod, naming each component's part.
- Build: the project.
- Design: choose and defend replicas, requests, limits, probes and storage for a stated service.

## Words to own
[1] pod, manifest, context; [2] deployment, replicaset, reconcile, desired state; [3] api server, etcd, controller, scheduler, kubelet;
[4] label, selector; [5] service, endpointslice; [6] ingress controller, gateway; [7] configmap, secret; [8] request, limit, throttling;
[9] liveness probe, readiness probe, startup probe, grace period; [10] rollout; [11] persistentvolumeclaim, storageclass, reclaim policy, statefulset;
[12] namespace, rbac, serviceaccount; [13] event, ephemeral container
