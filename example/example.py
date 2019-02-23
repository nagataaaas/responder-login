import os

import responder

from responder_login import LoginManager, UserMixin
try:
    import sqlalchemy
except ImportError:
    os.system("pip install SQLAlchemy")
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
import sqlalchemy.ext.declarative


api = responder.API()
lm = LoginManager(api)
Base = sqlalchemy.ext.declarative.declarative_base()
url = "sqlite:///database.db"


class Student(Base, UserMixin):
    __tablename__ = "students"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(20))
    grade = sqlalchemy.Column(sqlalchemy.Integer)
    password = sqlalchemy.Column(sqlalchemy.String(20))

    def get_id(self):
        return self.id


engine = sqlalchemy.create_engine(url, echo=False)
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)
session = scoped_session(SessionMaker)


@lm.user_loader
def user_loader(_id):
    return session.query(Student).get(_id)


@api.route("/show")
@lm.login_required
def show(req, resp):
    user = lm.current_user
    resp.text = f"your are logging in as {user.name}, {user.grade}th grader"


@api.route("/signup")
@lm.login_prohibited
async def signup(req, resp):
    if req.method == "get":
        resp.html = """
        SignUp<br>
        <form action="/signup" method="post">
        <input name="name"><label>name</label></input><br>
        <input name="grade" type="number"><label>grade</label></input><br>
        <input name="password" type="password"><label>password</label></input><br>
        <button type="submit">submit</button>
        </form>"""
    else:
        data = await req.media(format="form")
        user = Student()
        user.name = data["name"]
        user.grade = int(data["grade"])
        user.password = data["password"]
        session.add(user)
        session.commit()
        lm.login_user(user)
        resp.text = "Signup succeed!!!"


@api.route("/login")
@lm.login_prohibited
async def login(req, resp):
    if req.method == "get":
        resp.html = """
        Login<br>
        <form action="/login" method="post">
        <input name="name"><label>name</label></input><br>
        <input name="password" type="password"><label>password</label></input><br>
        <button type="submit">submit</button>
        </form>"""
    else:
        data = await req.media(format="form")
        name = data["name"]
        password = data["password"]
        user = session.query(Student).filter(Student.name == name, Student.password == password).first()
        if user:
            lm.login_user(user)
            resp.text = "Login succeed!!!"
        else:
            resp.html = """
            login failed!!!!!!!<br>
            Login<br>
            <form action="/login" method="post">
            <input name="name"><label>name</label></input><br>
            <input name="password" type="password"><label>password</label></input><br>
            <button type="submit">submit</button>
            </form>"""


@api.route("/logout")
@lm.login_required
def logout(req, resp):
    lm.logout_user()
    resp.text = "Logout succeed!!!"


if __name__ == "__main__":
    api.run()
