def UNAUTHORIZED(req, resp, message):
    resp.text = message
    resp.status_code = 401


def AUTHORIZED(req, resp, message):
    resp.text = message
    resp.status_code = 403
