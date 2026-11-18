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

