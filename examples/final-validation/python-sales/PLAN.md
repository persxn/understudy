# Python for your shop's sales sheet
for: a commerce student at home in spreadsheets (formulas, filters) who has never programmed, and wants to clean and summarise a small shop's sales sheet with Python, on Ubuntu, with nothing extra to install
run: python
kind: language
env: PYTHON_BASIC_REPL=1

## Part I · Write and run small programs

### 1 Running your first program
1.1 Python is already on your laptop | short | teaches: terminal, python-version
1.2 Typing Python one line at a time | teaches: interactive-prompt, expression
1.3 A program is a file you run | teaches: script-file, print-call
1.4 Names for values, like cells that hold numbers | teaches: variable, assignment
1.5 Numbers and text are different things | teaches: int-float, string
1.6 Reading an error message without fear | teaches: traceback, name-error, type-error | level: 2
1.7 Practice: add up one day's sales | practice | level: 3

### 2 Deciding and repeating
2.1 Asking yes-or-no questions | teaches: boolean, comparison
2.2 Doing something only when it is true | teaches: if-statement, indentation
2.3 More than two cases | short | teaches: elif-else
2.4 A list of sales | teaches: list, index
2.5 Going through every sale | teaches: for-loop, running-total | needs: variable
2.6 Counting and picking out sales in a loop | teaches: filter-in-loop, len-function
2.7 Practice: the day's total, biggest sale and big orders | practice | level: 3

### 3 Cleaning text and naming your work
3.1 Tidying text: spaces and capitals | teaches: string-method, strip-method, lower-method | needs: string
3.2 Cutting a line into pieces | teaches: split-method
3.3 Turning text into numbers | teaches: type-conversion, value-error | needs: traceback
3.4 Writing your own function | teaches: def-statement, return-value
3.5 Giving a function its input | teaches: parameter, argument
3.6 Catching a bad value instead of crashing | teaches: try-except | needs: if-statement
3.7 Checking a function with assert | short | teaches: assert-statement
3.8 Practice: a clean_amount function for messy prices | practice | level: 3

## Part II · Clean and summarise the shop's sheet

### 4 Reading your sales sheet
4.1 From spreadsheet to CSV file | teaches: csv-format
4.2 Opening and reading a file | teaches: open-function, with-statement, file-path | needs: for-loop
4.3 Borrowing ready-made tools: import and csv | teaches: import-statement, csv-reader | needs: list
4.4 Columns by name: dictionaries | teaches: dictionary, dict-reader
4.5 When the file is not where you said | short | teaches: file-not-found | needs: try-except
4.6 Practice: print every sale from the shop's file | practice | level: 3

### 5 Cleaning the data
5.1 What dirty data looks like | teaches: data-check | needs: dict-reader
5.2 Blank cells and missing values | teaches: empty-value, skip-row | needs: if-statement
5.3 One item, many spellings | teaches: normalise-text | needs: strip-method, lower-method
5.4 Dates written as text | teaches: datetime-parse, month-key | needs: try-except
5.5 The same sale typed twice | teaches: set-type, duplicate-row
5.6 Writing the clean file | teaches: csv-writer, write-mode | needs: with-statement
5.7 Practice: turn the shop's sheet into clean.csv | practice | level: 3

### 6 Summarising the sales
6.1 Totals by item with a dictionary | teaches: group-total, dict-get | needs: dictionary, running-total
6.2 Totals by month | teaches: group-by-key | needs: month-key
6.3 Sorting the results | teaches: sorted-function, sort-key
6.4 Printing a neat table | teaches: f-string, number-format
6.5 Checking your answer against the spreadsheet | teaches: cross-check | level: 2
6.6 Where pandas comes in | short | teaches: pandas-preview
6.7 Practice: the shop's monthly report | practice | level: 3
