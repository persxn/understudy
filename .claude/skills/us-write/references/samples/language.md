## 8.2 Pointers and what they do

### The question

An address is a number, and you can print one. Could you keep one? In §7.12, R1 held an address, in a register, while the program ran. You'd like the same thing in C: a variable that holds an address, so that you could pass it around, or change it to a different address.

What type would that variable be? `int` is too small, as an address takes 8 bytes (§7.7). And anyway, it'd be good if the variable knew what kind of thing was at that address.

### The picture

Think of a small box with a slip of paper inside it, and on the slip, a house number. The box is an ordinary box, with its own address, sitting in its own place on the street. It holds a number. But that number leads to another place.

We'll picture it as an arrow, drawn from the box to the house it names. Call that the **pointer arrow**. The arrow is what you get in your head when you read the number on the slip. This isn't the control arrow of §1.2, which is the Program Counter, and these two have nothing to do with each other, until function pointers bring them together in §8.11. The picture stops being true in one way: there's no arrow in memory. There's only a number, and the arrow is what that number means to you. Figure 8.2a draws it.

![Two memory boxes side by side. Left, p holding 1000, with "at 2000" under it. Right, x holding 5, with "at 1000" under it. A purple dashed curved arrow leaves a dot inside p's box and ends with an open V head on the edge of x's box. In a corner, a key shows the orange control arrow, solid with a filled head, beside the purple pointer arrow, dashed with an open head, with the words two different things](../diagrams/08/pointer-box-and-arrow.png)

*Figure 8.2a: The pointer arrow. It's dashed and curved, starts from a dot in the box that holds the number, and ends on the box that the number names. From now on, every pointer is drawn this way.*

### The idea

<!-- teaches: pointer-idea = pointer -->
**A pointer is a variable that holds an address.** That's the whole definition. Everything that seems hard about pointers comes from forgetting that a pointer is an ordinary box, with an ordinary number in it.

In the drawing, `p` is a box. It has an address of its own, 2000, and it holds 1000. Holding the address of `x` is called **pointing to `x`**. It's the `R1` of §7.12, kept in a variable.

<!-- teaches: pointer-declare = pointer declaration -->
**Declaring a pointer.** To declare one, you write the type that it will point to, and a star in front of the name.

<!-- code: id=pointer-declare-shape mode=fragment -->
```c
int *p;       // p holds the address of an int
double *q;    // q holds the address of a double
char *c;      // c holds the address of a char
```

Read `int *p` from the name outwards: "`p` is a pointer to `int`". Its type is written `int *`. Spaces don't matter, so `int* p` and `int * p` mean the same, but this book attaches the star to the name, for a reason that comes up in a moment.

To make it point somewhere, store an address in it.

<!-- code: id=pointer-first-assign mode=fragment -->
```c
int x = 5;
int *p;
p = &x;       // p now holds the address of x
```

Or do both at once: `int *p = &x;`. This is initialising `p`, as in `int n = 3;`. It's easy to misread, so say it aloud: "`p` is a pointer to `int`, and `p` starts as `&x`".

**The trap in a declaration.** Each name in a declaration gets its own star.

<!-- code: id=pointer-star-trap mode=fragment -->
```c
int *p, q;     // p is a pointer. q is a plain int!
int *r, *s;    // both are pointers
```

The star belongs to the name and not the type, which is why this book writes it there.

<!-- teaches: percent-p = %p -->
**Printing a pointer.** The specifier for an address is `%p`, which prints it in a form chosen by the system. `printf` wants to be given a `void *` for it, which §8.6 explains, so you cast it.

<!-- code: id=percent-p mode=fragment -->
```c
#include <stdio.h>

int main(void) {
    int x = 5;
    int *p = &x;
    printf("%p\n", (void *)p);
    printf("%p\n", (void *)&x);
    return 0;
}
```

One run on this machine printed this.

```text
000000BBF87FFC54
000000BBF87FFC54
```

That's hex (§5.8), with 16 digits, which is 8 bytes. The two lines match, as `p` holds exactly what `&x` gave. Other systems print a `0x` in front, and may leave out the zeros. A note about this book: since those values change on every run, only a few programs here print them, and the other programs print comparisons and distances.

<!-- teaches: pointer-size = size of a pointer -->
**How big is a pointer?** On this machine, every pointer takes 8 bytes, whatever it points to. §7.7 gave the reason: a pointer holds an address, and an address has a fixed width. A `char *` and a `double *` are the same size, as a house number doesn't get longer for a larger house. That's what `sizeof` measured for the slip of paper in §5.4.

