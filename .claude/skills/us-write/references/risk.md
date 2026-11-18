# Risk notes

A `<!-- risk: why -->` note asks the review to check one passage. The review reads only what is marked (plus dangerous commands, dangling references and unrun blocks, which the script finds by itself), so a missing note is an unchecked error and a needless note is wasted cost. The five reasons are in `rules/writers-guide.md`; this file is how to apply them.

**Mark it** when you would want to look it up before saying it to a room of experts. Write the reason so the reviewer knows what to check: not `<!-- risk: check -->` but `<!-- risk: default timeout, 30 s? -->`.

**Do not mark** what a run settles (tagged code whose output `us_run.py` pastes is already checked by the machine), what `PRACTICES.md` already states (it was looked up once for the book), definitions and reasoning you derive in the text, and stable facts every practitioner knows (`ls` lists files; HTTP 404 means not found; a sentence has a subject).

**Seven examples across kinds.**

1. *Language, versions differ.*
   "Since Python 3.7, a `dict` keeps the order you inserted keys in." `<!-- risk: version where dict order became guaranteed -->` Mark: version claims are easy to get off by one.

2. *Tool, deletes.*
   A session with `docker system prune -a --volumes`. `<!-- risk: deletes every unused volume, not just the book's -->` The script lists `prune` lines anyway; the note adds why it matters here, and the block is better made `mode=fragment`.

3. *Framework, default.*
   "Spring Boot's embedded Tomcat listens on port 8080 unless you set `server.port`." Do not mark: well known, and the run of the app shows it. But "the default connection pool holds 10 connections" `<!-- risk: HikariCP default pool size -->`: a number you would not swear to.

4. *System, quoted standard.*
   "RFC 9110 says a GET request has no defined meaning for a body." `<!-- risk: wording of the RFC on GET bodies -->` A rule from a standard, paraphrased.

5. *Skill, a research number.*
   "Testing with five users finds most usability problems." `<!-- risk: source and exact claim of the five-user finding -->` Widely quoted, often overstated; the review should make it say exactly what the source says.

6. *Any kind, unsure.*
   "Git for Windows converts line endings on checkout by default." `<!-- risk: unsure; depends on installer choice -->` When you are not sure, say so in the note; never write the sentence with more confidence than you have.

7. *Any kind, a case you did not run.*
   "If you leave out the `fflush`, the prompt appears only after you type." It reads like a fact and nobody ran it (on Linux the prompt appears anyway). Either add the changed program as a second tagged block and let the run answer, or mark it: `<!-- risk: not run: does the prompt really wait without fflush? -->`. The same goes for "with two of them, each takes twice as long": quote the run's numbers, do not predict them.

**Not a risk note**: "A pointer holds an address." It is the definition the section builds, and the program below it demonstrates it running. Marking it would spend the review on something already proven.
