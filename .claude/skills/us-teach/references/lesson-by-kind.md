# A lesson, by kind of subject

Read when a lesson starts and the book's `kind:` (in `PLAN.md` or `BOOK.md`) is not one you have taught this session. The moves in `rules/teaching.md` hold for every kind; what changes is what the learner does with their hands and what a question can ask of them. A check question is good when the learner must produce something they could not copy from the section.

## language

The learner predicts what a short program prints, then runs it; changes one line and predicts again. Ask about what the machine does, not what the syntax is called.

- Weak: "What does `&` mean?" (a definition they can look up).
- Better: "After `int *p = &x; *p = 5;`, what is `x`, and which line changed it?" They must follow the program, which is the skill.

## tool

The learner types a command on their own machine and says what it changed: which file, which state, which list. Ask them to predict the state before they look.

- Weak: "What does `git add` do?"
- Better: "You edited two files and ran `git add a.txt`. What will `git status` show for each, and why?"

## framework

The learner adds one small piece to the running project and says who calls it and when. Ask about the order of events the framework runs, since that is what feels like magic.

- Example: "You added a handler for `/orders`. A request arrives. Name, in order, what runs before your function and what runs after it returns."

## system

The learner traces by hand: a table of steps, a drawing of who sends what to whom, or a small experiment. Ask them to predict what happens when one condition changes. Nothing to type is normal here; the trace is the work.

- Weak: "What is a page fault?"
- Better: "A process touches an address whose page is on disk. List what happens, in order, until the instruction runs again. Which part knows the page is missing?"

## skill

The learner does the practice on a small real case, then judges a weak and a better version. Ask them to decide and give the reason, or to find the fault in an example. Use their own field for the case where you can.

- Weak: "Why should a test task not lead the user?"
- Better: "Here is a task from a usability test: 'Use the handy search bar to find a red jacket.' Find two problems and rewrite it." Then: "What would you see in the session if you left it as it was?"

## If you cannot tell the kind

Ask what the chapter's "real thing" is (see the table in `rules/writers-guide.md`) and teach to that: a program, a session, a growing project, a trace or a worked case. A chapter that mixes kinds is taught section by section, each in its own way.
