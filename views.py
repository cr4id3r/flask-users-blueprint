import os
import random, string

from flask import Blueprint, request, render_template, redirect, abort
from sqlalchemy import select

# TODO: Fix dependencies to allow use isolated
from blueprints.users_blueprint.models import FLUserWrapper, row2dict
from blueprints.users_blueprint.forms import LoginForm, RegistrationForm, EmailAuthInitiateForm

from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from blueprints.users_blueprint.utils import get_user, register_user

users_blueprint_app = Blueprint('users', __name__,
                                template_folder='templates',
                                static_folder='static',
                                url_prefix='/users'
                                )

@users_blueprint_app.route('/<int:user_id>')
def user_view(user_id):
    user = get_user(id=user_id)
    return render_template("user.html", user=row2dict(user))


@users_blueprint_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        register_user(email=form.email.data, password=form.password.data)
        return redirect('/')

    return render_template('registration.html', form=form)


@users_blueprint_app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect('/users/%s' % current_user.id)

    form = LoginForm()

    if form.validate_on_submit():
        # login and validate the user...
        user = FLUserWrapper(form.user)
        login_user(user)
        return redirect('/')
    
    return render_template('login.html', form=form)


@users_blueprint_app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@users_blueprint_app.route("/email-auth", methods=['GET', 'POST'])
def email_auth():

    form = EmailAuthInitiateForm()

    if form.validate_on_submit():
        reset_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(120))
        print('reset_key:' + reset_key)
        form.user.email_auth_hash = generate_password_hash(reset_key)
        db.session.commit()
        return redirect('/')
    return render_template('email-auth.html', form=form)


# @users_blueprint_app.route("/email-auth-confirm", methods=['GET', 'POST'])
# def password_reset_change():
#     if 'id' in request.args and 'reset-key' in request.args:
#         user_id = request.args.get('id')
#         reset_key = request.args.get('reset-key')
#         user = User.query.filter_by(id=user_id).first()
#         print(user)
#         if check_password_hash(user.email_auth_hash, reset_key):
#             user.reset_password_hash = ''
#             db.session.commit()
#             user = FLUserWrapper(user)
#             login_user(user)
#             return redirect('/')
#     abort(403)


def user_debug():
    out = ""
    if current_user.is_anonymous():
        out += "Not Logged In"
    else:
        out += "Logged In "
        out += "(user id : " + str(current_user._user.id) + ") "
        out += "(username : " + current_user._user.username + ") "
        out += "(email : " + current_user._user.email + ") "
        out += "(roles : "
        for role in current_user._user.roles:
            out += role.name + ", "
        out += ") "
    return out