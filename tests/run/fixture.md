# 9 A chapter for testing us_run.py

Every mode and attribute, in C, Python, bash, JavaScript and console.

<!-- code: id=hello -->
```c
#include <stdio.h>

int main(void) {
    printf("Hello, reader!\n");
    return 0;
}
```

The next program's output fence was typed by hand and is wrong. The script replaces it.

<!-- code: id=stale-output -->
```c
#include <stdio.h>

int main(void) {
    printf("%d\n", 6 * 7);
    return 0;
}
```
```text
41
```

<!-- code: id=add-stdin stdin="3 4\n" -->
```c
#include <stdio.h>

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) return 1;
    printf("%d + %d = %d\n", a, b, a + b);
    return 0;
}
```

<!-- code: id=echo-args args="a b 'c d'" -->
```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        printf("argument %d: %s\n", i, argv[i]);
    }
    return 0;
}
```

<!-- code: id=util-header file=util.h mode=fragment -->
```c
static int twice(int x) {
    return 2 * x;
}
```

<!-- code: id=use-header -->
```c
#include <stdio.h>
#include "util.h"

int main(void) {
    printf("twice 21 is %d\n", twice(21));
    return 0;
}
```

<!-- code: id=show-address -->
```c
#include <stdio.h>

int main(void) {
    int x = 5;
    printf("x is at %p\n", (void *)&x);
    return 0;
}
```

<!-- code: id=unused-in-run -->
```c
#include <stdio.h>

int main(void) {
    int temp;
    printf("done\n");
    return 0;
}
```

<!-- code: id=unused-lesson mode=warns -->
```c
#include <stdio.h>

int main(void) {
    int temp;
    printf("done\n");
    return 0;
}
```

<!-- code: id=not-assignable mode=error -->
```c
int main(void) {
    int a[3] = {1, 2, 3};
    int b[3] = {4, 5, 6};
    a = b;
    return 0;
}
```

<!-- code: id=builds-only mode=compile -->
```c
#include <stdio.h>

int main(void) {
    for (;;) {
        getchar();
    }
}
```

<!-- code: id=forever timeout=1 -->
```c
int main(void) {
    volatile unsigned long n = 0;
    for (;;) {
        n++;
    }
}
```

<!-- code: id=waits-for-input timeout=1 -->
```c
#include <stdio.h>

int main(void) {
    int c;
    while ((c = getchar()) != '\n') {
    }
    return 0;
}
```

<!-- code: id=too-long -->
```c
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 100; i++) {
        printf("line %d\n", i);
    }
    return 0;
}
```

<!-- code: id=exit-three exit=3 -->
```c
#include <stdio.h>

int main(void) {
    printf("leaving with 3\n");
    return 3;
}
```

<!-- code: id=writes-file -->
```c
#include <stdio.h>

int main(void) {
    FILE *f = fopen("notes.txt", "w");
    if (f == NULL) return 1;
    fprintf(f, "kept for later\n");
    fclose(f);
    printf("wrote notes.txt\n");
    return 0;
}
```

<!-- code: id=py-sum stdin="1 2 3\n" -->
```python
numbers = [int(x) for x in input().split()]
print("sum:", sum(numbers))
```

<!-- code: id=py-stderr stderr=show exit=2 -->
```python
import sys
print("to standard output")
print("to standard error", file=sys.stderr)
sys.exit(2)
```

<!-- code: id=bash-loop -->
```bash
for word in one two three; do
    echo "word: $word"
done
```

<!-- code: id=js-hello -->
```javascript
console.log([1, 2, 3].map(x => x * x).join(" "));
```

<!-- code: id=look-around -->
```console
$ cat notes.txt
$ mkdir -p demo
$ echo hello > demo/a.txt
$ ls demo
```

<!-- code: id=clean-up-refused -->
```console
$ rm -rf demo
```

<!-- code: id=clean-up danger="removes only the demo folder this chapter made" -->
```console
$ rm -r demo
$ test -e demo || echo "demo is gone"
```

<!-- code: id=star-trap mode=fragment -->
```c
int *p, q;
```
```text
This fence belongs to the author and is never touched.
```

The end.
