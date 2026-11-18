# What "checked" means for each kind of subject

Read the book's `Kind:` line in BOOK.md, then only that part below. "Checked" means you have evidence a reader could repeat, not that the passage sounds right. Fluent text is exactly what a model gets wrong without noticing.

## language

Checked means the program ran and its pasted output is real: `python3 scripts/us_run.py <chapter file> --only ID`. A claim about what the language does ("integer division truncates toward zero") is checked by a three-line program that shows it, run once, not kept in the chapter. A claim about the standard ("undefined behaviour") is checked against the standard or the language reference, by section.

Example: "a `for` loop over a dict yields its keys". Run `for k in {"a": 1}: print(k)`; it prints `a`. Settled.

## tool

Checked means the session ran on this machine, or, if it is `unrun`, each command and its shown output agree with the tool's own documentation for the book's version. Look at flags and defaults especially: they change between versions. A session that changes state must show the state before and after.

Example: "`docker rm` refuses a running container". The run prints the refusal; settled. If Docker is absent, the `docker rm` reference page says the same: settled as judged, not run, and REVIEW.md says so.

## framework

Checked means the claim matches the framework's reference for the book's version: who calls your code, in what order, what the default is. The project at this chapter's stage must still build and run. A claim about "what the framework does for you" is the riskiest kind: find the page that says it.

## system

Checked means the claim agrees with a standard text (the RFC, the textbook the book names, the system's own documentation) or with a small experiment the reader could do. An order of events is checked event by event against the source, not as a whole.

Example: "the client sends SYN, the server answers SYN-ACK, the client sends ACK". RFC 9293, section 3.5, shows the same three steps. Settled.

## skill

There is nothing to run, so checked means two things. The advice agrees with a recognised source (a standard, a widely used book or guide in the field, a professional body), named where the text leans on it. And the worked case is consistent with itself: the "better" version really applies the advice the section gives, the "weak" version really shows the fault named, and the reasons given are the actual differences between the two.

Weak: the section says "lead with the decision", and the improved memo still opens with background. The advice may be sound; the case contradicts it, and the reader learns the case. Fix the case, not the advice.
