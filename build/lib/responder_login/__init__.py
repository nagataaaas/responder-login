"""
    responder_login
    -----------
    This module provides user session management for Responder. It lets you log
    your users in and out in a database-independent manner.
    :copyright: (c) 2019 by Yamato Nagata.
    :license: MIT.
"""

from .__about__ import __version__
from .config import (COOKIE_NAME, COOKIE_REMEMBER_ME, COOKIE_DURATION,
                     COOKIE_SECURE, COOKIE_HTTPONLY, LOGIN_REQUIRED_MESSAGE, LOGIN_REQUIRED_ROUTE,
                     LOGIN_PROHIBITED_MESSAGE, LOGIN_PROHIBITED_ROUTE, DISABLE_RUNTIME_WARNING)
from .login_manager import LoginManager
from .mixins import (UserMixin, AnonymousUserMixin)


__all__ = [
    LoginManager.__name__,
    UserMixin.__name__,
    AnonymousUserMixin.__name__,
    __version__,
    "COOKIE_NAME",
    "COOKIE_REMEMBER_ME",
    "COOKIE_DURATION",
    "COOKIE_SECURE",
    "COOKIE_HTTPONLY",
    "LOGIN_REQUIRED_MESSAGE",
    "LOGIN_REQUIRED_ROUTE",
    "LOGIN_PROHIBITED_MESSAGE",
    "LOGIN_PROHIBITED_ROUTE",
    "LoginManager",
    "UserMixin",
    "AnonymousUserMixin",

]