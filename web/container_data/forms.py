from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        [validators.Length(1, 30, message='Incorrect username length'),
         validators.regexp(r"^([a-zA-Z0-9]+)$", message="Incorrent username data")]
    )
    password = PasswordField(
        'Password',
        [validators.Length(8, 30, message='Incorrect password length'),
         validators.regexp(r"^(?=.*[A-ZĄĆĘŁŃÓŚŹŻ])(?=.*[a-ząćęłńóśźż])(?=.*[0-9])(?=.*[!@#$%^&*]).*$",
                           message="Incorrect password data")])


class SignupForm(FlaskForm):
    username = StringField(
        'Username',
        [validators.Length(1, 30, message='Username has to be between 1 and 30 characters long'),
         validators.regexp(r"^([a-zA-Z0-9]+)$", message="Only English alphabet letters and numbers are allowed")]
    )
    password = PasswordField(
        'Password',
        [validators.Length(8, 30, message='Password has to be between 8 and 30 characters long'),
         validators.regexp(r"^(?=.*[A-ZĄĆĘŁŃÓŚŹŻ])(?=.*[a-ząćęłńóśźż])(?=.*[0-9])(?=.*[!@#$%^&*]).*$",
                           message="Password has to include at least one small character, one big character, one digit and one special character")]
    )


class ResetForm(FlaskForm):
    old_password = PasswordField(
        'Old Password',
        [validators.Length(8, 30),
         validators.regexp(r"^(?=.*[A-ZĄĆĘŁŃÓŚŹŻ])(?=.*[a-ząćęłńóśźż])(?=.*[0-9])(?=.*[!@#$%^&*]).*$")]
    )
    new_password = PasswordField(
        'New Password',
        [validators.Length(8, 30, message='Password has to be between 8 and 30 characters long'),
         validators.regexp(r"^(?=.*[A-ZĄĆĘŁŃÓŚŹŻ])(?=.*[a-ząćęłńóśźż])(?=.*[0-9])(?=.*[!@#$%^&*]).*$",
                           message="Password has to include at least one small character, one big character, one digit and one special character")]
    )
    new_password_repeat = PasswordField(
        'Repeat New Password',
        [validators.DataRequired(),
         validators.EqualTo('new_password', message='Passwords do not match')]
    )


class NoteForm(FlaskForm):
    note = StringField('Note', [validators.DataRequired(message='No note provided')])
    users = StringField(
        "Users",
        [validators.Optional(),
         validators.DataRequired(message='No users provided'),
         validators.regexp(r"^([a-zA-Z0-9,\s]+)$", message='Incorrect formatting')]
    )
