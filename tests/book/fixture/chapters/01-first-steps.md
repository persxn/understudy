# Chapter 1: First steps

## 1.1 Where C came from

C was made at Bell Labs in the early 1970s, to write the Unix operating system. It sits close to the
machine, so a line of C turns into a few machine instructions. That's why it's still used for
operating systems, small devices and anything that must be fast. You're about to learn the language
that much of the software you use every day is written in, and to see the machine underneath it.

## 1.2 Printing a line

### The question

In §1.1 you saw how a program runs line by line. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own.

### The picture

Think of a row of labelled boxes on a shelf. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. The picture stops being true when a box holds more than one thing.

### The idea

<!-- teaches: printf = printf -->
**`printf`** is the function that prints text on the screen. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want.

<!-- teaches: string-literal = string literal, string literals -->
A **string literal** is text between double quotes, written into the program. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it.

When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### The code

<!-- code: id=1-2-demo -->
```c
#include <stdio.h>

int main(void) {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

Line 4 does the work. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### The trace

| Step | Line | Value |
|---|---|---|
| 1 | 3 | x = 1 |
| 2 | 4 | prints 1 |
| 3 | 5 | returns 0 |

It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### What goes wrong

**Forgetting the semicolon.** Every statement ends with one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic.

**Reading too fast.** Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected.

### Remember

- Take it slowly, and say each step out loud as you read it.
- You've met every piece of this before, so nothing here is magic.
- The computer does exactly what the lines say, one after another, and nothing more.
- When you're unsure, run the program and compare what it prints with what you expected.

**Check yourself**

1. What happens in step 1 of the trace?

<details>
<summary>Answer</summary>

Step 1 runs line 3. Take it slowly, and say each step out loud as you read it.

</details>

2. What happens in step 2 of the trace?

<details>
<summary>Answer</summary>

Step 2 runs line 4. You've met every piece of this before, so nothing here is magic.

</details>

3. What happens in step 3 of the trace?

<details>
<summary>Answer</summary>

Step 3 runs line 5. The computer does exactly what the lines say, one after another, and nothing more.

</details>

## 1.3 Variables

### The question

In §1.2 you saw how a program runs line by line. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own.

### The picture

Think of a row of labelled boxes on a shelf. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. The picture stops being true when a box holds more than one thing.

### The idea

<!-- teaches: variable = variable, variables -->
A **variable** is a named box in memory that holds one value. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want.

<!-- teaches: assignment = assignment -->
An **assignment** puts a new value into a variable's box. When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it.

When you're unsure, run the program and compare what it prints with what you expected. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### The code

<!-- code: id=1-3-demo -->
```c
#include <stdio.h>

int main(void) {
    int x = 2;
    printf("%d\n", x);
    return 0;
}
```

Line 4 does the work. A small change to one line can change the whole result, so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### The trace

| Step | Line | Value |
|---|---|---|
| 1 | 3 | x = 2 |
| 2 | 4 | prints 2 |
| 3 | 5 | returns 0 |

It helps to draw the boxes on paper, with the value written inside each one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more.

### What goes wrong

**Forgetting the semicolon.** Every statement ends with one. Most mistakes at this stage come from reading too fast, not from the idea being hard. Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic.

**Reading too fast.** Keep the example short, and add one thing at a time until it does what you want. Take it slowly, and say each step out loud as you read it. You've met every piece of this before, so nothing here is magic. The computer does exactly what the lines say, one after another, and nothing more. When you're unsure, run the program and compare what it prints with what you expected.

### Remember

- Take it slowly, and say each step out loud as you read it.
- You've met every piece of this before, so nothing here is magic.
- The computer does exactly what the lines say, one after another, and nothing more.
- When you're unsure, run the program and compare what it prints with what you expected.

**Check yourself**

1. What happens in step 1 of the trace?

<details>
<summary>Answer</summary>

Step 1 runs line 3. Take it slowly, and say each step out loud as you read it.

</details>

2. What happens in step 2 of the trace?

<details>
<summary>Answer</summary>

Step 2 runs line 4. You've met every piece of this before, so nothing here is magic.

</details>

3. What happens in step 3 of the trace?

<details>
<summary>Answer</summary>

Step 3 runs line 5. The computer does exactly what the lines say, one after another, and nothing more.

</details>

## 1.4 Practice: first steps

These exercises cover the whole chapter. Try each before you open the answer.

**Exercise 1.** What does `printf("%d\n", 0 + 1);` print?

<details>
<summary>Answer</summary>

It prints 1.

</details>

**Exercise 2.** What does `printf("%d\n", 1 + 2);` print?

<details>
<summary>Answer</summary>

It prints 3.

</details>

**Exercise 3.** What does `printf("%d\n", 2 + 3);` print?

<details>
<summary>Answer</summary>

It prints 5.

</details>

**Exercise 4.** What does `printf("%d\n", 3 + 4);` print?

<details>
<summary>Answer</summary>

It prints 7.

</details>

**Exercise 5.** What does `printf("%d\n", 4 + 5);` print?

<details>
<summary>Answer</summary>

It prints 9.

</details>

**Exercise 6.** What does `printf("%d\n", 5 + 6);` print?

<details>
<summary>Answer</summary>

It prints 11.

</details>

**Exercise 7.** What does `printf("%d\n", 6 + 7);` print?

<details>
<summary>Answer</summary>

It prints 13.

</details>

**Exercise 8.** What does `printf("%d\n", 7 + 8);` print?

<details>
<summary>Answer</summary>

It prints 15.

</details>

**Exercise 9.** What does `printf("%d\n", 8 + 9);` print?

<details>
<summary>Answer</summary>

It prints 17.

</details>

**Exercise 10.** What does `printf("%d\n", 9 + 10);` print?

<details>
<summary>Answer</summary>

It prints 19.

</details>

**Exercise 11.** What does `printf("%d\n", 10 + 11);` print?

<details>
<summary>Answer</summary>

It prints 21.

</details>

**Exercise 12.** What does `printf("%d\n", 11 + 12);` print?

<details>
<summary>Answer</summary>

It prints 23.

</details>

This chapter showed you how to print and how to keep a value in a box. Chapter 2 lets a program choose between two paths.
