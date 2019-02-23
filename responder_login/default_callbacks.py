def UNAUTHORIZED(req, resp, message, view):
    if view:
        resp.headers.update({"Location": view})
    resp.text = message
    resp.status_code = 401


def AUTHORIZED(req, resp, message, view):
    if view:
        resp.headers.update({"Location": view})
    resp.text = message
    resp.status_code = 403
