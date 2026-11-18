# Teaching a framework or library

**At the end of a chapter** the reader can add a feature to their own project with the framework, read the error it gives when they get it wrong, and answer for every annotation, decorator, hook or configuration line they wrote: who reads it, when, and what it makes happen. A framework calls your code; the reader must know when and why it calls.

**The usual arc.** A feature the project needs next (list the books; reject a request without a title) → what you would have to write without the framework (a socket loop, a SQL string, a re-render by hand), briefly, so the framework's work is visible → the framework's way, as the smallest change to the running project → who calls what, in order, from the request (or the event, or the render) to your code and back → the error the reader will see when it is wrong, read line by line → a feature they add alone.

**The real thing** is the book's small project, grown one feature per section, run, with the result shown (a `curl` response, a rendered page, a test passing). Weak: "Add `@Transactional` to make the method transactional." Better: show `transferMoney` failing halfway with the first update saved and the second not, then add `@Transactional`, then explain that Spring wraps the bean in a proxy that opens a transaction before the call and rolls back on a runtime exception; then show the trap that follows from the mechanism: calling the method from inside the same class skips the proxy, so nothing is rolled back.

**Three exercise types.**
- *Add a feature*: "Add `GET /books/{id}` that answers 404 when the id is unknown", with the expected `curl -i` output.
- *Read the error*: give a real stack trace (`NoSuchBeanDefinitionException`, React's "Too many re-renders") and ask which line of the reader's code caused it and why.
- *Who calls it*: "Put the five things that happen between the browser sending `POST /books` and your method running in order."

**Mark with a risk note** anything tied to a version (Spring Boot 2 against 3 and `javax` against `jakarta`, React class against function components, Django settings names), default values (ports, timeouts, pool sizes), generated starter files whose contents change between releases, and security settings you show switched off for the example.

**Usual failures of generated material, and the cure.**
- *Annotations or configuration used as magic*: `@Autowired` "injects the dependency". Name the reader of each label and what it does at start-up or at run time, once, the first time it appears.
- *A new toy app per section*: the reader never sees features meet. Keep one project; each section leaves it running (record it in `BOOK.md`).
- *Copy-paste setup walls*: forty lines of generated configuration. Show only the lines this section changes, and say what the rest is for in a sentence.
- *Tutorial drift*: mixing the styles of two major versions. Write one version, stated in `BOOK.md` `Versions:`.
