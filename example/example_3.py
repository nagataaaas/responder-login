import responder
from responder_login import LoginManager, UserMixin
from responder_login.decorators import method_decorator, class_decorator

api = responder.API()
lm = LoginManager(api)

users = []


class User(UserMixin):
    def __init__(self, name, age):
        global users
        self.name = name
        self.age = age
        self.id = len(users)
        users.append(self)

    def get_id(self):
        return self.id


@lm.user_loader
def user_loader(user_id):
    try:
        return users[int(user_id)]
    except IndexError:
        return None


@api.route("/method")
class MethodDec:
    @method_decorator(lm.login_required)
    def on_get(self, req, resp):
        resp.text = "login-required area. method"


@api.route("/class")
@class_decorator(lm.login_required)
class ClassDec:
    def on_get(self, req, resp):
        resp.text = "login-required area. class"


@api.route("/without")
class Without:
    def on_get(self, req, resp):
        resp.text = "yay"


@api.route("/login")
def login(req, resp):
    lm.login_user(users[0])


@api.route("/logout")
def logout(req, resp):
    lm.logout_user()


if __name__ == "__main__":
    users.append(User("louise", 17))
    api.run()
