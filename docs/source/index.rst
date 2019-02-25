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
`Github <https://github.com/delta114514/responder-login>`_ -- 
`Simple example <https://github.com/delta114514/responder-login/blob/master/example/example_2.py>`_


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

Before you use Responder_Login, you have to make instance of :code:`LoginManager`

.. code:: python

   import responder
   from responder_login import LoginManager

   api = responder.API()
   lm = LoginManager()
   lm.init_app(api)  # or you can do lm = LoginManager(api)

How It Works
------------
To make this work, You have to provide :code:`LoginManager.user_loader` callback.
callback is used to specify user object with the data which stored in the session. This should take :code:`unicode` and return the instance of user object. If no object found, please return :code:`None`. Then, the instance of :code:`AnonymousUserMixin` object will be an returned.

.. code:: python

   @lm.user_loader
   def load_user(user_id):
      return User.get(user_id)

Custom User Object
==================
This section is quoted from `Flask-Login documentation <https://flask-login.readthedocs.io/en/latest/#your-user-class>`_
The class that you use to represent users needs to implement these properties and methods:

`is_authenticated`
    This property should return :code:`True` if the user is authenticated, i.e. they
    have provided valid credentials. (Only authenticated users will fulfill
    the criteria of :code:`login_required`.)

`is_active`
    This property should return :code:`True` if this is an active user - in addition
    to being authenticated, they also have activated their account, not been
    suspended, or any condition your application has for rejecting an account.
    Inactive accounts may not log in (without being forced of course).

`is_anonymous`
    This property should return :code:`True` if this is an anonymous user. (Actual
    users should return :code:`False` instead.)

`get_id()`
    This method must return a :code:`str` that uniquely identifies this user,
    and can be used to load the user from the :code:`LoginManager.user_loader`
    callback. Note that this **must** be a :code:`unicode` - if the ID is natively
    an :code:`int` or some other type, you will need to convert it to :code:`str`.

