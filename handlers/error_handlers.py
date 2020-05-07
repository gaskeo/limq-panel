from flask import redirect, Blueprint


app = Blueprint("errors", __name__)


@app.errorhandler(401)
def error_401(e):
    """ Handler for procession of error 401 """
    return redirect("/login")

