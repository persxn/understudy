# 8. Pointers (a short fake chapter)

A pointer is a box that holds an address.

<!-- fig: id=pointer-box-and-arrow
title: p holds 1000, and 1000 leads to x
vars: p=1000@2000 x=5@1000
ptr p -> x
-->

*Figure 8.1: The pointer arrow starts from a dot and ends on the box it names.*

Calling `swap(&x, &y)` hands `swap` two addresses.

<!-- fig: id=swap-frames
frame swap: `swap`'s frame
vars: a=1000@3000 b=1004@3008
frame main: `main`'s frame
vars: x=3@1000 y=7@1004
ptr a -> x
ptr b -> y
-->
![an old reading that must be replaced](fig/swap-frames.svg)

A null pointer leads nowhere.

<!-- fig: id=null-pointer
vars: p=NULL@2000
ptr p -> null -->

That's the end of the fake chapter.
