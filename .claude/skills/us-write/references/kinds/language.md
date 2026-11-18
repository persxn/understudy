# Teaching a language

**At the end of a chapter** the reader can write, from a blank file, a short program that solves a problem using the chapter's constructs, and can say what the machine does with each line. Recognising syntax is not the goal; choosing the construct for a problem is.

**The usual arc.** A problem the reader cannot yet solve neatly (repeat this for every line of a file; keep twenty scores) → the smallest program that solves it with the new construct → a trace of what happens, line by line, in memory → the variations that matter (each one shown running, not listed) → the classic mistakes, each with its real compiler message or wrong output → a program the reader writes. Reuse the book's running program so each chapter adds a capability to something the reader already owns.

**The real thing** is a complete program the reader types and runs, with its real output pasted below and a trace of the interesting lines. Weak: a fragment `for i in range(3): print(i)` and the sentence "range generates numbers". Better: a ten-line program that reads `scores.txt` and prints the average, then a table showing `total` and `count` after each pass of the loop, then the question "what does it print for an empty file?" (a `ZeroDivisionError`, shown running). The problem made the loop necessary; the trace made it visible; the empty file made the edge real.

**Three exercise types.**
- *Predict the output*: "Before running it: what does `print(a)` show after `b = a; b.append(4)`?" Forces a model of names and objects.
- *Fix the program*: give a loop that skips the last line of the file, with its wrong output; the reader finds the off-by-one.
- *Write one*: "Count the words in `notes.txt` that appear more than twice", with the expected output for the sample file.

**Mark with a risk note**: behaviour that differs between versions (Python 3.12 f-string rules, C23 features, Java records before 16), between compilers or platforms (size of `long`, path separators, line endings), undefined behaviour you show on purpose, exact error message wording you could not run, and any performance number.

**Usual failures of generated material, and the cure.**
- *A syntax tour*: every form of `for`, one after another, no problem to solve. Start from the problem; show only the forms this reader needs for the promise, each where a problem calls for it.
- *Output typed by hand*: always tag the block so `us_run.py` pastes the real output; typed output is where wrong answers hide.
- *A file the reader never saved*: an exercise says "change `labels.py`" but the text never told the reader to save it. The reader has only the files the text told them to save (`file=NAME` and the words "save this as"); name those, and no others.
- *A program named after a module*: a block's `id` (or `file=`) is its file name, so `id=types` or `file=random.py` hides Python's own module; name it after what it does (`sales-total`). A pasted traceback shows the file as `/home/you/...`; the reader sees their own name there.
- *Toy names*: `foo`, `x1`, `myFunction`. Use names from the running program; the reader is learning to name things too.
- *No machine*: "a variable stores a value." Say where it lives, what an assignment copies (the value or a reference), and draw it once.
- *Mistakes without symptoms*: "be careful with indentation." Show the exact `IndentationError` or the silently wrong output, and how the reader would notice.
