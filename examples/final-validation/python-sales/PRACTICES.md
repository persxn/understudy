# Python practices worth teaching

Sources read 2026-11-18 as reading material only:
- [Tutorial] The Python Tutorial, docs.python.org/3/tutorial/ (2. Using the Python Interpreter), Python 3.15.2 docs
- [csv] csv module reference, docs.python.org/3/library/csv.html (reader, writer, DictReader, DictWriter, footnotes), Python 3.15.2 docs
- [PEP 8] Style guide, peps.python.org/pep-0008/ (indentation, names) — from knowledge, not re-read
- [general] general knowledge of Ubuntu packaging, not looked up: marked [unchecked]

## Habits

1. Save every program as a file in ~/shop and run it with `python3 name.py`; use the `>>>` prompt only to try one line. From chapter 1. [Tutorial, 2026-11-18]
2. Read an error message from the bottom line up: the last line names the error, the line above it says where. From chapter 1. [Tutorial, 2026-11-18]
3. Indent with four spaces, never tabs. From chapter 2. [PEP 8, 2026-11-18]
4. Names in lower case with underscores, saying what they hold (`day_total`, not `x`). From chapter 1. [PEP 8, 2026-11-18]
5. Open CSV files with `newline=''` for both reading and writing. From chapter 4. [csv, 2026-11-18]
6. Never change the original sales file: read sales.csv, write clean.csv. From chapter 4. [csv, 2026-11-18]
7. Check a program's total against the same total worked out in the spreadsheet before trusting it. From chapter 1.

## Facts that change

- On Ubuntu the command is `python3`; a plain `python` command is not there by default. [Tutorial, 2026-11-18; Ubuntu 24.04 detail [unchecked]]
- Ubuntu 24.04 ships Python 3.12 (package python3 3.12.3) as `python3`; the book's examples run on 3.12 and newer. [Ubuntu packages, packages.ubuntu.com/noble/python3, 2026-11-18]
- Leave the `>>>` prompt with Ctrl-D on Linux, or type `quit()`. [Tutorial, 2026-11-18]
- Python source files are UTF-8 by default, so ₹ and Hindi text can appear in strings without any setting. [Tutorial, 2026-11-18]
- `open()` reads text as UTF-8 by default on these docs' version; a file saved in another encoding needs `encoding=`. [csv, 2026-11-18]
- `csv.reader` gives each row as a list of strings; nothing is turned into numbers for you. [csv, 2026-11-18]
- `csv.DictReader` uses the first row as column names when none are given; since Python 3.8 each row is a plain `dict`. [csv, 2026-11-18]
- A short row in `DictReader` fills the missing columns with `restval` (default `None`); extra cells go into a list under `restkey` (default `None`). [csv, 2026-11-18]
- `csv.writer` ends lines with `\r\n` by default; the reader accepts either ending. [csv, 2026-11-18]

## Handle with care

- `open('sales.csv', 'w')`: opening the original file in write mode empties it at once, before anything is written. The book always writes to a new file, clean.csv. [csv, 2026-11-18]
- Saving a sheet as CSV from a spreadsheet keeps only the active sheet and drops formulas and formatting: keep the original .xlsx/.ods file too.
- `pip install pandas`: a download of tens of megabytes on a capped connection, and not needed for this book; chapter 6.6 only shows what it would look like.
