from flask import g
from flask_login import UserMixin

from .models import User


def get_user(**kwargs):
    users = g.db.query(User)
    for attr_element, attr_value in kwargs.items():
        users = users.filter(getattr(User, attr_element) == attr_value)

    found_user = users.scalar()

    return found_user if found_user else None


def register_user(email, password):
    new_user = User()
    new_username = email.split('@')[0]
    exists_user = get_user(username=new_username)
    if exists_user:
        return None

    new_user.username = new_username
    new_user.email = email
    new_user.set_password(password)
    g.db.session.add(new_user)
    g.db.session.commit()

    return new_user


class UserClass(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active
