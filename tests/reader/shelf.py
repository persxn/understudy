"""Temporary book shelves for the reading-page tests. Nothing here touches the learner's book/.

    make_shelf()        three books beside a copy of reader/index.html:
                          first-steps-c  the two-chapter fixture (one chapter planned), with an SVG figure
                                         from scripts/us_draw.py, a console block, a text block and a long line
                          learn-c        the owner's 11-chapter C book, if $JOJO_CHAPTERS is set
                          long-read      one generated chapter of about 30,000 words
    make_shelf(books=['ship-it'])  one small book about a terminal tool: blocks marked unrun="why", and
                          terminal and output lines far too long for their boxes
    make_shelf(books=[]) an empty shelf: only index.html
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
JOJO = os.path.dirname(os.environ.get('JOJO_CHAPTERS', '').rstrip('/'))
PY = sys.executable

FIG = '''
<!-- fig: id=pointer-box-and-arrow
title: p holds 1000, and 1000 leads to x
vars: p=1000@2000 x=5@1000
ptr p -> x
-->
![Memory. p holds 1000 at address 2000 and points to x. x holds 5 at address 1000.](fig/01-first-steps/pointer-box-and-arrow.svg)

*Figure 1.2a: The pointer arrow starts from a dot and ends on the box it names.*
'''
EXTRA = '''
```console
$ gcc first.c -o first
$ ./first
1
```

```text
1
```

```c
printf("%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\\n", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16); /* one very long line that must scroll inside its block */
```

A hand trace with many columns:

| Step | Line | a | b | c | d | e | f | g | h | i | j | k | What happened in this step, said in a full sentence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | The first row of a deliberately wide table for the phone |
| 2 | 4 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | The second row |
'''
LONG = 'error from the registry at registry-1.docker.io while it was asked for the list of layers of the image, ' * 2 + 'and at the far right: Forbidden'
SHIP = '''# Chapter 1: Containers

## 1.1 Pulling an image

### The idea

<!-- teaches: image = image -->
An **image** is a program packed with everything it needs to run.

### The code

<!-- code: id=pull unrun="Docker Hub cannot be reached from here." -->
```console
$ docker pull alpine:3.20
```

The command above asks for the image by its name and its tag.

<!-- code: id=ps -->
```console
$ docker ps --all --no-trunc
CONTAINER ID   IMAGE   COMMAND   STATUS
%(long)s
```

<!-- code: id=version -->
```console
$ docker --version
Docker version 29.9.3, build 5f2a1c9 (linux/amd64)
```

<!-- code: id=hello -->
```c
#include <stdio.h>
int main(void) { puts("%(long)s"); return 0; }
```

```text
%(long)s
```

### Remember

- An image is pulled once and kept.

**Check yourself**

1. Which command starts a container from the image?

<details>
<summary>Answer</summary>

<!-- code: id=run unrun="it needs the image, and the image could not be pulled" -->
```console
$ docker run --rm alpine:3.20 echo "%(long)s"
```

</details>

## 1.2 Listing containers

### The idea

<!-- teaches: container = container -->
A **container** is one running copy of an image.

### The code

<!-- code: id=hostile unrun="<img src=x onerror=alert(1)> *star* & `tick`" -->
```console
$ docker ps
```

<!-- code: id=ok -->
```console
$ docker ps --quiet
```

### Remember

- A container is listed until it is removed.
''' % {'long': LONG}
PARA = ('The computer does exactly what the lines say, one after another, and nothing more. When you are unsure, run the '
        'program and compare what it prints with what you expected. A small change to one line can change the whole result, '
        'so read each line on its own. It helps to draw the boxes on paper, with the value written inside each one. ')


def run(*args):
    res = subprocess.run([PY] + list(args), capture_output=True, text=True)
    if res.returncode:
        raise RuntimeError('%s failed:\n%s%s' % (' '.join(args), res.stdout, res.stderr))
    return res.stdout


def long_chapter(words=30000, sections=16):
    """One chapter of about `words` words: every lesson has the seven beats, a program, a trace and hidden answers."""
    per = max(1, words // sections // 8 // len(PARA.split()))
    block = (PARA * per).strip()
    out = ['# Chapter 1: A very long chapter', '']
    for i in range(1, sections + 1):
        out += ['## 1.%d Lesson %d of the long chapter' % (i, i), '']
        for beat in ('The question', 'The picture', 'The idea', 'The code', 'The trace', 'What goes wrong', 'Remember'):
            out += ['### ' + beat, '', block, '']
            if beat == 'The idea':
                out += ['<!-- teaches: idea-%d = idea %d -->' % (i, i), '**Idea %d** is the idea of this lesson. %s' % (i, block), '']
            if beat == 'The code':
                out += ['<!-- code: id=long-%d -->' % i, '```c', '#include <stdio.h>', '', 'int main(void) {', '    int x = %d;' % i,
                        '    printf("%d\\n", x);', '    return 0;', '}', '```', '', '```text', str(i), '```', '', block, '']
            if beat == 'The trace':
                out += ['| Step | Line | Value |', '|---|---|---|', '| 1 | 4 | x = %d |' % i, '| 2 | 5 | prints %d |' % i, '', block, '']
            if beat == 'Remember':
                out += ['- One.', '- Two.', '- Three.', '']
        out += ['**Check yourself**', '']
        for q in range(1, 4):
            out += ['%d. Question %d of lesson %d?' % (q, q, i), '', '   <details>', '   <summary>Answer</summary>', '',
                    '   The hidden answer %d.%d zebra-%d-%d.' % (i, q, i, q), '', '   </details>', '']
    return '\n'.join(out) + '\n'


def make_shelf(books=('first-steps-c', 'learn-c', 'long-read'), index=True):
    shelf = tempfile.mkdtemp(prefix='us-shelf-')
    if index:
        shutil.copy(os.path.join(ROOT, 'reader', 'index.html'), os.path.join(shelf, 'index.html'))
    made = []
    if 'first-steps-c' in books:
        book = os.path.join(shelf, 'first-steps-c')
        shutil.copytree(os.path.join(ROOT, 'tests', 'book', 'fixture'), book)
        figs = os.path.join(book, 'chapters', 'fig', '01-first-steps')
        os.makedirs(figs)
        shutil.copy(os.path.join(ROOT, 'tests', 'draw', 'examples', 'pointer-box-and-arrow.svg'), figs)
        path = os.path.join(book, 'chapters', '01-first-steps.md')
        text = open(path, encoding='utf-8').read()
        head, rest = text.split('### The idea', 1)                       # section 1.2: the figure ends "The picture"
        text = head.rstrip('\n') + '\n' + FIG + '\n### The idea' + rest
        a, b = text.split('### The trace', 1)                            # and the extra blocks end "The code"
        text = a.rstrip('\n') + '\n' + EXTRA + '\n### The trace' + b
        open(path, 'w', encoding='utf-8').write(text)
        made.append(book)
    if 'learn-c' in books and JOJO and os.path.isdir(os.path.join(JOJO, 'chapters')):
        book = os.path.join(shelf, 'learn-c')
        os.makedirs(book)
        shutil.copytree(os.path.join(JOJO, 'chapters'), os.path.join(book, 'chapters'))
        shutil.copytree(os.path.join(JOJO, 'diagrams'), os.path.join(book, 'diagrams'))
        run(os.path.join(ROOT, 'scripts', 'us_plan.py'), 'from-chapters', book, '--title', 'Learn C the Jojo way')
        made.append(book)
    if 'long-read' in books:
        book = os.path.join(shelf, 'long-read')
        os.makedirs(os.path.join(book, 'chapters'))
        open(os.path.join(book, 'chapters', '01-a-very-long-chapter.md'), 'w', encoding='utf-8').write(long_chapter())
        run(os.path.join(ROOT, 'scripts', 'us_plan.py'), 'from-chapters', book, '--title', 'The long read')
        made.append(book)
    if 'ship-it' in books:
        book = os.path.join(shelf, 'ship-it')
        os.makedirs(os.path.join(book, 'chapters'))
        open(os.path.join(book, 'chapters', '01-containers.md'), 'w', encoding='utf-8').write(SHIP)
        run(os.path.join(ROOT, 'scripts', 'us_plan.py'), 'from-chapters', book, '--title', 'Ship it')
        made.append(book)
    for book in made:
        run(os.path.join(ROOT, 'scripts', 'us_index.py'), book)
    return shelf


if __name__ == '__main__':
    print(make_shelf())
