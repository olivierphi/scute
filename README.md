# Scute

Scute is a small Dependency Injection Container for Python 3.6+, ported from PHP's [Pimple](https://github.com/silexphp/Pimple/tree/1.1), that consists
of just one file and one class (about 100 lines of code).

The test suite, and even this README file, are basically a copy-n-paste of Pimple's ones, with only a light adaptation to Python
and some Pythonic additions like decorators.

So all kudos go to [Fabien Potencier](http://fabien.potencier.org/) and to Pimple contributors!


Install it from PyPi:

```bash
    $ pip install scute
```

Then import it in your code, and you're good to go:

```python
    from scute import Container
```

Creating a container is a matter of instating the `Container` class:

```python
    container = Container()
```

As many other dependency injection containers, Scute is able to manage two
different kind of data: *services* and *parameters*.

(note that a quick look at [the test suite](scute/tests/test_container.py) can also give you a pretty good overview of this module features)

Defining Parameters
-------------------

Defining a parameter is as simple as using the Scute instance as an array:

```python
    # define some parameters
    container['cookie_name'] = 'SESSION_ID'
    container['session_storage_class'] = 'SessionStorage'
```

Defining Services
-----------------

A service is an object that does something as part of a larger system.
Examples of services: Database connection, templating engine, mailer. Almost
any object could be a service.

Services are defined by callables (lambda, functions or callable classes) that return an instance of an
object:

```python
    // #define some services
    define session_storage(c: Container):
        session_storage_class_ref = getattr(importlib.import_module('app'), c['session_storage_class'])
        return session_storage_class_ref(c['cookie_name'])
    container['session_storage'] = session_storage

    container['session'] = labmda c: new Session(c['session_storage'])
```

Notice that the function has access to the current container
instance, allowing references to other services or parameters.

As objects are only created when you get them, the order of the definitions
does not matter, and there is no performance penalty.

Using the defined services is also very easy:

```python
    # get the session object
    session = container['session']

    # the above call is roughly equivalent to the following code:
    # storage = app.SessionStorage('SESSION_ID')
    # session = Session(storage)
```

Defining Factory Services
------------------------

By default, each time you get a service, Scute returns the same instance of it.
If you want a different instance to be returned for all calls, wrap your callable with the `factory()` method:

```python
    container['session'] = container.factory(lambda c: new Session(c['session_storage'])
```

Now, each call to `container['session']` returns a new instance of the session.

Protecting Parameters
---------------------

Because Scute sees callables as service definitions, you need to
wrap anonymous functions with the `protect()` method to store them as
parameter:

```python
    container['random'] = container.protect(lambda: randrange(10000))
```

Modifying services after creation
---------------------------------

In some cases you may want to modify a service definition after it has been
defined. You can use the `extend()` method to define additional code to
be run on your service just after it is created:

```python
    container['mail'] = lambda c: MailjetApi(user = c['email.user'], password = ['email.password'])

    def extended_email(mail, c: Container):
        mail.set_from(c['mail.default_from'])
        return mail
    container.extend('mail', extended_email)
```

The first argument is the name of the object, the second is a callable that
gets access to the object instance and the container. The return value is
a service definition, so you need to re-assign it on the container.

Fetching the service creation function
--------------------------------------

When you access an object, Scute automatically calls the callable (function, lambda, callable class...)
that you defined, which creates the service object for you. If you want to get
raw access to this function, you can use the `raw()` method:

```python
    session_function = container.raw('session')
```

Managing injections with a decorator
------------------------------------

You can also manage a callable dependencies with a decorator:

```python
    @container.bind_callable(('mailer', 'signal'))
    def send_email(mailer: Mailer, email_sent_signal: Signal):
        mailer.send_email(config)
        email_sent_signal.send()

```

But if you add the `injection_id` parameter, this callable will also be a service itself!


```python
    @container.bind_callable(('config', 'mailer', 'signal'), injection_id='app_mailer')
    def app_mailer(config: tuple, mailer: Mailer, signal: Signal):
        mailer.add_config(config)
        mailer.set_signal(signal)

        return mailer

    # your container now has a new 'app_mailer' service, that can be injected into other services
```