<!-- teaches: null-pointer = NULL, null pointer -->
**A pointer to nothing.** What if a pointer has nothing to point to yet? It needs a special value meaning "no address here". C has one, called **`NULL`**, which comes with `<stdio.h>`. It's written as an ordinary value, and it can be stored in any pointer. In practice, its value is 0, and systems arrange for address 0 never to be a valid place for data.

<!-- code: id=null-shape mode=fragment -->
```c
int *p = NULL;
if (p != NULL) {
    // safe to use what p points to
}
```

`NULL` does the job that -1 did for `find` in §5.6: a signal that means "not found". You'll see functions return it, and you've seen it already: `strstr` returning "false" in §5.15 was `NULL`. It's also the answer to a safety habit: **a pointer that doesn't yet point at something should hold `NULL`.** Then a test can tell you so. §8.10 shows what happens otherwise.

### The code

Here are all the ideas together. It's a program about the boxes themselves. It doesn't yet use what they point to, which is §8.3's job.

<!-- code: id=pointer-boxes -->
```c
#include <stdio.h>

int main(void) {
    int x = 5, y = 7;
    double d = 2.5;
    char c = 'a';
    int *p = &x;
    double *pd = &d;
    char *pc = &c;
    int *nothing = NULL;

    printf("Sizes: %zu %zu %zu\n", sizeof(p), sizeof(pd), sizeof(pc));
    printf("p holds the address of x: %d\n", p == &x);
    x = 99;
    printf("After changing x: %d\n", p == &x);
    p = &y;
    printf("After p = &y: %d %d\n", p == &x, p == &y);
    printf("nothing is NULL: %d\n", nothing == NULL);
    return 0;
}
```
```text
Sizes: 8 8 8
p holds the address of x: 1
After changing x: 1
After p = &y: 0 1
nothing is NULL: 1
```

Pointers can be compared with `==`, as they're numbers. Line 14 is the key. Changing `x` doesn't change `p`, as `p` holds where `x` is, and that doesn't change. Line 16 is the other half: a pointer can be aimed somewhere else, by storing a new address.

### The trace

Suppose that `x` is at 1000, `y` at 1004, and `p` at 2000.

| Line | Statement | `x` | `y` | `p` | `p` points to |
|---|---|---|---|---|---|
| 7 | `int *p = &x;` | 5 | 7 | 1000 | `x` |
| 14 | `x = 99;` | 99 | 7 | 1000 | `x` |
| 16 | `p = &y;` | 99 | 7 | 1004 | `y` |

`p`'s own address, 2000, never changes. A pointer is a box with its own address, like any other.

### What goes wrong

**Thinking a pointer is a special kind of thing.** It's a box holding a number.

**Mixing up the two arrows.** The control arrow is the PC. A pointer arrow is what an address means.

**Writing `int *p, q;` for two pointers.** `q` is an `int`.

**Printing with `%d`.** An address doesn't fit in an `int`. Use `%p`, with a `(void *)` cast.

**Thinking `sizeof(p)` tells you the size of what it points to.** It's the size of the pointer: 8 here.

**Leaving a pointer unset.** Set it to an address or to `NULL` straight away.

**Mixing `NULL` with `'\0'`.** One is an address that means nothing there. The other is a `char` that ends a string (§5.13).

### Remember

- A **pointer** is a variable that holds an address.
- `int *p` reads "`p` is a pointer to `int`", and `p = &x` makes it point to `x`.
- In `int *p, q;`, only `p` is a pointer.
- `%p` prints a pointer, cast to `(void *)`.
- Every pointer takes the same space: 8 bytes on this machine.
- **`NULL`** means "points at nothing".

**Check yourself**

1. Declare a pointer `pm` to a `double` called `mass`, and make it point there.

<details>
<summary>Answer</summary>

`double *pm = &mass;`, or `double *pm;` then `pm = &mass;`.

</details>

2. In `char *a, b, *c;`, which of the three are pointers?

<details>
<summary>Answer</summary>

`a` and `c`. `b` is a plain `char`.

</details>

3. `p` points to `x`, and then `x` changes from 5 to 6. What happens to the value held in `p`?

<details>
<summary>Answer</summary>

Nothing. `p` holds the address of `x`, and that hasn't changed.

</details>

4. Why does a `char *` take 8 bytes here, when a `char` takes 1?

<details>
<summary>Answer</summary>

Its size is the width of an address, not the size of what it leads to.

</details>

