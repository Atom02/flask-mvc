import sys

# print(sys.executable)

# path = '/var/www/python/santanu'
# if path not in sys.path:
#     sys.path.append(path)

# sys.path.insert(0, '/var/www/html/Pywww/flaskmvc')
#

from project import socketio as sc,app as application
#from flask_cors import CORS, cross_origin
#from flask_socketio import SocketIO

# application.secret_key = 'onehotonekill'
# CORS(application)
# socketio = SocketIO(application)

#if __name__ == '__main__':
#    socketio.run(application, host="0.0.0.0", port=80)

# socketio = SocketIO(application)
# def application(environ,start_response):
#      status = '200 OK'
#      html = ("<html>kkktest</html>").encode()
#      sys.executable.encode()
#      html = html.encode()
#      response_header = [('Content-type','text/html')]
#      start_response(status,response_header)
#      return [html]
