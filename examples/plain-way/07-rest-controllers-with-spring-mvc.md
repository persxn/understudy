# Chapter 7: REST controllers with Spring MVC

<!-- contents -->
- [7.1 Your first @RestController](#71-your-first-restcontroller)
- [7.3 Path variables and query parameters](#73-path-variables-and-query-parameters)
- [7.5 Accepting JSON with @RequestBody](#75-accepting-json-with-requestbody)
- [7.7 Create, read, update and delete books](#77-create-read-update-and-delete-books)
- [7.12 Practice: the books and members endpoints, in memory](#712-practice-the-books-and-members-endpoints-in-memory)
<!-- /contents -->

Six chapters ago your `library` app started, printed a banner, and did nothing. Since then you have learned what HTTP is, what JSON looks like, how Spring makes beans and hands them to each other, and how auto-configuration switches things on for you. In this chapter the app finally answers. By the end, `curl` will be able to list books, fetch one, add one, change one and delete one, all over HTTP, all with JSON. Everything here is true of Spring Boot 4.1.2, which uses Spring Framework 7 underneath.

## 7.1 Your first @RestController

### The question

You know how to send a request with `curl`. You know Spring can build objects for you. But when a request for `GET /hello` arrives at your running app, who reads it, and how does that person know that *your* method, of all the methods in your project, is the one to call?

### The picture

Think of a large library building with one front desk. Every visitor comes through the same door and talks to the same clerk. The clerk does not answer questions himself. He has a card index: "questions about the catalogue go to room 3, questions about fines go to room 7." He reads the visitor's question, looks it up in the index, walks the visitor to the right room, waits while the specialist answers, and then hands the answer back at the door.

In Spring, the clerk is called the DispatcherServlet, the rooms are your methods, and the card index is built from your annotations. Where the picture stops being true: a real clerk writes his index by hand, once. Spring writes its index by itself, at start-up, by reading your classes; and the clerk can serve many visitors at the same moment, because each request runs on its own thread.

### The idea

Start with the problem from the bottom. When your app runs, something must listen on a network port, usually 8080, read the bytes of an HTTP request (`GET /hello HTTP/1.1`, some headers, maybe a body), and write the bytes of a response. Writing that yourself would mean sockets, parsing, threads. Nobody does that by hand.

**The web server.** Spring Boot's web starter brings an embedded web server, Tomcat by default. *Embedded* means it is a library inside your jar, started by your `main` method, not a separate program you install. Tomcat does the socket work. It turns the raw bytes into a Java object that describes the request and gives you an object to write the response into.

**The servlet.** Tomcat speaks one Java standard, called the Servlet API (today under the name Jakarta Servlet). A *servlet* is a Java object with one job: given a request object and a response object, fill in the response. Tomcat does not know about Spring. It only knows: "for paths like this, call that servlet."

**The DispatcherServlet.** Spring provides exactly one servlet that matters to you: the `DispatcherServlet`. Its name says what it does: it *dispatches*, sends each request on to someone else. Spring Boot's auto-configuration (chapter 6) sees that Spring MVC is on the classpath, creates a `DispatcherServlet` bean, and registers it with Tomcat for every path, `/` and everything under it. So every request to your app reaches the same object first. This is the front desk.

**Spring MVC.** The part of Spring that contains the DispatcherServlet and everything around it is called Spring MVC. MVC stands for Model, View, Controller, an old way of splitting a program that shows web pages. You will not build web pages in this book; you will build an API that answers with JSON. But the name has stuck, and the *controller* part is exactly what you need.

**A controller.** A *controller* is a class whose methods answer requests. Each method that answers a request is called a *handler method*, or just a *handler*. Your job in this chapter is to write controllers. The DispatcherServlet's job is to find the right handler for each request and call it.

Now, how does it find it? Here the annotations come in, and here is where they stop being magic. Remember from chapter 3: an annotation is a label. It does nothing on its own. It sits in the compiled class file, and some other code, at run time, asks Java "does this class carry that label?" (this asking is *reflection*) and then acts on the answer. So for every annotation in this chapter, ask two questions: who reads it, and what does it make them do?

**`@RestController`.** You put this on a class. It is read by two readers.

The first reader is component scanning, from chapter 5. `@RestController` is itself labelled with `@Controller`, which is labelled with `@Component`. So when Spring scans your package at start-up, it finds this class and makes a bean of it, just like a `@Service`. One object, created once, injected with whatever its constructor asks for.

The second reader is Spring MVC. At start-up, a Spring MVC bean with the long name `RequestMappingHandlerMapping` (you will never type it; it is created by auto-configuration) walks through every bean in the context and asks: "is your class labelled `@Controller`?" `@RestController` counts, since it carries `@Controller`. For each such bean it looks at every method, searching for mapping annotations. Each one it finds becomes an entry in its card index.

`@RestController` carries one more label: `@ResponseBody`. That label tells Spring MVC "whatever the handler methods of this class return *is* the body of the response". Without it, Spring MVC would treat a returned `String` as the *name of a web page template* to render. With it, a returned `String` is written straight into the response. So `@RestController` means: "this class is a bean, it answers requests, and what its methods return is the answer itself." That is the whole meaning, in three parts.

**`@GetMapping`.** You put this on a method. It is read by `RequestMappingHandlerMapping` at start-up, as just described. `@GetMapping("/hello")` says: "add a card to the index: requests with method GET and path `/hello` go to this method." There is one per HTTP method you met in chapter 4: `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`.

**`@RequestMapping`.** All of those are shorthands for one general annotation, `@RequestMapping`. `@GetMapping("/hello")` means exactly `@RequestMapping(path = "/hello", method = RequestMethod.GET)`. You will mostly use `@RequestMapping` on the *class*, to give every method in it a shared path prefix. If the class says `@RequestMapping("/books")` and a method says `@GetMapping("/{id}")`, the full path is `/books/{id}`. The class-level annotation is read by the same reader, at the same time, and its path is glued in front of each method's path.

Put it together and you get the two moments in the life of every handler.

*At start-up, once:* component scanning makes your controller a bean; `RequestMappingHandlerMapping` reads the mapping annotations of every controller bean and builds its index, a table from "method plus path" to "this bean, this Java method". If two methods claim the same method and path, start-up fails right there, because the clerk would not know which room to send people to.

*At each request:* Tomcat accepts the connection and hands the request to the `DispatcherServlet`. The DispatcherServlet asks its handler mappings, "who handles GET `/hello`?" The index answers with your bean and method. The DispatcherServlet then asks a second helper, a *handler adapter*, to actually call that method: the adapter works out what arguments the method wants (none, so far), calls it, takes the return value, and, because of `@ResponseBody`, writes it into the response body. The status is 200 OK unless something says otherwise. Tomcat sends the bytes back.

You do not have to remember the class names `RequestMappingHandlerMapping` or "handler adapter". You do have to remember the shape: an index built once at start-up from your annotations, and a front desk that uses it on every request. Every mistake in this chapter is easier to understand with that shape in mind. A 404 means "no card in the index for this path". A 405 means "there is a card for this path, but not for this HTTP method".

One last word: *thread*. Tomcat keeps a pool of threads, and each request runs on one of them. Two requests at the same moment run your one controller bean on two threads at once. This is fine as long as your controller keeps no changing data in its own fields. Keep that in mind for section 7.7, where you will store books in memory.

Where should the controller live? PRACTICES rule 2: one sub-package per feature, below `com.example.library`. A greeting is not a library feature, so put this first, throwaway controller in `com.example.library.hello`. Component scanning starts at the package of the class marked `@SpringBootApplication` and goes down, so anything under `com.example.library` is found.

### The code

First check that your `pom.xml` has the web starter. In chapter 1 you created the project with Spring Web selected; in Spring Boot 4 the starter for Spring MVC is called `spring-boot-starter-webmvc`. Look for it:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>
```

No `<version>`: the Spring Boot parent chooses it (PRACTICES rule 3). Now create the controller.

src/main/java/com/example/library/hello/HelloController.java
```java
package com.example.library.hello;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello from the library";
    }
}
```

That is all. No `main` change, no registration. Start the app in one terminal and leave it running.

<!-- code: id=hello-run unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ ./mvnw spring-boot:run
...
INFO 41210 --- [library] [           main] o.s.b.w.e.tomcat.TomcatWebServer         : Tomcat started on port 8080 (http) with context path '/'
INFO 41210 --- [library] [           main] c.e.library.LibraryApplication           : Started LibraryApplication in 1.9 seconds (process running for 2.2)
```

Open a second terminal and call your method.

<!-- code: id=hello-curl unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ curl -i localhost:8080/hello
HTTP/1.1 200
Content-Type: text/plain;charset=UTF-8
Content-Length: 22
Date: Wed, 18 Nov 2026 10:00:00 GMT

Hello from the library
```

Tomcat prints the status line as `HTTP/1.1 200` with no word after the number; that is normal. The content type is `text/plain` because you returned a `String`.

### The trace

Follow `GET /hello` through the app.

| Step | Who | What happens |
|---|---|---|
| 0 | Spring, at start-up | Scanning finds `HelloController` (it carries `@Component` through `@RestController`) and makes a bean. The handler mapping reads `@GetMapping("/hello")` and adds the card "GET /hello → `HelloController.hello()`". |
| 1 | curl | Sends `GET /hello HTTP/1.1` to port 8080. |
| 2 | Tomcat | Reads the bytes on a worker thread, builds a request object, passes it to the `DispatcherServlet`, which is mapped to `/`. |
| 3 | DispatcherServlet | Asks the handler mapping: who handles GET `/hello`? Answer: `hello()` on the `HelloController` bean. |
| 4 | Handler adapter | Method takes no arguments. Calls `hello()`. |
| 5 | Your method | Returns `"Hello from the library"`. |
| 6 | Handler adapter | Class has `@ResponseBody` (from `@RestController`), so the `String` is the body. Writes it as `text/plain`, status 200. |
| 7 | Tomcat | Sends the response bytes back to curl. |

```text
curl ──> Tomcat ──> DispatcherServlet ──> handler mapping (index)
                          │                      │
                          │   "HelloController.hello()"
                          ▼
                    handler adapter ──> hello() ──> "Hello from the library"
                          │
curl <── Tomcat <── body written, 200
```

### What goes wrong

**The controller is outside the scanned packages.** If you put `HelloController` in `com.example.hello` (not under `com.example.library`), scanning never sees it, no card is added, and every call gives a 404:

```text
HTTP/1.1 404
Content-Type: application/json

{"timestamp":"2026-11-18T10:00:00.000+00:00","status":404,"error":"Not Found","path":"/hello"}
```

That JSON is Spring Boot's default error body. Move the class under `com.example.library`.

**`@Controller` instead of `@RestController`.** The class is found and the card exists, but there is no `@ResponseBody`, so Spring MVC takes `"Hello from the library"` as the name of a page template, finds no such template, and answers with an error (with no template engine in the project, you get a 500 or a 404 depending on setup). The fix is `@RestController`.

**Two methods claim the same card.** Two `@GetMapping("/hello")` methods make start-up fail with `IllegalStateException: Ambiguous mapping. Cannot map 'helloController' method ... to {GET [/hello]}: There is already 'helloController' bean method ... mapped.` Rename one path.

**The app is not running, or is still starting.** curl prints `curl: (7) Failed to connect to localhost port 8080`. Look at the first terminal.

**Port 8080 is taken** by another program (or an old copy of your app): start-up stops with `Web server failed to start. Port 8080 was already in use.` Stop the old one with Ctrl+C in its terminal.

### Remember

- Tomcat, embedded in your app, does the network work; it hands every request to one Spring object, the `DispatcherServlet`.
- At start-up, Spring MVC reads the mapping annotations of every `@Controller` bean and builds an index from "HTTP method + path" to a Java method.
- `@RestController` = bean (`@Component`) + answers requests (`@Controller`) + return value is the body (`@ResponseBody`).
- `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping` are shorthands for `@RequestMapping` with a fixed HTTP method; `@RequestMapping` on a class gives a shared path prefix.
- 404: no card for that path. 405: a card for the path, not for that method.

**Check yourself**

1. Add a second method `GET /hello/shout` that returns the greeting in capital letters. Use `@RequestMapping("/hello")` on the class. What paths do the two methods need now?

<details><summary>Answer</summary>

Put `@RequestMapping("/hello")` on the class, `@GetMapping` (no path, or `""`) on `hello()`, and `@GetMapping("/shout")` on the new method, which returns `"HELLO FROM THE LIBRARY"`. The full paths are the class path glued to the method path: `/hello` and `/hello/shout`.
</details>

2. Without running anything: what does `curl -i -X POST localhost:8080/hello` answer, and why?

<details><summary>Answer</summary>

`405 Method Not Allowed`. The index has a card for the path `/hello`, but only for GET. Spring also adds a header `Allow: GET,HEAD,OPTIONS` (or similar) telling the client which methods would work.
</details>

3. Who reads `@RestController`, and when? Name both readers.

<details><summary>Answer</summary>

Component scanning, at start-up, reads it (through `@Component`) and makes the class a bean. Spring MVC's handler mapping, also at start-up, reads it (through `@Controller`) to know the bean's methods should be indexed; and at each request, the `@ResponseBody` it carries tells Spring to write the return value as the body.
</details>

## 7.3 Path variables and query parameters

### The question

A library has thousands of books. You cannot write one method for `/books/1`, another for `/books/2`, and so on. And when the reader wants "books by Le Guin", the request has to carry that author somehow. How does one method answer for any id, and how does it read the extra details in the URL? And once you have a real `Book`, how does a Java object become the JSON text from chapter 4?

### The picture

A library call slip has blanks: "Shelf: ____. Copies wanted: ____." The form is printed once; each visitor fills in the blanks. The URL `/books/{id}` is the printed form, and the `42` in `/books/42` is what this visitor wrote in the blank. The `?author=Le Guin` part is like a note in the margin: optional, named, and there may be several.

On the way back, think of a translator who turns a letter written in Java into one written in JSON, word by word. Where the picture stops being true: the translator is not clever. She copies field names exactly, and she cannot translate what she cannot see.

### The idea

**The parts of a URL.** Take `http://localhost:8080/books/42?author=Le%20Guin&limit=5`. After the host and port comes the *path*, `/books/42`. After the `?` comes the *query string*, `author=Le%20Guin&limit=5`: pairs of `name=value`, joined with `&`. The `%20` is how a space is written inside a URL; Spring decodes it back to a space for you. In curl, quote any URL with `?` or `&` in it, or the shell will take the `&` as "run in the background".

Two rules of thumb in REST, from chapter 4: the path names *which thing* (`/books/42` is one book), the query string *adjusts* the request (filter, sort, limit). That is why there are two different annotations.

**Path variables.** A *path variable* is a part of the path that changes. You write it in the mapping in curly braces: `@GetMapping("/books/{id}")`. The handler mapping reads that at start-up as a pattern, "`/books/` followed by one segment, call it `id`". A *segment* is the text between two slashes. So `/books/42` matches, `/books/abc` matches (we will come back to that), `/books/42/loans` does not, and `/books` does not.

**`@PathVariable`.** You put this on a *method parameter*, not on the method. It is read at each request by the handler adapter, in the step where it works out what arguments to pass. `@PathVariable long id` says: "take the segment captured as `id` and pass it in here." The adapter matches the name of the parameter to the name in the braces. That needs the parameter's name to be present in the compiled class; Spring Boot's Maven parent switches on the compiler flag `-parameters`, which keeps it. If the names differ, give the name: `@PathVariable("id") long bookId`.

The captured text is always a `String` first, because a URL is text. The adapter then *converts* it to the type of your parameter, `long` here, using Spring's conversion service. If the text cannot be converted, `abc` into a `long`, the method is never called and the client gets a 400 Bad Request. This is a gift: you never write `Long.parseLong` and never handle its exception.

**Query parameters and `@RequestParam`.** A *query parameter* is one `name=value` pair of the query string. `@RequestParam String author` on a parameter tells the adapter: "find the query parameter called `author` and pass its value". Again it is read per request, again names must match, again conversion happens (`@RequestParam int limit` turns `"5"` into `5`).

Unlike a path variable, a query parameter is often optional. By default, `@RequestParam` is *required*: if it is missing, the client gets a 400. You have three ways to make it optional:

- `@RequestParam(required = false) String author`: missing means `null`. Use a reference type, not `int`, since an `int` cannot be `null`.
- `@RequestParam(defaultValue = "10") int limit`: missing means `"10"`, converted to `10`. Setting a default also makes it not required.
- `@RequestParam Optional<String> author`: missing means `Optional.empty()`. This uses generics from chapter 3.

**Returning objects.** Until now your method returned a `String`. A real API returns things: a book, a list of books. Let the book be a record (chapter 3):

```text
record Book(long id, String title, String author, int year)
```

What happens when a handler returns a `Book`? The handler adapter has the value, and `@ResponseBody` says it must become the body. But a body is bytes, and a `Book` is an object in memory. Something must translate.

**Message converters.** That something is an `HttpMessageConverter`, a *message converter*: an object that knows how to turn one kind of Java value into body bytes of one content type, and back. Spring MVC holds a list of them. For a `String` there is one that writes plain text; that is what you saw in 7.1. For any other object, the one that is used is the JSON converter, built on a library called Jackson.

**Jackson.** Jackson is the most widely used Java library for JSON. Spring Boot 4 uses Jackson 3. The web starter brings it in, and auto-configuration (chapter 6) creates a Jackson `JsonMapper` bean, configured with sensible settings, and plugs it into the JSON message converter. You did nothing to get it, which is exactly what auto-configuration promised.

How does Jackson write a `Book`? By reflection. It looks at the class and finds its *properties*: for a record, its components (`id`, `title`, `author`, `year`); for an ordinary class, its public getters (`getTitle()` becomes `title`). For each property it writes `"name": value`. Numbers become JSON numbers, `String`s become JSON strings, `null` becomes `null`, a `List` becomes a JSON array, a nested object becomes a nested JSON object. So `new Book(1, "A Wizard of Earthsea", "Ursula K. Le Guin", 1968)` becomes

```text
{"id":1,"title":"A Wizard of Earthsea","author":"Ursula K. Le Guin","year":1968}
```

and a `List<Book>` becomes `[ {...}, {...} ]`.

**Which converter is chosen?** The adapter goes through its list of converters and asks each, "can you write this type, in a content type the client accepts?" The client says what it accepts in the `Accept` header; curl sends `Accept: */*`, meaning "anything". For a `Book`, the first converter that can say yes is Jackson's, with `application/json`. That is where the `Content-Type: application/json` header in the response comes from. This choosing is called *content negotiation*; you need only the idea for now.

So, two annotations and one library: `@PathVariable` and `@RequestParam` bring data *in* from the URL, Jackson takes objects *out* as JSON. Neither annotation is read by Jackson; both are read by Spring MVC's handler adapter, at each request, before your method runs.

For now, keep the books in a fixed list inside the controller. Section 7.7 will move them into a service bean, where they belong (chapter 5's layers).

### The code

src/main/java/com/example/library/book/Book.java
```java
package com.example.library.book;

public record Book(long id, String title, String author, int year) {
}
```

src/main/java/com/example/library/book/BookController.java
```java
package com.example.library.book;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/books")
public class BookController {

    private static final List<Book> BOOKS = List.of(
            new Book(1, "A Wizard of Earthsea", "Ursula K. Le Guin", 1968),
            new Book(2, "The Left Hand of Darkness", "Ursula K. Le Guin", 1969),
            new Book(3, "Kindred", "Octavia E. Butler", 1979));

    @GetMapping
    public List<Book> list(@RequestParam(required = false) String author) {
        if (author == null) {
            return BOOKS;
        }
        return BOOKS.stream()
                .filter(b -> b.author().equalsIgnoreCase(author))
                .toList();
    }

    @GetMapping("/{id}")
    public Book one(@PathVariable long id) {
        return BOOKS.stream()
                .filter(b -> b.id() == id)
                .findFirst()
                .orElse(null);
    }
}
```

`BOOKS` is `static final` and made with `List.of`, which cannot be changed, so two threads reading it at once is safe. Restart the app (Ctrl+C, then `./mvnw spring-boot:run` again in the first terminal), then in the second terminal:

<!-- code: id=books-get unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ curl -i localhost:8080/books/1
HTTP/1.1 200
Content-Type: application/json

{"id":1,"title":"A Wizard of Earthsea","author":"Ursula K. Le Guin","year":1968}
$ curl -i "localhost:8080/books?author=octavia%20e.%20butler"
HTTP/1.1 200
Content-Type: application/json

[{"id":3,"title":"Kindred","author":"Octavia E. Butler","year":1979}]
$ curl -i localhost:8080/books/abc
HTTP/1.1 400
Content-Type: application/json

{"timestamp":"2026-11-18T10:05:00.000+00:00","status":400,"error":"Bad Request","path":"/books/abc"}
```

(curl also prints `Transfer-Encoding` and `Date` headers; they are left out here and below.)

### The trace

Follow `GET /books/1`.

| Step | Who | What happens |
|---|---|---|
| 1 | Tomcat | Receives `GET /books/1`, passes it to the `DispatcherServlet`. |
| 2 | Handler mapping | Class path `/books` + method path `/{id}` = pattern `/books/{id}`. It matches; `id` is captured as the text `"1"`. |
| 3 | Handler adapter | Parameter `long id` has `@PathVariable`: takes `"1"`, converts it to `1L`. |
| 4 | Your method | `one(1)` finds the record and returns `Book[id=1, ...]`. |
| 5 | Handler adapter | Asks the converters who can write a `Book`; Jackson's JSON converter can. |
| 6 | Jackson | Reads the record's components by reflection, writes `{"id":1,...}`. |
| 7 | Tomcat | Sends 200 with `Content-Type: application/json`. |

```text
/books/{id}         the printed form
/books/1            the filled-in form   ──>  id = "1" ──> 1L ──> one(1L)
                                                               │
Book[id=1, title=..]  ──> Jackson ──> {"id":1,"title":...} <──┘
```

### What goes wrong

**Asking for a book that does not exist.** `curl -i localhost:8080/books/99` answers `200` with an *empty body*. Your method returned `null`, and Spring writes nothing for `null`. That is wrong in REST terms: it should be a 404. Section 7.5 fixes it with `ResponseEntity`.

**A required query parameter is missing.** If you write `@RequestParam String author` without `required = false`, then plain `GET /books` gives a `400 Bad Request`, and the app's log says `Required request parameter 'author' for method parameter type String is not present`.

**`int` with `required = false`.** `@RequestParam(required = false) int limit` fails when the parameter is missing, because `null` cannot go into an `int`: Spring reports that it cannot convert null to the primitive type. Use `Integer`, or a `defaultValue`.

**A name mismatch.** `@GetMapping("/{bookId}")` with `@PathVariable long id` fails at the first request with a 500, and the log says something like `Missing URI template variable 'id' for method parameter of type long`. Make the names equal, or write `@PathVariable("bookId")`.

**Jackson writes nothing for a class.** If you return an ordinary class with private fields and no getters, Jackson finds no properties and fails with `No serializer found for class ... and no properties discovered to create BeanSerializer`. Records do not have this problem: their components count as properties.

### Remember

- The path names which thing; the query string adjusts the request.
- `{id}` in a mapping is a pattern for one path segment; `@PathVariable` passes the captured text, converted to your parameter's type. Unconvertible text gives 400.
- `@RequestParam` reads one `name=value` from the query string; required by default; `required = false`, `defaultValue` or `Optional` make it optional.
- Both are read by Spring MVC's handler adapter at each request, before your method runs.
- A returned object goes through a message converter; for objects that is Jackson, which writes each record component or getter as a JSON property.

**Check yourself**

1. Add `GET /books/count` that returns the number of books as a number. Does it clash with `/books/{id}`? Try it and explain.

<details><summary>Answer</summary>

```java
@GetMapping("/count")
public int count() {
    return BOOKS.size();
}
```

`/books/count` matches both patterns, but Spring prefers the more specific one: a pattern with no variables beats a pattern with one. So `count()` is called and the answer is `3`. Without that rule, `count` would be converted to `long` and fail with 400.
</details>

2. Add an optional `limit` query parameter to the list method so that `GET /books?limit=2` returns at most two books, and plain `GET /books` returns all.

<details><summary>Answer</summary>

Add `@RequestParam(defaultValue = "100") int limit` (or `Integer limit` with `required = false`) and end the stream with `.limit(limit).toList()`; for the no-author branch use `BOOKS.stream().limit(limit).toList()`.
</details>

3. What JSON does Jackson write for `new Book(4, "Dune", null, 1965)`?

<details><summary>Answer</summary>

`{"id":4,"title":"Dune","author":null,"year":1965}`. A `null` property is written as JSON `null` by default.
</details>

## 7.5 Accepting JSON with @RequestBody

### The question

Reading books is half an API. To add a book, the client must send one: a title, an author, a year. That will not fit nicely in a URL. In chapter 4 you sent JSON in the body of a POST with `curl -d`. How does that JSON text become a Java object in your method? And how do you answer "201 Created" instead of the 200 that Spring sends by default, or "404 Not Found" for a book that is not there?

### The picture

Back to the translator from 7.3. Now letters also come *in*, written in JSON, and she rewrites them in Java before they reach your desk. She first checks the envelope: it must say "written in JSON". A letter marked as something else she hands back unopened.

For the answer, think of a parcel with a label. Up to now you handed back only the contents, and Spring stuck on a standard label saying "200 OK". `ResponseEntity` lets you fill in the label yourself: the status, extra headers, and the contents. Where the picture stops being true: a real label can be anything; an HTTP status must be one of the agreed numbers from chapter 4.

### The idea

**The request body.** An HTTP request can carry a *body* after its headers, just like a response. GET requests normally have none. POST and PUT carry the data to create or replace. With `curl -d '...'` you put text into that body.

**`Content-Type`.** The body is just bytes. To say how to read them, the client sends a header, `Content-Type`. For JSON it is `Content-Type: application/json`. This matters a lot: when you write `curl -d '{"title":"Dune"}'` *without* naming a content type, curl sends `Content-Type: application/x-www-form-urlencoded`, the format of an HTML form. So in this book every JSON request carries `-H "Content-Type: application/json"`. `-H` adds a header.

**`@RequestBody`.** You put this on one method parameter. It is read by the handler adapter at each request. It says: "read the whole request body and turn it into an object of this parameter's type." The adapter does that with the same list of message converters from 7.3, now used the other way round. It asks each converter: "can you *read* this `Content-Type` into this Java type?" For `application/json`, Jackson's converter says yes.

So the flow is the mirror of returning an object. Jackson reads the JSON text, looks at the target type, say a record `NewBook(String title, String author, int year)`, finds its components by reflection, and for each JSON property with a matching name puts the value in. For a record, it calls the record's constructor with those values. The object arrives in your method fully built. You never see the JSON text.

Some rules of the translation, which you will meet in the mistakes below:

- A JSON property with no matching component is ignored by default in Spring Boot (its Jackson settings turn off failing on unknown properties).
- A component with no matching JSON property gets its *default*: `null` for a `String`, `0` for an `int`.
- A JSON value of the wrong type, `"year": "nineteen"`, cannot be put in an `int`: Jackson fails, and Spring answers 400 Bad Request.
- JSON that is not valid JSON at all (a missing quote) is also a 400.
- A body whose `Content-Type` no converter can read gives 415 Unsupported Media Type. That is the envelope handed back unopened.

Notice that `@RequestBody` takes the *whole* body. A method has at most one `@RequestBody` parameter. It can sit next to `@PathVariable` parameters; a PUT to `/books/{id}` will have both, in 7.7.

Why a separate record `NewBook`, not `Book`? Because the client should not choose the id. The server gives out ids. If you accepted a `Book`, the client could send `"id": 7` and you would have to decide what that means. A type that has exactly the fields a client may send is clearer. This is the first glimpse of an idea that 7.8 names: the shape the API shows is not always the shape you store.

**Choosing the status.** So far, Spring chose the status: 200 if your method returned normally. But REST, from chapter 4, wants different statuses for different outcomes:

- `201 Created` after a POST that made something, with a `Location` header giving the URL of the new thing.
- `204 No Content` after a DELETE: success, and nothing to send back.
- `404 Not Found` when the id names nothing.

**`ResponseEntity<T>`.** This is not an annotation. It is a plain class from Spring, generic in the type of its body (chapter 3's generics): a `ResponseEntity<Book>` is "a response whose body is a `Book`". It holds three things: a status, headers, and a body. When a handler returns a `ResponseEntity`, the handler adapter uses all three: it sets the status, adds the headers, and writes the body through the message converters exactly as before. If your method returns a plain `Book`, Spring treats it as "status 200, no extra headers, this body". So `ResponseEntity` is the full form, a plain return value the short form.

You build one with static methods that read almost like English:

- `ResponseEntity.ok(book)`: 200 with that body.
- `ResponseEntity.notFound().build()`: 404, no body.
- `ResponseEntity.created(uri).body(book)`: 201, header `Location: <uri>`, that body.
- `ResponseEntity.noContent().build()`: 204, no body.
- `ResponseEntity.status(HttpStatus.CONFLICT).body(x)`: any status you like.

`build()` means "finish, with no body". `body(x)` means "finish, with this body". Between the start and the finish you may add headers.

`created` takes a `java.net.URI`, the address of the new book. You could write `URI.create("/books/" + id)`. Spring offers a helper that builds it from the current request, so it is right even if the class path changes: `ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(id).toUri()`. It reads the URL of the request now being served (`http://localhost:8080/books`), adds `/{id}`, fills in the id, and turns it into a `URI`. That is a long line; you will see it written out once below and then reuse it.

A handy pair of methods for the 404 case: `ResponseEntity.of(optional)` returns 200 with the body if the `Optional` has a value, and 404 if it is empty. Chapter 8 (section 8.5) shows a second way, with exceptions; for this chapter `ResponseEntity` is all you need.

**The status code is part of the contract.** Clients do not read your Java. They read statuses. A client that receives 200 with an empty body for a missing book (as in 7.3) has to guess. A 404 tells it plainly. That is why choosing the status is a real design act, not decoration.

### The code

The controller grows a list it can add to. The list must now change, so it cannot be `List.of`; and because two requests can run at once on two threads (7.1), use a thread-safe list for now. Section 7.7 replaces this with a proper service.

src/main/java/com/example/library/book/NewBook.java
```java
package com.example.library.book;

public record NewBook(String title, String author, int year) {
}
```

src/main/java/com/example/library/book/BookController.java
```java
package com.example.library.book;

import java.net.URI;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@RequestMapping("/books")
public class BookController {

    private final List<Book> books = new CopyOnWriteArrayList<>();
    private final AtomicLong nextId = new AtomicLong(1);

    @GetMapping
    public List<Book> list() {
        return books;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Book> one(@PathVariable long id) {
        return ResponseEntity.of(
                books.stream().filter(b -> b.id() == id).findFirst());
    }

    @PostMapping
    public ResponseEntity<Book> add(@RequestBody NewBook request) {
        Book book = new Book(nextId.getAndIncrement(),
                request.title(), request.author(), request.year());
        books.add(book);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(book.id())
                .toUri();
        return ResponseEntity.created(location).body(book);
    }
}
```

`AtomicLong` is a `long` that two threads can increase at once without both getting the same number; `getAndIncrement()` returns the current value and adds one. Restart the app in the first terminal, then in the second:

<!-- code: id=books-post unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ curl -i -X POST localhost:8080/books -H "Content-Type: application/json" -d '{"title":"Kindred","author":"Octavia E. Butler","year":1979}'
HTTP/1.1 201
Location: http://localhost:8080/books/1
Content-Type: application/json

{"id":1,"title":"Kindred","author":"Octavia E. Butler","year":1979}
$ curl -i localhost:8080/books/1
HTTP/1.1 200
Content-Type: application/json

{"id":1,"title":"Kindred","author":"Octavia E. Butler","year":1979}
$ curl -i localhost:8080/books/99
HTTP/1.1 404
Content-Length: 0
```

The 404 has no body: `notFound().build()`, which `ResponseEntity.of` uses, sends none.

### The trace

Follow the POST.

| Step | Who | What happens |
|---|---|---|
| 1 | Tomcat → DispatcherServlet | `POST /books`, header `Content-Type: application/json`, body `{"title":"Kindred",...}`. |
| 2 | Handler mapping | `@RequestMapping("/books")` + `@PostMapping` = POST `/books` → `add`. |
| 3 | Handler adapter | Parameter has `@RequestBody`; type `NewBook`; content type JSON. Asks converters; Jackson can read it. |
| 4 | Jackson | Parses the text, matches `title`, `author`, `year` to the record's components, calls `new NewBook("Kindred", "Octavia E. Butler", 1979)`. |
| 5 | Your method | Gives id 1, stores the `Book`, builds `http://localhost:8080/books/1`, returns `ResponseEntity` 201 + `Location` + body. |
| 6 | Handler adapter | Sets status 201, adds the header, hands the body `Book` to Jackson. |
| 7 | Jackson → Tomcat | Writes `{"id":1,...}`; Tomcat sends it. |

```text
JSON text ──Jackson──> NewBook ──> add(...) ──> ResponseEntity
                                                 ├─ status  201
                                                 ├─ headers Location: .../books/1
                                                 └─ body    Book ──Jackson──> JSON text
```

### What goes wrong

**Forgetting the content type.** `curl -i -X POST localhost:8080/books -d '{"title":"Dune"}'` gives

```text
HTTP/1.1 415
Content-Type: application/json

{"timestamp":"2026-11-18T10:10:00.000+00:00","status":415,"error":"Unsupported Media Type","path":"/books"}
```

and the log says `Content-Type 'application/x-www-form-urlencoded;charset=UTF-8' is not supported`. Add `-H "Content-Type: application/json"`.

**Forgetting `@RequestBody`.** Without it, Spring does not read the body at all. It tries to fill `NewBook` from query parameters instead, finds none, and your method receives a `NewBook` full of `null`s and `0`. You get a 201 with `"title":null`. No error, just wrong data: the most dangerous kind. If you see nulls, look for the missing annotation first.

**Broken JSON.** A missing closing brace or quote gives 400, and the log mentions `JSON parse error`. Single quotes around the whole `-d` argument in the shell and double quotes inside it, as above, avoid most of these.

**A misspelt property.** `{"titel":"Dune"}` is not an error: unknown properties are ignored, and `title` arrives as `null`. Chapter 8 (section 8.2) adds validation to catch this.

**Returning `ResponseEntity` without a body type.** Writing `ResponseEntity` with no `<Book>` compiles with a warning about a raw type. Always give the type parameter, or `<Void>` for responses with no body.

### Remember

- `Content-Type: application/json` tells the server the body is JSON; without it, curl sends a form type and Spring answers 415.
- `@RequestBody` on one parameter: the handler adapter, at each request, has a message converter (Jackson) turn the body into that type.
- Jackson fills a record through its constructor, by property name; unknown names are ignored, missing ones get defaults, wrong types give 400.
- `ResponseEntity<T>` is status + headers + body. A plain return value means 200.
- 201 with `Location` after creating; 204 after deleting; 404 for a missing id. `ResponseEntity.of(optional)` gives 200 or 404.

**Check yourself**

1. POST a book with `"year":"soon"`. Predict the status, then try it.

<details><summary>Answer</summary>

400 Bad Request. Jackson cannot put the text `"soon"` into an `int`, so the method is never called.
</details>

2. Change `one` so that it does not use `ResponseEntity.of`, but an `if` with `ResponseEntity.ok(...)` and `ResponseEntity.notFound().build()`.

<details><summary>Answer</summary>

```java
@GetMapping("/{id}")
public ResponseEntity<Book> one(@PathVariable long id) {
    var found = books.stream().filter(b -> b.id() == id).findFirst();
    if (found.isPresent()) {
        return ResponseEntity.ok(found.get());
    }
    return ResponseEntity.notFound().build();
}
```
</details>

3. Send `{"title":"Dune","author":"Frank Herbert","year":1965,"id":500}`. What id does the new book get, and why?

<details><summary>Answer</summary>

The next id from `nextId`, not 500. `NewBook` has no `id` component, so Jackson ignores the property; the server alone chooses ids.
</details>

## 7.7 Create, read, update and delete books

### The question

You can list, read and add. A library also fixes typos in titles and withdraws old books. And your controller has quietly grown a second job: it stores books, hands out ids, searches. Chapter 5 said a controller should talk HTTP and leave the work to a service. How do you finish the four operations, and where does each piece of code belong?

### The picture

At the front desk of the library, the clerk takes your form and checks it is filled in, but he does not walk into the stacks. The stack keeper does that: she knows where every book is, gives new books their numbers, and takes withdrawn ones off the shelf. The clerk speaks to visitors; the keeper speaks to shelves. Neither does the other's job. Where the picture stops being true: here the "shelves" are a `Map` in memory, so every book vanishes when the app stops. Chapter 11 brings a real database.

### The idea

**CRUD.** Create, Read, Update, Delete: the four things you do with stored data. In REST (chapter 4) they line up with HTTP methods on two kinds of URL: the *collection* `/books` and one *item* `/books/{id}`.

| Operation | Method and path | Body in | Success answer |
|---|---|---|---|
| list | `GET /books` | none | 200, a JSON array |
| read one | `GET /books/{id}` | none | 200, the book; 404 if none |
| create | `POST /books` | the new book | 201, `Location`, the book |
| update | `PUT /books/{id}` | the whole new version | 200, the book; 404 if none |
| delete | `DELETE /books/{id}` | none | 204; 404 if none |

**PUT means replace.** `PUT /books/3` with a body says: "the book at this address is now exactly this". The client sends all the fields, and the id comes from the path, not the body. (A `PATCH` would change only some fields; this book does not use it.) PUT is *idempotent*: sending the same PUT twice leaves the same result as sending it once. That is a property clients rely on when they retry after a network failure. POST is not idempotent: two POSTs make two books.

**Where the work goes.** The controller's job, after this section: read the HTTP parts (path variable, body), call the service, choose a status. The service's job: store, find, change, remove, hand out ids. The controller gets the service through its constructor, as in chapter 5 (PRACTICES rule 4). This split pays off in chapter 12: the service will switch from a `Map` to a database, and the controller will not change one line.

**`@Service`.** You met it in chapter 5: a stereotype annotation, read by component scanning at start-up; it carries `@Component`, so the class becomes a bean. It tells Spring nothing more than that; the name tells *people* "this class holds business logic".

**A thread-safe map.** The service keeps books in a `Map<Long, Book>`, from id to book. There is exactly one service bean, and Tomcat runs requests on many threads, so two requests may change the map at the same moment. A plain `HashMap` can be corrupted by that. `ConcurrentHashMap` is a `Map` made for it: many threads can read and write at once safely. Ids come from an `AtomicLong`, as in 7.5. Keep the map's entries in id order for nicer listings: you will sort when listing.

The service returns `Optional<Book>` for "may not be there" (find, update) and `boolean` for "did I delete something". It knows nothing about HTTP: no `ResponseEntity`, no status codes. The controller translates: empty `Optional` → 404, `false` → 404.

**`@PutMapping` and `@DeleteMapping`.** Same reader as `@GetMapping` (the handler mapping, at start-up), same kind of card, different HTTP method.

**`ResponseEntity<Void>`.** For DELETE there is no body. `Void` (capital V) is the type for "no value"; `ResponseEntity<Void>` says "this response never has a body". `ResponseEntity.noContent().build()` gives one with status 204.

**DTOs, in one page.** You already made `NewBook` in 7.5, a type that has only what a client may send. That is a *DTO*, a Data Transfer Object: a plain type whose only job is to carry data across a boundary, here the HTTP boundary. It has no behaviour, and is a natural fit for a record.

Why bother, when you could send and receive `Book` itself? Because what you *store* and what you *show* drift apart over time, and you want to be able to change one without breaking the other.

- **Fields the client must not set.** The id, a creation time, a count of loans. If the input type has them, a client can send them. `NewBook` simply has no `id`.
- **Fields the client must not see.** Later, a `Member` will be stored with an email and maybe a password hash. If you return the stored type, Jackson writes *every* property, including those. A response DTO lists only what is public, so nothing leaks by accident.
- **A stable contract.** In chapter 12, `Book` becomes a JPA entity with annotations, links to other entities and fields for the database. If the API returned the entity, every change to the table would change the JSON your clients depend on. With a DTO, the JSON changes only when you change the DTO.

The cost is a little copying: a method that turns a `Book` into a `BookResponse` and a `NewBook` into a `Book`. Keep those conversions in one place, for example a static method `from` on the response record. In this chapter `Book` is still a plain record whose fields are all public-safe, so you return `Book` directly and use `NewBook` for input; the practice tasks of 7.12 add a response DTO for members, where it matters. Where DTOs live: next to the feature, in the `book` package.

### The code

src/main/java/com/example/library/book/BookService.java
```java
package com.example.library.book;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Service;

@Service
public class BookService {

    private final Map<Long, Book> books = new ConcurrentHashMap<>();
    private final AtomicLong nextId = new AtomicLong(1);

    public List<Book> findAll() {
        return books.values().stream()
                .sorted(Comparator.comparingLong(Book::id))
                .toList();
    }

    public Optional<Book> findById(long id) {
        return Optional.ofNullable(books.get(id));
    }

    public Book create(NewBook request) {
        long id = nextId.getAndIncrement();
        Book book = new Book(id, request.title(), request.author(), request.year());
        books.put(id, book);
        return book;
    }

    public Optional<Book> update(long id, NewBook request) {
        Book replacement = new Book(id, request.title(), request.author(), request.year());
        return Optional.ofNullable(books.computeIfPresent(id, (key, old) -> replacement));
    }

    public boolean delete(long id) {
        return books.remove(id) != null;
    }
}
```

`computeIfPresent` replaces the value only if the key is there, in one safe step, and returns the new value (or `null` if the key was missing). `Optional.ofNullable` turns that `null` into an empty `Optional`.

src/main/java/com/example/library/book/BookController.java
```java
package com.example.library.book;

import java.net.URI;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@RequestMapping("/books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @GetMapping
    public List<Book> list() {
        return bookService.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Book> one(@PathVariable long id) {
        return ResponseEntity.of(bookService.findById(id));
    }

    @PostMapping
    public ResponseEntity<Book> create(@RequestBody NewBook request) {
        Book book = bookService.create(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(book.id())
                .toUri();
        return ResponseEntity.created(location).body(book);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Book> replace(@PathVariable long id, @RequestBody NewBook request) {
        return ResponseEntity.of(bookService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        if (bookService.delete(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
```

One constructor, so no `@Autowired` (PRACTICES rule 4). Restart the app in the first terminal; in the second, walk through all four operations.

<!-- code: id=books-crud unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ curl -i -X POST localhost:8080/books -H "Content-Type: application/json" -d '{"title":"A Wizard of Earthesa","author":"Ursula K. Le Guin","year":1968}'
HTTP/1.1 201
Location: http://localhost:8080/books/1
Content-Type: application/json

{"id":1,"title":"A Wizard of Earthesa","author":"Ursula K. Le Guin","year":1968}
$ curl -i -X PUT localhost:8080/books/1 -H "Content-Type: application/json" -d '{"title":"A Wizard of Earthsea","author":"Ursula K. Le Guin","year":1968}'
HTTP/1.1 200
Content-Type: application/json

{"id":1,"title":"A Wizard of Earthsea","author":"Ursula K. Le Guin","year":1968}
$ curl -i localhost:8080/books
HTTP/1.1 200
Content-Type: application/json

[{"id":1,"title":"A Wizard of Earthsea","author":"Ursula K. Le Guin","year":1968}]
$ curl -i -X DELETE localhost:8080/books/1
HTTP/1.1 204

$ curl -i -X DELETE localhost:8080/books/1
HTTP/1.1 404
Content-Length: 0

```

The second DELETE is a 404: the book is already gone.

### The trace

Follow `PUT /books/1`.

| Step | Who | What happens |
|---|---|---|
| 1 | DispatcherServlet | Receives PUT `/books/1`; handler mapping finds `replace` via `@PutMapping("/{id}")`. |
| 2 | Handler adapter | `@PathVariable long id` ← `"1"` → `1L`. `@RequestBody NewBook` ← Jackson reads the JSON body. |
| 3 | `BookController.replace` | Calls `bookService.update(1, request)`. |
| 4 | `BookService.update` | `computeIfPresent` finds key 1, stores the new `Book(1, "A Wizard of Earthsea", ...)`, returns it in an `Optional`. |
| 5 | `BookController.replace` | `ResponseEntity.of(...)`: value present → 200 with the book. |
| 6 | Handler adapter, Jackson | Status 200, body written as JSON. |

```text
HTTP world                      |  Java world
                                |
PUT /books/1 + JSON ──> BookController ──> BookService ──> Map<Long, Book>
                        (paths, bodies,    (ids, storing,
                         status codes)      finding)
200 + JSON  <────────── ResponseEntity <── Optional<Book>
```

### What goes wrong

**Forgetting `@Service`.** Start-up fails: `Parameter 0 of constructor in com.example.library.book.BookController required a bean of type 'com.example.library.book.BookService' that could not be found.` You met this in chapter 5. Scanning never made a bean because nothing labelled the class.

**Using `HashMap`.** Nothing fails when you test alone with curl. Under load, two threads writing at once can lose entries or worse. Bugs that show up only under load are the hardest to find, so choose `ConcurrentHashMap` from the start.

**Putting the id in the body and the path.** If `PUT /books/1` took a `Book` with `"id": 2`, which wins? Avoid the question: the input DTO has no id; the path is the only source.

**Expecting data to survive a restart.** Stop the app, start it, and `GET /books` returns `[]`. That is not a bug: the `Map` lives in memory. Chapter 11 fixes it.

**Returning a body with 204.** `ResponseEntity.noContent()` has no `body(...)` method for a reason: a 204 must not have a body.

### Remember

- CRUD maps to `GET` collection, `GET` item, `POST` collection, `PUT` item, `DELETE` item; statuses 200, 200/404, 201, 200/404, 204/404.
- PUT replaces the whole thing, takes the id from the path, and is idempotent; POST is not.
- The controller handles HTTP; the `@Service` bean handles data, knows nothing of HTTP, and is injected through the constructor.
- One service bean serves every thread: use `ConcurrentHashMap` and `AtomicLong`.
- A DTO is a plain type that carries data across the HTTP boundary; it keeps what clients send and see separate from what you store.

**Check yourself**

1. Send the same PUT twice, then the same POST twice. Count the books after each. Which is idempotent?

<details><summary>Answer</summary>

Two identical PUTs leave one book with the same content: idempotent. Two identical POSTs make two books with different ids: not idempotent.
</details>

2. Add `GET /books/count` returning a number, and move the counting into the service.

<details><summary>Answer</summary>

In `BookService`: `public int count() { return books.size(); }`. In `BookController`: `@GetMapping("/count") public int count() { return bookService.count(); }`. The literal path wins over `/{id}`.
</details>

3. Write a response DTO `BookSummary(long id, String title)` and an endpoint `GET /books/summaries` that returns only ids and titles.

<details><summary>Answer</summary>

```java
public record BookSummary(long id, String title) {
    static BookSummary from(Book book) {
        return new BookSummary(book.id(), book.title());
    }
}
```

```java
@GetMapping("/summaries")
public List<BookSummary> summaries() {
    return bookService.findAll().stream().map(BookSummary::from).toList();
}
```
</details>

## 7.12 Practice: the books and members endpoints, in memory

### The question

You have built the books API. Now you will build its twin for members, alone. Before that, one skill you need more than any annotation: when curl answers 404, 405 or 415, how do you find out *which* card in Spring's index was missing, and fix it fast?

### The picture

When a letter comes back marked "return to sender", the stamp tells you why: "no such address", "addressee does not accept parcels", "wrong envelope". You do not rewrite the whole letter. You read the stamp and fix that one thing. The three statuses are those stamps. Where the picture stops being true: the post office never tells you what it *did* find; Spring's log often does, if you look in the first terminal.

### The idea

Each of the three errors happens at a different step of the trace you have drawn all chapter, and each step points to a different line of your code.

**404 Not Found: no card for the path.** The handler mapping looked for a pattern matching the path and found none (or your own code returned `notFound()`; tell them apart by the body: Spring Boot's own 404 has the JSON error body with `"path"`, yours from `ResponseEntity.notFound()` is empty). Causes, from most to least common:

- A typo in the URL or in the mapping: `/book` against `/books`.
- The class-level `@RequestMapping` forgotten, so the method is at `/{id}` instead of `/books/{id}`.
- The controller is not a bean: it is outside `com.example.library`, or it has no `@RestController`.
- The app you are calling is an old copy, started before your change. Restart.

How to check: does any method's full path (class path + method path) match the URL, segment by segment?

**405 Method Not Allowed: a card for the path, not for this method.** The path matched a pattern, but no handler for this HTTP method. The response carries an `Allow` header listing the methods that would work; read it. Causes: `@GetMapping` where you meant `@PutMapping`; a curl call missing `-X PUT` (curl with `-d` defaults to POST); or a method you never wrote.

**415 Unsupported Media Type: the envelope is wrong.** The handler was found, it has a `@RequestBody`, but no message converter can read the request's `Content-Type` into the parameter's type. Nearly always: curl without `-H "Content-Type: application/json"`. Less often: a typo in that header, such as `application/jason`.

And two more you met: **400** (a path variable or body could not be converted; the method was never called) and **500** (your method, or a converter, threw an exception; chapter 8 is about turning those into proper answers).

The method is always the same: read the status, place it on the trace, and look at the one annotation or curl option that belongs to that step.

### The code

Break the working books API on purpose and watch each stamp. App running in the first terminal; in the second:

<!-- code: id=break-it unrun="needs Spring Boot's libraries from Maven Central, not reachable on this machine" -->
```console
$ curl -i localhost:8080/book/1
HTTP/1.1 404
Content-Type: application/json

{"timestamp":"2026-11-18T10:20:00.000+00:00","status":404,"error":"Not Found","path":"/book/1"}
$ curl -i -X PATCH localhost:8080/books/1 -H "Content-Type: application/json" -d '{"title":"Dune"}'
HTTP/1.1 405
Allow: GET,PUT,DELETE
Content-Type: application/json

{"timestamp":"2026-11-18T10:20:01.000+00:00","status":405,"error":"Method Not Allowed","path":"/books/1"}
$ curl -i -X POST localhost:8080/books -d '{"title":"Dune","author":"Frank Herbert","year":1965}'
HTTP/1.1 415
Content-Type: application/json

{"timestamp":"2026-11-18T10:20:02.000+00:00","status":415,"error":"Unsupported Media Type","path":"/books"}
```

The exact list in `Allow` may also include `HEAD` and `OPTIONS`, which Spring answers for you.

### The trace

Where each status is decided:

| Step | Who | Can stop with |
|---|---|---|
| 1 | Handler mapping: any pattern for this path? | 404 |
| 2 | Handler mapping: any handler for this method on that path? | 405 |
| 3 | Handler adapter: `@RequestBody` readable from this `Content-Type`? | 415 |
| 4 | Handler adapter: path variables, params and body convertible? | 400 |
| 5 | Your method runs | your status, or 500 if it throws |

```text
path? ──no──> 404
  │yes
method? ──no──> 405
  │yes
content type? ──no──> 415
  │yes
convert? ──no──> 400
  │yes
your method ──> 200 / 201 / 204 / 404 ... (or 500)
```

### What goes wrong

- **Fixing the wrong layer.** A 415 is never fixed in the service. A 404 from Spring's error body is never fixed by changing `ResponseEntity`. Place the status first.
- **Testing an old app.** Changes to Java need a restart. If nothing you change makes a difference, check the start-up time in the first terminal.
- **Reading only the status.** The log in the first terminal usually names the cause, for example `Request method 'PATCH' is not supported` or `Content-Type '...' is not supported`.

### Remember

- 404: no pattern for the path. 405: path known, method not (read `Allow`). 415: body's `Content-Type` unreadable. 400: conversion failed. 500: something threw.
- Each status belongs to one step of the trace, and each step to one annotation or one curl option.

**Check yourself**

The tasks grow harder. Do them in order; each builds on the last. Members live in `com.example.library.member`.

1. **Do it again.** Without looking, add to `BookController` a method that answers `GET /books?author=...` filtering by author, using a `findByAuthor(String)` method on `BookService`. Plain `GET /books` must still list all.

<details><summary>Answer</summary>

In `BookService`:

```java
public List<Book> findByAuthor(String author) {
    return findAll().stream()
            .filter(b -> b.author().equalsIgnoreCase(author))
            .toList();
}
```

In `BookController`, change `list`:

```java
@GetMapping
public List<Book> list(@RequestParam(required = false) String author) {
    return author == null ? bookService.findAll() : bookService.findByAuthor(author);
}
```
</details>

2. **A member record and a service.** Create `Member(long id, String name, String email)`, `NewMember(String name, String email)` and a `MemberService` bean storing members in a `ConcurrentHashMap`, with `findAll`, `findById`, `create`.

<details><summary>Answer</summary>

```java
public record Member(long id, String name, String email) {
}
```

```java
public record NewMember(String name, String email) {
}
```

```java
@Service
public class MemberService {

    private final Map<Long, Member> members = new ConcurrentHashMap<>();
    private final AtomicLong nextId = new AtomicLong(1);

    public List<Member> findAll() {
        return members.values().stream()
                .sorted(Comparator.comparingLong(Member::id))
                .toList();
    }

    public Optional<Member> findById(long id) {
        return Optional.ofNullable(members.get(id));
    }

    public Member create(NewMember request) {
        long id = nextId.getAndIncrement();
        Member member = new Member(id, request.name(), request.email());
        members.put(id, member);
        return member;
    }
}
```
</details>

3. **A response DTO.** Members' emails are private. Write `MemberResponse(long id, String name)` with a static `from(Member)`, and a `MemberController` at `/members` with `GET /members`, `GET /members/{id}` (404 if absent) and `POST /members` (201 with `Location`), all returning `MemberResponse`, never `Member`.

<details><summary>Answer</summary>

```java
public record MemberResponse(long id, String name) {
    static MemberResponse from(Member member) {
        return new MemberResponse(member.id(), member.name());
    }
}
```

```java
@RestController
@RequestMapping("/members")
public class MemberController {

    private final MemberService memberService;

    public MemberController(MemberService memberService) {
        this.memberService = memberService;
    }

    @GetMapping
    public List<MemberResponse> list() {
        return memberService.findAll().stream().map(MemberResponse::from).toList();
    }

    @GetMapping("/{id}")
    public ResponseEntity<MemberResponse> one(@PathVariable long id) {
        return ResponseEntity.of(memberService.findById(id).map(MemberResponse::from));
    }

    @PostMapping
    public ResponseEntity<MemberResponse> create(@RequestBody NewMember request) {
        Member member = memberService.create(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(member.id()).toUri();
        return ResponseEntity.created(location).body(MemberResponse.from(member));
    }
}
```

`Optional.map` turns an `Optional<Member>` into an `Optional<MemberResponse>`, still empty if there was no member.
</details>

4. **Find and fix: 404.** A friend's controller answers 404 to `GET /members/1` though the member exists. What is wrong?

```java
@RestController
public class MemberController {
    @GetMapping("/{id}")
    public ResponseEntity<MemberResponse> one(@PathVariable long id) { ... }
}
```

<details><summary>Answer</summary>

The class has no `@RequestMapping("/members")`, so the method answers `/{id}`, that is `/1`, not `/members/1`. Spring's handler mapping has no pattern for `/members/1`: 404 with Spring's JSON error body. Add `@RequestMapping("/members")` to the class (and check the other methods' paths).
</details>

5. **Find and fix: 405.** `curl -i -X DELETE localhost:8080/members/1` gives 405 with `Allow: GET`. Explain and fix by adding `delete` to the service and the controller (204, or 404 if absent).

<details><summary>Answer</summary>

There is a pattern for `/members/{id}`, but only a GET handler. Add `public boolean delete(long id) { return members.remove(id) != null; }` to `MemberService` and to the controller:

```java
@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable long id) {
    return memberService.delete(id)
            ? ResponseEntity.noContent().build()
            : ResponseEntity.notFound().build();
}
```
</details>

6. **Find and fix: 415, and a silent bug.** A friend runs `curl -i -X POST localhost:8080/members -d '{"name":"Ada","email":"ada@example.com"}'` and gets 415. She adds the header, gets 201, but the answer is `{"id":1,"name":null}`. Two bugs: name them.

<details><summary>Answer</summary>

First, the missing `-H "Content-Type: application/json"`: curl sent a form type, which no converter reads into `NewMember`, so 415. Second, the `create` parameter has no `@RequestBody`: Spring then fills `NewMember` from request parameters, finds none, and passes `null`s. Add `@RequestBody` before `NewMember request`.
</details>

7. **Build it: replace a member.** Add `PUT /members/{id}` that replaces name and email, returns 200 with the `MemberResponse`, or 404. Then show with curl that sending it twice changes nothing more than sending it once.

<details><summary>Answer</summary>

In `MemberService`:

```java
public Optional<Member> update(long id, NewMember request) {
    Member replacement = new Member(id, request.name(), request.email());
    return Optional.ofNullable(members.computeIfPresent(id, (key, old) -> replacement));
}
```

In `MemberController`:

```java
@PutMapping("/{id}")
public ResponseEntity<MemberResponse> replace(@PathVariable long id, @RequestBody NewMember request) {
    return ResponseEntity.of(memberService.update(id, request).map(MemberResponse::from));
}
```

Run the same `curl -i -X PUT localhost:8080/members/1 -H "Content-Type: application/json" -d '{"name":"Ada L.","email":"ada@example.com"}'` twice, then `GET /members`: one member, the same content both times.
</details>

8. **Build it: a member's books.** A member may borrow books. Without a database, keep in `MemberService` a `Map<Long, Set<Long>>` from member id to borrowed book ids (use `ConcurrentHashMap.newKeySet()` for each set). Add `POST /members/{memberId}/books/{bookId}` (borrow: 204; 404 if the member or the book does not exist) and `GET /members/{memberId}/books` (the borrowed `Book`s; 404 if no member). The controller needs both services.

<details><summary>Answer</summary>

In `MemberService`:

```java
private final Map<Long, Set<Long>> borrowed = new ConcurrentHashMap<>();

public void borrow(long memberId, long bookId) {
    borrowed.computeIfAbsent(memberId, k -> ConcurrentHashMap.newKeySet()).add(bookId);
}

public Set<Long> borrowedBookIds(long memberId) {
    return borrowed.getOrDefault(memberId, Set.of());
}
```

`MemberController` takes both beans in its constructor:

```java
public MemberController(MemberService memberService, BookService bookService) {
    this.memberService = memberService;
    this.bookService = bookService;
}

@PostMapping("/{memberId}/books/{bookId}")
public ResponseEntity<Void> borrow(@PathVariable long memberId, @PathVariable long bookId) {
    if (memberService.findById(memberId).isEmpty() || bookService.findById(bookId).isEmpty()) {
        return ResponseEntity.notFound().build();
    }
    memberService.borrow(memberId, bookId);
    return ResponseEntity.noContent().build();
}

@GetMapping("/{memberId}/books")
public ResponseEntity<List<Book>> borrowedBooks(@PathVariable long memberId) {
    if (memberService.findById(memberId).isEmpty()) {
        return ResponseEntity.notFound().build();
    }
    List<Book> books = memberService.borrowedBookIds(memberId).stream()
            .map(bookService::findById)
            .flatMap(Optional::stream)
            .toList();
    return ResponseEntity.ok(books);
}
```

Import `com.example.library.book.Book` and `BookService` (both public). `flatMap(Optional::stream)` drops ids of books deleted since. Two path variables in one pattern work the same way as one. Chapter 13 replaces this map with a real relationship between tables.
</details>
