from project import app
from flask import Response,send_file,abort
import os
# YOUR STATIC FILES IS CONFIGURE HERE
@app.route('/staticfile/<path:filename>')
def custom_static(filename):
	fl = os.path.join(app.root_path,'data',filename)
	if os.path.isfile(fl):
		return send_file(fl)
	else:
		abort(404)