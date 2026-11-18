## 3.2 A bug report a developer can act on

### Two days on "Checkout broken!!"

Tuesday, 10:40. The release is on Thursday and you are testing checkout on the staging site. You put a rain jacket in the basket, type the discount code you were given for testing, choose card payment and press **Pay**. The spinner on the button starts turning, and keeps turning. You wait a minute, reload, try again: the same spinner. You open the tracker and write, fast, because it matters:

```text
Title:    Checkout broken!!
Severity: Critical

Checkout doesn't work, it just keeps loading forever. I tried several times.
This is really bad, customers won't be able to buy anything! Please fix ASAP!!
```

Wednesday, 15:10, the ticket comes back. Priya, the developer who owns checkout, has written: "Tried checkout on staging with my test account, paid fine, order confirmation shown. Cannot reproduce. Closing." You try again at once. Spinner. You reopen the ticket: "Still broken, I just tried!!" Thursday morning, at the stand-up meeting, the release is on hold, and the team lead asks the two of you to sit at your desk together. Priya watches you do it, and in the second minute she says: "Oh. You're using a discount code. And that jacket is on sale."

That was it. The payment fails only when a discount code is applied to an item that is already reduced. Priya had bought a full-price item with no code, which is what almost everyone does when they test checkout, and that path has always worked. You knew about the code the whole time; you typed it yourself. It did not go into the report because it felt like background, not like part of the problem.

Nobody in this story was careless. The bug took two days because everything that mattered was in your head and the report carried none of it. This section is about the report that carries it: what a developer does with a bug report, what each missing piece costs them, and how to write one they can act on the first time.

### What happens to your report on the other side

A report is not a message that says "something is wrong". It is the starting material for three jobs the developer has to do, in this order.

<!-- teaches: reproduce = reproduce, steps to reproduce -->
**First, reproduce it.** The developer has to make the failure happen in front of them, on their own machine or on staging, before they can do anything else. Until they see it, they cannot look at what the program was doing at that moment, and later they cannot prove that their change fixed it. So the most valuable part of a report is a list of *steps to reproduce*: the actions, from a known starting point, that make the bug appear. Every fact you leave out turns into a guess: which account, which items, which payment method, which build? With five unknowns nobody tries every combination; they try the usual one, and the usual path is the one least likely to be broken, because everybody tests it. That is exactly what Priya did. "Cannot reproduce" rarely means the developer did not try. It nearly always means the report sent them down a different path from yours.

**Second, find where it happens.** A shop like this one is a browser page talking to a server, which talks to a payment service, a discount service and a database. A spinner that never stops could come from any of them. The developer narrows it down with evidence: an error message, a failed request in the browser's network tab, and above all a time. The server writes logs that the developer can read and you usually cannot; "it failed at 10:42 on staging" takes them straight to the lines from that minute. Without a time, they start reading code.

<!-- teaches: severity = severity, priority -->
**Third, judge how bad it is.** Someone has to decide whether this bug stops what the team is doing now, and for that they need to know who is affected, how badly, and whether there is a way round it. Two words get mixed up here. *Severity* is how bad the effect is when the bug happens: lost money, lost data, a blocked task, an ugly screen. *Priority* is how soon the team will fix it, and it is decided by the team, weighing severity against everything else. You set severity honestly from what you saw; you do not set priority by shouting.

Here is a picture for the whole thing. You ring a garage about your car. "It's making a weird noise, it's really bad, please fix it ASAP" gives the mechanic almost nothing. "A grinding noise from the front left wheel when I brake gently below 20 mph, only for the first few minutes after a cold start, since Monday" tells them which part to look at and how to make it happen. Most of a bug report's skill is in that difference.

The picture stops being true in an important place. If the description is poor, the mechanic can still drive the car round the block until it grinds. A developer cannot take your browser, your account, your basket and your Tuesday morning. The report is all of your situation that travels; whatever is not written in it does not exist on the other side. And there is one way the developer is better placed than the mechanic: they can see inside the system (the logs, the database) if you give them the time and place to look.

### The weak report, read as the developer reads it

Look at the first report again, line by line, from Priya's chair.

**"Checkout broken!!"** The title names an area, not a behaviour. Checkout has a basket page, an address form, payment and a confirmation page; "broken" fits dozens of different bugs in it. Priya cannot tell whether this is new or a ticket she already has open, and nobody will find it later by its symptom.

**"Checkout doesn't work, it just keeps loading forever."** Hidden in this line is the one real fact of the report: a spinner that does not stop. But after pressing which button? And "forever" is an interpretation; what you saw was that it was still turning when you gave up. After how long?

**"I tried several times."** Did it fail every time, or some of the times? With the same basket? "Always" and "sometimes" send the developer looking in different places.

**"Customers won't be able to buy anything!"** A claim about scope that you never checked, and it was false: most customers could pay. Worse, it pointed Priya at the most ordinary purchase, which worked, so she concluded the report was wrong.

