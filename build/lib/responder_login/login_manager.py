import inspect
import warnings
import asyncio
import datetime

from functools import wraps


from .mixins import AnonymousUserMixin
from .config import (COOKIE_NAME, COOKIE_REMEMBER_ME, COOKIE_DURATION,
                     COOKIE_SECURE, COOKIE_HTTPONLY, LOGIN_REQUIRED_MESSAGE, LOGIN_REQUIRED_ROUTE,
                     LOGIN_PROHIBITED_MESSAGE, LOGIN_PROHIBITED_ROUTE, DISABLE_RUNTIME_WARNING)

from .default_callbacks import (UNAUTHORIZED, AUTHORIZED)

from responder.models import (Response, Request)


def get_data_from_stack():
    req, resp = None, None
    for stack in inspect.stack():
        data = stack[0].f_locals
        for datum in data.items():
            datum = datum[1]
            if isinstance(datum, Request):
                req = datum
            elif isinstance(datum, Response):
                resp = datum
        if req and resp:
            break
    else:
        req, resp = None, None
    return req, resp


def get_data_from_args(*args, **kwargs):
    try:
        req, resp = args
        assert isinstance(req, Request) and isinstance(resp, Response), ValueError
    except ValueError:
        req, resp = None, None
    return req, resp


class LoginManager:

    def __init__(self, api=None):
        #: If no user is logged in, This will be used.
        self.anonymous_user = AnonymousUserMixin()

        #: Disable displaying RuntimeWarning if DISABLE_RUNTIME_WARNING in config.
        if DISABLE_RUNTIME_WARNING:
            warnings.filterwarnings(action="ignore", message="coroutine\s.+\swas\snever\sawaited",
                                    category=RuntimeWarning)

        self._authorized_callback = None

        self._unauthorized_callback = None

        self._user_callback = None

        self._api = None

        self.config = {"COOKIE_NAME": COOKIE_NAME,
                       "COOKIE_REMEMBER_ME": COOKIE_REMEMBER_ME,
                       "COOKIE_DURATION": COOKIE_DURATION,
                       "COOKIE_SECURE": COOKIE_SECURE,
                       "COOKIE_HTTPONLY": COOKIE_HTTPONLY,
                       "LOGIN_REQUIRED_ROUTE": LOGIN_REQUIRED_ROUTE,
                       "LOGIN_REQUIRED_MESSAGE": LOGIN_REQUIRED_MESSAGE,
                       "LOGIN_PROHIBITED_ROUTE": LOGIN_PROHIBITED_ROUTE,
                       "LOGIN_PROHIBITED_MESSAGE": LOGIN_PROHIBITED_MESSAGE
                       }

        if api:
            self.init_api(api)

    def init_api(self, api):
        api.login_manager = self
        self._api = api

    def _unauthorized(self, *args, **kwargs):
        """
        If _unauthorized_handler is not registered, This is called when the user is required to log in.
        Otherwise, this will be called.
        """
        if self._unauthorized_callback:
            return self._unauthorized_callback(*args, **kwargs)
        if self.config["LOGIN_REQUIRED_ROUTE"]:
            _, resp = args
            self._api.redirect(resp, self.config["LOGIN_REQUIRED_ROUTE"])
        return UNAUTHORIZED(*args, **kwargs, message=self.config["LOGIN_REQUIRED_MESSAGE"])

    def _authorized(self, *args, **kwargs):
        """
        If authorized_handler is not registered, This is called when the user is logged in.
        Otherwise, this will be called.
        """
        if self._authorized_callback:
            return self._authorized_callback(*args, **kwargs)
        if self.config["LOGIN_PROHIBITED_ROUTE"]:
            _, resp = args
            self._api.redirect(resp, self.config["LOGIN_PROHIBITED_ROUTE"])
        return AUTHORIZED(*args, **kwargs, message=self.config["LOGIN_PROHIBITED_MESSAGE"])

    def unauthorized_handler(self, callback):
        self._unauthorized_callback = callback

        @wraps(callback)
        def _unauthorized_handler_wrap(*args, **kwargs):
            return callback(*args, **kwargs)

        return _unauthorized_handler_wrap

    def authorized_handler(self, callback):
        self._authorized_callback = callback

        @wraps(callback)
        def _authorized_handler_wrap(*args, **kwargs):
            return callback(*args, **kwargs)

        return _authorized_handler_wrap

    def login_required(self, fn):
        """
        if user is not logged in, this will call self.unauthorized_callback with args.
        """
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def login_required_wrap(*args, **kwargs):
                user = self._load_user(*args, **kwargs)
                if user.is_anonymous:
                    return await self._unauthorized(*args, **kwargs)
                return await fn(*args, **kwargs)

            return login_required_wrap
        else:
            @wraps(fn)
            def login_required_wrap(*args, **kwargs):
                user = self._load_user(*args, **kwargs)
                if user.is_anonymous:
                    return self._unauthorized(*args, **kwargs)
                return fn(*args, **kwargs)

            return login_required_wrap

    def login_prohibited(self, fn):
        """
        if user is logged in, this will call self._authorized_callback with args.
        """
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def login_prohibited_wrap(*args, **kwargs):
                user = self._load_user(*args, **kwargs)
                if user.is_authenticated:
                    return await self._authorized(*args, **kwargs)
                return await fn(*args, **kwargs)

            return login_prohibited_wrap
        else:
            @wraps(fn)
            def login_prohibited_wrap(*args, **kwargs):
                user = self._load_user(*args, **kwargs)
                if user.is_authenticated:
                    return self._authorized(*args, **kwargs)
                return fn(*args, **kwargs)

            return login_prohibited_wrap

    def user_loader(self, callback):
        """
        This sets the callback for reloading a user from the session. The
        function you set should take a user ID (a ``str``) and return a
        user object, or ``None`` if the user does not exist.
        """

        self._user_callback = callback
        self._api.jinja_values_base['current_user'] = self.current_user

        @wraps(callback)
        def _user_loader_wrap(*args, **kwargs):
            return callback(*args, **kwargs)

        return _user_loader_wrap

    def _load_user(self, req, resp, *_, **__):
        if not self._user_callback:
            raise UnboundLocalError("Please set LoginManager._user_callback")
        try:
            account_cookie = req.cookies.get(COOKIE_NAME["ACCOUNT"])
            user = self._user_callback(account_cookie)
            return user if user else self.anonymous_user
        except (AttributeError, TypeError):
            return self.anonymous_user

    def login_user(self, account):
        req, resp = get_data_from_stack()
        account_id = account.get_id()
        self._set_cookie(account_id, "ACCOUNT", resp)
        self._set_cookie("1", "IS_FRESH", resp)

    def logout_user(self):
        req, resp = get_data_from_stack()
        self._set_cookie("", "ACCOUNT", resp, delete=True)
        self._set_cookie("", "IS_FRESH", resp, delete=True)

    @property
    def is_fresh(self):
        try:
            req, resp = get_data_from_stack()
            is_fresh = req.cookies.get(COOKIE_NAME["IS_FRESH"])
            if is_fresh:
                return True
        except Exception:
            pass
        return False

    @property
    def current_user(self):
        req, resp = get_data_from_stack()
        try:
            return self._load_user(req, resp)
        except (AttributeError, TypeError):
            return self.anonymous_user

    def _set_cookie(self, cookie, cookie_type, resp, delete=False):
        assert cookie_type in self.config["COOKIE_NAME"], "cookie_type must be a key of COOKIE_NAME"

        key = self.config["COOKIE_NAME"][cookie_type]
        value = cookie
        if self.config["COOKIE_REMEMBER_ME"][cookie_type]:
            expires = datetime.datetime.now() + self.config["COOKIE_DURATION"]
            max_age = self.config["COOKIE_DURATION"].total_seconds()
        else:
            expires, max_age = None, None
        if delete:
            expires, max_age = 0, 0
        secure = COOKIE_SECURE
        httponly = COOKIE_HTTPONLY
        resp.set_cookie(key=key, value=value, expires=expires,
                        max_age=max_age, secure=secure, httponly=httponly)
