# Plan pattern: a framework or library

For Django, React, Spring, Rails, Flask, pandas. Header: `run:` the language (`python`), `kind: framework`. The language itself is another book: put its ideas in `needs:`, never teach them again.

## The shape

- **Chapter 1** creates the smallest app that runs, changes one thing and sees the change, then draws the picture the whole book hangs on: who calls whom (a request through Django's URL dispatcher to a view and back; a React render triggered by state). The reader writes code the framework calls; say so from the start.
- **Order follows the life of a request or a render**: routing, views or components, templates or state, input and forms, data and the ORM, migrations, authentication, testing, then deployment. Each convention is taught as what the framework does for you, then what it costs when you fight it.
- **Carried through:** one app that grows a feature each chapter (a booking site, a reading list), so later chapters edit earlier code like real work.
- **Tests from the chapter that first has logic**, using the framework's own test client.
- **Practice:** add a feature to the app; read an error that comes from deep in framework code.

## What weak plans miss

Decorators and annotations used as magic with no section on what they do; reading a stack trace through framework frames; security the framework gives you and how to break it (CSRF, escaping, SQL parameters); migrations on data that already exists; deployment and settings per environment; versions (frameworks change their recommended way often: set `Versions:` on the sheet).

## Sample

Weak: a chapter of features with no app (`5.1 Forms`, `5.2 Fields`, `5.3 Widgets`). Better:

```text
### 5 Forms: taking input safely
5.1 The guest who typed a script tag | story
5.2 What happens when a form is posted | teaches: post-request | needs: url-dispatch | fig
5.3 A Form class: fields, validation, cleaned data | teaches: form-class, cleaned-data
5.4 Showing errors back to the user | teaches: bound-form, form-errors
5.5 The CSRF token and why Django insists on it | teaches: csrf-token | level: 2
5.6 A form made from a model | teaches: model-form | needs: model-class
5.7 Redirect after a post | short | teaches: post-redirect-get
5.8 Testing a form view | teaches: test-client-post | needs: test-client | level: 3
5.9 Practice: the booking form, from blank page to tested | practice | level: 3
```

It opens on a threat, shows the request cycle before the API, and ends with the form tested inside the running app.
