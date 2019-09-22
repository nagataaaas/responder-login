# Reponder-Login
The Simple Login/Logout Management for Responder
```python
import responder
from responder_login import LoginManager

api = responder.API()
lm = LoginManager(api)

@api.route("/login_required")
@lm.login_required
def login_required(req, resp):
    resp.text = "You can't see this without logging in!"
```
Powered by [Yamato Nagata](https://twitter.com/514YJ)

[Simple Example](https://github.com/delta114514/responder-login/blob/master/example/example_2.py)

[ReadTheDocs](https://responder-login.readthedocs.io/en/latest/)

The basic idea is based on [Flask-Login](https://github.com/maxcountryman/flask-login)

# Usage

make instance of `LoginManager` with `responder.API`

```python
import responder
from responder_login import LoginManager

api = responder.API()
lm = LoginManager(api)
```

You will use this instance for almost all of Responder-Login features.

Next, you need to make a `class` you want to use in login/logout.
in this example, I use [SQLAlchemy](https://www.sqlalchemy.org/)

```python
from responder_login import UserMixin

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()
url = "sqlite:///database.db"


class Student(Base, UserMixin):
    __tablename__ = "students"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(20))
    grade = sqlalchemy.Column(sqlalchemy.Integer)
    password = sqlalchemy.Column(sqlalchemy.String(20))  # Please encrypt if you use :)

    def get_id(self):
        return str(self.id)


engine = sqlalchemy.create_engine(url, echo=False)
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)
session = scoped_session(SessionMaker)
```

All you have to understand in what I done in above, is making class inheriting `LoginManager.UserMixin` and make attribute `get_id`.

Then you need to set callback which specifies User Object.

```python
@lm.user_loader
def load_user(user_id):
    return session.query(Student).get(user_id)
```
The callback you set to `LoginManager.user_loader` must return a User object or `None`. Do not raise any Exceptions.

Once you made user object and set `LoginManager.user_loader`, you can use all features of Responder-Login.

The simple example is [Here](https://github.com/delta114514/responder-login/blob/master/example/example.py)

# Documentation

### LoginManager(api=None)
Initialize `LoginManager`.`api` must be an instance of `Responder.API`. `api` can be None or not provided. But, you have to `LoginManager.init_api()`

### LoginManager.init_api(api)
Set `Responder.API` with given `api`.

### @LoginManager.user_loader
This decorates callback to set it `LoginManager._user_callback`
callback must take one argument and return instance of User object or `None`.

### @LoginManager.login_required
The decorator which decorates `Responder.route` callback.
If user want to access decorated route but he/her must log in, this will call `LoginManager._unauthorized_callback` if it's provided. That can be set by decorating callback with `LoginManager.unauthorized_handler` which takes `Request` and `Response`. If `LoginManager._unauthorized_callback` isn't provided, this will redirect to `LoginManager.config["LOGIN_REQUIRED_ROUTE"]` if it's set. If not, return `LoginManager.config["LOGIN_REQUIRED_MESSAGE"]` 

### @LoginManager.unauthorized_handler
This decorates callback to set it `LoginManager._unauthorized_callback`

### @LoginManager.login_prohibited
The decorator which decorates `Responder.route` callback.
If user want to access decorated route but he/her must log out, this will call `LoginManager._authorized_callback` if it's provided. That can be set by decorating callback with `LoginManager.authorized_handler` which takes `Request` and `Response`. If `LoginManager._authorized_callback` isn't provided, this will redirect to `LoginManager.config["LOGIN_PROHIBITED_ROUTE"]` if it's set. If not, return `LoginManager.config["LOGIN_PROHIBITED_MESSAGE"]` 

### @LoginManager.authorized_handler
This decorates callback to set it `LoginManager._authorized_callback`

### LoginManager.login_user(user)
`user` must be an instance of user object. Set cookies with `Response.set_cookie()`

about account data, each value is below:
 
 - _key_ : `LoginManager.config[COOKIE_NAME]["ACCOUNT"]`
 - _value_ : `user.get_id()`
 - _expires_ : if `LoginManager.config["COOKIE_REMEMBER_ME"]["ACCOUNT"]` (Defaults to `True`), True, `datetime.datetime.now()` + `LoginManager.config["COOKIE_DURATION"]`. Otherwise, `None`
 - _max_age_ : if `LoginManager.config["COOKIE_REMEMBER_ME"]["ACCOUNT"]` (Defaults to `True`), True, `LoginManager.config["COOKIE_DURATION"].total_seconds()`. Otherwise, `None`
 - _secure_ : `LoginManager.config["COOKIE_SECURE"]` Defaults to `False`
 _ _httponly_ : `LoginManager.config["COOKIE_HTTPONLY"]` Defaults to `False`
 
 about `is_fresh`:
 
 
 - _key_ : `LoginManager.config[COOKIE_NAME]["IS_FRESH"]`
 - _value_ : `1`
 - _expires_ : if `LoginManager.config["COOKIE_REMEMBER_ME"]["IS_FRESH"]` (Defaults to `False`), `True`, `datetime.datetime.now()` + `LoginManager.config["COOKIE_DURATION"]`. Otherwise, `None`
 - _max_age_ : if `LoginManager.config["COOKIE_REMEMBER_ME"]["IS_FRESH"]` (Defaults to True), `True`, `LoginManager.config["COOKIE_DURATION"].total_seconds()`. Otherwise, `none`
 - _secure_ : `LoginManager.config["COOKIE_SECURE"]` Defaults to `False`
 _ _httponly_ : `LoginManager.config["COOKIE_HTTPONLY"]` Defaults to `False`
 
 
 ### LoginManager.logout_user()
 This log users out by setting cookie that `expires` and `max_age` are `0` 
 
 ### LoginManager.current_user
 This returns instance of user object by searching instance by `LoginManager._user_callback`. If no user found (callback returned `None`), this will return `LoginManager.anonumous_user`
 
 ### LoginManager.is_fresh
 Return If the user logging in is logged in current session(not using Remember me). If logged in current session, returns `True`. If not, `False`. This returns `False` if user is not logged in.
 
 ### LoginManager.config
 - _COOKIE_NAME_ : The dictionary of cookie name. keys are`"ACCOUNT"` and `"IS_FRESH"`. Defaults to `{"ACCOUNT": "account", "IS_FRESH": "fresh" }`
- _COOKIE_REMEMBER_ME_ : The dictionary of setting whether each cookie is Remember-me. keys are`"ACCOUNT"` and `"IS_FRESH"`. Defaults to `{"ACCOUNT": True, "IS_FRESH": False }`
- _COOKIE_DURATION_ : The amount of time before the cookie expires, as a `datetime.timedelta object`. Defaults to `datetime.timedelta(60)`
- _COOKIE_SECURE_ : Restricts the "Remember Me" cookie's scope to https. Defaults to `False`
- _COOKIE_HTTPONLY_ : Prevents the  "Remember Me" cookie from being accessed by client-side scripts. Defaults to `False`
- _LOGIN_REQUIRED_ROUTE_ : The route redirect to if user is not logged in and tried to access endpoint decorated with `LoginManager.login_required`. Defaults to `None`
- _LOGIN_REQUIRED_MESSAGE_ : The default message to display when users need to log in. Defaults to `"Please log in to access this page."`
- _LOGIN_PROHIBITED_ROUTE_ : The route redirect to if user is logged in and tried to access endpoint decorated with `LoginManager.login_prohibited`. Defaults to `None`
- _LOGIN_PROHIBITED_MESSAGE_ : The default message to display when users need to log out. Defaults to `"Please log out to access this page."`

### UserMixin
The simple mixin to make user object.

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
            
### AnonymousUserMixin
The user mixin for not logged in users

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