**Severity: Critical.** Set by how alarming it felt, not by what the bug does. Priya has seen many "Critical" tickets; the word no longer moves her.

And then what is missing entirely: which site and build, which account, what was in the basket, the discount code, what you expected to see, and any evidence. That is the whole content of the bug.

### The same bug, reported so it can be fixed

Before writing again, you spend ten more minutes at the keyboard. The same basket without the code: it works. The code on a full-price hat: it works. The jacket and the code in another browser: it fails. You open the browser's developer tools, press **Pay** once more, and note what the network tab shows. Then you write:

```text
Title:    Payment never completes when a discount code is applied to a sale item
          (staging, build 2.14.0-rc2)
Severity: Major

Where:    staging, build 2.14.0-rc2 (shown in the site footer)
          Chrome on Windows 11; the same happens in Firefox
Account:  tester3 (test account from the team wiki, UK address)

Steps to reproduce
  1. Log in as tester3. Make sure the basket is empty.
  2. Add "Rain jacket, blue, M" to the basket. It is on sale: 80.00 reduced to 60.00.
  3. Go to checkout. Enter discount code SPRING10 and press Apply.
     The total changes to 54.00.
  4. Choose Card and enter the test card from the team wiki.
  5. Press Pay.

Expected
  The "Thank you for your order" page appears and the order is listed
  under My orders.

Actual
  The spinner on the Pay button keeps turning. I waited 2 minutes, then stopped.
  No error message is shown. No order appears under My orders.
  Happened 5 times out of 5 with these steps.

What I checked
  - Same jacket, no discount code: payment completes (3 of 3).
  - SPRING10 on a full-price item (Wool hat, 25.00): payment completes (2 of 2).
  - So it seems to need both a sale item and a discount code.

Evidence
  Network tab, last try: POST /api/checkout/confirm returned 500 at 10:42:13 UTC.
  Screen recording of the last try attached (40 seconds).

Impact
  Any customer who uses a discount code on a sale item cannot pay.
  Workaround: remove the code, which loses them the discount.
```

### Why each change matters

Match these against the diagnosis above. Each change answers one of Priya's three jobs.

**The title states the behaviour and the condition.** It is a sentence about what happens and when. It can be searched, and it already tells Priya the most surprising fact in the report.

**Steps start from a known state.** The empty basket and the named account mean that Priya starts where you started. Every item is named exactly, including the price, because the price turned out to matter. One action per numbered step, so if step 3 looks different on her screen she can say so.

<!-- teaches: expected-actual = expected result, actual result -->
**Expected and actual are both concrete.** The *expected result* is what should have happened, described so precisely that someone could check it: a named page and an order in a list. The *actual result* is what you saw, described as you saw it. "The spinner kept turning; I waited 2 minutes" is an observation. "It loads forever" and "the payment service is down" are interpretations. **Say what you saw, not what you think it means.** A guess can send the developer the wrong way; an observation stays true.

**How often, with numbers.** "5 of 5" tells Priya this will reproduce on her first try. If it had been "2 of 10", she would know to try several times before concluding anything.

**What you checked is the part that saves the most time.** **Narrow it before you send it.** Two more tries told you the bug needs both a sale item and a code. That turns Priya's search from "something in checkout" to "the place where a discount meets a sale price". Ten minutes of your time can save her an afternoon. And "it seems to need both" is honest about what two tries can show; it does not claim to know the cause.

**The evidence gives her a way in.** A 500 status is the server saying that it failed, so she can start on the server side, and the time to the second finds the matching error in its log. You did not need to understand the request; you needed to copy it.

**Severity follows from impact.** A main flow fails for some orders, there is a workaround, and nothing is lost: serious, but not "nobody can buy anything". Written this way, the severity is an argument the reader can check.

### Where the rule bends

**A bug you cannot make happen on demand.** Sometimes the spinner appears on one try in ten and you cannot find what makes the difference. Report it anyway; waiting for perfect steps means nobody looks. But change what the report promises: "intermittent" in the title, the steps you were following, and plainly "about 3 times in 20 tries". Write down the exact time of every failure, because each is a separate way into the logs, and what the failures had in common (always the first try after logging in?). An honest "I could not find the pattern" is useful; steps that claim "always" and then work for the developer cost you their trust.

**A security problem.** Suppose that while testing you change the number at the end of an order page address, from `/orders/1043` to `/orders/1042`, and see another customer's name and address. Do not write the steps in the normal tracker if people outside the team can read it (some projects keep theirs public, or share it with customers): here, steps to reproduce are instructions for an attacker. Find out how your team handles security reports before you need to; usually it is a private ticket or a named person. Stop trying it on real customers' data. The report is written the same way, with steps, expected and actual; only where it goes changes.

