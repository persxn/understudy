# Security and penetration-testing track

Read this when a goal involves security. Its books and route are planned by `us-map` like any other; this file fixes their shape and their limits.

## Limits (these override everything else)

- **Allowed targets only:** machines, containers and networks the learner owns; deliberately vulnerable practice systems they run themselves; public practice platforms and contests built for this, within their rules; bug-bounty programmes strictly inside the published scope. Anything else needs the owner's written permission.
- **Before every lab** the learner states the target and why it is authorised. Write it at the top of the lab notes. If they cannot say, the lab does not start.
- **Isolation:** labs run on an internal or host-only network with snapshots, never bridged to a home, college or work network. Tear down afterwards.
- **Refuse and redirect** any request aimed at a system they do not own or have permission for, or at hiding activity from a system's owner. Say why, and offer the same technique against their own lab.
- **Every attack is learned with its defence.** For each technique the learner also shows how it is detected and how it is fixed.
- **Law and ethics come first.** Authorisation, scope, rules of engagement, handling of data found, and responsible disclosure are the first chapter, at level 2, before any offensive lab.

## Shape of the route

**Stage 0: foundations, from other books.** Networking, the Linux and Windows command line, how the web works, one scripting language, how computers run programs (processes, memory), basic cryptography.

**Stage 1: core security.** Security goals and threat modelling, least privilege, authentication and access control, the main classes of weakness (web, memory, configuration, human), secure coding, logging and detection basics.

**Stage 2: the method.** Scope and rules of engagement → reconnaissance → enumeration → finding weaknesses → controlled exploitation in the lab → what an attacker could do next → a report with fixes. Method before tools; every flag and every line of output is read, not copied.

**Stage 3: branches, chosen by the goal.** Web application security · networks and directory services · cloud security · mobile · reverse engineering and exploit development (needs how computers run programs at level 2 to 3) · defence: detection engineering, incident response, forensics · application security engineering: design review and threat modelling · hardware and embedded (links to electronics).

**Stage 4: advanced.** End-to-end exercises in the learner's own multi-machine lab, attack and detection run together, original research write-ups, responsible disclosure.

## Labs, projects, proof

- The learner builds the lab: they deploy deliberately weak services, attack them, then harden them and attack again.
- Projects: a full test of their own lab with a professional report; a small detection pipeline; fix-and-retest; write-ups of practice challenges where the platform's rules allow publishing.
- Level 1: follows the method on a lab target. Level 2: explains why the weakness exists, at the level of the mechanism. Level 3: writes their own minimal tool, and a vulnerable and a fixed version of the same code. Level 4: produces and defends a threat model and a defence design. Level 5: teaches it.
- Find the current reputable practice platforms and put them on the `library/` shelf with their rules noted. Finishing a challenge is not a level.
- Certifications only if the learner picks one; see `rules/engineer-standard.md`.

## Where things live

Security subjects are books of their own. A technique that is really another subject seen from the attacker's side (how sign-in works, how memory is laid out) is taught in that subject's book; the security book `needs:` it and does not teach it again.
