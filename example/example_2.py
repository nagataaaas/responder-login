import responder
from responder_login import LoginManager, UserMixin

api = responder.API()
lm = LoginManager(api)

users = []


class User(UserMixin):
    id = None
    name = "Anonymous"
    age = 0

    def __init__(self, name, age):
        global users
        self.name = name
        self.age = age
        users.append(self)
        print(users)
        self.id = users.index(self)

    def get_id(self):
        return self.id

@lm.user_loader
def user_loader(user_id):
    print(users)
    try:
        return users[int(user_id)]
    except IndexError:
        return None


@api.route("/login/{name}/{age}")
@lm.login_prohibited
def login(req, resp, *, name, age):
    user = User(name, age)
    lm.login_user(user)
    resp.text = f"you've logged in as User; name: {user.name}, age: {user.age}"


@api.route("/show")
def show(req, resp):
    user = lm.current_user
    if user.is_authenticated:
        resp.text = f"you're logging in as User; name: {user.name}, age: {user.age}"
    else:
        resp.text = "you're not logging in"


@api.route("/logout")
@lm.login_required
def logout(req, resp):
    lm.logout_user()
    resp.text = "you've logged out"


if __name__ == "__main__":
    api.run()