To make implementing a user class easier, you can inherit from :code:`UserMixin`,
which provides default implementations for all of these properties and methods.
(It's not required, though.)

Login Example
=============

We can use :code:`LoginManager.login_user` to log users in.

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

and then, :code:`LoginManager.logout_user()` to log out.
like this

.. code:: python

   @api.route("/logout")
   def logout(req, resp):
       user = lm.current_user
       lm.logout_user()
       resp.html = f"""logged out the user.<br>
        name: {user.name}<br>
        age: {user.age}"""

But in case if user isn't logged in, above code will raise :code:`AttributeError` when find :code:`name` or :code:`age` in of user.
So, :code:`LoginManager` provides :code:`LoginManager.login_required` decorator. like below.


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
you can set :code:`LoginManager.login_prohibited` decorator.

Customizing
===========

`LoginManager(api=None)`
------------------------
Initialize :code:`LoginManager`.:code:`api` must be an instance of :code:`Responder.API`. :code:`api` can be None or not provided. But, you have to :code:`LoginManager.init_api()`

`LoginManager.init_api(api)`
----------------------------
Set :code:`Responder.API` with given :code:`api`.

`@LoginManager.user_loader`
---------------------------
This decorates callback to set it :code:`LoginManager._user_callback`
callback must take one argument and return instance of User object or :code:`None`.

`@LoginManager.login_required`
------------------------------
The decorator which decorates :code:`Responder.route` callback.
If user want to access decorated route but he/her must log in, this will call :code:`LoginManager._unauthorized_callback` if it's provided. That can be set by decorating callback with :code:`LoginManager.unauthorized_handler` which takes :code:`Request` and :code:`Response`. If :code:`LoginManager._unauthorized_callback` isn't provided, this will redirect to :code:`LoginManager.config["LOGIN_REQUIRED_ROUTE"]` if it's set. If not, return :code:`LoginManager.config["LOGIN_REQUIRED_MESSAGE"]`

`@LoginManager.unauthorized_handler`
------------------------------------
This decorates callback to set it :code:`LoginManager._unauthorized_callback`

`@LoginManager.login_prohibited`
--------------------------------
The decorator which decorates :code:`Responder.route` callback.
If user want to access decorated route but he/her must log out, this will call :code:`LoginManager._authorized_callback` if it's provided. That can be set by decorating callback with :code:`LoginManager.authorized_handler` which takes :code:`Request` and :code:`Response`. If :code:`LoginManager._authorized_callback` isn't provided, this will redirect to :code:`LoginManager.config["LOGIN_PROHIBITED_ROUTE"]` if it's set. If not, return :code:`LoginManager.config["LOGIN_PROHIBITED_MESSAGE"]`

`@LoginManager.authorized_handler`
------------------------------------
This decorates callback to set it :code:`LoginManager._authorized_callback`

`LoginManager.login_user(user)`
-------------------------------
:code:`user` must be an instance of user object. Set cookies with :code:`Response.set_cookie()`

about account data, each value is below:

* key : :code:`LoginManager.config[COOKIE_NAME]["ACCOUNT"]`
* value : :code:`user.get_id()`
* expires : if :code:`LoginManager.config["COOKIE_REMEMBER_ME"]["ACCOUNT"]` (Defaults to :code:`True`), True, :code:`datetime.datetime.now()` + :code:`LoginManager.config["COOKIE_DURATION"]`. Otherwise, :code:`None`
* max_age : if :code:`LoginManager.config["COOKIE_REMEMBER_ME"]["ACCOUNT"]` (Defaults to :code:`True`), True, :code:`LoginManager.config["COOKIE_DURATION"].total_seconds()`. Otherwise, :code:`None`
* secure : :code:`LoginManager.config["COOKIE_SECURE"]` Defaults to :code:`False`
* httponly :  :code:`LoginManager.config["COOKIE_HTTPONLY"]` Defaults to  :code:`False`

 about  :code:`is_fresh`:


* key : :code:`LoginManager.config[COOKIE_NAME]["IS_FRESH"]`
* value : :code:`1`
* expires : if :code:`LoginManager.config["COOKIE_REMEMBER_ME"]["IS_FRESH"]` (Defaults to :code:`False`), :code:`True`, :code:`datetime.datetime.now()` + :code:`LoginManager.config["COOKIE_DURATION"]`. Otherwise, :code:`None`
* max_age : if :code:`LoginManager.config["COOKIE_REMEMBER_ME"]["IS_FRESH"]` (Defaults to True), :code:`True`, :code:`LoginManager.config["COOKIE_DURATION"].total_seconds()`. Otherwise, :code:`none`
* secure : :code:`LoginManager.config["COOKIE_SECURE"]` Defaults to :code:`False`
* httponly : :code:`LoginManager.config["COOKIE_HTTPONLY"]` Defaults to :code:`False`

`LoginManager.logout_user()`
--------------------------
This log users out by setting cookie that :code:`expires` and :code:`max_age` are :code:`0`

`LoginManager.current_user`
---------------------------
This returns instance of user object by searching instance by :code:`LoginManager._user_callback`. If no user found (callback returned :code:`None`), this will return :code:`LoginManager.anonumous_user`

`LoginManager.is_fresh`
-----------------------
Return If the user logging in is logged in current session(not using Remember me). If logged in current session, returns :code:`True`. If not, :code:`False`. This returns :code:`False` if user is not logged in.

`LoginManager.config`
---------------------

* COOKIE_NAME : The dictionary of cookie name. keys are`"ACCOUNT"` and :code:`"IS_FRESH"`. Defaults to :code:`{"ACCOUNT": "account", "IS_FRESH": "fresh" }`
* COOKIE_REMEMBER_ME : The dictionary of setting whether each cookie is Remember-me. keys are`"ACCOUNT"` and :code:`"IS_FRESH"`. Defaults to :code:`{"ACCOUNT": True, "IS_FRESH": False }`
* COOKIE_DURATION : The amount of time before the cookie expires, as a :code:`datetime.timedelta object`. Defaults to :code:`datetime.timedelta(60)`
* COOKIE_SECURE : Restricts the "Remember Me" cookie's scope to https. Defaults to :code:`False`
* COOKIE_HTTPONLY : Prevents the  "Remember Me" cookie from being accessed by client-side scripts. Defaults to :code:`False`
* LOGIN_REQUIRED_ROUTE : The route redirect to if user is not logged in and tried to access endpoint decorated with :code:`LoginManager.login_required`. Defaults to :code:`None`
* LOGIN_REQUIRED_MESSAGE : The default message to display when users need to log in. Defaults to :code:`"Please log in to access this page."`
* LOGIN_PROHIBITED_ROUTE : The route redirect to if user is logged in and tried to access endpoint decorated with :code:`LoginManager.login_prohibited`. Defaults to :code:`None`
* LOGIN_PROHIBITED_MESSAGE : The default message to display when users need to log out. Defaults to :code:`"Please log out to access this page."`

`UserMixin`
-----------
The simple mixin to make user object.

.. code:: python

    class UserMixin:

        @property
        def is_active(self):
            return True

        @property
        def is_authenticated(self):
            return True

        @property
        def is_anonymous(self):
            return False

        def get_id(self):
            try:
                return self.id
            except AttributeError:
                raise NotImplementedError('No `id` attribute. override `get_id` or set `id` attribute')

        def __eq__(self, other):
            if isinstance(other, UserMixin):
                return self.get_id() == other.get_id()
            return NotImplemented

        def __ne__(self, other):
            equal = self.__eq__(other)
            if equal is NotImplemented:
                return NotImplemented
            return not equal

`AnonymousUserMixin`
--------------------
The user mixin for not logged in users

.. code:: python

    class AnonymousUserMixin(UserMixin):
        @property
        def is_authenticated(self):
            return False

        @property
        def is_active(self):
            return False

        @property
        def is_anonymous(self):
            return True

        def get_id(self):
            return None




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


In End
======
Sorry for my poor English.
I want **you** to join us and send many pull requests about Doc, code, features and more!!