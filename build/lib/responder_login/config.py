"""
    responder_login.config
    ------------------
    This provides configuration values.
"""

import datetime

#: The name of cookie which stores the data. Do not change key values
COOKIE_NAME = {"ACCOUNT": "account"
               }

#: Whether the app uses "Remember-Me".
COOKIE_REMEMBER_ME = {COOKIE_NAME["ACCOUNT"]: True
                      }

#: The default time before the "Remember-Me" cookie expires; Defaults to -- datetime.timedelta(365) --
COOKIE_DURATION = datetime.timedelta(365)

#: Whether the "Remember-Me" cookie requires Secure; Defaults to -- False --
COOKIE_SECURE = False

#: Whether the "Remember-Me" cookie uses HttpOnly; Defauls to -- False --
COOKIE_HTTPONLY = False

#: The default message to display when users need to log in.
LOGIN_REQUIRED_MESSAGE = "Please log in to access this page."

#: view to redirect when users need to log in.
LOGIN_REQUIRED_ROUTE = None

#: The default message to display when users need to log out.
LOGIN_PROHIBITED_MESSAGE = "Please log out to access this page."

#: view to redirect when users need to log out.
LOGIN_PROHIBITED_ROUTE = None

#: Decorating coroutine with async will give RuntimeError
#: So this is whether disable RuntimeError or not; Defaults to -- True --
DISABLE_RUNTIME_WARNING = True
