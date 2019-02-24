from .config import (COOKIE_NAME, COOKIE_REMEMBER_ME, COOKIE_DURATION,
                     COOKIE_SECURE, COOKIE_HTTPONLY, LOGIN_REQUIRED_MESSAGE, LOGIN_REQUIRED_ROUTE,
                     LOGIN_PROHIBITED_MESSAGE, LOGIN_PROHIBITED_ROUTE, DISABLE_RUNTIME_WARNING)


def UNAUTHORIZED(req, resp, *_, **__):
    if LOGIN_REQUIRED_ROUTE:
        resp.headers.update({"Location": LOGIN_REQUIRED_ROUTE})
    resp.text = LOGIN_REQUIRED_MESSAGE
    resp.status_code = 401


def AUTHORIZED(req, resp, *_, **__):
    if LOGIN_PROHIBITED_ROUTE:
        resp.headers.update({"Location": LOGIN_PROHIBITED_ROUTE})
    resp.text = LOGIN_PROHIBITED_MESSAGE
    resp.status_code = 403
