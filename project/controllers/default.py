from project import app,cache
from flask import redirect,url_for,request,g
import importlib
import pprint

@app.route("/")
def defroute():
    To_default=url_for("SiteView:index")
    return redirect(To_default)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,"db"):
        g.db.close()
        print("TEARDOWN")