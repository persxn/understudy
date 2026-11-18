# Building an explanation

The guide names the moves (need, intuition, mechanism). This file is how to make each one work.

**Start from a need the reader already feels.** Not "X is important", but a moment: the file that vanished, the query that took nine seconds, the meeting that ended with no decision. If the reader cannot have had the problem yet, build it in two sentences from the running project. An idea that arrives as the answer to a question is remembered; one that arrives as a definition is not.

**Choose the picture by its structure, not its charm.** A good picture has the same *parts and relations* as the idea, so the reader can reason with it. A pointer is a slip with a house number: you can copy the slip or cross it out and the house is unaffected, as with pointers. A "pointer is like a signpost" is pretty but has no slip to copy. Before using a picture, list the three things the reader will do with the idea and check that the picture does them too.

**Say where the picture breaks, at once.** Every picture is false somewhere, and the reader will reason with the false part unless told. One sentence: "where this stops being true: ...". Choose the break that matters for the next sections.

**Then the mechanism, which replaces the picture.** Walk from the picture to the real parts, naming each the moment it acts. By the end the reader thinks in the real terms and uses the picture only to check.

**Introduce terms one at a time, after the thing.** Show the thing, then give its name: "this thin layer on top, that belongs to one container only, is called the *writable layer*." Never two new terms in one sentence. Once named, never change the name (synonyms make the reader think there are two things); `BOOK.md` `Names:` holds the book's choices.

**Weak paragraph.**

> Caching is a technique used to improve performance by storing frequently accessed data in a faster storage layer. There are many types of caches, including CPU caches, browser caches and CDN caches. Caching is important in modern systems.

No reader, five terms, nothing to predict with.

**Better paragraph.**

> The product page took 900 ms, and 850 of them were spent asking the database for the same twelve prices it gave a second ago. So keep the answer: the first request asks the database and writes the prices into memory; the next request finds them there and skips the trip. That memory is a **cache**. Like a sticky note on your monitor with a phone number you keep looking up, it is fast because it is close. Where the note stops being true: when the number changes, the note does not know. Keeping a cache from lying is the hard part, and it is the next section.

A need with a number, the mechanism in order, the term after the thing, a picture with its break.