**One report or two.** The rule is one report per problem, so that each can be fixed, tested and closed on its own; a ticket called "Checkout issues" with five numbered items never closes, because item 4 is always waiting. But one problem can have two symptoms. If the payment fails *and* no confirmation email arrives, that is one bug: no order exists, so there is nothing to confirm. If the payment fails and the discount field also accepts letters, those are two reports, even though you found them in the same minute. When you cannot tell whether two symptoms share a cause, file two and link them; merging later is easy, untangling is not.

### Three reports that look helpful and are not

**The report that prescribes a fix.** "Title: Increase the payment timeout to 60 seconds." You saw a long spinner, guessed a timeout, and wrote the guess as the task. A developer may do what the title says, and the bug stays, because the real cause was an error on the server; the problem itself was never stated. Describe the problem; if you have a guess about the cause, add it at the end, labelled as a guess: "Possibly related: ...".

**"Expected: it should work."** "Work" has to be turned into something a person could check: which page, which message, what total. Writing it out often uncovers a real question: should SPRING10 apply on top of a sale price at all? If you do not know what should happen, say so and say why you expected what you did: "Expected: either a total of 54.00 and a completed order, or a clear message that the code cannot be used on sale items. I am not sure which is intended." That turns a vague complaint into a question the product owner can answer in one line.

**Severity inflated.** Marking everything Critical feels like making sure it gets done. It has the opposite effect: the team learns that your Critical means "Major", and on the day you find a bug that really does lose customers' money, it waits in the same queue. Your team will have its own scale. A common one: *Critical*, data is lost, money is wrong, a security hole, or nobody can do a main task and there is no workaround; *Major*, a main task fails for some users, or there is a poor workaround; *Minor*, something works wrongly but the task can be done; *Trivial*, cosmetic. Use your team's words, and choose by the effect you saw, not by how close the release is.

### A list to keep

Before you press **Submit**, read your report as the developer will, with none of what is in your head:

1. Does the title say what happens and when, not just where?
2. Could someone start from nothing and follow the steps: account, data, build, exact items?
3. Is the expected result something a person could check?
4. Is the actual result what you saw, not what you think caused it?
5. Did you say how often it happens, with numbers?
6. Did you try one or two variations, and say which made the bug go away?
7. Is there a time, an error message or a recording for the developer to start from?
8. Is the severity argued from the effect, with any workaround named?
9. Is it one problem? Is it safe to post where this tracker can be read?

**Check yourself**

1. Three titles for the same bug. Which one can a developer act on soonest, and what is wrong with each of the other two?
   (a) "Profile page bug - URGENT"
   (b) "Photo upload fails with no message for PNG files over 5 MB"
   (c) "Fix the file size check in the uploader"

<details>
<summary>Answer</summary>

(b). It names the behaviour (fails with no message) and the condition (PNG, over 5 MB), so the developer knows what to try first and can search for duplicates. (a) names only an area and an emotion; "URGENT" is a priority the tester cannot set. (c) prescribes a fix: it guesses that a size check is the cause, and if the real cause is elsewhere, the fix will be done and the bug will stay.

</details>

2. Rewrite this report. Say what you would have to find out first, then write the better version with details you invent.

   "Login doesn't work sometimes. Expected: should log in. Severity: Critical."

<details>
<summary>Answer</summary>

First find out: which build and site, which account, which browser, what exactly happens (an error message? the same page again? a blank page?), how often ("sometimes" as a number), and what is different when it works. One version:

Title: Login returns to the login page with no message, about 1 try in 4 (staging, build 2.14.0-rc2). Severity: Major. Steps: 1. Open the staging login page in Chrome. 2. Log in as tester3 with the wiki password. Expected: the My account page. Actual: the login page shows again, empty, with no error; about 3 of 12 tries; failure times 09:14:05, 09:16:40, 09:21:12 UTC. Checked: the same happens in Firefox; the password is right, because the next try usually works. Impact: users must retry; nobody is locked out.

The reasons: the title says what happens and how often; "sometimes" became a number; each failure has a time for the logs; severity follows from a workaround existing.

</details>

3. One report or two? While testing the profile page you find that (a) uploading a PNG over 5 MB fails with no message, and (b) on a phone-sized screen the Save button overlaps the footer.

<details>
<summary>Answer</summary>

Two. They are different problems, almost certainly in different code, and will probably be fixed by different people at different times. In one ticket, the layout fix would ship and the ticket would stay open, waiting for the upload fix. You may link them as "found together on the profile page".

</details>

4. You notice that a password-reset link still works after it has been used once. The team's tracker is shared with two customer companies. What do you do, and what goes in the shared tracker?

<details>
<summary>Answer</summary>

Treat it as a security problem: a reset link that works twice could let someone else reset the account after the owner did. Report it through the team's security route (a private ticket, the security contact, or the lead), with full steps, expected and actual there. In the shared tracker put nothing that shows how to do it; if your team wants a visible placeholder, a neutral title such as "Account security issue, tracked privately" is enough. If you do not know the route, ask the lead before writing anything down.

</details>
