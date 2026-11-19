# Chapter 2: Deciding and repeating

<!-- contents -->
- [2.1 Asking yes-or-no questions](#21-asking-yes-or-no-questions)
- [2.2 Doing something only when it is true](#22-doing-something-only-when-it-is-true)
- [2.3 More than two cases](#23-more-than-two-cases)
- [2.4 A list of sales](#24-a-list-of-sales)
- [2.5 Going through every sale](#25-going-through-every-sale)
- [2.6 Counting and picking out sales in a loop](#26-counting-and-picking-out-sales-in-a-loop)
- [2.7 Practice: the day's total, biggest sale and big orders](#27-practice-the-days-total-biggest-sale-and-big-orders)
<!-- /contents -->

## 2.1 Asking yes-or-no questions

At the end of chapter 1, `day_total.py` printed the day's report for Sharma General Store: a total of 2657 rupees from eight sales. A report like that answers "how much?". The next questions a shopkeeper asks are different. Did today beat the target of 2500? Was the 1340-rupee sale a big order, worth a thank-you call? Is this amount the same as the one in the notebook?

Each of these has only two possible answers: yes or no. In a spreadsheet you have asked such questions already. Type `=B7>=300` into a cell and the cell shows `TRUE` or `FALSE`. Python has the same thing, and this section is about it. Everything else in the chapter, deciding what to print (2.2) and choosing which sales to count (2.6), is built on these yes-or-no answers.

### The question, written in Python

<!-- teaches: comparison = comparison, comparison operator, == -->
Save this in `~/shop` as `big_sale.py` and run it with `python3 big_sale.py`:

<!-- code: id=big_sale -->
```python
sale = 1340
print(sale > 1000)
print(sale < 100)
print(sale >= 1340)
print(sale <= 1000)
print(sale == 1340)
print(sale != 1340)
```
```text
True
False
True
False
True
False
```

Six lines of output, each one a word: `True` or `False`. Each `print` line holds a **comparison**: two values with a **comparison operator** between them, which asks how the two values stand to each other. Python has six of them:

| Operator | Asks | Spreadsheet | Here |
|---|---|---|---|
| `>` | greater than? | `>` | `1340 > 1000` is `True` |
| `<` | less than? | `<` | `1340 < 100` is `False` |
| `>=` | greater than or equal to? | `>=` | `1340 >= 1340` is `True` |
| `<=` | less than or equal to? | `<=` | `1340 <= 1000` is `False` |
| `==` | equal to? | `=` | `1340 == 1340` is `True` |
| `!=` | not equal to? | `<>` | `1340 != 1340` is `False` |

Four of them you know from the spreadsheet. Two are written differently, and they are the two that catch people.

**Equal is `==`, two equals signs.** In a spreadsheet one `=` does both jobs: at the start of a cell it means "here comes a formula", and inside a formula it means "is equal to". Python cannot do that, because one `=` already has a job: since 1.4, `sale = 1340` means "stick the label `sale` on the value 1340". So "is equal to" got a sign of its own, `==`. Read `sale == 1340` aloud as "sale equals 1340?", with the question mark, and `sale = 1340` as "sale becomes 1340". One asks, the other does.

**Not equal is `!=`.** The `!` is Python's way of writing "not". A spreadsheet writes `<>` instead; Python 3 does not accept `<>` at all.

**`>=` and `<=` are written in that order:** the `=` comes second, as you say it, "greater than or equal". `=>` is not an operator, and Python stops with a `SyntaxError` before running anything.
<!-- checked: how=run date=2026-11-18 ref="try: print(5 => 3) and print(5 <> 3) both SyntaxError, Python 3.13" h=c137a65c -->

**There is no space inside the operator.** `> =` with a space is two signs, not one, and is also a `SyntaxError`. Spaces *around* the operator are fine and make the line easier to read: `sale >= 300`.

### True and False are values

<!-- teaches: boolean = boolean, bool -->
What exactly did `print` get each time? Not the text "True". A comparison is an expression, like `450 + 120` in 1.2, and an expression has a value. The value of `sale > 1000` is one of exactly two values, `True` or `False`, and these are a type of their own, called **bool** (short for *Boolean*, after George Boole, who worked out the arithmetic of yes and no in the 1850s). A value of this type is called a **boolean**.

Ask Python with `type()`, as you did for numbers and strings in 1.5. Save this as `bool_type.py`:

<!-- code: id=bool_type -->
```python
sale = 1340
is_big = sale >= 300
print(is_big)
print(type(is_big))
print(type(True))
print(type("True"))
```
```text
True
<class 'bool'>
<class 'bool'>
<class 'str'>
```

`is_big` holds `True`, and its type is `bool`. `True` written on its own, with a capital T and no quotes, is the same value. `"True"` in quotes is something else entirely: a string of four letters, which happens to spell a word. Python's two booleans are not text. They are like the `TRUE` and `FALSE` in a spreadsheet cell, which are not text either: the cell would not hold them that way if you typed `'TRUE` with an apostrophe in front.

The capital letter matters. Python's names are case-sensitive (1.4), and `true` with a small t is just a name nobody made. Write `print(true)` and you get the `NameError` you met in 1.6: `name 'true' is not defined`, and on recent versions Python adds a guess, `Did you mean: 'True'?`.
<!-- checked: how=run date=2026-11-18 ref="try: print(true) -> NameError: name 'true' is not defined. Did you mean: 'True'?, Python 3.13" h=fa53998b -->


### What Python does with a comparison

Take line 2 of `bool_type.py`, `is_big = sale >= 300`, and follow it the way 1.4 followed an assignment:

1. Python sees `=` with a name on its left, so it is an assignment. It works out the right-hand side first.
2. On the right is `sale >= 300`. Python looks up the label `sale` and finds the value 1340.
3. It compares 1340 with 300: is 1340 greater than or equal to 300? Yes. The comparison's value is `True`.
4. It sticks the label `is_big` on that value, `True`.

After line 2 there are two labels, holding two values of two types:

| Name | Value | Type |
|---|---|---|
| `sale` | `1340` | `int` |
| `is_big` | `True` | `bool` |

Notice what did *not* happen. `is_big` does not keep the question `sale >= 300` and ask it again later. It holds the answer, worked out once, on line 2. Change `sale` on line 3 and `is_big` stays `True`. This is the same lesson as `no_recalc.py` in 1.4: a Python name is not a spreadsheet formula, and nothing is worked out again unless a line of the program does it.

**Which comes first, the sum or the comparison?** In a line like `print(sale + 40 >= 500)`, Python does the arithmetic first and compares after: `sale + 40` is worked out, and then the result is compared with 500. Arithmetic before comparison is the order you would expect, and it is the one Python uses, so you rarely need brackets. Put them in anyway when it helps you read the line: `(sale + 40) >= 500` means the same.

### Comparing text

Comparisons work on strings too, and the shop's item names are strings. Save this as `compare_text.py`:

<!-- code: id=compare_text -->
```python
item = "Soap"
print(item == "Soap")
print(item == "soap")
print(item == "Soap ")
print("rice" < "soap")
print("Soap" < "rice")
```
```text
True
False
False
True
True
```

The first line is `True`: the two strings are the same letters in the same order. The next two are `False`, and they matter for this book. To Python, `"Soap"` and `"soap"` are different strings, because a capital S is a different character from a small s. And `"Soap "` with a space at the end is different again: the space is a character like any other. In Excel or Google Sheets, `="Soap"="soap"` gives `TRUE`, because they ignore capitals when they compare text (LibreOffice Calc has a setting for it, under its calculation options). Python never ignores them.
<!-- checked: how=source date=2026-11-18 ref="help.libreoffice.org/latest/en-US/text/shared/optionen/01060500.html (Calc > Calculate > Case sensitive)" h=a10d15f7 -->
 When the shop's sales sheet has `Soap`, `soap` and `Soap ` typed by three different people, Python sees three different items. Chapter 3 (3.1) is how you make them one.

The last two lines show that `<` and `>` work on text as well: `"rice" < "soap"` is `True` because *r* comes before *s* in the alphabet, the order you would find them in a dictionary. But `"Soap" < "rice"` is `True` too, though *s* comes after *r*. Python compares strings character by character using each character's number in a code table, and in that table every capital letter comes before every small letter. So a list sorted this way puts `Soap` before `rice`. Useful to know when a sorted list of items looks wrong; for now, use `==` and `!=` on text, and leave `<` and `>` for numbers.

### Two questions at once: and, or, not

Some questions are made of two. The shop's daily target is "at least 2500 rupees, from at least 8 sales". Python joins two booleans with **`and`**, which is `True` only when both are `True`, and with **`or`**, which is `True` when at least one is. **`not`** turns one boolean into the other. Save this as `target.py`:

<!-- code: id=target -->
```python
total = 2657
count = 8
print(total >= 2500 and count >= 8)
print(total >= 3000 or count >= 8)
print(total >= 3000 and count >= 8)
print(not total >= 3000)
```
```text
True
True
False
True
```

Follow line 3. Python works out `total >= 2500`, which is `True`, and `count >= 8`, which is `True`. Then `and` joins them: both are `True`, so the whole is `True`. On line 4, `total >= 3000` is `False` but `count >= 8` is `True`, and for `or` one is enough, so the whole is `True`. Line 5 asks for both, and only one holds, so it is `False`. Line 6 works out `total >= 3000`, which is `False`, and `not` turns it round to `True`.

These are the spreadsheet's `AND(...)` and `OR(...)` and `NOT(...)`, written between the values instead of around them. The order is: arithmetic first, then the comparisons, then `not`, then `and`, then `or`. So in line 3 both comparisons are done before `and` joins them, which is what you want.

**"Between" is two comparisons.** A medium-sized sale, at least 100 and under 500, is `sale >= 100 and sale < 500`. You must write `sale` twice. In speech you say "sale is at least 100 and under 500", and it is tempting to write `sale >= 100 and < 500`, but `< 500` on its own compares nothing with 500, and Python refuses the line with a `SyntaxError`.
<!-- checked: how=run date=2026-11-18 ref="try: print(sale >= 100 and < 500) SyntaxError, Python 3.13" h=a62e1e9e -->
 Python also lets you write the "between" the way a maths book does, `100 <= sale < 500`, which means exactly the same as the `and` version. Use whichever you read more easily.

### When it goes wrong

**Text that looks like a number.** The most expensive mistake with comparisons is the one that gives no error. Suppose the amount 450 reached your program as text, `"450"`, the way every amount will when you read the sales file in chapter 4. Save this as `text_amount.py`:

<!-- code: id=text_amount exit=1 -->
```python
amount = "450"
print(amount == 450)
print(amount > 100)
```
```text
False
Traceback (most recent call last):
  File "/home/you/text_amount.py", line 3, in <module>
    print(amount > 100)
          ^^^^^^^^^^^^
TypeError: '>' not supported between instances of 'str' and 'int'
```

Line 2 printed `False`. Python was not confused: `"450"` is a string and `450` is an int, and a string is never equal to a number, whatever its letters spell. No error, no warning, just a wrong answer. A program that asks "is this the 450-rupee sale?" would answer no, quietly, every time.

Line 3 is kinder: it stops with a `TypeError`. `==` can always answer, because two things of different types are simply not equal, but `>` would have to say which is bigger, a string or a number, and Python refuses to guess. Read it from the bottom up, as in 1.6: `'>' not supported between instances of 'str' and 'int'` says the operator, then the two types it was given, in order. When you see this message, one side of the comparison is text that should be a number. Chapter 3 (3.3) turns such text into a number; for now, notice that the quietly wrong `False` on line 2 is the more dangerous of the two, and that checking the program's answer against the same sum in the spreadsheet, as in 1.7, is what catches it.

**`=` where you meant `==`.** Writing `print(sale = 1340)` does not compare anything; Python reads `sale = ...` inside the brackets as a setting for `print`, and stops with a `TypeError` saying that `'sale'` is not a setting `print` knows.
<!-- checked: how=run date=2026-11-18 ref="try: print(sale = 1340) -> TypeError: print() got an unexpected keyword argument 'sale', Python 3.13" h=9ca2cb91 -->
 Inside an `if` (2.2) the same slip gives a `SyntaxError` that even suggests `==`. Whenever you mean "is equal to?", count the signs.

**Comparing floats for equality.** In 1.5, `0.1 + 0.2` printed `0.30000000000000004`. So `0.1 + 0.2 == 0.3` is `False`. Amounts in this book are whole rupees, ints, and ints compare exactly; when you do have floats, such as an average, compare with `<` or `>`, not `==`.

### Keep it

- A **comparison** (`>`, `<`, `>=`, `<=`, `==`, `!=`) is an expression whose value is `True` or `False`, the two values of type **bool**.
- `==` asks "equal?"; `=` assigns. `!=` is "not equal".
- A name holding a comparison holds the answer, not the question.
- Text compares letter by letter: `"Soap" == "soap"` is `False`. A string never equals a number: `"450" == 450` is `False`, with no error.
- `and` needs both, `or` needs one, `not` turns a boolean round.

**Check yourself**

<!-- q: idea=comparison type=predict wrong="> counts the number itself" -->
1. Before running it: what do these two lines print?

<!-- code: id=boundary_predict answer -->
```python
sale = 300
print(sale > 300, sale >= 300)
```

<details>
<summary>Answer</summary>

```text
False True
```

`300 > 300` is `False`: 300 is not greater than itself. `300 >= 300` is `True`, because "or equal" lets it in. If you said `True True`, you read `>` as "at least". This is the difference between a big order "over 300" and one "of 300 or more", and in 2.6 it changes the count.

</details>

<!-- q: idea=comparison type=predict wrong="Python ignores capitals when comparing text" -->
2. One sale was typed as `"Rice"` and another as `"rice"`. What does `print("Rice" == "rice")` show, and what would Excel or Google Sheets show for `="Rice"="rice"`?

<details>
<summary>Answer</summary>

Python prints `False`; those spreadsheets show `TRUE`. A capital R and a small r are different characters to Python, so the strings are different. The spreadsheets ignore case when they compare text, which is why this surprises people coming from one. Chapter 3 makes the two spellings match.

</details>

<!-- q: idea=comparison type=explain wrong="a string that looks like a number equals the number" -->
3. A friend's program says `amount = "120"` near the top, and later `print(amount == 120)` prints `False`. They say Python is broken. What do you tell them, in two sentences?

<details>
<summary>Answer</summary>

`amount` holds a string, the characters 1, 2, 0, and `120` without quotes is an int; values of different types are never equal, so `False` is the right answer. Take the quotes off the 120 in the assignment (or, for text that comes from a file, convert it, chapter 3) and the comparison prints `True`. The tempting wrong idea is that Python looks at what the text spells; it looks at the type first.

</details>

<!-- q: idea=boolean type=apply -->
4. Write one expression that is `True` when `sale` is at least 100 and under 500, and check it in your head for 100, 499 and 500.

<details>
<summary>Answer</summary>

`sale >= 100 and sale < 500` (or `100 <= sale < 500`). For 100: `True and True`, so `True`. For 499: `True`. For 500: `500 < 500` is `False`, so the whole is `False`. Writing `sale >= 100 and < 500` is the usual slip; Python stops with a `SyntaxError`, because `< 500` has nothing on its left.

</details>

<!-- q: idea=boolean type=predict wrong="the name keeps the question and re-asks it" -->
5. Before running it: what does the last line print?

<!-- code: id=stale_answer answer -->
```python
sale = 1340
is_big = sale >= 300
sale = 64
print(sale, is_big)
```

<details>
<summary>Answer</summary>

```text
64 True
```

`is_big` was given the answer `True` on line 2, when `sale` was 1340. Changing `sale` on line 3 does not ask the question again, so `is_big` still holds `True`. If you said `64 False`, you pictured `is_big` as a spreadsheet formula that recalculates; in Python a name holds a value, not a formula (1.4).

</details>

## 2.2 Doing something only when it is true

You can now ask "did today beat the target?" and get `True`. But a report that prints `True` in the middle of it is a strange report. What the shop wants is a line that says *Target reached!* on a good day, and no line at all on a bad one. In a spreadsheet you would write `=IF(B10>=2500, "Target reached!", "")`. In Python you write an `if` statement, and it does something a spreadsheet formula cannot: it decides whether whole lines of the program run at all.

### The picture: a step in the recipe that you may skip

Since 1.3 a program has been a recipe that the computer follows from the top to the bottom, every line, one at a time. Real recipes are not quite like that. "If the dough is sticky, add a spoon of flour." The cook reads the condition, looks at the dough, and either does the step or goes straight on to the next. An `if` statement is that kind of step.

This is where the recipe picture first stops being true. The computer still reads from top to bottom, and it still never goes back up (that comes in 2.5). But from now on, it does not always do every line. Which lines run depends on the values the program has when it gets there.

### The first `if`

<!-- teaches: if-statement = if statement, condition, block, body -->
Save this in `~/shop` as `target_check.py` and run it:

<!-- code: id=target_check -->
```python
total = 2657
target = 2500

print("Sharma General Store")
print("Total sales:", total)
if total >= target:
    print("Target reached!")
    print("Above target by:", total - target)
print("End of report")
```
```text
Sharma General Store
Total sales: 2657
Target reached!
Above target by: 157
End of report
```

All five lines of report appear. Now change line 1 to `total = 2400`, save the file as `target_missed.py`, and run that:

<!-- code: id=target_missed -->
```python
total = 2400
target = 2500

print("Sharma General Store")
print("Total sales:", total)
if total >= target:
    print("Target reached!")
    print("Above target by:", total - target)
print("End of report")
```
```text
Sharma General Store
Total sales: 2400
End of report
```

Two lines are missing, the two that were indented under the `if`. Python did not even work out `total - target`; it skipped both lines and went straight on to `End of report`.

The `if` statement has four parts, and every one of them matters:

<!-- code: id=if-shape mode=fragment -->
```python
if total >= target:
    print("Target reached!")
    print("Above target by:", total - target)
print("End of report")
```

1. The word **`if`**, in small letters.
2. The **condition**: any expression whose value is `True` or `False`, usually a comparison from 2.1.
3. A **colon** `:` at the end of the line. It says "the lines that depend on this come next".
4. The **block** (also called the **body**): the lines under the `if`, each pushed in by four spaces. They run only when the condition is `True`.

The block ends at the first line that is no longer pushed in. Here that is `print("End of report")`, which sits at the same depth as `if`, so it is not part of the block and runs every time, whatever the condition was.

### Indentation is part of the program

<!-- teaches: indentation = indentation, indent, four spaces -->
The spaces at the start of a line are called its **indentation**. In most of what you have typed so far they were decoration; here they are the program. They are the only thing that tells Python which lines belong to the `if`. There are no brackets around the block and no "end if" line: the indentation is the boundary.

The rule this book follows, which is the one almost all Python code follows: **indent with four spaces, never a tab character.** Python would accept another fixed number of spaces, but four is the agreed style (PEP 8, the Python style guide), and mixing tabs and spaces can make lines that look the same to you look different to Python. In Ubuntu's Text Editor, the Tab key may put in a tab character or spaces depending on its settings; the safe habit is to press the space bar four times until you have checked that setting (it is under the editor's indentation options).
<!-- checked: how=reworded date=2026-11-18 ref="one look did not settle the 24.04 default; the text says it depends on the setting and tells the reader to press space four times" h=c92c03c5 -->

Watch how one line's indentation changes what a program means. The shop charges 30 rupees for home delivery on orders under 500; delivery is free from 500 up. Save this as `delivery.py`:

<!-- code: id=delivery -->
```python
bill = 420
delivery = 0
if bill < 500:
    delivery = 30
    print("Delivery charge added")
print("Bill:", bill)
print("Delivery:", delivery)
print("To pay:", bill + delivery)
```
```text
Delivery charge added
Bill: 420
Delivery: 30
To pay: 450
```

For a bill of 420, the condition `420 < 500` is `True`, so both indented lines run: `delivery` becomes 30, and the message is printed. To pay: 450.

Here is the same program with two changes: the message is not indented, and the bill is 650, which should get free delivery. Save it as `delivery_wrong.py`:

<!-- code: id=delivery_wrong -->
```python
bill = 650
delivery = 0
if bill < 500:
    delivery = 30
print("Delivery charge added")
print("Bill:", bill)
print("Delivery:", delivery)
print("To pay:", bill + delivery)
```
```text
Delivery charge added
Bill: 650
Delivery: 0
To pay: 650
```

The output contradicts itself: it says a charge was added, then shows a delivery of 0. The `if` block is now only one line long, `delivery = 30`, and `print("Delivery charge added")` is an ordinary line that runs for every bill. Python gave no error, because the program is perfectly correct Python. It just is not the program you meant. That is why indentation deserves a second look every time a report says something odd: the symptom is a line printed when it should not be, or a value changed when it should not be.

### What Python does, line by line

Here is `delivery.py` again, followed for two bills. For each, the table says which lines ran.

| Line | Code | `bill = 420` | `bill = 650` |
|---|---|---|---|
| 1 | `bill = ...` | runs | runs |
| 2 | `delivery = 0` | runs: `delivery` is 0 | runs: `delivery` is 0 |
| 3 | `if bill < 500:` | `420 < 500` is `True` | `650 < 500` is `False` |
| 4 | `delivery = 30` | runs: `delivery` is 30 | skipped |
| 5 | `print("Delivery charge added")` | runs | skipped |
| 6 to 8 | the three `print` lines | `To pay: 450` | `To pay: 650` |

At line 3 Python works out the condition, exactly as in 2.1, and gets one boolean. If it is `True`, Python goes into the block and runs its lines in order. If it is `False`, Python jumps to the first line after the block, the first line indented no deeper than the `if` itself. Either way, it then carries on down the file as before. The condition is asked once, at the moment Python reaches it; later lines do not ask it again.

Notice line 2, `delivery = 0`. It is there so that `delivery` exists whatever happens at line 3. Take it out, run the program with `bill = 650`, and after `Bill: 650` the line `print("Delivery:", delivery)` stops with a `NameError`: `name 'delivery' is not defined`, because the only line that would have made the name was skipped. (The traceback calls it line 6, not 7: the file is one line shorter.) When a name is made inside an `if` block and used after it, give it a starting value before the `if`.
<!-- checked: how=run date=2026-11-18 ref="try: delivery.py without line 2, bill = 650, Python 3.13" h=3039787e -->

**The condition can be any boolean.** A name that holds `True` or `False` works on its own:

<!-- code: id=if_bool_name -->
```python
sale = 1340
is_large = sale >= 1000
if is_large:
    print("Large sale: call the customer to say thank you")
print("Sale:", sale)
```
```text
Large sale: call the customer to say thank you
Sale: 1340
```

Write `if is_large:`, not `if is_large == True:`. Both work, but the second asks "is (the answer) equal to yes?", which is the same question asked twice.

**A block can hold an `if` of its own.** The inner block is then pushed in by eight spaces, four for each level. You will see this in 2.6, where an `if` sits inside a loop.

### When it goes wrong

Python checks the whole file before it runs any of it (1.3), so most mistakes with `if` stop the program before even the first line runs. Each has its own message.

**Forgetting the colon.** Save this as `no_colon.py`:

<!-- code: id=no_colon mode=error -->
```python
total = 2657
if total >= 2500
    print("Target reached!")
```
```text
  File "no_colon.py", line 2
    if total >= 2500
                    ^
SyntaxError: expected ':'
```

The last line names the error, `SyntaxError`, and says exactly what was missing; the `^` under the line points at where the colon should go. Nothing was printed, not even from line 1: a `SyntaxError` means Python could not read the file, so it ran none of it.

**Forgetting to indent the block.** Save this as `no_indent.py`:

<!-- code: id=no_indent mode=error -->
```python
total = 2657
if total >= 2500:
print("Target reached!")
```
```text
Sorry: IndentationError: expected an indented block after 'if' statement on line 2 (no_indent.py, line 3)
```

`IndentationError` is a kind of `SyntaxError` about spaces. Python saw the colon, so it expected at least one pushed-in line next, and the message even names the line of the `if` that wanted it.

**Indenting a line for no reason.** A line pushed in where no block was opened is an error too:

<!-- code: id=stray_indent mode=error -->
```python
total = 2657
    print("Total:", total)
```
```text
Sorry: IndentationError: unexpected indent (stray_indent.py, line 2)
```
<!-- checked: how=run date=2026-11-18 ref="try: python3 stray_indent.py and python3 no_indent.py in a terminal session, Python 3.13" h=81bda804 -->

These two messages are shown here squeezed onto one line. In your terminal, `python3 stray_indent.py` prints them in the same shape as `no_colon.py`'s: a `File "stray_indent.py", line 2` line, the line itself, and `IndentationError: unexpected indent` as the last line (for `no_indent.py`, `^^^^^` under `print` too).

`unexpected indent`: every line outside a block must start at the left edge. This often happens after copying a line from somewhere else that had spaces in front of it.

**One `=` in the condition.** In 2.1 you were warned about this; here is what it looks like. Save it as `one_equals.py`:

<!-- code: id=one_equals mode=error -->
```python
total = 2657
if total = 2657:
    print("Exactly the same as yesterday")
```
```text
  File "one_equals.py", line 2
    if total = 2657:
       ^^^^^^^^^^^^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

Python refuses to read the line, and its message suggests `==`, which is almost always what you meant.

**A block that is right in Python but wrong for you.** The worst mistake is the one with no message: a line indented one level too few or too many, like `delivery_wrong.py`. Read your indentation as part of the logic: for each indented line, ask "should this happen only when the condition is true?"

### Keep it

- `if condition:` followed by an indented block runs the block only when the condition is `True`; otherwise Python skips to the first line after the block.
- The colon opens the block; four spaces per level mark it; the first line back at the `if`'s depth ends it.
- Indentation is meaning. A wrongly indented line gives no error, only wrong output.
- A name made inside an `if` needs a starting value before it, if it is used after.

**Check yourself**

<!-- q: idea=if-statement type=predict wrong="the condition < 500 is true for 500" -->
1. Before running it: in `delivery.py`, change the bill to exactly 500. What are the three report lines?

<details>
<summary>Answer</summary>

```text
Bill: 500
Delivery: 0
To pay: 500
```

`500 < 500` is `False`, so the block is skipped: no message, no charge. That matches the shop's rule, "free from 500 up". If you expected a charge, you read `<` as "up to and including"; that would be `<=`, and it would charge a customer who reached the free-delivery amount exactly.

</details>

<!-- q: idea=indentation type=fix wrong="indentation is only for looks" -->
2. This program prints `Target reached!` on every day, even a day of 1800. Find the fault and fix it.

<!-- code: id=target_fault -->
```python
total = 1800
target = 2500
if total >= target:
    print("Well done.")
print("Target reached!")
print("Total sales:", total)
```
```text
Target reached!
Total sales: 1800
```

<details>
<summary>Answer</summary>

The line `print("Target reached!")` is not indented, so it is outside the `if` block and runs every time. Push it in by four spaces so that it sits under `print("Well done.")`; then, for 1800, both lines are skipped and only `Total sales: 1800` is printed. There was no error message, because the program was valid Python: the only symptom was a report line that contradicted the numbers.

</details>

<!-- q: idea=if-statement type=predict -->
3. Before running it: which lines of this program run, and what does it print?

<!-- code: id=which_lines answer -->
```python
sale = 98
if sale >= 300:
    print("Big order")
    sale = sale - 10
print("Sale:", sale)
```

<details>
<summary>Answer</summary>

```text
Sale: 98
```

Lines 1, 2 and 5 run. `98 >= 300` is `False`, so lines 3 and 4 are skipped, and `sale` keeps its value 98. The tempting wrong answer is `Sale: 88`, from running line 4 anyway; but line 4 is inside the block, so it is skipped with line 3.

</details>

<!-- q: idea=if-statement type=apply -->
4. Add to `delivery.py` a line that prints `Large order: thank the customer` when the bill is 1000 or more. Where does it go, and how is it indented?

<details>
<summary>Answer</summary>

A second `if`, after the first block, at the left edge:

<!-- code: id=thank_shape mode=fragment -->
```python
if bill >= 1000:
    print("Large order: thank the customer")
```

It must not go inside the first block, because a bill of 1000 or more never gets into that block (`bill < 500` is `False`), so the line would never run. Two separate questions get two separate `if` statements, one after the other.

</details>

## 2.3 More than two cases

The shop sorts its sales into three sizes for the weekly notebook: small (under 100 rupees), medium (100 up to 999) and large (1000 and over). One `if` answers one yes-or-no question. Three sizes need a chain: try the first case, and only if it fails try the next, and if all fail, take the last one.

<!-- teaches: elif-else = elif, else -->
Save this as `sale_size.py`:

<!-- code: id=sale_size -->
```python
sale = 210
if sale >= 1000:
    print("Large sale")
elif sale >= 100:
    print("Medium sale")
else:
    print("Small sale")
print("Sale:", sale)
```
```text
Medium sale
Sale: 210
```

**`elif`** is short for "else if": it is only tried when every condition above it was `False`. **`else`** has no condition at all; its block runs when nothing above it was `True`. Python goes down the chain and stops at the first `True` condition: for 210, `210 >= 1000` is `False`, so it tries `210 >= 100`, which is `True`, runs `print("Medium sale")`, and skips the rest of the chain, `else` included. Exactly one of the three blocks runs, every time. Then Python carries on at line 8, which is outside the chain.

That is why the second condition can be just `sale >= 100` and not `sale >= 100 and sale < 1000`: by the time Python reaches the `elif`, it already knows the sale is under 1000. In a spreadsheet this is a nested `=IF(B2>=1000, "Large", IF(B2>=100, "Medium", "Small"))`; in Python the nesting is flattened into a list you read from the top. You can have as many `elif` lines as you need, and at most one `else`, which must come last. Each `elif` and the `else` end with a colon and sit at the same depth as the `if`.

`else` on its own also finishes a plain two-way `if`. The delivery rule of 2.2 can be written so that both cases are spelt out:

<!-- code: id=delivery_else -->
```python
bill = 650
if bill < 500:
    delivery = 30
else:
    delivery = 0
print("To pay:", bill + delivery)
```
```text
To pay: 650
```

Here `delivery` needs no starting value before the `if`: one of the two blocks always runs, so the name always exists by line 6.

### The order of the conditions is the logic

Because the first `True` wins, the order matters. Here the two tests are swapped, and the sale is the day's biggest. Save it as `sale_size_wrong.py`:

<!-- code: id=sale_size_wrong -->
```python
sale = 1340
if sale >= 100:
    print("Medium sale")
elif sale >= 1000:
    print("Large sale")
else:
    print("Small sale")
```
```text
Medium sale
```

1340 is called medium. `1340 >= 100` is `True`, so the first block runs and Python never reaches the `>= 1000` test. No error: just a large sale filed as medium, which you notice only by checking a case whose answer you know. When the conditions are "at least" thresholds, go from the biggest down; with "under" thresholds (`sale < 100`, then `sale < 1000`), go from the smallest up.

**Check yourself**

<!-- q: idea=elif-else type=predict wrong="every true condition in the chain runs" -->
1. Before running it: what does `sale_size.py` print, for the first line, when `sale` is 100? When it is 99? When it is 1000?

<details>
<summary>Answer</summary>

`Medium sale`, `Small sale`, `Large sale`. For 100, `100 >= 1000` is `False` and `100 >= 100` is `True`. For 99 both are `False`, so `else` runs. For 1000 the first test is already `True`. Note that 1000 is also `>= 100`; but only the first `True` block runs, so you never get `Large sale` and `Medium sale` together.

</details>

<!-- q: idea=elif-else type=decide wrong="two ifs are the same as if and elif" -->
2. A friend writes the size check as two separate `if` statements, `if sale >= 1000: print("Large sale")` and then `if sale >= 100: print("Medium sale")`. For which sales does it go wrong, and what is the fix?

<details>
<summary>Answer</summary>

For every sale of 1000 or more: both conditions are `True`, and two separate `if` statements are two separate questions, so it prints `Large sale` and then `Medium sale`. Turning the second `if` into `elif` fixes it, because an `elif` is only tried when everything above it was `False`. Use separate `if` statements for independent questions (2.2's delivery and thank-you), and a chain for cases where exactly one must win.

</details>

## 2.4 A list of sales

Look again at the chapter project of 1.7. To add up one day's eight sales, `day_total.py` needed eight names, `sale_1` to `sale_8`, a long sum that named all eight, and a `count = 8` that you had to keep in step by hand. Add a ninth sale and three lines change. A busy day at Sharma General Store has well over a hundred sales; nobody is going to type `sale_137`.

A spreadsheet never had this problem. The day's sales sit in one column, B2 to B9, and `=SUM(B2:B9)` takes the whole range at once. Python's version of that column is a **list**.

### The picture: one label on a whole column

Since 1.4 a name has been a label stuck on one value. A list is a single value that holds other values in order, the way a column holds cells. So one label, `sales`, can be stuck on the whole column, and you can still reach each cell in it by its position.

The picture is close, and it breaks in two places that you need to know. First, positions in a list are counted from 0, not from 1: the first sale is at position 0. Second, a spreadsheet column has a heading at the top and a fixed place on the sheet; a list has no heading, and it grows and shrinks as you add and remove values.

### Making a list

<!-- teaches: list = list, square brackets, item, append -->
Save this as `sales_list.py`:

<!-- code: id=sales_list -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print(sales)
print(type(sales))
```
```text
[450, 120, 75, 210, 98, 1340, 64, 300]
<class 'list'>
```

A list is written as values separated by commas, between square brackets `[` and `]`. Each value in it is an **item**. Python prints a list the same way you wrote it, brackets and commas included, so you can see at a glance what it holds. Its type is `list`, a type of its own, as `int` and `str` are.

Line 1 makes one value, the list, holding eight items in this order, and sticks the label `sales` on it. The order is kept: the list is not sorted, and 450 stays first because you wrote it first. The items here are ints, but a list can hold any values, strings for instance:

<!-- code: id=items_list -->
```python
items = ["rice", "soap", "biscuits", "tea", "matches", "oil", "salt", "sugar"]
print(items)
empty = []
print(empty)
```
```text
['rice', 'soap', 'biscuits', 'tea', 'matches', 'oil', 'salt', 'sugar']
[]
```

`[]` with nothing inside is an **empty list**: a list with no items yet. It looks useless, and it will be the starting point of almost every list you build in 2.6.

### Reaching one item: the index

<!-- teaches: index = index, position, IndexError -->
To get one item out, write the list's name and the item's position in square brackets after it. The position is called the **index**. Save this as `sales_index.py`:

<!-- code: id=sales_index -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print(sales[0])
print(sales[1])
print(sales[5])
print(sales[7])
print(sales[-1])
print(sales[-2])
```
```text
450
120
1340
300
300
64
```

`sales[0]` is 450, the first sale. `sales[1]` is the second, 120. The last of the eight is `sales[7]`, not `sales[8]`. Here is the whole list laid out like the spreadsheet column it came from:

| Spreadsheet cell | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 |
|---|---|---|---|---|---|---|---|---|
| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| Negative index | -8 | -7 | -6 | -5 | -4 | -3 | -2 | -1 |
| Value | 450 | 120 | 75 | 210 | 98 | 1340 | 64 | 300 |

**Why start at 0?** An index is not "which number item is this?" but "how many steps from the start?". The first item is zero steps from the start; the second is one step along. That is how the list is kept in memory: Python keeps its places one after another, so to find item 5 it works out the spot 5 places past the start and goes straight there, without looking at the items before it. Many programming languages count this way, for the same reason. It feels wrong for a week and then you stop noticing it.

**Negative indexes count from the end.** `sales[-1]` is the last item, `sales[-2]` the one before it. This is handy when you want the last sale of the day and do not want to count how many there were.

An item reached by its index can be used wherever a value can: `sales[0] + sales[1]` is 570, `sales[5] >= 1000` is `True`.

### Changing a list

A list can be changed after it is made, and that is what makes it a good fit for a day's sales, which keep coming in. Say the shopkeeper finds that the third sale was written down as 75 when the bill says 57, and that one more sale of 150 came in after the list was typed. Save this as `sales_fix.py`:

<!-- code: id=sales_fix -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
sales[2] = 57
print(sales)
sales.append(150)
print(sales)
print(sales[-1])
```
```text
[450, 120, 57, 210, 98, 1340, 64, 300]
[450, 120, 57, 210, 98, 1340, 64, 300, 150]
150
```

Line 2 is an assignment, but to one place in the list: "item 2 of `sales` becomes 57". The old value 75 is gone; the other items are untouched. Line 4 adds 150 at the end: the list is now nine items long, and `sales[-1]` is the new sale.

`append` is written differently from `print`. It comes after the list's name and a dot, `sales.append(150)`, because it is something a list can do to itself: "list, add this item to your end". Commands that belong to a value and are written after a dot like this are called methods; chapter 3 is full of them, for strings (3.1). For now you need only this one, and it is the one you will use most: it is how a list is built up, one item at a time.

Notice that `sales.append(150)` is a line on its own, not `sales = sales.append(150)`. It changes the list in place. The assignment version is a classic mistake, shown below.

### When it goes wrong

**One past the end.** Save this as `past_end.py`:

<!-- code: id=past_end exit=1 -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print("First sale:", sales[0])
print("Last sale:", sales[8])
```
```text
First sale: 450
Traceback (most recent call last):
  File "/home/you/past_end.py", line 3, in <module>
    print("Last sale:", sales[8])
                        ~~~~~^^^
IndexError: list index out of range
```

Read from the bottom: an `IndexError`, and `list index out of range`. There are eight items, so the indexes run from 0 to 7, and 8 is one past the end. The first line of output shows that line 2 ran; the marks under line 3, `~~~~~^^^`, underline `sales[8]`, the part that failed, with the `^` under the index. When you see this message, the fix is almost always "one less", or `-1` for the last item.

**The quiet version: counting from 1.** If you write `sales[1]` meaning the first sale, you get no error at all, just the second sale, 120. Only a check against what you expected (the first sale of the day was 450) shows it.

**A missing comma.** Save this as `no_comma.py`:

<!-- code: id=no_comma mode=error -->
```python
sales = [450, 120 75, 210]
print(sales)
```
```text
  File "no_comma.py", line 1
    sales = [450, 120 75, 210]
                  ^^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma?
```

Python cannot read the line, and on recent versions it guesses the cause: a forgotten comma. A space is not enough to separate two items.

**Round brackets instead of square ones.** `sales(0)` asks Python to *call* `sales`, the way `print(...)` is called, and a list cannot be called. Save this as `round_brackets.py`:

<!-- code: id=round_brackets exit=1 -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print(sales(0))
```
```text
Traceback (most recent call last):
  File "/home/you/round_brackets.py", line 2, in <module>
    print(sales(0))
          ~~~~~^^^
TypeError: 'list' object is not callable
```

`'list' object is not callable`: you used a list as if it were a command. Square brackets after a name get an item out; round brackets call.

**Assigning the result of `append`.** Save this as `append_assign.py`:

<!-- code: id=append_assign -->
```python
sales = [450, 120, 75]
sales = sales.append(210)
print(sales)
```
```text
None
```

It prints `None`, and the list is lost. `append` changed the list and then gave back nothing, Python's special value `None`, and line 2 stuck the label `sales` on that nothing. The three sales are no longer reachable. Write `sales.append(210)` on its own line.

### Back to the day's total

With a list, the eight names of chapter 1 become one:

<!-- code: id=total_by_index -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
total = sales[0] + sales[1] + sales[2] + sales[3] + sales[4] + sales[5] + sales[6] + sales[7]
print("Total sales:", total)
```
```text
Total sales: 2657
```

It prints 2657, which matches chapter 1. But look at line 2: it is no shorter than the old one, and if a ninth sale is appended, it is wrong without saying so. The list holds every sale; what is missing is a way to say "every item, however many there are". That is a loop, and it is the next section.

### Keep it

- A **list** is one value holding items in order: `[450, 120, 75]`. `[]` is an empty list.
- `sales[i]` is the item at **index** `i`; the first is `sales[0]`, the last is `sales[-1]`. An index one past the end is an `IndexError`.
- `sales[2] = 57` replaces one item; `sales.append(150)` adds one at the end, in place.
- Square brackets get an item; round brackets call.

**Check yourself**

<!-- q: idea=index type=predict wrong="the first item is at index 1" -->
1. Before running it: with `sales = [450, 120, 75, 210, 98, 1340, 64, 300]`, what are `sales[3]`, `sales[-2]` and `sales[1] + sales[2]`?

<details>
<summary>Answer</summary>

`210`, `64` and `195`. Index 3 is the fourth item, because counting starts at 0. `-2` is the second from the end. `sales[1] + sales[2]` is `120 + 75`. If you said `75` for `sales[3]`, you counted from 1; that slip gives no error, only the wrong sale.

</details>

<!-- q: idea=index type=fix wrong="the last index is the number of items" -->
2. A program for a day with five sales has `sales = [210, 64, 300, 98, 450]` and prints `sales[5]` as "the last sale". What happens, and what are two ways to fix the line?

<details>
<summary>Answer</summary>

It stops with `IndexError: list index out of range`: five items have the indexes 0 to 4. Write `sales[4]`, or better `sales[-1]`, which is the last item whatever the length of the list, so it stays right when a sale is appended.

</details>

<!-- q: idea=list type=predict wrong="append returns the changed list" -->
3. Before running it: what does this print?

<!-- code: id=append_predict answer -->
```python
sales = [450, 120]
sales.append(75)
sales.append(210)
sales[0] = 400
print(sales, sales[-1])
```

<details>
<summary>Answer</summary>

```text
[400, 120, 75, 210] 210
```

Each `append` adds at the end, in order, so 75 then 210. `sales[0] = 400` replaces the first item. The last item is 210. If you expected 400 at the end, you read `sales[0] = 400` as adding; it replaces.

</details>

<!-- q: idea=list type=explain -->
4. In one or two sentences: why is a list better than `sale_1` to `sale_8` for a day's sales, even before you know loops?

<details>
<summary>Answer</summary>

The whole day sits under one name, so a new sale is one `append` instead of a new name, and the list can be any length. With separate names, every sale needs its own line and every sum must be retyped when a sale is added; a list can be handed around whole, and (2.5) gone through item by item.

</details>

## 2.5 Going through every sale

The day's sales are in one list now, but adding them up still meant typing `sales[0] + sales[1] + ...` out to `sales[7]`. You want to say, once: "for every sale in the list, add it to the total". That one sentence is almost exactly the Python.

If you have ever made a running-total column in a spreadsheet, you already know how it works inside. Column B holds the sales; in C2 you type `=B2`, in C3 `=C2+B3`, and you drag that formula down. Each cell takes the total so far from the cell above and adds one more sale. The last cell of column C is the day's total. A Python loop does the same thing, with one name instead of a column of cells.

### The picture: the recipe goes back up

"For each potato: peel it, then cut it into four." A cook reading that does not write the two steps out twelve times for twelve potatoes. They take a potato, do the two steps, take the next, do the two steps again, until the bowl is empty, and then go on to the next line of the recipe.

This is the second place where "top to bottom, one line at a time" stops being true. In 2.2 the computer learnt to skip lines. Now it goes *back up*: after the last line of the repeated steps, it returns to the top of them for the next item. It still never wanders; it repeats exactly the indented lines, once per item, and then carries on downwards.

### The first loop

<!-- teaches: for-loop = for loop, loop variable, loop body, iteration -->
Save this as `each_sale.py` and run it:

<!-- code: id=each_sale -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
for sale in sales:
    print("Sale:", sale)
print("Done")
```
```text
Sale: 450
Sale: 120
Sale: 75
Sale: 210
Sale: 98
Sale: 1340
Sale: 64
Sale: 300
Done
```

Eight `Sale:` lines from one `print`, one for each item, in the list's order, and then `Done` once. The shape is the same as an `if`: a first line ending in a colon, and an indented block under it. The block is called the **loop body**. Line 2 says: "for each item in `sales`, stick the label `sale` on it, then run the body".

`sale` is an ordinary name, called the **loop variable**. You choose it; nothing in Python links the word `sale` to the word `sales`. The habit of naming the list in the plural and the loop variable in the singular, `for sale in sales`, `for item in items`, makes the line read like English, and it is the habit of this book.

### What Python does with a `for` loop

Here is exactly what happens when Python reaches line 2 of `each_sale.py`:

1. It looks up `sales` and finds the list of eight items.
2. It takes the first item, 450, and sticks the label `sale` on it.
3. It runs the body, line 3, with `sale` meaning 450: `Sale: 450`.
4. It reaches the end of the body, and goes back up to line 2. Is there another item? Yes, 120. It moves the label `sale` onto 120.
5. It runs the body again: `Sale: 120`.
6. And so on, for 75, 210, 98, 1340, 64, 300. Each run through the body is one **iteration**, or one *pass*.
7. After the pass for 300, it goes back to line 2 and there is no next item. The loop is over. Python goes on to the first line after the body, line 4, and prints `Done`.

So the body ran eight times, and line 4 ran once. The label picture from 1.4 holds well here: there is one label, `sale`, and the loop peels it off one item and sticks it on the next. The list itself is not changed by the loop at all. After the loop, `sale` is still stuck on the last item, 300, and you can use it, though you rarely want to.

### Adding up: the running total

<!-- teaches: running-total = running total, accumulator, += -->
Now the day's total. Save this as `day_loop.py`:

<!-- code: id=day_loop -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
total = 0
for sale in sales:
    total = total + sale
print("Total sales:", total)
```
```text
Total sales: 2657
```

2657, the same as chapter 1, and the same as `SUM` in a spreadsheet. The pattern has three parts, and each is needed:

1. **Before the loop**, `total = 0`: the total of no sales yet, the zero the running column starts from before the first sale.
2. **In the body**, `total = total + sale`: the total so far, plus this sale, becomes the new total. This is the dragged formula `=C2+B3`. You met this kind of line in 1.4, in `late_sale.py`: the right side uses the old value, then the label moves to the new one.
3. **After the loop**, `print`: only when every sale has been added is the total the day's total.

A name used this way, that starts at nothing and gathers something up on every pass, is called a **running total** (programmers also say an *accumulator*). Here is what `sale` and `total` hold each time line 4 finishes, made from a real run of the program:

<!-- trace: id=day_loop watch="sale total" at="4" -->
| Line | Statement | `sale` | `total` |
|---|---|---|---|
| 4 | `total = total + sale` | 450 | 450 |
| 4 | `total = total + sale` | 120 | 570 |
| 4 | `total = total + sale` | 75 | 645 |
| 4 | `total = total + sale` | 210 | 855 |
| 4 | `total = total + sale` | 98 | 953 |
| 4 | `total = total + sale` | 1340 | 2293 |
| 4 | `total = total + sale` | 64 | 2357 |
| 4 | `total = total + sale` | 300 | 2657 |

Read it as the spreadsheet column: each row's `total` is the row above's `total` plus this row's `sale`. The last row is the answer.

**A shorter way to write it.** Adding to a running total is so common that Python has a short form for it: `total += sale` means exactly `total = total + sale`. The same works for the other operators: `count += 1`, `stock -= 3`. This book uses the short form from here on; when you read `+=`, say "add to".

### Counting and the average, in the same loop

A loop can keep more than one running value. The day's report also needs the number of sales and the average. Save this as `day_loop_report.py`:

<!-- code: id=day_loop_report -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
total = 0
count = 0
for sale in sales:
    total += sale
    count += 1
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

This is chapter 1's report, line for line the same output, but the program is different in the way that matters. `count` is not typed in as 8: it starts at 0 and goes up by one on every pass, so it is always exactly the number of items the loop went through. The average is worked out *after* the loop, once, from the finished totals; inside the loop it would be worked out eight times, seven of them too early.

Now see the payoff. The late sale of 150 from 2.4 comes in. Add one line under the list, `sales.append(150)`, and save the result as `day_loop_late.py`:

<!-- code: id=day_loop_late -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
sales.append(150)
total = 0
count = 0
for sale in sales:
    total += sale
    count += 1
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
Total sales: 2807
Number of sales: 9
Average sale: 311.8888888888889
```

Nine sales, a total of 2807, and no other line had to change. (The average now runs to many decimal places, `311.8888888888889`; section 6.4 shows how to round it for a printed report.) The same program would work for a day of 200 sales. That is what the loop bought you.

**Python's own `sum`.** Adding up a list is so common that Python has it built in: `sum(sales)` gives the total in one call. Use it as a cross-check when you like (`print(sum(sales))` should print the same as your loop). The loop is still the thing to learn, because the next section does what `sum` cannot: it looks at each sale and decides what to do with it.

### Seeing the loop work

When a loop gives a total you do not believe, make it show its work: put a `print` *inside* the body. Save this as `day_loop_show.py`:

<!-- code: id=day_loop_show -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
total = 0
for sale in sales:
    total += sale
    print("added", sale, "total now", total)
print("Total sales:", total)
```
```text
added 450 total now 450
added 120 total now 570
added 75 total now 645
added 210 total now 855
added 98 total now 953
added 1340 total now 2293
added 64 total now 2357
added 300 total now 2657
Total sales: 2657
```

The indented `print` runs on every pass, so you get the whole running-total column, row by row, and then the one line after the loop. This is the most useful debugging trick you will learn in this book: a `print` inside a loop shows you what the loop really did, and you take it out again when the program is right.

The same trick is a mistake when you do not mean it. If the line `print("Total sales:", total)` gets indented by accident, it is in the body: you get eight "Total sales" lines, and only the last one is the day's total. Which lines are in the body is decided by indentation alone, exactly as for `if`.

### When it goes wrong

**Starting the total inside the loop.** Save this as `reset_inside.py`:

<!-- code: id=reset_inside -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
for sale in sales:
    total = 0
    total += sale
print("Total sales:", total)
```
```text
Total sales: 300
```

It prints the last sale, 300, and calls it the total. No error. On every pass, line 3 puts the total back to 0, then line 4 adds one sale, so after the last pass the total is just the last sale. The symptom to know: *a total that equals the last item*. The fix is to move `total = 0` above the `for` line, where it runs once.

**Forgetting to start the total at all.** Save this as `no_start.py`:

<!-- code: id=no_start exit=1 -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
for sale in sales:
    total += sale
print("Total sales:", total)
```
```text
Traceback (most recent call last):
  File "/home/you/no_start.py", line 3, in <module>
    total += sale
    ^^^^^
NameError: name 'total' is not defined
```

A `NameError` on the first pass: `total += sale` means `total = total + sale`, and the right side asks for the old value of `total`, which was never made. The traceback says line 3; the cure is `total = 0` before the loop.

**A day with no sales.** The shop was shut on a festival day, so the list is empty. Save this as `empty_day.py`:

<!-- code: id=empty_day exit=1 -->
```python
sales = []
total = 0
count = 0
for sale in sales:
    total += sale
    count += 1
print("Total sales:", total)
average = total / count
print("Average sale:", average)
```
```text
Total sales: 0
Traceback (most recent call last):
  File "/home/you/empty_day.py", line 8, in <module>
    average = total / count
              ~~~~~~^~~~~~~
ZeroDivisionError: division by zero
```

The loop body never ran: there was no first item, so Python went straight past the loop. `total` and `count` stayed 0, and the total line was printed correctly. Then `0 / 0`: a `ZeroDivisionError`, `division by zero`. Nothing is wrong with the loop; an empty list is a real case, and the average of no sales does not exist. Section 2.7 asks you to guard this with an `if`.

**Thinking that changing the loop variable changes the list.** Inside the loop, `sale` is a label on an item. Writing `sale = sale - 10` in the body moves that label to a new value, 10 less; it does not reach back into the list. After the loop, `sales` is exactly as it was. To change the list itself you assign to an index, `sales[2] = 57`, as in 2.4. This book builds new lists instead (2.6), which leaves the original sales untouched; the book keeps the same rule for the sales file itself in chapter 4.

### Keep it

- `for sale in sales:` runs the indented body once for each item, with `sale` stuck on that item, in order; then Python carries on after the body.
- A **running total** starts before the loop (`total = 0`), grows in the body (`total += sale`), and is used after the loop.
- Counting is a running total of ones: `count += 1`.
- A total equal to the last item means the start was inside the loop. An empty list means the body never runs.
- A `print` inside the loop shows every pass; take it out when the program is right.

**Check yourself**

<!-- q: idea=for-loop type=predict wrong="the line after the loop runs on every pass" -->
1. Before running it: how many lines does this print, and what is the last one?

<!-- code: id=loop_lines_predict answer -->
```python
items = ["rice", "soap", "tea"]
for item in items:
    print("Item:", item)
    print("-")
print("3 items")
```

<details>
<summary>Answer</summary>

```text
Item: rice
-
Item: soap
-
Item: tea
-
3 items
```

Seven lines: the two indented lines run three times each, and the last line runs once, after the loop. If you said four, you ran the body once; if you said nine, you put `print("3 items")` inside the body, but it is at the left edge, so it runs after the loop is over.

</details>

<!-- q: idea=running-total type=fix wrong="the total is set up once even when it is inside the body" -->
2. A friend's loop prints `Total sales: 300` for the eight sales. Without seeing the program, name the most likely fault and the fix.

<details>
<summary>Answer</summary>

`total = 0` is inside the loop body, so the total is reset on every pass and only the last sale, 300, survives. Move `total = 0` above the `for` line. A total that equals the last item is the fingerprint of this mistake.

</details>

<!-- q: idea=for-loop type=predict wrong="changing the loop variable changes the list" -->
3. Before running it: what does the last line print?

<!-- code: id=discount_predict answer -->
```python
sales = [450, 120, 75]
for sale in sales:
    sale = sale - 10
print(sales)
```

<details>
<summary>Answer</summary>

```text
[450, 120, 75]
```

The list is unchanged. On each pass `sale = sale - 10` moves the label `sale` to a new number, 440, then 110, then 65, but that never touches the list's items. If you expected `[440, 110, 65]`, you pictured `sale` as the cell itself; it is a label that was stuck on the cell's value.

</details>

<!-- q: idea=running-total type=apply -->
4. Change `day_loop.py` so that it also prints the number of sales of the day, without typing the number 8 anywhere. Which three lines do you add, and where?

<details>
<summary>Answer</summary>

`count = 0` before the loop, next to `total = 0`, and `count += 1` inside the body, indented like `total += sale`. Then `print("Number of sales:", count)` after the loop prints 8. Putting `count = 0` inside the body would give 1, for the same reason the misplaced total gives 300.

</details>

## 2.6 Counting and picking out sales in a loop

The total says how the day went. The shopkeeper's next questions are about particular sales. How many big orders were there today, 300 rupees or more? What did they add up to? And which were they, so that someone can ring those customers to say thank you?

In a spreadsheet you would reach for three tools you already know: `=COUNTIF(B2:B9, ">=300")` for how many, `=SUMIF(B2:B9, ">=300")` for how much, and a filter on column B to see which rows. In Python all three are one loop with an `if` inside it. Before that, one small tool that the loop will lean on.

### How many items: `len`

<!-- teaches: len-function = len, length -->
In 2.5 the loop counted the sales with `count += 1`. Python can tell you the number of items in a list directly: **`len(sales)`** gives its length. Save this as `how_many.py`:

<!-- code: id=how_many -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print(len(sales))
sales.append(150)
print(len(sales))
print(len([]))
print(len("Sharma General Store"))
```
```text
8
9
0
20
```

`len` is called like `print`, with the list between round brackets, and its value is an int: 8, then 9 after the `append`, and 0 for an empty list. It works on strings too, where it counts characters, spaces included; chapter 3 uses that.

`len` asks the list how long it is; it does not go through the items. So for "how many sales today", `len(sales)` is the plain way to say it, and the report's average becomes `total / len(sales)`. The `count += 1` pattern is still the one you need when you count only *some* of the items, which is the rest of this section. The largest index of a list is always `len(sales) - 1`: with 8 items, the last is `sales[7]`. That is the `IndexError` of 2.4 seen from the other side.

### An `if` inside the loop

<!-- teaches: filter-in-loop = filter in a loop, if inside for, picking out, counting matches -->
Save this as `big_orders.py`:

<!-- code: id=big_orders -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
big_count = 0
big_total = 0
big_sales = []
for sale in sales:
    if sale >= 300:
        big_count += 1
        big_total += sale
        big_sales.append(sale)
print("Big orders:", big_count, "of", len(sales))
print("Big order total:", big_total)
print("Big orders:", big_sales)
```
```text
Big orders: 3 of 8
Big order total: 2090
Big orders: [450, 1340, 300]
```

Three big orders out of eight, worth 2090 rupees together: 450, 1340 and 300. Check it against the list by eye: those are the only three of 300 or more, and 450 + 1340 + 300 is 2090.

Look at the shape, because you will write it again and again. The `for` line opens a block; inside it, at four spaces, the `if` line opens a second block; inside *that*, at eight spaces, are the three lines that run only for a big sale. Each level of indentation is one level of "only when". Lines 7 to 9 run only on a pass where the sale is 300 or more; line 6 runs on every pass; lines 10 to 12 run once, after the loop.

The program holds three running values, one for each spreadsheet tool:

| Before the loop | In the `if` block | Spreadsheet |
|---|---|---|
| `big_count = 0` | `big_count += 1` | `COUNTIF` |
| `big_total = 0` | `big_total += sale` | `SUMIF` |
| `big_sales = []` | `big_sales.append(sale)` | a filter on the column |

The third is new. An empty list before the loop, and an `append` for each item that passes the test, builds a new list holding just the items you picked out. This is **picking out** (also called *filtering*) items in a loop. Unlike a spreadsheet filter, which hides rows of the one sheet, this makes a second list and leaves `sales` exactly as it was, so the full day is still there for the next question.

### What happens on each pass

Here is the loop pass by pass. The last three columns show the values *after* the pass.

| Pass | `sale` | `sale >= 300` | `big_count` | `big_total` | `big_sales` |
|---|---|---|---|---|---|
| 1 | 450 | `True` | 1 | 450 | `[450]` |
| 2 | 120 | `False` | 1 | 450 | `[450]` |
| 3 | 75 | `False` | 1 | 450 | `[450]` |
| 4 | 210 | `False` | 1 | 450 | `[450]` |
| 5 | 98 | `False` | 1 | 450 | `[450]` |
| 6 | 1340 | `True` | 2 | 1790 | `[450, 1340]` |
| 7 | 64 | `False` | 2 | 1790 | `[450, 1340]` |
| 8 | 300 | `True` | 3 | 2090 | `[450, 1340, 300]` |

On a `False` pass nothing changes: the `if` block is skipped, the body is over, and Python goes back up to the `for` line for the next sale. On a `True` pass all three values move together. That is why `big_count` and `len(big_sales)` always agree: they are counted by the same test, at the same moment. Once you build the list, you could drop `big_count` and print `len(big_sales)` instead; the counter is shown here because counting without keeping is common too.

### Several cases in one loop

The test inside the loop can be any `if`, including the chain of 2.3. To count the day's sales by size, in one pass, save this as `size_counts.py`:

<!-- code: id=size_counts -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
small = 0
medium = 0
large = 0
for sale in sales:
    if sale >= 1000:
        large += 1
    elif sale >= 100:
        medium += 1
    else:
        small += 1
print("Small:", small)
print("Medium:", medium)
print("Large:", large)
print("Checked:", small + medium + large, "of", len(sales))
```
```text
Small: 3
Medium: 4
Large: 1
Checked: 8 of 8
```

Each sale goes into exactly one of the three counters, because exactly one block of the chain runs on each pass. So the three counts must add up to the number of sales, and the last line checks that they do. It is a small version of checking against the spreadsheet: when a program splits something into parts, check that the parts add back up to the whole.

### Picking out text

The same pattern works on strings, and there it meets the lesson of 2.1. Here are the items sold in the first hour, as the assistant typed them. Save this as `soap_count.py`:

<!-- code: id=soap_count -->
```python
items = ["rice", "soap", "tea", "Soap", "rice", "soap"]
soap_count = 0
for item in items:
    if item == "soap":
        soap_count += 1
print("Soap sold:", soap_count)
```
```text
Soap sold: 2
```

You can see three soaps; Python counts two. `"Soap"` with a capital S is not equal to `"soap"` (2.1), so the fourth item fails the test. The loop is right; the data is untidy. This is exactly the kind of mess the book's real sales sheet has, and making `Soap`, `soap` and `soap ` count as one is the first job of chapter 3.

### When it goes wrong

**The `append` at the wrong depth.** Save this as `big_wrong.py`:

<!-- code: id=big_wrong -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
big_sales = []
for sale in sales:
    if sale >= 300:
        print("Big order found")
    big_sales.append(sale)
print("Big orders:", big_sales)
```
```text
Big order found
Big order found
Big order found
Big orders: [450, 120, 75, 210, 98, 1340, 64, 300]
```

Three "found" messages, so the test works, but every one of the eight sales is in the list. `big_sales.append(sale)` is at four spaces, the depth of the `if` line, so it belongs to the loop, not to the `if`: it runs on every pass. One level of indentation, no error. The symptom is a "picked out" list as long as the original; a quick check is to compare `len(big_sales)` with `len(sales)`.

**Asking a list for `.len()`.** `append` is written after a dot (2.4), so it is natural to try `sales.len()`. Save this as `len_dot.py`:

<!-- code: id=len_dot exit=1 -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
print(sales.len())
```
```text
Traceback (most recent call last):
  File "/home/you/len_dot.py", line 2, in <module>
    print(sales.len())
          ^^^^^^^^^
AttributeError: 'list' object has no attribute 'len'
```

`AttributeError`, and the message says a list has no attribute called `len`: lists have no method of that name. `len` is called the way `print` is, with the list inside the brackets: `len(sales)`. There is no rule you could have guessed this from; it is one of the few things to simply remember.

**The new list made inside the loop.** If `big_sales = []` is put inside the body, the list is emptied on every pass, and at the end it holds at most the last sale. It is the reset mistake of 2.5 again, with a list instead of a number. Anything that gathers across the passes is made *before* the `for` line.

### Keep it

- `len(sales)` is the number of items in a list (0 for `[]`), or of characters in a string. The last index is `len(sales) - 1`.
- An `if` inside a `for` loop does the jobs of `COUNTIF`, `SUMIF` and a filter: `count += 1`, `total += sale`, `picked.append(sale)` in the `if` block.
- Anything that gathers across passes starts before the loop: `0` for counts and totals, `[]` for a list.
- Each indentation level is one more "only when". A line at the wrong depth runs too often or too seldom, with no error.

**Check yourself**

<!-- q: idea=filter-in-loop type=predict wrong="> 300 counts the 300-rupee sale" -->
1. Before running it: in `big_orders.py`, the test is changed to `if sale > 300:`. What are the three output lines now?

<!-- code: id=over_300 answer -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
big_count = 0
big_total = 0
big_sales = []
for sale in sales:
    if sale > 300:
        big_count += 1
        big_total += sale
        big_sales.append(sale)
print("Big orders:", big_count, "of", len(sales))
print("Big order total:", big_total)
print("Big orders:", big_sales)
```

<details>
<summary>Answer</summary>

```text
Big orders: 2 of 8
Big order total: 1790
Big orders: [450, 1340]
```

The 300-rupee sale is not greater than 300, so it drops out: two orders, 1790 rupees. Nothing warns you; the only way to notice is to know what the answer should be. When a rule says "300 or more", write `>=`; when it says "over 300", write `>`, and say which in the report.

</details>

<!-- q: idea=filter-in-loop type=fix wrong="a line in the loop body only runs when the if is true" -->
2. A friend wants the total of the small sales (under 100) and gets 2657, the whole day. Here is the loop. Which line is wrong, and how do you fix it?

<!-- code: id=small_fault mode=fragment -->
```python
small_total = 0
for sale in sales:
    if sale < 100:
        print("small sale:", sale)
    small_total += sale
```

<details>
<summary>Answer</summary>

`small_total += sale` is at the depth of the `if` line, so it is in the loop body but not in the `if` block, and it adds every sale: 2657. Indent it by four more spaces, under the `print`, and the total becomes 75 + 98 + 64 = 237. The `print` lines appearing for only three sales is the clue that the test itself works.

</details>

<!-- q: idea=len-function type=decide -->
3. To print "Number of sales" in the day's report, you could keep `count += 1` in the loop, or use `len(sales)`. To print "Number of big orders", you could keep `big_count += 1` in the `if` block, or use `len(big_sales)`. Which would you choose in each case, and why?

<details>
<summary>Answer</summary>

`len(sales)` for the day: it says what you mean, and needs no extra lines in the loop. For the big orders, if you are building `big_sales` anyway, `len(big_sales)` is simpler and cannot disagree with the list; if you only need the number and not the list, `big_count += 1` saves keeping a list. Either is correct; the point is that `len` measures a list that exists, and a counter is what you use when there is no list to measure.

</details>

<!-- q: idea=filter-in-loop type=apply -->
4. Write a loop that builds `small_sales`, the list of sales under 100, and prints it with its length. What should it print for the day's eight sales?

<details>
<summary>Answer</summary>

<!-- code: id=small_sales -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
small_sales = []
for sale in sales:
    if sale < 100:
        small_sales.append(sale)
print("Small sales:", small_sales, len(small_sales))
```
```text
Small sales: [75, 98, 64] 3
```

`small_sales = []` comes before the loop, the `append` sits inside the `if` block, and the `print` after the loop. The three small sales are 75, 98 and 64, in the order they were made.

</details>

## 2.7 Practice: the day's total, biggest sale and big orders

At the start of this chapter your program could add up eight sales that you had typed one by one, and say nothing about them. Now it can hold a day of any length in one list, go through every sale, keep running totals and counts, ask a yes-or-no question of each sale, and act on the answer. This practice proves it. The guided tasks work on the chapter's own programs; the next three are new problems with no hints; the last is the full day's report for a new day, which you write from a blank file and check against a spreadsheet.

Save every program in `~/shop` under the name the task gives, and run it with `python3`.

### Guided

<!-- q: idea=filter-in-loop type=predict wrong="and is true when either side is true" -->
1. **Predict.** Before running it: what does this program print? Work through the loop pass by pass on paper, writing down `count` and `total` after each pass, the way the table in 2.6 does.

<!-- code: id=medium_predict answer -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
count = 0
total = 0
for sale in sales:
    if sale >= 100 and sale < 500:
        count += 1
        total += sale
print("Medium sales:", count)
print("Medium total:", total)
```

<details>
<summary>Answer</summary>

```text
Medium sales: 4
Medium total: 1080
```

The sales that are at least 100 *and* under 500 are 450, 120, 210 and 300: four of them, adding to 1080. 75, 98 and 64 fail the first half, and 1340 fails the second; `and` needs both halves to be `True`. If you got 8 sales, you read `and` as `or`: every sale is either at least 100 or under 500. If you got 3 and 780, you left out 300, which is under 500. These four are the same sales that `size_counts.py` called medium in 2.6, which is a good cross-check.

</details>

<!-- q: idea=running-total type=apply wrong="a running value is always added to" -->
2. **The biggest sale.** Write `biggest_sale.py`, which prints the biggest of the day's eight sales. A nudge: you need a running value, as for a total, but on each pass you do not add to it. You *replace* it, and only when this sale is bigger than the biggest you have seen so far. Start it at the first sale, `sales[0]`.

<details>
<summary>Answer</summary>

<!-- code: id=biggest_sale -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
biggest = sales[0]
for sale in sales:
    if sale > biggest:
        biggest = sale
print("Biggest sale:", biggest)
```
```text
Biggest sale: 1340
```

The pattern is the running total's, with two changes: the body is an `if` around an assignment, and the assignment replaces the value instead of adding to it. `biggest` starts at 450. It stays 450 for 120, 75, 210 and 98, because none of them is bigger; it becomes 1340 on the sixth pass; and nothing after that is bigger. If you wrote `biggest += sale`, you got 2657, a total; "biggest so far" is kept with `=`, not `+=`.

Python also has this built in, `max(sales)`, as it has `sum` (2.5). Writing it yourself is the point here: the same shape answers questions `max` cannot, such as "the biggest sale under 1000".

</details>

<!-- q: idea=running-total type=fix wrong="0 is a safe starting value for any running value" -->
3. **Find the fault.** A friend copied the biggest-sale program to find the *smallest* sale, changing `>` to `<`. It runs without an error and prints `Smallest sale: 0`. What is wrong, and what is the fix?

<!-- code: id=smallest_fault -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
smallest = 0
for sale in sales:
    if sale < smallest:
        smallest = sale
print("Smallest sale:", smallest)
```
```text
Smallest sale: 0
```

<details>
<summary>Answer</summary>

`smallest` starts at 0, and no sale is smaller than 0, so the `if` is `False` on every pass and the starting value comes out as the answer. 0 is not one of the sales at all. Start it at a real sale, `smallest = sales[0]`, and the program prints 64:

<!-- code: id=smallest_sale -->
```python
sales = [450, 120, 75, 210, 98, 1340, 64, 300]
smallest = sales[0]
for sale in sales:
    if sale < smallest:
        smallest = sale
print("Smallest sale:", smallest)
```
```text
Smallest sale: 64
```

A total starts at 0 because 0 is "the total of nothing". A biggest or smallest starts at the first item because there is no "smallest of nothing". (Starting `biggest` at 0 happens to work while every sale is positive, which is why it is the safer habit to start both at `sales[0]`.) The symptom to remember: *an answer that is not in the list at all* means the starting value won.

</details>

### On your own

<!-- q: idea=filter-in-loop type=apply -->
4. **Returns.** On Tuesday two customers brought things back, and the shop wrote each refund into the day's list as a negative amount: `[450, 120, -120, 210, 98, 1340, -64, 300]`. Write `returns.py`, which prints the number of refunds, the total refunded (as a positive number of rupees), the takings before refunds, and the net total for the day.

<details>
<summary>Answer</summary>

<!-- code: id=returns -->
```python
sales = [450, 120, -120, 210, 98, 1340, -64, 300]
refund_count = 0
refunded = 0
takings = 0
for sale in sales:
    if sale < 0:
        refund_count += 1
        refunded += -sale
    else:
        takings += sale
print("Refunds:", refund_count)
print("Refunded:", refunded)
print("Takings:", takings)
print("Net total:", takings - refunded)
```
```text
Refunds: 2
Refunded: 184
Takings: 2518
Net total: 2334
```

Two refunds, 184 rupees refunded, 2518 taken, a net total of 2334. Check the net: a plain running total of all eight numbers, positives and negatives, gives the same 2334, which is a good cross-check (`sum(sales)` does it in one call). `-sale` turns a negative amount positive: for `-120`, `-sale` is 120. The `else` sends every sale that is not a refund to `takings`, so each sale is counted in exactly one place. A likely slip is `refunded += sale`, which makes the refunded total -184 and the net total 2702, more than was taken: a sign that a minus went the wrong way.
<!-- checked: how=run date=2026-11-18 ref="try: returns.py with refunded += sale -> -184, 2702" h=eee7fc45 -->

</details>

<!-- q: idea=elif-else type=apply wrong="the order of the conditions does not matter" -->
5. **Delivery charges.** The shop has changed its delivery rule: 40 rupees for a bill under 300, 20 rupees from 300 up to 499, free from 500. Today's delivered bills were `[250, 650, 420, 180, 900]`. Write `delivery_day.py`, which prints the charge for each bill and the total collected in delivery charges.

<details>
<summary>Answer</summary>

<!-- code: id=delivery_day -->
```python
bills = [250, 650, 420, 180, 900]
charges_total = 0
for bill in bills:
    if bill < 300:
        charge = 40
    elif bill < 500:
        charge = 20
    else:
        charge = 0
    charges_total += charge
    print("Bill:", bill, "charge:", charge)
print("Delivery charges collected:", charges_total)
```
```text
Bill: 250 charge: 40
Bill: 650 charge: 0
Bill: 420 charge: 20
Bill: 180 charge: 40
Bill: 900 charge: 0
Delivery charges collected: 100
```

40 + 0 + 20 + 40 + 0 = 100 rupees. The chain goes from the smallest threshold up, because its tests are "under": a bill of 250 is caught by `< 300` before it can reach `< 500`. Written the other way round, `bill < 500` first, the 250 bill would be charged 20. The line `charges_total += charge` is at the depth of the `if`, not inside any branch, because every bill adds its charge, whichever branch set it; and since one branch always runs, `charge` always exists by then.

</details>

<!-- q: idea=if-statement type=decide wrong="an empty list makes the loop crash" -->
6. **A day with no sales.** `empty_day.py` in 2.5 crashed with `ZeroDivisionError` on a day when the shop was shut. Change it so that on an empty day it prints `Total sales: 0` and then `No sales today` instead of an average, and on a normal day it prints the average as before. Before you write it, decide: does the `if` go around the loop, or around the average? Why?

<details>
<summary>Answer</summary>

Around the average. The loop is harmless on an empty list: its body simply never runs, and `total` stays 0, which is the right total. Only the division fails, so only the division needs guarding.

<!-- code: id=empty_day_safe -->
```python
sales = []
total = 0
for sale in sales:
    total += sale
print("Total sales:", total)
if len(sales) == 0:
    print("No sales today")
else:
    print("Average sale:", total / len(sales))
```
```text
Total sales: 0
No sales today
```

Put the eight sales back into the list and the same program prints the total and `Average sale: 332.125`. Guarding the whole loop would also work, but it adds a block for no reason; put a test exactly where the danger is.

</details>

### The chapter project: Saturday's report

<!-- q: idea=filter-in-loop type=build -->
7. **Saturday's report.** Saturday was the shop's busiest day of the week. Its twelve sales, in rupees, were: 520, 85, 1200, 40, 315, 99, 260, 75, 610, 300, 150 and 45.

Write `day_report.py` from a blank file. It keeps the twelve sales in one list, `sales`, and goes through them with loops, so that the program would still be right if a thirteenth sale were appended. It prints this report, exactly:

```text
Sharma General Store
--------------------
Total sales: 3699
Number of sales: 12
Average sale: 308.25
Biggest sale: 1200
Smallest sale: 40
Big orders (300 or more): 5
Big order total: 2945
Big orders: [520, 1200, 315, 610, 300]
Target of 2500 reached
```

The last line comes from an `if`: on a day under 2500 it must print `Below target by` followed by the shortfall instead (try it by changing the list).

Done looks like this: the program prints those eleven lines, character for character; no number in it is typed in by you except the sales themselves, the 300 and the 2500; and its total matches the twelve numbers added with `SUM` in a spreadsheet. Then append a thirteenth sale of 500 to the list, run it again, and check that the total, the count, the average and the big orders all change, with no other line touched.

<details>
<summary>Answer</summary>

One version:

<!-- code: id=day_report check="python3 day_report.py" -->
```python
sales = [520, 85, 1200, 40, 315, 99, 260, 75, 610, 300, 150, 45]
target = 2500

total = 0
biggest = sales[0]
smallest = sales[0]
big_total = 0
big_sales = []
for sale in sales:
    total += sale
    if sale > biggest:
        biggest = sale
    if sale < smallest:
        smallest = sale
    if sale >= 300:
        big_total += sale
        big_sales.append(sale)

print("Sharma General Store")
print("-" * 20)
print("Total sales:", total)
print("Number of sales:", len(sales))
print("Average sale:", total / len(sales))
print("Biggest sale:", biggest)
print("Smallest sale:", smallest)
print("Big orders (300 or more):", len(big_sales))
print("Big order total:", big_total)
print("Big orders:", big_sales)
if total >= target:
    print("Target of", target, "reached")
else:
    print("Below target by", target - total)
```
```text
Sharma General Store
--------------------
Total sales: 3699
Number of sales: 12
Average sale: 308.25
Biggest sale: 1200
Smallest sale: 40
Big orders (300 or more): 5
Big order total: 2945
Big orders: [520, 1200, 315, 610, 300]
Target of 2500 reached
```

One loop does all the work: four running values and one picked-out list, each with its own `if`. They are three separate `if` statements, not a chain, because they are three independent questions: a sale can be the biggest so far *and* a big order at once (1200 is both). A chain with `elif` would skip the big-order test whenever a sale was a new biggest, and the big-order total would come out short. Everything that is printed is worked out after the loop, once.

`SUM` of the twelve numbers in a spreadsheet gives 3699, and `=COUNTIF(B2:B13, ">=300")` gives 5, so the report agrees with the sheet. With a thirteenth sale of 500 appended, the total becomes 4199, the count 13, the average 323.0, and 500 joins the big orders, and no other line changes.
<!-- checked: how=run date=2026-11-18 ref="try: day_report sales with 500 appended -> 4199 13 323.0; > 300 gives 4" h=9fde48d8 -->

The likely mistakes, each with its symptom: `smallest = 0` (the report says the smallest sale was 0, which is not a sale); `>` instead of `>=` for big orders (4 big orders, and 300 missing from the list); `print("Target of 2500 reached")` typed in full, which is fine for the check today but wrong the day the target changes; and `big_sales.append(sale)` one level too shallow (a list of all twelve sales).

You can now write, from a blank file, a program that goes through a whole day's sales and answers questions about them. What it cannot yet do is cope with the sales sheet as people really type it: `" 450"`, `"Rs 120"`, `soap` and `Soap`. Chapter 3 builds the tools for that.

</details>
