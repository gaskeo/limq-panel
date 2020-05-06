from flask import redirect, Blueprint


app = Blueprint("errors", __name__)


@app.errorhandler(401)
def error_401(e):
    return redirect("/login")

