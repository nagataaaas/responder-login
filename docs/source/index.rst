.. Responder-Login documentation master file, created by
   sphinx-quickstart on Sun Feb 24 01:43:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Simple Login/Logout Management for Responder
================================================
|image1| |image2| |image3|

.. |image1| image:: https://img.shields.io/pypi/v/responder-login.svg
   :target: https://pypi.org/project/responder/
.. |image2| image:: https://img.shields.io/pypi/l/responder-login.svg
   :target: https://pypi.org/project/responder/
.. |image3| image:: https://img.shields.io/pypi/pyversions/responder-login.svg
   :target: https://pypi.org/project/responder/

Powered by `Yamato Nagata <https://twitter.com/514YJ>`_.
Responder-Login provides simple user session management.


The basic idea is based on `Flask-Login <https://github.com/maxcountryman/flask-login>`_

Features
=========
- Simple login/logout management
- Provides easy Login_Required/Login_Prohibited decorating.
- Storing user object in session.

.. contents::
   :local:
   :backlinks: none

Instllation
===========

Install with pip::

   $pip install responder_login

Configuring Application
=======================

Before you use Responder_Login, you have to make instance of `LoginManager`

.. code:: python

   import responder
   from responder_login import LoginManager

   api = responder.API()
   lm = LoginManager()
   lm.init_app(api)  # or you can do lm = LoginManager(api)

How It Works
------------
To make this work, You have to provide `~LoginManager.user_loader` callback.
callback is used to specify user object with the data which stored in the session. This should take `unicode` and return the instance of user object. If no object found, please return `None`. Then, the instance of `~AnonymousUserMixin` object will be an returned.

.. code:: python

   @lm.user_loader
   def load_user(user_id):
      return User.get(user_id)

Custom User Object
==================
This section is quoted from `Flask-Login documentation <https://flask-login.readthedocs.io/en/latest/#your-user-class>`_
The class that you use to represent users needs to implement these properties and methods:

`is_authenticated`
    This property should return `True` if the user is authenticated, i.e. they
    have provided valid credentials. (Only authenticated users will fulfill
    the criteria of `login_required`.)

`is_active`
    This property should return `True` if this is an active user - in addition
    to being authenticated, they also have activated their account, not been
    suspended, or any condition your application has for rejecting an account.
    Inactive accounts may not log in (without being forced of course).

`is_anonymous`
    This property should return `True` if this is an anonymous user. (Actual
    users should return `False` instead.)

`get_id()`
    This method must return a `unicode` that uniquely identifies this user,
    and can be used to load the user from the `~LoginManager.user_loader`
    callback. Note that this **must** be a `unicode` - if the ID is natively
    an `int` or some other type, you will need to convert it to `unicode`.

To make implementing a user class easier, you can inherit from `UserMixin`,
which provides default implementations for all of these properties and methods.
(It's not required, though.)

Login Example
=============

We can use `~LoginManager.login_user` to log users in.

for example.

.. code:: python

    @api.route("/login")
    async def login(req, resp):
        if req.method == "get":
            # this returns the form let the users
            # input and send server some data to specify User Object
            resp.html = """
            Login<br>
            <form action="/login" method="post">
            <input name="name"><label>name</label></input><br>
            <input name="age"><label>age</label></input><br>
            <button type="submit">submit</button>
            </form>"""
        else:
            data = await req.media(format="form")
            user = UserObject(name=data["name"], age=data["age"])
            # We made an UserObject from user's data
            lm.login_user(user)
            # this make users log in.
            resp.html = f"""
            you are now logging in as <br>
            name: {user.name},
            age: {user.age}"""

and then, `~LoginManager.logout_user` to log out.
like this

.. code:: python

   @api.route("/logout")
   def logout(req, resp):
       user = lm.current_user
       lm.logout_user()
       resp.html = f"""logged out the user.<br>
        name: {user.name}<br>
        age: {user.age}"""

But in case if user isn't logged in, above code will raise `AttributeError` when find `name` or `age` in of user.
So, lm provides `~LoginManager.login_required` decorator. like below.


.. code:: python

   @api.route("/logout")
   @lm.login_required
   def logout(req, resp):
       user = lm.current_user
       lm.logout_user()
       resp.html = f"""logged out the user.<br>
        name: {user.name}<br>
        age: {user.age}"""

and, If you want to make some page you don't want logged in user to get in,
you can set `~LoginManager.login_prohibited` decorator.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
