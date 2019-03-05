from project import app,config
from flask import Response,send_file,abort
import os

@app.route('/data/<path:filename>')
def custom_static(filename):
	fl = os.path.join(app.root_path,'data',filename)
	if os.path.isfile(fl):
		return send_file(fl)
	else:
		abort(404)

@app.route('/datamat/<path:filename>')
def datamat_static(filename):
	fl = os.path.join(app.root_path,'datamat',filename)
	if os.path.isfile(fl):
		return send_file(fl)
	else:
		abort(404)

@app.route('/mask/<path:filename>')
def mask_static(filename):
	return send_file(os.path.join(app.root_path,'mask',filename))

    # return send_from_directory(app.config['CUSTOM_STATIC_PATH'], filename)