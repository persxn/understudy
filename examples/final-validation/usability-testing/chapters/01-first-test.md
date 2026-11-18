# Chapter 1: Your first usability test: one person, one task

<!-- contents -->
- [1.1 Watching someone fail to pay: what a usability test shows that a review cannot](#11-watching-someone-fail-to-pay-what-a-usability-test-shows-that-a-review-cannot)
- [1.2 The cycle in one picture: plan, prepare, run, analyse, report](#12-the-cycle-in-one-picture-plan-prepare-run-analyse-report)
- [1.3 One question to answer, one task to answer it](#13-one-question-to-answer-one-task-to-answer-it)
- [1.4 Getting a participant and their consent](#14-getting-a-participant-and-their-consent)
- [1.5 Running the session: ask, watch, stay quiet](#15-running-the-session-ask-watch-stay-quiet)
- [1.6 Notes that keep what happened apart from what you think](#16-notes-that-keep-what-happened-apart-from-what-you-think)
- [1.7 From one session to one finding you can show](#17-from-one-session-to-one-finding-you-can-show)
- [1.8 Practice: test one task of your own checkout prototype on one person](#18-practice-test-one-task-of-your-own-checkout-prototype-on-one-person)
<!-- /contents -->

## 1.1 Watching someone fail to pay: what a usability test shows that a review cannot

Thursday afternoon at Thaliwala, a small food-delivery startup. The new checkout has been in Figma for three weeks. Meera, the product manager, has looked at every screen. Kabir, the developer, has walked through it twice to plan the build. You designed it, and you have clicked through it more times than you can count. In the design review everyone agreed: basket, address, delivery slot, payment, done. Four screens, one obvious path. "It's clean," Meera said. "Ship it to Kabir."

Before it goes, you ask Ravi, who works on the support desk downstairs and has never seen the new design, to try it. You open the prototype on your laptop, put a plate of paneer tikka in the basket for him, and say only: "Order this for delivery to your home tonight, and pay for it. Please say out loud what you're thinking."

Ravi checks the basket. Good. He types his address. Good. Then the delivery-slot screen. He reads it, scrolls down, scrolls back up. "Okay, so it's coming... when?" The screen shows a row of time chips, and the first one, "ASAP", is already selected in the brand's orange. Ravi reads the orange as a warning colour, not as "chosen". He taps "ASAP" to choose it. It turns grey, because tapping a selected chip unselects it. Now nothing is selected and the **Continue** button is greyed out. He taps **Continue** three times. Nothing happens. "Is it loading?" He waits. He goes back to the address screen, comes forward again. "ASAP" is orange again. He taps it again. Grey again.

You are sitting on your hands. After more than two minutes on that screen he says, "I'd just call the restaurant, honestly," and puts the laptop down.

Nobody in the review was careless. Three people who knew the design well could not see this, for one plain reason: they already knew what the orange meant. You chose that colour; Meera had heard you explain it; Kabir had read the spec. Knowing a design is exactly what stops you from seeing it the way a newcomer does. A review asks "does this look right to us?" Only a person who does not know the answer, trying to do a real thing with it while you watch, can tell you "this is where people get stuck".

That is a usability test: you give someone who has not seen your design a realistic task, you watch them try it, and you keep quiet long enough to learn where it fails. It took fifteen minutes and one person. It saved Kabir a week of building a screen that would have sent customers to the phone.

This chapter walks you through that whole small test from start to finish: choosing what to ask, asking someone to take part, running the session, writing notes, and turning what you saw into one finding you can show Meera. At the end you will do the same with your own checkout prototype and one person.

## 1.2 The cycle in one picture: plan, prepare, run, analyse, report

### Why Ravi's fifteen minutes worked

Ravi's test looked casual: a laptop, a plate of paneer tikka in a basket, one sentence of instruction. It was not casual. Before Ravi sat down you had decided what you wanted to learn (can a newcomer get from basket to paid order?), set up the prototype so the basket already held something, and chosen words that did not tell him where to tap. While he worked you watched and kept quiet. Afterwards you wrote down what happened, worked out what it meant, and took it to Meera. Every usability test, from fifteen minutes with one colleague to a two-week study with twenty customers, goes through those same five phases. Knowing them is what lets you plan a test in an evening instead of staring at a blank page.

<!-- teaches: test-cycle = test cycle, plan, prepare, run, analyse, report -->
### The five phases

<!-- fig: id=test-cycle
title: The usability test cycle
kind: flow
dir: down
round plan: Plan\nwhat must we learn?
box prep: Prepare\ntask, prototype, person
box run: Run\nwatch, stay quiet
box anal: Analyse\nnotes to findings
round rep: Report\nwhat the team changes
plan -> prep -> run -> anal -> rep
rep ..> plan: next round
hot: run
-->
![Flow chart, top to bottom. Plan what must we learn? leads to Prepare task, prototype, person. Prepare task, prototype, person leads to Run watch, stay quiet. Run watch, stay quiet leads to Analyse notes to findings. Analyse notes to findings leads to Report what the team changes. Report what the team changes leads back to Plan what must we learn? by a dashed arrow (next round). Run watch, stay quiet is highlighted.](fig/01-first-test/test-cycle.svg)

Read the picture from top to bottom. Each phase hands something to the next, and each one can quietly ruin the ones after it.

**Plan: what must we learn?** You start with a question the test must answer, not with a list of screens. For Ravi's test the question was "can someone who has never seen this checkout get from a full basket to a paid order without help?" The question decides everything after it: which task you write, who you ask, what you look for. A test with no question still produces an hour of watching, but nobody can say afterwards whether it went well, because nothing was being asked. Chapter 2 turns a manager's request into proper questions; in this chapter you write one, in section 1.3.

**Prepare: a task, a prototype, a person.** Here you turn the question into something a participant can do. *Participant* is the word for the person who tries your design; you will meet it everywhere. You write the task (the one sentence you said to Ravi), you make sure the prototype starts where the task starts (the basket already full, so he did not have to hunt for paneer tikka on a menu you never designed), and you find someone to take part and ask their permission. Section 1.3 covers the task and section 1.4 the person.

**Run: watch, stay quiet.** The session itself. You read the task, the participant tries it while saying their thoughts aloud, and you watch and write. The hard part is not talking. When Ravi tapped **Continue** three times, every instinct in you wanted to say "it's the orange one". If you had, you would have learned nothing, and the screen would have gone to Kabir broken. Section 1.5 is about this phase.

**Analyse: notes into findings.** Straight after the session you have a page of scribbles. Analysis turns them into a short list of problems you can defend: what happened, where, how bad, and what probably caused it. "Ravi got stuck on the delivery slot" is a note. "The orange highlight on the selected slot reads as a warning, and tapping it deselects it, so participants cannot continue" is the beginning of a finding. Sections 1.6 and 1.7 cover this for one session; chapter 5 does it properly for five.

**Report: what the team changes.** A finding nobody acts on was not worth the session. The report is the smallest thing that makes the team change the design: for one session, often a two-minute conversation with a screenshot; for a full round, a one-page report and a short meeting. The dashed arrow back to Plan in the picture is the point of the whole cycle: you fix the problem, then test again to see whether the fix worked and what the next problem is. Chapter 6 covers reporting in a team.

### A picture, and where it stops being true

Think of the cycle as cooking for guests. You decide what you are making and for whom (plan), buy and chop (prepare), cook while watching the pan (run), taste and decide what is wrong (analyse), and tell the table what you changed (report). Next time you cook it, you start from what you learned.

The picture stops being true in two places, and both matter in a real team.

First, the phases overlap. Analysis starts in the middle of the run: by Ravi's third tap on **Continue** you already had a guess about the orange chip. That is fine, as long as you write the guess separately from what you saw (section 1.6 shows how). With five participants, you will often change a task's wording after the first session because it confused everyone; that is preparation leaking into running, and it is normal.

Second, the loop is not one big circle you go round once a quarter. At a startup the cycle can turn in a day: test on Monday morning, fix the screen in Figma on Monday afternoon, test again on Tuesday. Small and often beats big and rare.

### Walking the cycle on Ravi's test

Here is the whole of Ravi's test laid out phase by phase, with what each phase produced. This is the shape you will copy for your own test at the end of the chapter.

| Phase | What you did | What it produced |
|---|---|---|
| Plan | Asked: can a newcomer get from basket to paid order without help? | One question, written down |
| Prepare | Wrote one task; set the prototype to start with paneer tikka in the basket; asked Ravi, told him it was the design being tested, not him | A task sentence, a prototype at the right starting screen, a willing participant |
| Run | Read the task, asked him to say his thoughts aloud (§1.5), watched until he gave up, said nothing that helped | A page of timed notes |
| Analyse | Read the notes the same afternoon; the slot screen stood out | One problem, with what happened and a guess at why (§1.7) |
| Report | Showed Meera the notes and a screenshot of the slot screen | A decision: change the selected-slot style, test again |

Notice how little each box asks of you. None of it needs a lab, a budget, recording software or a research team. What it needs is the order: a question before the task, the task before the person, quiet during the session, notes before opinions.

### When the cycle goes wrong

Each phase has a way of failing that ruins the ones after it. You will meet each of them again later in the book; for now, learn to recognise them.

**Skipping Plan.** You put the prototype in front of someone and say "have a look and tell me what you think". They give you opinions about the colours. You come away with a list of likes and dislikes and no idea whether anyone can actually pay. Symptom: after the session you cannot say whether it went well.

**Rushing Prepare.** The prototype starts on a home screen you never designed, so the participant spends ten minutes lost in a menu that does not matter, and runs out of patience before reaching checkout. Or the task says "tap Continue on the delivery slot screen", which tells them exactly what to do. Symptom: the session tests something other than what you asked.

**Talking during Run.** You explain, you help, you defend the design. The participant succeeds because you carried them. Symptom: your notes say "completed", and the problem is still in the design.

**Mixing what you saw and what you think in Analyse** (§1.6). Your notes say "confusing slot screen". A week later nobody, including you, can say what actually happened, so the team argues about whether it is really confusing. Symptom: the finding cannot be shown to someone who was not there.

**No Report.** The notes sit in your laptop. Symptom: the next test finds the same problem.

### Keep it

A usability test has five phases in a fixed order: plan (the question), prepare (task, prototype, participant), run (watch and stay quiet), analyse (notes into findings), report (what the team changes), and then the loop starts again. Each phase hands something concrete to the next. A weak phase shows up later as a session that taught you nothing.

**Check yourself**

1. A classmate says: "I tested my app with three friends yesterday. They liked it, but I don't really know what I learned." Which phase did they most likely skip, and what would they have written down before the sessions if they had not?

<details>
<summary>Answer</summary>

Plan. Without a question, nothing in the sessions can count as an answer, so "they liked it" is all that is left. Before the sessions they should have written one question the test must answer, such as "can someone who has never seen the app book a table for four on Saturday without help?". The tempting wrong answer is "they did not write good tasks"; that may also be true, but you cannot write a good task until you know what it is meant to find out.

</details>

2. Put these in the order they happen in a test, and name the phase of each: (a) you show Meera a screenshot of the slot screen; (b) you put paneer tikka in the prototype's basket; (c) you decide to find out whether newcomers can pay unaided; (d) Ravi taps **Continue** three times; (e) you notice in your notes that the slot screen took him 2 minutes 20 seconds.

<details>
<summary>Answer</summary>

(c) Plan, (b) Prepare, (d) Run, (e) Analyse, (a) Report. If you put (e) during the run, that is not wrong in practice, because analysis starts in your head while you watch; but what you write down during the session is the observation, and the reading of it comes after.

</details>

3. Your team wants to test the new checkout "properly, with ten customers, next month". You have a prototype today. Using the cycle, argue for a different plan in two sentences.

<details>
<summary>Answer</summary>

One version: "Let's test it with one or two people this week, fix what they find, and test again next week; each turn of the cycle is cheap, and the big problems usually show up with the first few people. By next month we will have fixed several problems that ten customers would otherwise all have hit on the same screen." The idea is that the loop is meant to turn often; one large round finds the same obvious problem many times and has no fix-and-retest in it. How many people a round needs is chapter 2's subject (section 2.4).

</details>

## 1.3 One question to answer, one task to answer it

### The blank page

You have a prototype and someone who has agreed to give you twenty minutes. Now what do you ask them to do? Most first tests fail right here, before anyone has touched the prototype, because the designer opens the file and says "so, have a look around". This section gives you the two sentences that replace that: one question for you, one task for them.

<!-- teaches: test-question = test question -->
### The question is for you

A *test question* is the one thing you want to know when the session is over, written as a question that the session can answer with what you see. It is never shown to the participant. It is for you, so that you know what to watch and so that, afterwards, you can say whether you got an answer.

A test question has three parts:

1. **Who**: what kind of person. "Someone who has never seen this checkout" is enough for a first test.
2. **Can do what**: a goal a real user has, in their words, from a starting point to an end point. "Get from a full basket to a paid order."
3. **Under what condition**: the thing you are unsure about. "Without help", "on the first try", "and choose a later delivery time".

Put together: *"Can someone who has never seen this checkout get from a full basket to a paid order, without help?"* That is the question you had before Ravi sat down.

Why so narrow? Because one session with one person can answer only a little. Twenty minutes is time for one goal tried properly, with room to watch the person get stuck and recover. If your question is "is the checkout good?", nothing in twenty minutes can answer it, and you will come out with impressions. If it is "can a newcomer pay unaided?", Ravi's session gave you a clear answer: no, and here is the screen where it fails.

Think of it as the question a doctor has before ordering a test. "Is the patient healthy?" is not something one blood test can answer. "Is their iron low?" is. The blood test is chosen for the question. The picture stops being true in one helpful way: a doctor's blood test shows only what it was built to measure, but a usability session shows you everything the person does. You will notice problems you were not asking about, and you should write them down. The question still decides what the session is built around.

### The weak question and a better one

Here are three first attempts at a test question for Thaliwala's checkout, and what is wrong with each.

**Weak: "Do users like the new checkout?"** Liking is an opinion, and opinions from one person, asked to their face by the person who designed it, are nearly worthless: people are polite. And a checkout people like but cannot finish is a failure.

**Weak: "Is the delivery slot screen confusing?"** This one is closer, but it already contains your guess (you think the slot screen is confusing), so you will watch that screen hard and miss the address form. And "confusing" cannot be seen; only what people do can be seen.

**Weak: "Test the checkout flow."** That is a job title, not a question. There is nothing to answer.

**Better: "Can someone who has never seen this checkout get from a full basket to a paid order, without help?"** Each part is visible in a session. You can see who they are, you can see whether they reach "Order placed", and you can see whether you had to help. When the session ends you write "yes", "no" or "yes, but" and then the evidence.

<!-- teaches: first-task = task, task wording, end point -->
### The task is for them

The *task* is the sentence you read to the participant: what you would like them to do, in words that give them a goal but not the route. It is your test question, turned round to face the participant and dressed in a situation they can picture.

Ravi's task was: *"Order this for delivery to your home tonight, and pay for it."* Look at what it does:

- It gives a **goal** a real customer has: get this food delivered and paid for.
- It has a clear **end point**: paid. Ravi knows when he is done, and so do you.
- It **names nothing on the screen**. No "Continue", no "delivery slot", no "ASAP". He has to find his way, which is exactly what you want to see.
- It is **one sentence**, said once, and you can repeat it word for word if he asks.

Now the weak versions you might have written, and what each would have cost you:

> Weak: "Go through the checkout and tell me what you think."

There is no goal and no end point. Ravi would comment on each screen ("nice colours") and you would never see whether he could finish. "Tell me what you think" invites opinions, which is the wrong kind of talk; section 1.5 shows the right kind.

> Weak: "Tap Continue, choose a delivery slot, then go to payment and pay with UPI."

This gives away the route. Ravi would have read the words "delivery slot", looked for a slot, and maybe tapped a chip without thinking about what the orange meant. You would have tested whether he can follow instructions. The slot problem might never have shown up.

> Weak: "Imagine you are a 34-year-old software engineer in Bengaluru who works late and wants dinner. You open the app, you have already chosen paneer tikka, and you want it delivered by 9 pm to your flat in Koramangala. Please complete your order."

This has a goal, but it buries it in a story Ravi has to remember, about a person he is not. Half his attention goes to remembering "9 pm" and "Koramangala". Real stories are useful when the detail matters for the test; that is section 3.2's subject. For a first task, the shortest sentence that gives a goal and an end point is the best one.

> Better: "Order this for delivery to your home tonight, and pay for it."

### When the task must mention something

Sometimes you cannot avoid a word that also appears on the screen. Thaliwala's payment screen says "Pay", and the task says "pay for it". That is fine: "pay" is how any customer would describe the goal. The rule is about the route, not every word: do not name the button, label or screen they must find in order to succeed. If your task uses a word only because you see it on your design ("go to Delivery Options"), change it to the word a customer would use for what they want ("choose when it arrives"). Section 3.3 goes further into words that lead the participant without your meaning to.

### Set the prototype to match the task

The task starts somewhere, and the prototype must start there too. Ravi's task begins with food already chosen ("order *this*"), so you opened the Figma prototype at the basket screen with paneer tikka in it. If the prototype had opened on a home screen with a menu you never designed, Ravi would have spent his first five minutes on screens that are not being tested.

In Figma, a prototype plays from a *flow starting point*: a frame you mark in the Prototype tab of the right sidebar (Figma also adds one by itself when you first connect two frames). A file can have several flows, and a viewer can pick another flow from the prototype's sidebar, so make sure the flow you open starts on the basket. Check this before every session: open the prototype link yourself, see which screen appears first, and click through the task once to make sure every link you need is wired up. A dead link in the middle of a task looks to the participant exactly like a design problem, and you will not be able to tell the two apart afterwards.

### When it goes wrong

**The question has two goals.** "Can a newcomer pay, and do they understand the delivery fee?" With one session, you will watch one closely and miss the other. Pick the one that matters most; the other goes in the next session.

**The task leaks the answer.** Read your task aloud and underline every word that also appears on the screen. Each underlined word must be one a customer would use anyway.

**The task has no end point.** "Look at the payment options." When are they done? They will look, then turn to you and wait, and you will have to say "is that it?", which tells them something was missing. Every task needs a moment when the participant knows they have finished.

**The prototype cannot do the task.** If your task says "pay" but the payment screen is not linked, the session stops halfway. Click through the task yourself the morning of the test.

### Keep it

Write a test question for yourself (who, can do what, under what condition), then turn it into one task sentence for the participant: a goal, an end point, no names of things on the screen. Start the prototype where the task starts, and click through the task once before anyone else does.

**Check yourself**

1. Which of these is a test question a single session can answer, and what is wrong with the other two? (a) "Is our checkout better than the app people already use?" (b) "Can someone who has never seen our checkout change the delivery address to their office and still pay, without help?" (c) "Do people find the address screen intuitive?"

<details>
<summary>Answer</summary>

(b). It names who, a goal with a start and end, and a condition, and each part can be seen in a session. (a) needs a comparison with another product and many people, and "better" is an opinion; it is not something one session shows. (c) asks for a feeling ("intuitive") and contains your guess that the address screen is the issue. The tempting choice is (c) because it sounds focused; turn it into what you could see: "can they enter a new address without help?"

</details>

2. Rewrite this task so that it gives a goal and an end point without naming anything on the screen: "Click 'Schedule for later' and choose the 8 pm slot, then tap Continue."

<details>
<summary>Answer</summary>

One version: "You'd like this delivered at 8 tonight, not right now. Get the order to the point where it's paid." It keeps the real goal (a later time, 8 pm), which a customer would say in those words, but drops "Schedule for later", "slot" and "Continue", which are the route. The end point is "paid". If you wrote "arrange for it to arrive at 8 pm", that is good too; check that it still has an end point.

</details>

3. Your prototype opens on Thaliwala's home screen. Your task is "Order this for delivery to your home tonight, and pay for it." What do you change before the session, and why?

<details>
<summary>Answer</summary>

Set the prototype's starting frame to the basket screen with the item already in it (or open the link at that frame), because the task starts with food chosen. Otherwise the participant spends time on screens the test is not about, and "order this" makes no sense when no "this" is on screen. Then click through the whole task once yourself to check every link works.

</details>

## 1.4 Getting a participant and their consent

For a first test you need one person who has not seen your design and who roughly matches the people who will use it. For a food-delivery checkout that is almost anyone who orders food on their phone. Ravi was a fair choice: he orders dinner on apps, and he had never seen the new screens. Your designer friend who sat through your critique is not: they know what the orange means. Choosing participants properly, and how many, is chapter 2's subject (section 2.4); for now, "has not seen it, and could plausibly be a customer" is enough.

<!-- teaches: participant-consent = consent, informed consent, participant -->
### Asking, and what consent means here

*Consent* means the person agrees to take part knowing what will happen, and knowing they can stop. It is not a formality. People who feel watched and judged behave differently, so telling them clearly what is going on also makes your test better.

Here is a weak way to ask, then a better one.

> Weak: "Hey, can you just check something for me real quick?"

Ravi does not know what he is agreeing to, how long it takes, or that he is about to be watched struggling. If it goes badly, he may feel tricked.

> Better: "I'm testing a new checkout design and I'd like to watch someone try it. It takes about fifteen minutes. You'll try to place an order on my laptop and think out loud while you do it. It's the design I'm testing, not you: if something is hard, that's the design's fault and exactly what I need to find. I'll take written notes but won't record anything, and I won't use your name. You can stop at any point. Is that okay?"

Each sentence does a job: what it is, how long, what they will do, that it is not a test of them, what you will keep, and that they can stop. Say "we are testing the design, not you" again when they sit down. It is the single most useful sentence in a session.

### What changes if you record

The better version says "I won't record anything". If you do want to record the screen or their voice, ask for that separately and specifically, before you start, and say who will see it and when you will delete it. Never record first and ask later. Recording, and what you may keep and quote, is covered in section 4.6. Rules on recording and keeping data about people differ between countries and between companies, so at work, ask what your company's policy is before you record anyone; this book teaches the practice, not the law.

### One mistake

Testing a company's design on a friend outside the company. At your internship the checkout prototype may be confidential. Before you ask anyone outside the team to try it, ask your manager whether you may. For practice, use your own prototype, which is yours to show.

**Check yourself**

1. A classmate asks a participant: "Can you try my app? I really need good feedback for my grade." What two things are wrong with this request, and how would you rephrase it?

<details>
<summary>Answer</summary>

It puts pressure on the participant to be kind ("I really need good feedback"), so they will hide problems; and it does not say what will happen, how long it takes, or that they can stop. Better: "I'm testing an app design and would like to watch you try one task on it, about fifteen minutes, saying your thoughts out loud as you go (§1.5). It's the design I'm testing, not you; if something's hard, that's useful to me. I'll take notes but won't record or use your name, and you can stop any time. Is that okay?"

</details>

2. Halfway through, the participant says "sorry, I'm wasting your time, I'm bad with apps." What do you say?

<details>
<summary>Answer</summary>

Something like: "You're not wasting it at all. This is exactly what I need to see: if it's hard, that's the design's problem, not yours." Then go back to quiet. Do not help with the task to make them feel better; reassure the person, not their progress.

</details>

## 1.5 Running the session: ask, watch, stay quiet

### The fifteen minutes that decide everything

You have a question, a task, a prototype that opens on the basket and a person who has agreed. Now they are sitting next to you. What do you actually say, and what do you do with your hands for fifteen minutes? This section is the session itself, minute by minute, and the two skills it rests on: getting the participant to talk, and getting yourself not to.

<!-- teaches: think-aloud = think aloud, thinking aloud -->
### Asking them to think aloud

You cannot see inside Ravi's head. You can see him tap "ASAP" twice; you cannot see that he read the orange as "warning". What turns a tap into an explanation is *thinking aloud*: the participant says what they are looking at, looking for, expecting and deciding, as they do it. Without it you see what went wrong; with it you see why.

People do not do this naturally. Asked to "think aloud", most go quiet after a minute, or start giving you their opinions ("I don't like this font") instead of their thoughts ("I'm looking for where to put my flat number"). So you ask once, clearly, with an example, and you remind them gently when they go quiet.

> Weak: "Tell me what you think of it as you go."

This invites opinions about the design. You will get "nice colours", which helps nobody.

> Better: "While you do this, please say out loud whatever's going through your head: what you're looking at, what you're trying to do, what you expect to happen. For example, if you were buying a train ticket you might say 'okay, I'm looking for the date... is this it? I'll tap here and see.' There are no right answers. And it's the design I'm testing, not you."

The example matters more than the instruction. It shows the kind of talk you want: plain, running, about the task, not a review.

Here is a picture for it. Thinking aloud is like a sports commentator who is also the player: "Going left now, looking for the pass, nothing there, back to the middle." The picture breaks in one important place: a commentator explains for an audience, and you do not want the participant explaining for you. If Ravi starts saying "I think most users would find this confusing", he has stopped being a customer and started being a reviewer. Bring him back to himself (below).

<!-- teaches: moderator-silence = moderator, staying quiet -->
### Staying quiet

You are the *moderator*: the person who runs the session. Your job during the task has one rule that is harder than it sounds: **do not help, and do not explain**. Every word from you changes what the participant does, and then you are no longer watching the design work on its own, which is what it will have to do on a customer's phone at 9 pm.

Think of yourself as a quiet host. You make the guest comfortable, show them to their seat, and then you hand them the work and get out of the way. Where the picture stops being true: a good host jumps in when a guest is struggling. You do not, at least not for a while. You let the struggle happen, because the struggle is the data.

Why it is so hard: watching someone fail at your design is uncomfortable. You designed it; their trouble feels like your mistake, and the urge to say "oh, it's just there" is strong. Some things that help:

- Sit slightly behind and to the side, so they look at the screen, not at you.
- Have your notes open and write. Writing gives your hands and eyes something to do.
- Count to ten in your head before saying anything at all.
- Keep your face neutral. A wince when they tap the wrong chip tells them they are wrong.

### What you may say

Staying quiet does not mean silence. There are three kinds of thing you say during a task, and none of them helps with the task.

**A reminder to keep talking**, when they have gone quiet for a while: "What are you thinking now?" or just "What's going on here?" Not "Are you stuck?", which suggests they should be doing better.

**An answer to their question, with a question.** Ravi asked, "Is it loading?" The helpful answer, "No, you deselected it", would end your test. Instead: "What do you think is happening?" He said, "I think it's waiting for something... maybe I need to pick a time?" That sentence was worth the whole session: it shows he had worked out a time was needed but could not see that one was selected and then unselected. Turning a question back to the participant is taught fully in section 4.2.

**Reassurance about themselves, never about the task.** "You're doing fine, this is really useful" is reassurance about the person. "You're nearly there" is a hint about the task.

### The session, minute by minute

Here is Ravi's session laid out (it used about eight of the fifteen minutes you asked for), so you can see where each piece goes.

| Time | You | Ravi |
|---|---|---|
| 0:00 | Thank him; repeat that it's the design being tested, not him; remind him he can stop | Sits down |
| 0:30 | Ask him to think aloud, with the train-ticket example | "Okay." |
| 1:00 | Read the task once, word for word: "Order this for delivery to your home tonight, and pay for it." Then stop talking | Looks at the basket |
| 1:00 to 5:10 | Watch, write, stay quiet; say "What are you thinking?" once when he goes silent; answer "Is it loading?" with "What do you think is happening?" | Basket, address, slot screen, stuck, back, forward, gives up at 5:10 |
| 5:30 | "Thanks, that was really helpful. Before we finish, what did you expect to happen on that screen with the times?" | "I thought orange meant something was wrong." |
| 7:00 | "Is there anything else you'd want to tell me?" Thank him again | A comment about the delivery fee |

Three moments in this table deserve a closer look.

**Reading the task word for word.** You say exactly the sentence you wrote, once. If you paraphrase on the spot, you may slip in the route ("order this and choose a delivery time..."). Write it on a card and read it from the card, or put it on a piece of paper next to the laptop so the participant can look at it again.

**Letting him give up.** At 5:10 (4:10 into the task), Ravi said he would call the restaurant. That is a real result: "did not complete". You do not rescue it with "try tapping the orange one". If you need him to reach the payment screen for a second task, you can help him past the stuck point *after* you have written down that he could not do it alone, and you note that you helped. With one task, you just stop.

**Asking afterwards.** Once the task is over, you may ask questions you could not ask during it: "What did you expect on that screen?" Now his answer cannot change what he did, because it is already done. This is where "orange meant something was wrong" came from. Ask about what you saw, using his words, not yours: "that screen with the times", not "the delivery slot selector".

### When it goes wrong

**You helped and did not notice.** Read your notes after the session and look for your own words. "I said: try the top one" in the middle of the task means the task result is not "completed alone". Mark it as assisted. Next time, count to ten.

**The participant asks you to show them.** "Just tell me where it is." Say: "I'd like to see what you'd do if I weren't here. If you'd give up at this point in real life, that's fine to tell me." This lets them stop without feeling they failed.

**Thinking aloud turns into a review.** "The UX here isn't great, users would..." Bring them back: "What are you trying to do right now?" They return to the task.

**The prototype breaks.** A link is missing and the screen does nothing. This looks just like a design problem. If you know it is the prototype, say so: "Sorry, that part of the prototype isn't built; let me move you on." Then note it as a prototype fault, not a finding. Section 4.4 covers more ways sessions go wrong.

### Keep it

Ask the participant to think aloud with an example; read the task word for word, once; then watch and write, and do not help. You may remind them to talk, turn their questions back to them, and reassure them about themselves. If they give up, that is a result. Ask your "why" questions after the task, about what you saw.

**Check yourself**

1. During the task a participant says, "Should I press this green button?" Write what you say, and explain why the obvious answer is wrong.

<details>
<summary>Answer</summary>

"What do you think will happen if you press it?" or "What would you do if I weren't here?" The obvious answer ("yes") tells them the route, so you learn nothing about whether the design makes that button clear on its own. If it does not, a customer at home has no one to ask, and your test should show that.

</details>

2. Find the two moderator mistakes in this transcript. Moderator: "Okay, so go through it and let me know what you think." Participant (on the slot screen, quiet for 20 seconds). Moderator: "Are you stuck? It's the orange one."

<details>
<summary>Answer</summary>

First, the instruction invites opinions ("let me know what you think") and gives no task with an end point. Second, the moderator gives the answer ("it's the orange one"), so the slot problem is hidden. "Are you stuck?" also suggests the participant is failing. Better after the silence: "What are you thinking now?" and then wait.

</details>

3. Ravi gives up on the slot screen at 5:10. You also wanted to see whether he could use the UPI payment screen. What do you do, and what do you write down?

<details>
<summary>Answer</summary>

First write down that he did not complete the slot step on his own, with the time. Then you may help him past it ("Let me move you on to the next screen"), write that you helped, and watch the payment screen. Anything you learn about payment is still valid; what you must not do is record the whole task as "completed".

</details>

## 1.6 Notes that keep what happened apart from what you think

### The note that started an argument

After Ravi's session you write in your notebook: "Slot screen confusing. Users don't get the chips." You show Meera. She frowns. "Confusing how? Ravi's not a typical user, he's from support. And he chose the slot in the end, didn't he?" He had not. But your note does not say what he did, so you cannot show her. Now it is your opinion against hers, and she is the product manager.

The session was good. The note threw it away. This section is about writing notes that survive a sceptical reader: notes that keep what you saw apart from what you think it means.

<!-- teaches: observation-note = observation, interpretation, timestamped note -->
### Two kinds of sentence

Every sentence you write during a session is one of two kinds.

An *observation* is something you saw or heard, that anyone else in the room would also have seen or heard. "Tapped 'ASAP'; it turned grey." "Said: 'Is it loading?'" "Tapped Continue three times; nothing happened." Two people watching would write the same thing.

An *interpretation* is what you think it means. "He didn't understand the selected state." "The orange looks like an error." "Confusing." Interpretations are useful, and you will need them to find causes, but two people watching can disagree about them.

The skill is to write both, and never mix them up. Keep observations as the main record, and mark your interpretations clearly as yours.

A picture: a cricket scorer and a commentator. The scorer writes "over 14, ball 3: edged, caught at slip". The commentator says "he was tempted by the wide one, poor shot". The scorecard can be checked by anyone who was at the ground; the commentary is one person's view. You need both, but if you lose the scorecard you cannot argue about the commentary. Where the picture stops being true: in a session you are both people at once, so you must change hats on purpose, with a mark on the page.

### What a good note line holds

Each observation line has three parts:

1. **When**: a time from the start of the task (or the clock time). Times let you see where people spent long, and find the moment again if you record later.
2. **Where**: the screen or element.
3. **What**: the action or the words, as close to exact as you can. Quotes in quotation marks.

Interpretations go on their own line, starting with a mark that shows they are yours. Many people use "I:" or put them in square brackets.

### The weak notes and the better notes

Here are your first notes from Ravi's session:

```text
Basket fine.
Address ok, bit slow.
Slot screen confusing!! Didn't get chips.
Gave up. Said he'd call restaurant.
Thinks orange = error?
Fee annoying.
```

Read them as Meera would. "Fine", "ok", "confusing", "annoying" are all interpretations. "Bit slow": how slow, and was that a problem? "Didn't get chips": what did he do? "Thinks orange = error?" is a guess, and it is not clear whether he said it or you thought it. Only "Gave up. Said he'd call restaurant." is an observation, and even that has no time and no exact words.

Here are the same notes, rewritten from memory the same afternoon, the way you will write them during the session from now on:

```text
Thaliwala checkout, session 1, support-desk colleague, 18 Nov, 15:05
Task: "Order this for delivery to your home tonight, and pay for it."

0:10  Basket   Reads items aloud. Taps "Checkout".
0:40  Address  Types address. Stops at "Landmark" field: "Do I need this?" Leaves it empty. Taps Continue.
1:50  Slot     Reads screen. Scrolls down, then up. "Okay, so it's coming... when?"
2:20  Slot     Taps "ASAP" (was orange). It turns grey. Continue button greys out.
2:30  Slot     Taps Continue x3. Nothing happens. "Is it loading?"
      [I: thinks ASAP was not yet chosen; orange might not read as "selected"]
2:45  Me       "What do you think is happening?"
2:50  Slot     "I think it's waiting for something... maybe I need to pick a time?"
3:10  Slot     Taps back arrow. On address screen. Taps Continue. Slot screen: ASAP orange again.
3:30  Slot     Taps "ASAP" again. Grey again. Continue grey.
4:10  Slot     Puts laptop down. "I'd just call the restaurant, honestly."
      Task: NOT COMPLETED (stopped at slot screen)
After task:
      Me: "What did you expect to happen on that screen with the times?"
      Participant: "I thought orange meant something was wrong. Like, not available."
      Participant: "Also 40 rupees delivery, that's a lot." (unprompted)
```

### Why each change matters

**Times.** The slot screen took him from 1:50 to 4:10, more than two minutes, when the address screen took about one. Before, "bit slow" was attached to the wrong screen. Now the time shows where the trouble was without anyone's opinion. (The table in section 1.5 counts from when Ravi sat down; these notes count from when the task was read, so 4:10 here is 5:10 there. Say which you use.)

**Exact words.** "Is it loading?" and "I thought orange meant something was wrong" are evidence you can put in front of Meera. They are Ravi's, not yours, and nobody can argue that you made them up or put a spin on them.

**Interpretations marked.** "[I: thinks ASAP was not yet chosen]" is still there, because it is your best guess at the cause and you will need it. But it is in brackets, so anyone reading knows it is yours, and you can later check it against what Ravi said afterwards, which happened to confirm it.

**The result line.** "NOT COMPLETED (stopped at slot screen)" answers your test question in two words and says where.

**Things you were not testing.** The "Landmark" field question and the delivery fee comment were not part of your test question, but they are observations, so they go in. Do not throw away what you did not plan to see; just do not let it take over.

**The header.** Product, session number, who (by role, not by full name, if anyone else will see the notes), date, the exact task. When you have five sessions, you will need this to tell them apart.

### Writing fast enough

You cannot write full sentences while someone moves through a prototype. Some shortcuts:

- Write the time and screen name first, then the action in as few words as you need.
- Use "x3" for repeats and quotation marks only for exact words.
- Keep a short list of the screen names you will use (Basket, Address, Slot, Payment, Done) on the page before you start.
- If you fall behind, put a star and the time, and fill in the line straight after the session while you still remember.
- Fill in and tidy the notes within the hour. Memory goes quickly, and it fills gaps with what you expected to see.

If someone else can come and take notes while you moderate, that makes both jobs much easier; section 4.5 covers having a note-taker.

### When it goes wrong

**Notes written only after the session.** Your memory edits as it goes. By the evening, "tapped ASAP twice" has become "struggled with slots", and the times are gone. Write during, tidy after.

**Adjectives instead of actions.** "Frustrated", "confused", "happy". Ask yourself what you saw that made you write that. Did he sigh? Say "ugh"? Put the laptop down? Write that instead, and keep the adjective as a marked interpretation if you want it.

**Notes about you, not them.** "I explained the chips." If you said something during the task, write exactly what you said; it changes how to read everything after it.

**Writing the name into a shared sheet.** If notes go into a shared sheet like thaliwala-round1, use a participant code (P1, P2...) instead of names. Section 4.6 covers what you may keep.

### Keep it

Write observations (what anyone would have seen or heard) with a time, a screen and the action or exact words. Put your interpretations on separate lines, clearly marked as yours. Record the task result in a word and where it happened. Tidy the notes within the hour.

**Check yourself**

1. Sort these into observations and interpretations: (a) "Tapped Continue three times." (b) "Got frustrated." (c) "Said: 'Where's the UPI option?'" (d) "Didn't notice the payment methods." (e) "Spent 45 seconds on the payment screen without tapping."

<details>
<summary>Answer</summary>

Observations: (a), (c), (e). Interpretations: (b) and (d). (d) is tempting as an observation, but "didn't notice" is a claim about what was in his head; what you saw was something like (e), or "scrolled past the payment methods". Rewrite (b) as what you saw: for example "sighed, said 'come on'".

</details>

2. Rewrite this note so that Meera could not argue with it: "Address screen ok but landmark field confusing."

<details>
<summary>Answer</summary>

For example: "0:40 Address: types address. Stops at 'Landmark' field, says 'Do I need this?', leaves it empty, taps Continue. [I: unclear whether landmark is optional]" The first part is what happened, with a time and his words; the bracket is your reading. "Ok" is dropped because it says nothing.

</details>

3. Your notes show the participant took 30 seconds on the address screen and 2 minutes 20 seconds on the slot screen. Which screen would you look at first, and what would you check in your notes before concluding anything?

<details>
<summary>Answer</summary>

The slot screen. Before concluding it has a problem, check what happened in those minutes: was he stuck (repeated taps, questions, going back) or just reading carefully? Time alone tells you where to look, not what went wrong. Here the notes show repeated taps on a deselecting chip and "Is it loading?", which point to a real problem.

</details>

## 1.7 From one session to one finding you can show

### A page of notes is not an answer

You have a tidy page of notes from Ravi's session. Meera has five minutes between meetings. She will not read the page; she wants to know what you found and what to do. This section turns one session's notes into one finding: a short statement she can read in a minute, check against the evidence, and act on.

<!-- teaches: first-finding = finding, evidence, likely cause -->
### What a finding is

A *finding* is a problem (or a success) you saw in the session, stated so that someone who was not there can understand it, believe it and act on it. It has four parts:

1. **What happened**: the behaviour, in plain words, with where it happened.
2. **Evidence**: the observations that show it: times, actions, exact quotes.
3. **Likely cause**: your best explanation of why, labelled as yours.
4. **What it cost**: the effect on the task. Did they fail, take longer, or get it wrong?

You can add a fifth, **what to try**, a suggestion for the design. Keep it short and keep it a suggestion; turning findings into recommendations the team agrees on is section 5.6.

Here is the picture: a finding is like a good accident report on a construction site. "Worker slipped on the third-floor stairs at 10:15 (what happened); wet footprints and a spilled bucket, photo attached (evidence); the bucket was left on the landing after cleaning (likely cause); sprained ankle, half a day lost (cost)." Anyone can read it and decide what to change. Where the picture stops being true: an accident has already happened to a real worker. Your finding is about one person in a test, and the question "will this happen to customers?" is a judgement you make, not a fact you saw. With one participant, you must say so (below).

### From the notes to the finding

Start by reading the notes and asking one question: **where did the task go wrong, or nearly wrong?** In Ravi's notes, three things stand out:

- The slot screen, 1:50 to 4:10: tapped ASAP, it deselected, Continue greyed, gave up. The task failed here.
- The Landmark field at 0:40: a question, but he went on without trouble.
- The delivery fee comment after the task: an opinion about price, not a problem using the design.

Only the first one caused the task to fail. That is your finding for today. The other two are worth keeping in the notes; they are not the headline.

Now write it. Here is a first attempt:

> Weak: "The delivery slot screen is confusing and needs to be redesigned. Users don't understand the chips. We should probably use radio buttons instead."

Read it from Meera's chair. "Confusing": says who? "Users": it was one person. "Needs to be redesigned": the whole screen? On what evidence? "Radio buttons": a solution, before she has agreed there is a problem. Nothing in it can be checked, so she can only agree or disagree with you.

> Better:
>
> **Finding 1: The participant could not continue from the delivery slot screen, and gave up.**
>
> *What happened.* On the slot screen, "ASAP" is already selected and shown in orange. The participant tapped it to choose it; tapping a selected chip deselects it, so it turned grey and Continue was disabled. He tapped Continue three times, went back and forward, tapped ASAP again with the same result, and stopped after 2 minutes 20 seconds on this screen.
>
> *Evidence.* Notes 1:50 to 4:10. Quotes: "Is it loading?" (2:30); "I think it's waiting for something... maybe I need to pick a time?" (2:50); "I'd just call the restaurant, honestly." (4:10). After the task: "I thought orange meant something was wrong. Like, not available."
>
> *Likely cause (my reading).* The orange on the selected chip reads as a warning rather than as "selected", so he tried to select it, which deselected it. The disabled Continue gave no reason.
>
> *Cost.* Task not completed. A customer in this situation would not place the order.
>
> *Seen in.* 1 of 1 participants. One session shows this can happen; it does not show how often.
>
> *What to try.* Make the selected state look selected (for example a tick and a filled style), and stop a second tap on the selected chip from clearing it. Test again with one or two new people.

### Why each part is there

**The title says what happened and its cost**, not your opinion. "Could not continue... and gave up" is a fact from the notes. Meera can stop reading after the title and still know what matters.

**What happened is the mechanism of the failure, step by step**: the pre-selected chip, the tap, the deselect, the disabled button. This is what lets Kabir, who will build it, see exactly which behaviour to change.

**The evidence points back to the notes** by time, so anyone can check. The quotes do more persuading than any adjective of yours could.

**The likely cause is labelled as a reading.** It is your best explanation, and Ravi's after-task comment supports it, but it is still an explanation. Keeping it separate means that if Meera disagrees with the cause, she cannot dismiss what happened.

**"Seen in 1 of 1" is honest.** One person can show that a problem exists: Ravi really did get stuck, on a design the whole team thought was clear. One person cannot show how many customers will hit it. Say so plainly, and the finding becomes harder to argue with, not easier: you are not claiming more than you saw. How much five people can tell you is section 5.5.

**What to try is a suggestion, not a spec**, and it ends with testing again: the next turn of the cycle from section 1.2.

### Showing it

For one finding, the report is a conversation, not a document. Bring the finding (on paper or in a message), a screenshot of the slot screen with the orange chip, and your notes in case she asks. Say the title first. Then show the screenshot and read the two strongest quotes. Then stop and let her ask. Five minutes.

Meera said: "Huh. I've looked at that screen ten times." And then: "Can you fix the chip and try it on someone else on Monday?" That is a finding that worked: the team changed something because of what one person did.

### When it goes wrong

**Too many findings from one session.** You list the slot screen, the landmark field, the delivery fee, the font size and the button colour. Meera reads five items of equal weight and does nothing. Lead with the one that made the task fail; put the rest under "also noticed".

**Opinions reported as findings.** "Ravi thought the delivery fee was too high." That is a view about price, not a problem using the design. Note it, pass it on if the team cares about price, but do not present it as a usability finding.

**Overclaiming.** "Users can't use the slot screen." It was one user. Say "the participant" and "1 of 1".

**Jumping to the fix.** A finding that is only a solution ("use radio buttons") hides the problem. If the fix is rejected, the problem goes with it.

### Keep it

Pick the problem that hurt the task most. Write it as: what happened (with where), evidence (times, quotes), likely cause (labelled as yours), cost, how many participants it was seen in; then, briefly, what to try. Show it in person with a screenshot and the best quotes.

**Check yourself**

1. From your notes, a participant spent 40 seconds on the payment screen, said "Oh, there's UPI, good", and paid successfully. Is this a finding? What would you write?

<details>
<summary>Answer</summary>

It is a success, not a problem, and successes are worth recording because they tell the team what not to break. You might write it under "also noticed": "Payment: found UPI and paid in 40 s without trouble (1 of 1)." It is not a headline finding, because nothing went wrong. The tempting mistake is to ignore it or to call 40 seconds "slow" with nothing in the notes to show it was a struggle.

</details>

2. Find three problems in this finding: "The address form is bad. Users get confused by the Landmark field and it should be removed."

<details>
<summary>Answer</summary>

(1) "Bad" and "confused" are interpretations with no evidence; what happened was that he asked "Do I need this?" and left it empty. (2) "Users" overclaims: it was one participant. (3) "It should be removed" is a fix, and maybe the wrong one (delivery riders may need landmarks); the problem is that it was unclear whether the field is optional. Also, the task did not fail there, so it is not the headline finding.

</details>

3. Meera reads your slot finding and says, "One person from support isn't a real customer." Write a two-sentence answer that does not overclaim.

<details>
<summary>Answer</summary>

One version: "You're right that one person can't tell us how many customers would get stuck. But he orders food on apps like anyone else and he hit a real behaviour, a selected chip that deselects when tapped, so it's worth a quick fix and a test with two or three more people to see if it holds." It agrees with what is true in the objection, keeps to what was seen, and proposes the next turn of the cycle.

</details>

## 1.8 Practice: test one task of your own checkout prototype on one person

You have seen the whole cycle once on Thaliwala. Now you run it yourself, on your own clickable checkout prototype, with one person. The tasks climb: first two warm-ups on Thaliwala material, then each phase on your own prototype, and finally the full small test with a finding. Give yourself about two hours, spread over two or three days: the session needs a person, and people need asking in advance.

Keep everything in one document or notebook page per test: question, task, consent words, notes, finding. You will add to this way of working in every chapter.

### Task 1 (guided): fix a weak plan

A classmate shows you their plan for testing a grocery app's checkout:

```text
Question: Is the checkout user-friendly?
Task:     "Go to your cart, tap 'Proceed', choose 'Express delivery' and pay with the saved card. Tell me what you think."
Person:   My flatmate, who helped me design it.
Prototype: opens on the app's home screen.
```

Find one problem in each of the four lines, and rewrite the plan.

<details>
<summary>Answer</summary>

Problems: the question asks for an opinion ("user-friendly") that a session cannot answer; the task names every button on the route ("Proceed", "Express delivery", the saved card) and ends with "tell me what you think", which invites opinions; the flatmate helped design it, so knows the answers; the prototype starts on a home screen the task does not need.

One rewrite:

```text
Question:  Can someone who has never seen this checkout get from a full cart to a paid order, with delivery today, without help?
Task:      "You need these groceries delivered today. Get the order placed and paid for."
Person:    Someone who buys groceries online and has not seen the design.
Prototype: opens on the cart, with the items already in it; I click through the task myself first.
```

Check your version against section 1.3: who, can do what, under what condition; a goal and an end point; no names from the screen.

</details>

### Task 2 (guided): turn notes into a finding

Here are notes from a session on the same grocery app:

```text
0:15 Cart     Taps "Proceed".
0:30 Delivery Reads options. "Express... 99? And standard is... where's standard?"
0:50 Delivery Scrolls down. Standard option is below the fold. Doesn't scroll far enough. Taps Express.
1:05 Payment  Pays with saved card. Done.
      After task: "I didn't want to pay 99 for express, but I couldn't see the other one."
```

Write one finding with the parts from section 1.7.

<details>
<summary>Answer</summary>

**Finding 1: The participant chose paid express delivery because the free option was below the fold.**

What happened: on the delivery screen, only "Express (99)" was visible without scrolling. The participant looked for standard delivery, scrolled a little, did not reach it, and chose Express. Evidence: notes 0:30 to 0:50; "where's standard?" (0:30); after the task: "I didn't want to pay 99 for express, but I couldn't see the other one." Likely cause (my reading): the standard option sits below the first screen and nothing shows there is more below. Cost: task completed, but with a choice the participant did not want; a customer would pay more than intended, and might complain or not come back. Seen in: 1 of 1. What to try: show both options without scrolling, cheapest first or clearly side by side; test again.

Note that the task was "completed", yet this is a serious finding: completing a task the wrong way can be worse than failing it.

</details>

### Task 3 (your prototype): question, task and starting point

Open your own checkout prototype in Figma.

1. Click through it yourself and list its screens in order, with a short name for each (as Basket, Address, Slot, Payment, Done were for Thaliwala).
2. Write one test question (who, can do what, under what condition).
3. Write one task sentence for the participant.
4. Set the prototype's starting point so that it opens where the task starts, and click through the task once to check every link you need works. Fix any broken links now; they are prototype faults, not findings.
5. Check your task against this list: Does it give a goal a real customer has? Does it have an end point the participant will recognise? Does it avoid every button, label and screen name they must find? Is it one sentence you can read word for word?

<details>
<summary>Answer</summary>

There is no single right answer; here is a model for a typical college checkout prototype (a café ordering app with Cart, Details, Pickup time, Payment, Confirmation).

Question: "Can someone who has never seen this app get from a filled cart to a paid order for pickup in 30 minutes, without help?" Task: "You'd like to pick this up on your way in about half an hour. Get it ordered and paid for." Starting point: the Cart frame with two items in it.

Judge yours against the four checks in step 5. The most common slip is in the third check: words such as "checkout", "pickup slot" or "confirm" that are on your screens. Replace each with what a customer would say. If your prototype cannot complete the task (a missing link to Payment, say), either fix the link or shorten the task's end point to what the prototype can do, and write that down.

</details>

### Task 4 (your prototype): the person and the words

Choose one participant: someone who has not seen this design and who orders food or shops on their phone. Not a classmate from your design course if they saw it in critique. Write out, word for word:

1. How you will ask them (what it is, how long, what they will do, that it is the design being tested, what you will keep, that they can stop).
2. Your think-aloud instruction, with your own example (not the train ticket: pick something they do often).
3. The two or three questions you will ask after the task, using neutral words.

<details>
<summary>Answer</summary>

Model:

1. "I'm testing a checkout design from a college project and would like to watch someone try it. It takes about fifteen minutes on my laptop. You'll try to place one order and think out loud while you do it. It's the design I'm testing, not you; if something is hard, that's useful. I'll take written notes, won't record, and won't use your name. You can stop any time. Is that okay?"
2. "While you do this, please say out loud what's going through your head: what you're looking at, what you're trying to do, what you expect to happen. Like if you were booking a cab you might say 'okay, where do I put the drop... is it this box? I'll type here.' There are no right answers."
3. "How did that go for you?" "On the screen where you [what they did, in their words], what did you expect to happen?" "Anything else you'd want to tell me?"

Check: no promise of a reward you cannot give; recording not mentioned unless you will ask for it separately (section 1.4); after-task questions use their words for things, not your design labels.

</details>

### Task 5 (small project): run it, write it up

Run the session. Then, within the hour:

1. Tidy your notes into timed observation lines, with interpretations marked, and a task result line (completed, completed with help, not completed, and where).
2. Write one finding with the parts from section 1.7: what happened, evidence, likely cause (labelled), cost, seen in 1 of 1, and briefly what to try. If the task went smoothly, write the success instead, plus the most useful thing you noticed along the way.
3. Show the finding to one person (a classmate, a friend, or a mentor) in five minutes: title, screenshot, two quotes, then stop. Write down the first question they ask.

Judge your work against this checklist:

- [ ] The test question was written before the task, and the session answered it (yes, no, or yes but).
- [ ] The task named no button, label or screen, and had an end point.
- [ ] The participant agreed knowing what would happen and that they could stop.
- [ ] You read the task word for word and did not help during it; any help is written down.
- [ ] Every note line has a time, a screen and an action or exact words; interpretations are marked.
- [ ] The finding can be checked against the notes, says "1 of 1", and keeps the likely cause separate from what happened.
- [ ] The first question your listener asked was about what to do, not "what do you mean?"

<details>
<summary>Answer</summary>

A model write-up, from a session on a café ordering prototype:

```text
Café app, session 1, P1 (friend, orders coffee on apps weekly), 21 Nov, 18:30
Task: "You'd like to pick this up on your way in about half an hour. Get it ordered and paid for."

0:05 Cart     Taps "Checkout".
0:20 Details  Fills name and phone. Taps Next.
0:35 Pickup   "Okay, when... it says 'Now'. I don't want now." Taps the time. A list opens: 10:00, 10:15 ... 
0:50 Pickup   Scrolls the list. "What time is it now? ... I'll do 10:45." Taps 10:45.
      [I: the list gives clock times only, she had to work out "in 30 minutes" herself]
1:10 Payment  Taps card. Pays. Done.
      Task: COMPLETED, no help.
After task: "Fine, but I had to look at my phone to see the time."
```

**Finding 1: The participant had to check the current time to choose a pickup 30 minutes away.** What happened: the pickup screen lists clock times only; she asked "what time is it now?", checked her phone, then chose. Evidence: 0:35 to 0:50; "What time is it now?"; after task: "I had to look at my phone to see the time." Likely cause (mine): no current time or "in 30 min" labels next to the slots. Cost: completed, slower, and a risk of picking the wrong time. Seen in 1 of 1. What to try: label slots relative to now ("in 15 min", "in 30 min") alongside the clock time; test again.

If your checklist has a box you could not tick, that is the part to practise next time. The most common ones on a first test are helping during the task without noticing (re-read your notes for your own words) and interpretations written as observations ("confused").

</details>
