# v 0.0.8
- `LoginManager()` is now callable to make deepcopy of it so that we can choose which `req` or `resp` to use. 
In previous version, `req` or `resp` cannot be searched properly in `@api.background.task` and other specific situation.
In order to solve this problem, `LoginManager()` became callable.
- Add `LoginManager().set_req_resp(req=None, resp=None)`. This will set `req` or `resp` to use it forever. This has been added to make `LoginManager()` callable.

# v 0.0.7
- Add `decorators.method_decorator` and `decorators.class_decorator`. 

# v 0.0.6
- Set `307` to `status_code` of redirect.

# v 0.0.5
- Fixed `LOGIN_PROHIBITED_ROUTE` and `LOGIN_REQUIRED_ROUTE` won't work problem.

# v 0.0.4
- Added `current_user` to jinja2 variable

# v.0.0.3
- Bug fix

# v0.0.2
- Bug fix

# v0.0.1
- Conception