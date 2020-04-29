from flask import Flask, render_template, send_from_directory, Response
# from flask_socketio import SocketIO
from pathlib import Path
from capture import capture_and_save
from camera import Camera
from capture import process_image
import argparse
import cv2
import json, random

# from example_output import GenerateOutput

app = Flask(__name__)
app.config['FLASK_APP'] ="server.py"
app.config['FLASK_ENV'] = "development"

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering or Chrome Frame,
    and also to cache the rendered page for 10 minutes
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r

@app.route("/")
def entrypoint():
  return render_template("index.html")
  
@app.route("/logs")
def logs():
  return render_template("logs.html")

@app.route("/abstract")
def abstract():
  #data=GenerateOutput( random.randint( 10, 70 ) )
  #return render_template("abstract.html", data=data) # Temporary for fake data
  arr = []
  p = Path("images/last.png")
  if p.exists():
    arr = process_image(None, hardcoded_image=True, should_return_image=False)
  return render_template("abstract.html", data=arr)

@app.route("/images/last")
def last_image():
    p = Path("images/last.png")
    if p.exists():
      r = "last.png"
    else:
      r = "not_found.jpeg"
    return send_from_directory("images",r)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-p','--port',type=int,default=5000, help="Running port")
  parser.add_argument("-H","--host",type=str,default='127.0.0.1', help="Address to broadcast")
  parser.add_argument("-FP","--staticfilepath",type=str,default=None, help="Set a static filepath for testing")
  args = parser.parse_args()

  # initialize camera with background thread
  camera = Camera(args.staticfilepath)
  app.run(host=args.host,port=args.port)
  