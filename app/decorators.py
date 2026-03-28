from functools import wraps

from flask import g, redirect


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        return redirect("/login")

    return inner
