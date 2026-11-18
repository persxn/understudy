# Chapter 1: Running your first program

<!-- contents -->
- [1.1 Python is already on your laptop](#11-python-is-already-on-your-laptop)
- [1.2 Typing Python one line at a time](#12-typing-python-one-line-at-a-time)
- [1.3 A program is a file you run](#13-a-program-is-a-file-you-run)
- [1.4 Names for values, like cells that hold numbers](#14-names-for-values-like-cells-that-hold-numbers)
- [1.5 Numbers and text are different things](#15-numbers-and-text-are-different-things)
- [1.6 Reading an error message without fear](#16-reading-an-error-message-without-fear)
- [1.7 Practice: add up one day's sales](#17-practice-add-up-one-days-sales)
<!-- /contents -->

## 1.1 Python is already on your laptop

You want Python to add up a shop's sales for you, the way a `SUM` formula does in a spreadsheet. Before you can ask it anything, you need two things: a place to type instructions, and Python itself. On Ubuntu you already have both. Nothing to download.

### The terminal: a window where you type instructions

<!-- teaches: terminal = terminal, command, prompt -->
A spreadsheet gives you a grid of cells to click on. The **terminal** gives you something plainer: a window with one line of text, where you type an instruction (a **command**) and press Enter, and the computer types its answer underneath. Then it waits for the next one.

Open it now. On Ubuntu, press Ctrl+Alt+T together, or open the list of apps and search for "Terminal".

You will see a line ending in `$`, something like `riya@laptop:~$`. That line is the **prompt**: the terminal saying "your turn". In this book a line starting with `$ ` is a command for you to type; you type only what comes after the `$ `, never the `$` itself. The lines without a `$` are what the computer typed back.

### Asking Python which version it is

Type this and press Enter:

<!-- code: id=python-version -->
```console
$ python3 --version
Python 3.13.18
```

That one line asked the program called `python3` to say which version of Python it is. Your number may differ: Ubuntu 24.04 comes with Python 3.12, and this book was run on 3.13. Anything that starts with `3.` and is 3.12 or higher works for every program here. The first number matters most: Python 2 was a different language, retired years ago, and nothing in this book is for it.

<!-- teaches: python-version = version, python3 -->

### A folder for the shop

Every program in this book lives in one folder called `shop`, in your home folder. Make it now, and step into it:

<!-- code: id=make-shop -->
```console
$ mkdir shop
$ cd shop
$ pwd
/home/you/shop
```

`mkdir shop` made a new, empty folder called `shop` (the name is short for "make directory"; *directory* is an older word for folder). `cd shop` moved you into it, the way double-clicking a folder opens it ("change directory"). `pwd` asked where you are now ("print working directory"). The answer is the `shop` folder inside your home folder; on your laptop it will say `/home/` and your user name in front of `shop` (this book writes your home folder as `~`).

Each time you open a new terminal it starts again in your home folder, so the first thing to type next time is `cd shop`.

### One mistake you will make: `python` instead of `python3`

On many websites you will see `python` without the 3. On Ubuntu that command is usually not there at all, and the terminal answers with something like `Command 'python' not found` and a hint about a package to install. Do not install anything: the program is called `python3` on your laptop, and that is all you need.

**Check yourself**

1. You open a fresh terminal tomorrow and type `python3 day_total.py`, a program you saved in `shop`. The terminal says it cannot find the file. What did you forget?

<details>
<summary>Answer</summary>

To step into the folder with `cd shop`. A new terminal starts in your home folder, and the file is one level down, inside `shop`. The tempting wrong answer is "Python is broken": it is not, it simply looked in the wrong folder. `pwd` tells you where you are.

</details>

2. A tutorial online says to type `python --version`, and your terminal says the command is not found. What do you type instead?

<details>
<summary>Answer</summary>

`python3 --version`. On Ubuntu the program is called `python3`. Installing a package to make `python` work is not needed for this book.

</details>

## 1.2 Typing Python one line at a time

In a spreadsheet you can click an empty cell, type `=450+120` and see `570` at once. Python has the same quick way to try something: you type one line, it answers straight away. This is the place to test a small idea before you put it in a program.

### Starting Python and asking it a sum

<!-- teaches: interactive-prompt = interactive prompt, >>> -->
Type `python3` on its own and press Enter. Python starts and gives you a new prompt of its own, three arrows: `>>>`. This is the **interactive prompt**. While you see `>>>`, you are talking to Python, not to the terminal. Type the sum after the arrows and press Enter:

<!-- code: id=first-sum stdin="450 + 120\nquit()\n" wait=1 timeout=15 varies -->
```console
$ python3
Python 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 450 + 120
570
>>> quit()
```

Here is what happened, step by step:

1. `python3` started Python. It printed two lines about itself: its version and when it was built (yours will differ), and a line about help.
2. It showed `>>>` and waited.
3. You typed `450 + 120` and pressed Enter. Python worked it out and typed the answer, `570`, on the next line.
4. It showed `>>>` again, ready for the next line.
5. `quit()` closed Python and gave you back the terminal's `$` prompt. (Pressing Ctrl+D at an empty `>>>` does the same on Linux.)

This is the same as typing `=450+120` into a cell, without the `=`. Python knows you are asking for a value because everything you type at `>>>` is treated as something to work out.

### An expression is something with a value

<!-- teaches: expression = expression, operator -->
`450 + 120` is an **expression**: a piece of Python that has a value. Python *evaluates* it, which means works out that value, and at the `>>>` prompt it shows you the result. The `+` in the middle is an **operator**, a sign for what to do with the values on each side. Spreadsheet formulas use the same idea and almost the same signs.

| Spreadsheet formula | Python expression | Means |
|---|---|---|
| `=450+120` | `450 + 120` | add |
| `=500-35` | `500 - 35` | subtract |
| `=3*45` | `3 * 45` | multiply |
| `=900/4` | `900 / 4` | divide |
| `=(450+120)*2` | `(450 + 120) * 2` | brackets first, as in a formula |

The spaces around the signs are not needed: `450+120` works too. Python's style guide asks for them because they make a long line easier to read, and this book keeps them.

Here is a short session at the shop's counter. Sharma General Store sold 3 packets of tea at 45 rupees each, and a customer paid with a 500-rupee note:

<!-- code: id=counter-sums stdin="3 * 45\n500 - 3 * 45\n(450 + 120 + 75) * 2\n900 / 4\nquit()\n" wait=1 timeout=15 varies -->
```console
$ python3
Python 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 3 * 45
135
>>> 500 - 3 * 45
365
>>> (450 + 120 + 75) * 2
1290
>>> 900 / 4
225.0
>>> quit()
```

Walk through the four answers:

- `3 * 45` is the bill: `135`.
- `500 - 3 * 45` is the change. Python did the multiplication first, as a spreadsheet would, so it worked out `500 - 135`, which is `365`. Without that rule the answer would be `(500 - 3) * 45`, which is nonsense for change.
- `(450 + 120 + 75) * 2` adds the three sales first, because brackets go first, then doubles: `1290`.
- `900 / 4` gives `225.0`, not `225`. The `.0` is not a mistake: dividing with `/` always gives a number with a decimal point in Python, even when it comes out even. Section 1.5 explains why Python keeps two kinds of numbers apart.

### What Python does with each line

Every time you press Enter at `>>>`, Python does the same three things, in a loop that only stops when you quit:

1. **Read** the line you typed.
2. **Evaluate** it: work out its value, step by step. For `500 - 3 * 45` that is first `3 * 45` → `135`, then `500 - 135` → `365`.
3. **Show** the value on the next line (programmers say *print*, even though nothing goes to paper).

Then it shows `>>>` and waits again. Programmers call this the *read-evaluate-print loop*, or REPL for short; you will see that word on websites. It is a calculator that understands the whole Python language.

Two things follow from this. First, nothing you type at `>>>` is kept. When you quit, it is gone, like typing into a cell and pressing Escape. That is why real work goes into a file, which is section 1.3. Second, Python answers each line on its own. It does not look at the line above unless you ask it to, and asking it is section 1.4.

### When it goes wrong at the prompt

**Typing a terminal command at `>>>`.** You forget you are inside Python and type `python3 --version` again. Python tries to read it as Python, and it is not:

<!-- code: id=wrong-place stdin="python3 --version\nquit()\n" wait=1 timeout=15 varies -->
```console
$ python3
Python 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> python3 --version
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    python3 --version
    ^^^^^^^
NameError: name 'python3' is not defined
>>> quit()
```

The last line starts with an error name, and the words after it say what Python thinks is wrong. Section 1.6 reads such messages properly. For now, the cure: look at the prompt. `>>>` means Python; `$` means the terminal. Type `quit()` to get back to `$`.

**Typing a Python sum at `$`.** The opposite mistake: you type `450 + 120` at the terminal's `$`. The terminal looks for a command called `450`, does not find one, and says so. Start `python3` first.

**Writing a number with a comma.** In a shop ledger you might write one thousand two hundred as `1,200`. In Python a comma separates two values, so `1,200 + 5` does not mean 1205. Write `1200`. (If you want a visible gap, Python allows an underscore: `1_200` is 1200.)

<!-- code: id=comma-number stdin="1,200 + 5\n1_200 + 5\nquit()\n" wait=1 timeout=15 varies -->
```console
$ python3
Python 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 1,200 + 5
(1, 205)
>>> 1_200 + 5
1205
>>> quit()
```

The first answer, `(1, 205)`, is Python seeing two separate values, `1` and `200 + 5`, and showing them together in brackets. No error, just a wrong answer, which is worse. The second line is the one you meant.

### Keep it

- `python3` starts Python's interactive prompt, `>>>`. `quit()` (or Ctrl+D) leaves it.
- At `>>>`, Python reads a line, evaluates it and prints its value.
- An expression is anything with a value; `+ - * /` are its operators, and brackets and "multiply before add" work as in a spreadsheet.
- `/` always gives a number with a decimal point.
- Nothing typed at `>>>` is kept.

**Check yourself**

1. Before trying it: what does Python show for `2 + 3 * 4`? And for `(2 + 3) * 4`?

<details>
<summary>Answer</summary>

`14`, then `20`. Multiplication goes before addition, so the first is `2 + 12`. Brackets go first, so the second is `5 * 4`. The tempting wrong answer for the first is `20`, reading left to right as a cashier adds on a calculator.

</details>

2. A customer buys 4 soaps at 38 rupees and pays 200. Write the one expression that gives the change, and say what it shows.

<details>
<summary>Answer</summary>

`200 - 4 * 38`, which shows `48`. No brackets are needed, because `4 * 38` is worked out first. `(200 - 4) * 38` would be wrong.

</details>

3. Your friend types `1,500 + 250` at `>>>` and gets `(1, 750)`. What happened, and what should they type?

<details>
<summary>Answer</summary>

The comma split the line into two values, `1` and `500 + 250`. They should type `1500 + 250` (or `1_500 + 250`), which shows `1750`.

</details>

## 1.3 A program is a file you run

At the `>>>` prompt every answer vanishes when you quit. Tomorrow you would have to type the day's sums again. A spreadsheet solves this by saving the sheet; Python solves it by saving your lines in a file. Run the file, and Python does every line in it again, the same way, as often as you like.

### The picture: a recipe

<!-- teaches: script-file = program, script, .py file -->
A **program** is a list of instructions saved in a file, which Python follows from the first line to the last, one line at a time, like a cook following a recipe. A small program like this is often called a **script**. Its file name ends in `.py`, the way a spreadsheet's ends in `.xlsx` or `.ods`, so that you and the computer can tell what kind of file it is.

The recipe picture holds for this whole chapter. It stops being true in chapter 2, where a program can skip lines (2.2) or go back and repeat them (2.5), and in chapter 3, where it can jump to a piece of recipe written elsewhere (3.4).

### Writing your first program

Open the app called **Text Editor** (search for it in the list of apps). It is a plain notepad: no fonts, no bold, which is what a program needs. Type these two lines exactly, with the brackets and the double quotes:

<!-- code: id=day_total -->
```python
print("Sharma General Store")
print(450 + 120 + 75)
```
```text
Sharma General Store
645
```

Save it with Ctrl+S. In the save window, go into your home folder, then into `shop`, and name the file `day_total.py`. The name matters: lower-case letters, an underscore instead of a space, and `.py` at the end.

Now run it from the terminal, from inside `shop`:

<!-- code: id=run-day-total -->
```console
$ ls
day_total.py
$ python3 day_total.py
Sharma General Store
645
```

`ls` listed the files in the folder ("list"), so you can see the file is really there. Then `python3 day_total.py` told Python: "run the program in this file". Python printed two lines and handed the terminal back to you. Run it again, and it prints the same two lines again: the work is kept.

### What `print` does

<!-- teaches: print-call = print, call, argument in brackets, string in quotes -->
At the `>>>` prompt Python showed you every value by itself. In a program it does not: a program shows only what you tell it to show. **`print(...)`** is how you tell it. Whatever you put between the brackets is worked out, then written on the screen, followed by a new line.

Writing a name followed by brackets is called a **call**: `print(450 + 120 + 75)` *calls* print, and hands it the value between the brackets. You will meet many other things that are called this way, and in chapter 3 you will write your own.

The two lines show two kinds of thing you can print:

- `print(450 + 120 + 75)` prints the value of a sum: `645`. Python works out the sum first, then prints it.
- `print("Sharma General Store")` prints text exactly as written. The double quotes mark where the text starts and ends; they are not printed. Text in quotes is called a *string*, and section 1.5 is about it.

You can give `print` several values at once, separated by commas. It prints them on one line, with a space between each. This is how you put a label next to a number (save it in `shop` as `day_total_labels.py` and run it):

<!-- code: id=day_total_labels -->
```python
print("Sharma General Store")
print("Sales today:", 450 + 120 + 75)
print("Average of the three sales:", (450 + 120 + 75) / 3)
print()
print("End of report")
```
```text
Sharma General Store
Sales today: 645
Average of the three sales: 215.0

End of report
```

Look at what each line did:

1. The heading, as before.
2. A label and a sum on one line. Python put a space between them by itself; you did not type one after the colon.
3. The average: the brackets make Python add first, then divide. It is `215.0`, with a decimal point, because of the `/` (1.2).
4. `print()` with nothing inside printed an empty line, which is handy to space out a report.
5. The last line.

### How Python runs the file

When you type `python3 day_total.py`, this is what happens:

1. Python opens the file and reads all of it.
2. It checks that every line is written correctly as Python. If one is not, it stops before doing anything and tells you which line (1.6 shows this).
3. It does line 1, then line 2, then line 3, and so on, each one completely before the next.
4. After the last line, it stops, and the terminal shows `$` again.

So the order of the lines is the order of the output. Swap two `print` lines in the file and the report changes order too. That is the recipe: top to bottom, one step at a time.

### When it goes wrong

**A sum with no `print`.** Suppose you wrote the file like this:

<!-- code: id=silent_total -->
```python
print("Sharma General Store")
450 + 120 + 75
```
```text
Sharma General Store
```

Run it and you see only the heading: there is no output after it at all. Python did work out 645, then threw it away, because nobody asked it to show the answer. At the `>>>` prompt values appear by themselves; in a file only `print` shows them. This catches almost everyone in their first week.

**The wrong folder, or a misspelt file.** If you are not in `shop`, or you misspell the file name, Python cannot find the file:

<!-- code: id=wrong-name exit=2 -->
```console
$ python3 day_totl.py
python3: can't open file '/home/you/shop/day_totl.py': [Errno 2] No such file or directory
```

The message says it cannot open the file, and the end says why: `No such file or directory`. Check with `pwd` where you are and with `ls` what the file is called.

**Running the file from inside `>>>`.** If you type `python3 day_total.py` at the `>>>` prompt, Python reads it as Python, not as a command, and says `SyntaxError`. Leave with `quit()`, then type it at `$`.

**Curly quotes.** If you copy a line from a website or a word processor, the quote marks around text (§1.5) may be the curly kind, `“ ”`, which Python does not accept as quotes. Type the quotes yourself in Text Editor; it uses the straight ones, `"`.

### Keep it

- A program is a `.py` file. `python3 name.py`, run from the folder it is in, does its lines top to bottom.
- In a program only `print(...)` shows anything. Values separated by commas print on one line with spaces.
- Text to print goes in straight double quotes.

**Check yourself**

1. Before running it: what does this program print, line by line?

<!-- code: id=bill_predict answer -->
```python
print("Bill")
print(2 * 38)
print("Paid:", 100)
```

<details>
<summary>Answer</summary>

```text
Bill
76
Paid: 100
```

Three lines, in the order of the program. The second line prints the value of the sum, not the text `2 * 38`, because it is not in quotes. A tempting wrong answer is `Paid:100` with no space: `print` puts the space in by itself.

</details>

2. You saved `report.py` in `shop` and typed `python3 report.py` in a new terminal. Python says `No such file or directory`. Name the two commands that find the problem, and the one that fixes it.

<details>
<summary>Answer</summary>

`pwd` shows that you are in your home folder, not `shop`; `ls` shows that `report.py` is not there. `cd shop` fixes it; then run the program again.

</details>

3. Change `day_total_labels.py` so that the empty line comes before the heading instead of before "End of report". What will the first line of the output be?

<details>
<summary>Answer</summary>

Move the `print()` line to the top of the file. The first line of the output is then empty, and the heading comes second, because Python runs the lines in the order they are written.

</details>

## 1.4 Names for values, like cells that hold numbers

`day_total_labels.py` has the three sales written inside the sum: `450 + 120 + 75`. To print the total and the average, you typed the same three numbers twice. If the evening sale turns out to be 300, not 75, you must find and change every copy, and missing one gives a wrong report with no warning. In a spreadsheet you would never do that: you would put each sale in its own cell once, and have the formulas point at the cells. Python's way of doing the same is to give a value a name.

### The picture: a label on a value

<!-- teaches: variable = variable, name -->
A **variable** is a name that Python keeps for a value, so that you can use the name wherever you need the value. Picture a sticky label with `morning` written on it, stuck on the number 450. Later, wherever Python meets the word `morning`, it looks at what the label is stuck on and uses 450.

This is close to naming a cell in a spreadsheet (B2 called "morning"), but not the same in one way that matters, and the next pages show it running. The picture of a label also stops being exact in chapter 6, where one value can carry two labels at once.

### Making a name: assignment

<!-- teaches: assignment = assignment, = sign -->
You make a variable with an **assignment**: the name, an `=` sign, and the value.

<!-- code: id=assign-shape mode=fragment -->
```python
morning = 450
```

Read it as "let `morning` be 450", not "morning equals 450". The `=` here is an instruction, not a question: put the label `morning` on the value on the right. Then use the name, in a program saved as `names_first.py`:

<!-- code: id=names_first -->
```python
morning = 450
afternoon = 120
evening = 75
total = morning + afternoon + evening
print("Sales today:", total)
print("Average sale:", total / 3)
```
```text
Sales today: 645
Average sale: 215.0
```

Now each sale is written once. The total is worked out once and given its own name, and both `print` lines use that name. If the evening sale changes, there is one place to change it.

### What Python does with each line

Python follows the recipe from the top. For each assignment it does two steps, always in this order:

1. Work out the value on the right of `=`.
2. Stick the name on the left onto that value.

The table shows what each name refers to just after each line has finished. A `?` means the name does not exist yet: Python has not reached the line that makes it.

<!-- trace: id=names_first watch="morning afternoon evening total" at="1 2 3 4" -->
| Line | Statement | `morning` | `afternoon` | `evening` | `total` |
|---|---|---|---|---|---|
| 1 | `morning = 450` | 450 | ? | ? | ? |
| 2 | `afternoon = 120` | 450 | 120 | ? | ? |
| 3 | `evening = 75` | 450 | 120 | 75 | ? |
| 4 | `total = morning + afternoon + evening` | 450 | 120 | 75 | 645 |

Line 4 is where the two steps matter. For the right side, Python looks up each name in turn: `morning` is 450, `afternoon` 120, `evening` 75. It adds them: 645. Only then does it stick the label `total` on 645. From then on `total` is simply 645; it does not remember how it was made.

### The difference from a spreadsheet formula

That last sentence is the one surprise for a spreadsheet user. In a sheet, if C1 holds `=A1+B1` and you change A1, C1 recalculates by itself. In Python, `total = morning + afternoon + evening` is worked out once, when that line runs, and never again on its own. Watch it happen in `no_recalc.py`:

<!-- code: id=no_recalc -->
```python
morning = 450
afternoon = 120
evening = 75
total = morning + afternoon + evening
print("Total:", total)

evening = 300
print("Evening corrected to:", evening)
print("Total is still:", total)

total = morning + afternoon + evening
print("Total worked out again:", total)
```
```text
Total: 645
Evening corrected to: 300
Total is still: 645
Total worked out again: 870
```

<!-- trace: id=no_recalc watch="evening total" at="4 7 11" -->
| Line | Statement | `evening` | `total` |
|---|---|---|---|
| 4 | `total = morning + afternoon + evening` | 75 | 645 |
| 7 | `evening = 300` | 300 | 645 |
| 11 | `total = morning + afternoon + evening` | 300 | 870 |

After line 7, the label `evening` was moved to 300, but `total` was still stuck on 645, the number worked out on line 4. Line 11 asks for the sum again, and only then is `total` 870. The rule for this whole book: **a variable holds a value, not a formula.** If an input changes, the lines that use it must run again after the change. In a program this is easy to arrange, because the order of lines is yours: put the corrections first, then the sums.

### Changing a value using its old value

The shop takes one more sale of 30 rupees after closing the books. You want `total` to grow by 30. In Python you write:

<!-- code: id=late_sale -->
```python
total = 645
total = total + 30
print("Total with the late sale:", total)
```
```text
Total with the late sale: 675
```

As algebra, `total = total + 30` is impossible. As an instruction it is ordinary, because of the two steps: first work out the right side, using the *current* `total`, so `645 + 30` gives 675; then move the label `total` onto 675. The old 645 is no longer labelled, and Python throws it away. You will use exactly this line in chapter 2 to add up a whole day's sales one at a time.

### Choosing names

Python lets you choose almost any name, with a few rules:

- Letters, digits and underscores only; no spaces, no `-`. `evening_sales` is fine, `evening sales` and `evening-sales` are not.
- It cannot start with a digit: `sale1` is fine, `1sale` is not.
- Capitals count: `Total` and `total` are two different names.
- A few words belong to Python itself (you will meet `if`, `for` and `def`), and cannot be names.

On top of the rules, a habit this book keeps: lower-case words joined by underscores, saying what the value is. `day_total` tells the next reader (often you, a week later) what it holds; `x` and `a1` tell them nothing.

### When it goes wrong

**Using a name before the line that makes it.** Python follows the recipe from the top, so this fails:

<!-- code: id=too_early exit=1 -->
```python
print("Sales today:", total)
total = 450 + 120 + 75
```
```text
Traceback (most recent call last):
  File "too_early.py", line 1, in <module>
    print("Sales today:", total)
                          ^^^^^
NameError: name 'total' is not defined
```

When line 1 runs, there is no label called `total` yet, so Python stops with a `NameError`, an error you will read properly in 1.6. The same happens if you misspell a name (`totl`) or change its capitals (`Total`): to Python, that is a name nobody made.

**Writing the assignment backwards.** `450 = morning` is an error: the name must be on the left, the value on the right.

**Expecting a total to update itself.** No error at all, only a wrong total, as `no_recalc.py` showed. If your report shows an old number, look for a sum worked out before the value it uses was changed.

### Keep it

- `name = value` sticks a name on a value. The right side is worked out first, then the name is moved.
- A variable holds a value, not a formula: a total does not recalculate when an input changes.
- `total = total + 30` grows a total by 30.
- Lower-case names with underscores that say what they hold.

**Check yourself**

1. Before running it: what does this print?

<!-- code: id=predict_names answer -->
```python
price = 45
packets = 3
bill = price * packets
price = 50
print(bill)
```

<details>
<summary>Answer</summary>

```text
135
```

`bill` was worked out on line 3, when `price` was 45, and it holds 135. Changing `price` on line 4 does not change `bill`. The tempting wrong answer is 150, which is what a spreadsheet would show.

</details>

2. The shop has `stock = 40` packets of tea. Write one line that records selling 6 packets, using `stock` itself, so that `stock` is then 34.

<details>
<summary>Answer</summary>

`stock = stock - 6`. The right side, `40 - 6`, is worked out first, then `stock` is moved onto 34.

</details>

3. Which of these names are not allowed, and why: `evening_sale`, `2nd_sale`, `sale total`, `Sale`?

<details>
<summary>Answer</summary>

`2nd_sale` starts with a digit and `sale total` has a space: both are not allowed. `evening_sale` is fine. `Sale` is allowed, but it is a different name from `sale`, and this book keeps names in lower case.

</details>

## 1.5 Numbers and text are different things

In a spreadsheet, a cell can hold the number 450 or the text "450", and if you have ever had a `SUM` come out short, you know they look the same and behave differently: a number typed as text is quietly left out of the sum. Python is stricter, which in the end is kinder: it keeps every value's kind attached to it, and it will tell you when you mix them. Your sales sheet will be full of this problem in chapter 4, because every cell read from a file arrives as text. This section is where you learn to see the kind of a value.

### Every value has a type

A value's kind is called its **type**. You can ask Python for it with `type(...)`, which is called the way `print` is:

<!-- code: id=three_types -->
```python
print(type(450))
print(type(45.50))
print(type("Sharma General Store"))
```
```text
<class 'int'>
<class 'float'>
<class 'str'>
```

Three values, three types. The word after `class` is the type's name. You will see these three names in error messages all through the book, so they are worth knowing on sight.

### Two kinds of number: int and float

<!-- teaches: int-float = int, float -->
- An **int** (short for *integer*) is a whole number: `450`, `0`, `-35`. Written without a decimal point.
- A **float** is a number with a decimal point: `45.50`, `0.5`, `225.0`. The name comes from *floating point*, the way computers store such numbers.

Why two? A whole number can be stored exactly, however large: Python's ints have no upper limit. A number with a fraction is stored in a fixed amount of space, in binary, the way a calculator keeps only so many digits. Most decimal fractions cannot be written exactly in binary, just as one third cannot be written exactly in decimal (0.3333...). So Python keeps the exact kind and the approximate kind apart, and you can always tell which you have.

You decide the type by how you write the number: `450` is an int, `450.0` is a float. Python decides the type of a result by these rules:

<!-- code: id=number_rules -->
```python
print(450 + 120)
print(450 + 0.5)
print(3 * 45.0)
print(900 / 4)
print(900 / 7)
```
```text
570
450.5
135.0
225.0
128.57142857142858
```

Line by line:

1. int plus int gives an int: `570`.
2. int plus float gives a float: as soon as one side has a fraction, the answer might have one too.
3. The same for multiplying: `135.0`.
4. `/` always gives a float, even when the division comes out even: `225.0`. That is the `.0` you met in 1.2.
5. When it does not come out even, you see as many digits as Python can give.

### Where floats surprise you

Money has paise, so you will add floats. Try adding a 10 rupees 10 paise packet of biscuits and a 20 rupees 20 paise packet of salt:

<!-- code: id=float_surprise -->
```python
biscuits = 10.10
salt = 20.20
print(biscuits + salt)
print(0.1 + 0.2)
```
```text
30.299999999999997
0.30000000000000004
```

The answer is not quite 30.3. Neither 10.10 nor 20.20 can be stored exactly in binary, so each is stored as the nearest number that can be, and the tiny differences show when Python prints the sum with all its digits. This is not a fault in your program or in Python: Excel and LibreOffice Calc store numbers the same way inside, and hide it by showing fewer digits. Two consequences for the shop:

- For printing, you will round the answer to two places; section 6.4 shows how.
- For checking your totals against the sheet (6.5), you compare to the paisa, not to the last digit.

### Text: the string

<!-- teaches: string = string, str, quotes -->
A **string** is a piece of text: letters, digits, spaces, anything, between quotes. Its type is called **str**. Single and double quotes both work, as long as both ends match: `"tea"` and `'tea'` are the same string. This book uses double quotes.

The important thing about a string is that Python does not look inside it. `"450"` is not a number; it is three characters, a 4, a 5 and a 0, that happen to look like one. So `+` does something different with strings: it joins them end to end.

<!-- code: id=strings_join -->
```python
shop = "Sharma"
print(shop + " General Store")
print("450" + "50")
print(450 + 50)
print("-" * 20)
```
```text
Sharma General Store
45050
500
--------------------
```

Look at lines 3 and 4. With numbers, `450 + 50` is 500. With strings, `"450" + "50"` sticks the characters together into `"45050"`, a string, which `print` shows without its quotes. Python did exactly what it was told, and gave no error. If those two strings had come from your sales file, your total would be wrong by a lot, silently. And line 5: a string times a whole number repeats it, which makes a cheap underline for a report.

This is the same trap as the spreadsheet cell with a number stored as text, and it is the one you will meet most when reading files. Chapter 3 (3.3) shows how to turn the text `"450"` into the number 450. For now the rule is: **if it is in quotes, it is text, whatever it looks like.**

### Seeing the difference when output hides it

`print` removes quotes, so `print("450")` and `print(450)` both show `450`. When you are not sure what kind of value you have, ask for its type:

<!-- code: id=what_is_it -->
```python
amount = "450"
print(amount)
print(type(amount))
```
```text
450
<class 'str'>
```

The first line looks like a number; the second tells the truth. Make this a habit whenever a total looks odd: print the type of the values that went into it.

### When it goes wrong

**Quotes around a number by mistake.** `evening = "75"` makes a string. Adding it to a number gives an error, which 1.6 reads in detail; adding it to another string gives a joined string like `"45075"`, with no error at all. The cure is to remove the quotes.

**Forgetting the quotes around text.** `shop = Sharma` makes Python look for a variable called `Sharma`, which does not exist, so it stops with `NameError`. Text needs quotes.

**Expecting `45.10` to print as `45.10`.** Python prints a float with as few digits as show it exactly, so `print(45.10)` shows `45.1`. The value is right; only the display differs. Section 6.4 prints money with two places.

### Keep it

- Every value has a type: `int` (whole number), `float` (with a decimal point), `str` (text in quotes). `type(...)` tells you which.
- int with int stays int; anything with a float, and any `/`, gives a float. Floats are close, not exact.
- `+` adds numbers but joins strings. Text that looks like a number is still text.

**Check yourself**

1. Before running it: what does each line print?

<!-- code: id=types_predict answer -->
```python
print(10 + 5)
print(10 / 5)
print("10" + "5")
print(type(10 / 5))
```

<details>
<summary>Answer</summary>

```text
15
2.0
105
<class 'float'>
```

`/` always gives a float, so `10 / 5` is `2.0`, and its type is `float`. The strings are joined, so `"10" + "5"` is the text `105`. The tempting wrong answer for line 3 is `15`.

</details>

2. A program prints `Total: 45075` when the real total is 525. Without seeing the program, what is the most likely cause?

<details>
<summary>Answer</summary>

Two amounts were strings, `"450"` and `"75"`, so `+` joined them instead of adding. Printing `type(...)` of each amount would show `<class 'str'>`.

</details>

3. Why does Python have both `int` and `float` instead of one kind of number?

<details>
<summary>Answer</summary>

Whole numbers can be stored exactly and without limit; numbers with fractions are stored as close binary approximations in a fixed space. Keeping them apart means counting stays exact (number of packets sold), and you know when a value may carry a tiny error (`30.299999999999997`).

</details>

## 1.6 Reading an error message without fear

Sooner or later, today probably, you run a program and instead of your report the terminal fills with lines you did not ask for, ending in a word like `Error`. It looks like something broke. Nothing broke: Python stopped on purpose, because it was asked to do something it could not do, and it wrote you a note saying exactly where and why. Learning to read that note is the skill that saves you the most time in this whole book, so this section takes it slowly, one real error at a time.

### The picture: a cashier who stops the queue

Picture a careful cashier working through a list of instructions. When an instruction makes no sense ("add the customer's name to the bill"), a careless one would guess and carry on. A careful one stops, and writes on a slip: which instruction, on which line, and what was wrong with it. Python is the careful cashier. It never guesses; it stops and writes the slip.

Where the picture stops being true: a cashier might come back and ask you. Python does not; the program has ended, and it is your turn to fix the line and run it again.

### A first real error

<!-- teaches: traceback = traceback, error message -->
Here is the day's total with names, saved as `day_total_typo.py`, with one small slip: a name is spelt differently on the line that uses it.

<!-- code: id=day_total_typo exit=1 -->
```python
morning = 450
afternoon = 120
evening = 75
print("Sharma General Store")
total = morning + afternoon + evenning
print("Sales today:", total)
```
```text
Sharma General Store
Traceback (most recent call last):
  File "day_total_typo.py", line 5, in <module>
    total = morning + afternoon + evenning
                                  ^^^^^^^^
NameError: name 'evenning' is not defined. Did you mean: 'evening'?
```

Everything Python printed after the heading is called a **traceback**: the error message, with the trail of where it happened. (*Traceback* because it traces back through the program to the line at fault.) Read it from the bottom up:

1. **The last line names the error and says what is wrong.** `NameError` is the kind of error. After the colon, Python says the name `'evenning'` is not defined: it has no label of that name. Python 3.10 and newer even guesses what you meant, and here it is right.
2. **The lines above point at the place.** `File "day_total_typo.py", line 5` says which file and which line. Under it is the line itself, copied from your file, and on recent versions a row of `^` marks underlines the exact part Python could not do. (On your laptop the file name will have the folder in front of it, like `/home/riya/shop/`.)
3. **The first line, `Traceback (most recent call last):`, is just the title.** You can skip it.

Notice the line *above* the traceback: `Sharma General Store`. Lines 1 to 4 ran before Python reached line 5, and the heading was already printed. Python stopped at line 5 and never ran line 6. This tells you something every time: output that appeared came from lines before the error; the report lines that are missing come after it.

The fix is one letter: `evening`. Run it again, and it prints the report.

### NameError: a name nobody made

<!-- teaches: name-error = NameError -->
A **NameError** means Python met a name that has no value stuck on it at that moment. It is almost always one of four things, and the message, with the line, tells you which:

- A spelling slip, as above (`evenning`, `totl`).
- Different capitals: `Total` when you made `total`. To Python they are different names.
- The right name, used too early: the line that makes it comes later in the file (1.4).
- Text without quotes. `shop = Sharma` looks for a variable called `Sharma`:

<!-- code: id=no_quotes exit=1 -->
```python
shop = Sharma
print(shop)
```
```text
Traceback (most recent call last):
  File "no_quotes.py", line 1, in <module>
    shop = Sharma
           ^^^^^^
NameError: name 'Sharma' is not defined
```

Here Python's message is the same, but the cure is different: you meant the text `"Sharma"`, so add the quotes. The error tells you where; you decide which of the four it is.

### TypeError: the wrong kind of value

<!-- teaches: type-error = TypeError -->
The second error you will meet most is about the types of 1.5. Suppose the evening sale was typed with quotes, as it might be if you copied it from somewhere:

<!-- code: id=day_total_text exit=1 -->
```python
morning = 450
afternoon = 120
evening = "75"
total = morning + afternoon + evening
print("Sales today:", total)
```
```text
Traceback (most recent call last):
  File "day_total_text.py", line 4, in <module>
    total = morning + afternoon + evening
            ~~~~~~~~~~~~~~~~~~~~^~~~~~~~~
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Read it bottom up again. **TypeError** means an operation was given a value of a type it cannot work with. The message is precise: the `+` operator got an `int` on one side and a `str` on the other, and Python does not know whether you meant to add numbers or join text, so it refuses to guess. Line 4 is the place; under it, the `^` mark points at the `+` that failed, and the `~` marks underline the values on each side of it.

Why does Python refuse, when a spreadsheet would quietly skip the text cell? Because a quiet guess gives a wrong total that nobody notices. A loud stop gives you a message that names the line. That is the bargain, and with your shop's money it is the right one.

To find which value was the string, print the type of each one, as 1.5 showed, just above the failing line:

<!-- code: id=type-check-line mode=fragment -->
```python
print(type(morning), type(afternoon), type(evening))
```

That prints `<class 'int'> <class 'int'> <class 'str'>`, and `evening` is the culprit. Here the cure is to remove the quotes. When the text comes from a file and you cannot remove them, section 3.3 turns `"75"` into `75`.

### SyntaxError: a line Python cannot even read

One more kind, because you will meet it in your first week: a line that is not written as Python at all, such as a bracket that is opened and never closed.

<!-- code: id=missing_bracket mode=error -->
```python
print("Sharma General Store")
print("Sales today:", 450 + 120 + 75
```
```text
  File "missing_bracket.py", line 2
    print("Sales today:", 450 + 120 + 75
         ^
SyntaxError: '(' was never closed
```

Two differences from the errors before. First, nothing at all was printed, not even the heading on line 1: as 1.3 said, Python checks that the whole file is written correctly *before* running any line. A **SyntaxError** (*syntax* is the grammar of a language) means that check failed. Second, the line it names is where it noticed the problem, which is sometimes the line *after* the real mistake; here it points at the bracket that was never closed. If a SyntaxError's line looks perfect, look at the line above it.

### A method for every error

You do not need to know every error name. Use the same five steps each time:

1. Read the **last line**: the kind of error, and what it says is wrong.
2. Read the **line number** and the copied line just above it.
3. Look at what **was printed** before the traceback: those lines ran fine.
4. Make one guess about the cause, and change **one** thing.
5. Run again, and read the new message, which may be a different, later error. That is progress.

When the message makes no sense to you, copy the last line into a search engine: you are never the first person to see it.

### When it goes wrong

**Reading from the top.** The top line is the least useful one. Start at the bottom.

**Fixing the line the error points at when the mistake is earlier.** For `NameError` from a name used too early, the line it points at is fine; the mistake is that the assignment is below it. For a `SyntaxError`, the missing bracket may be on the line above.

**Changing several things at once.** If the program then works, you do not know which change fixed it; if it does not, you have new mistakes mixed in with the old. One change, one run.

### Keep it

- A traceback is Python stopping on purpose. Read it bottom up: kind of error, message, then line.
- Lines before the error ran; lines after it did not. A SyntaxError stops everything before any line runs.
- `NameError`: a name with no value yet (spelling, capitals, order, missing quotes). `TypeError`: values of the wrong type for the operation, such as a number plus a string.

**Check yourself**

1. A program prints its heading and then this traceback. Which line must you look at, and what will you check there?

```text
Traceback (most recent call last):
  File "/home/riya/shop/report.py", line 7, in <module>
    print("Average:", totl / 3)
                      ^^^^
NameError: name 'totl' is not defined. Did you mean: 'total'?
```

<details>
<summary>Answer</summary>

Line 7 of `report.py`. The name `totl` is a misspelling of `total`; change it and run again. Lines 1 to 6 ran (that is why the heading appeared). The tempting wrong move is to look at line 1 because the traceback starts at the top.

</details>

2. Before running it: does this program print anything before it stops? Which error does it stop with, and on which line?

<!-- code: id=error_predict exit=1 answer -->
```python
price = 45
print("Price of tea:", price)
packets = "3"
print("Bill:", price * packets + 10)
```

<details>
<summary>Answer</summary>

```text
Price of tea: 45
Traceback (most recent call last):
  File "error_predict.py", line 4, in <module>
    print("Bill:", price * packets + 10)
                   ~~~~~~~~~~~~~~~~^~~~
TypeError: can only concatenate str (not "int") to str
```

It prints `Price of tea: 45`, then stops on line 4 with a `TypeError`. `price * packets` is `45 * "3"`, a number times a string; as 1.5 showed, that repeats the string 45 times, so no error yet. Then `+ 10` tries to add a number to that long string, and that is the TypeError. Removing the quotes from `"3"` fixes it; the bill is then 145.

</details>

3. Your program prints nothing at all, and the last line of the message is `SyntaxError: '(' was never closed`, pointing at line 3. Lines 1 and 2 only make variables. Why was nothing printed, even from lines before line 3?

<details>
<summary>Answer</summary>

Python checks the whole file's grammar before running any line. A SyntaxError means that check failed, so no line ran at all, not even line 1. Close the bracket on line 3 and run again.

</details>

## 1.7 Practice: add up one day's sales

You can now open a terminal, make a folder, write a program in a file, run it, name values, tell numbers from text and read an error when one comes. This practice proves it on Sharma General Store: a few warm-ups on programs from the chapter, two short programs of your own, then the day's sales report that the rest of the book grows from. Write every program in a file in `~/shop` and run it with `python3`; try each task before you open its answer.

### Guided

**Task 1. Predict, then run.** Before running it, write down what each line prints. Then run it and compare.

<!-- code: id=practice_predict answer -->
```python
tea = 45
packets = 4
bill = tea * packets
tea = 50
print("Bill:", bill)
print("Per packet:", bill / packets)
print("New price:", tea)
```

<details>
<summary>Answer</summary>

```text
Bill: 180
Per packet: 45.0
New price: 50
```

`bill` was worked out when `tea` was 45, so it stays 180 after the price changes (1.4). `bill / packets` uses `/`, so it is a float, `45.0` (1.5). If you wrote 200 for the bill, you expected the bill to recalculate like a spreadsheet cell.

</details>

**Task 2. Find the fault.** This program should print the day's total, but it stops. Run it, read the traceback bottom up, and fix it with one change.

<!-- code: id=practice_fault exit=1 -->
```python
morning = 450
afternoon = 120
Evening = 75
print("Sharma General Store")
print("Sales today:", morning + afternoon + evening)
```
```text
Sharma General Store
Traceback (most recent call last):
  File "practice_fault.py", line 5, in <module>
    print("Sales today:", morning + afternoon + evening)
                                                ^^^^^^^
NameError: name 'evening' is not defined. Did you mean: 'Evening'?
```

<details>
<summary>Answer</summary>

The last line says `NameError: name 'evening' is not defined`, on line 5. Line 3 made `Evening` with a capital E; line 5 uses `evening`. Python treats them as two different names. Change line 3 to `evening = 75`, and the program prints `Sales today: 645`. Changing line 5 to `Evening` would also run, but the book's habit is lower-case names.

</details>

**Task 3. Add a sale.** Take `names_first.py` from 1.4 and add a fourth sale, `night = 210`, so that the total and the average include it. What must change besides the new line?

<details>
<summary>Answer</summary>

<!-- code: id=names_four -->
```python
morning = 450
afternoon = 120
evening = 75
night = 210
total = morning + afternoon + evening + night
print("Sales today:", total)
print("Average sale:", total / 4)
```
```text
Sales today: 855
Average sale: 213.75
```

Two other lines change: the sum must include `night`, and the average must divide by 4, not 3. Forgetting the second gives a wrong average with no error, which is why a number like "how many sales" deserves a name of its own; the project below does that.

</details>

### On your own

**Task 4. The change at the counter.** A customer buys 3 packets of tea at 45 rupees, 2 soaps at 38 and one bag of rice at 320, and pays with a 1000-rupee note. Write `change.py` that names each price and quantity, works out the bill, and prints the bill and the change, each with a label.

<details>
<summary>Answer</summary>

<!-- code: id=change -->
```python
tea_price = 45
tea_packets = 3
soap_price = 38
soaps = 2
rice_price = 320
paid = 1000

bill = tea_price * tea_packets + soap_price * soaps + rice_price
change = paid - bill
print("Bill:", bill)
print("Change:", change)
```
```text
Bill: 531
Change: 469
```

Multiplication goes before addition, so no brackets are needed in `bill`. A good answer gives every number a name; one that writes `1000 - (3 * 45 + 2 * 38 + 320)` gives the right change but cannot print the bill without repeating the sum.

</details>

**Task 5. Explain a wrong total.** Your cousin's program prints `Sales today: 45012075`. They say "Python can't add". In two or three sentences, explain to them what happened and how they can prove it with one line of code.

<details>
<summary>Answer</summary>

The three sales were strings, `"450"`, `"120"` and `"75"`, probably typed with quotes, and `+` joins strings end to end instead of adding (1.5). Python added nothing: it did exactly what `+` means for text. `print(type(morning))` just before the total would show `<class 'str'>`; removing the quotes gives 645.

</details>

**Task 6. Decide: one name or two?** You need the day's total in three places in a report: on its own, in the average, and in the share of the month's target of 20000 rupees. Is it better to write the sum `morning + afternoon + evening` in each place, or to name it once? Give one reason that matters for a shop.

<details>
<summary>Answer</summary>

Name it once: `total = morning + afternoon + evening`. If a sale is corrected, the sum is changed in one place and every use agrees. With three copies, missing one gives two different totals in the same report, with no error to warn you.

</details>

### The chapter project: the day's sales report

Sharma General Store kept this list of one day's sales, in rupees: 450, 120, 75, 210, 98, 1340, 64 and 300. Write `day_total.py` again (replace the version from 1.3) so that it:

- names each of the eight sales once, with names that say which sale it is (`sale_1` to `sale_8` is fine for now),
- names the number of sales, `count = 8`, instead of typing 8 in a sum,
- prints a heading with the shop's name and an underline made with `"-" * 20`,
- prints the total, the number of sales and the average sale, each with a label.

Done looks like this: the program runs with no traceback, prints four lines of report under the heading, and its total matches the same eight numbers added with `SUM` in a spreadsheet. Check that by hand before you trust it: a program that runs is not yet a program that is right.

<details>
<summary>Answer</summary>

One version:

<!-- code: id=day_total_report -->
```python
sale_1 = 450
sale_2 = 120
sale_3 = 75
sale_4 = 210
sale_5 = 98
sale_6 = 1340
sale_7 = 64
sale_8 = 300
count = 8

total = sale_1 + sale_2 + sale_3 + sale_4 + sale_5 + sale_6 + sale_7 + sale_8
average = total / count

print("Sharma General Store")
print("-" * 20)
print("Total sales:", total)
print("Number of sales:", count)
print("Average sale:", average)
```
```text
Sharma General Store
--------------------
Total sales: 2657
Number of sales: 8
Average sale: 332.125
```

`SUM` of the eight numbers in a spreadsheet also gives 2657, so the total is right. The average has a decimal point because of `/`.

The likely mistakes: leaving one sale out of the long sum (the total is short and nothing warns you, which is what the spreadsheet check is for); typing a sale in quotes (a `TypeError` on the `total` line); and changing `count` but not the sum when a sale is added. That last one is the real weakness of this program: eight names, typed out one by one, is clumsy, and a day with 200 sales would be impossible. Chapter 2 keeps the whole day's sales under one name, a list (2.4), and adds them up in a loop (2.5), however many there are.

</details>
