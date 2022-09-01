#!/usr/bin/env python3.9
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from flask_restful import reqparse, abort, Api, Resource
from waitress import serve, logging
import requests
import os
import json
import glob
from bs4 import BeautifulSoup
from html import unescape
from PIL import Image

model_server = "http://" + os.environ['MODEL_SERVER']
# model_server = "http://localhost:8000"
SAFE_2_PROCESS = [".jpg",".jpeg",".png"]
os.chdir('/opt/app-root/src/web')
app = Flask(__name__,template_folder='templates',static_folder='static')
api = Api(app)

parser = reqparse.RequestParser()

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)
setup_console_handler = True

@app.route('/')
def web_hello():
    return render_template('index.html')

@app.route('/capture')
def web_capture():
    return render_template('capture.html')

@app.route('/clear')
def web_clear():
    resp = requests.get(url=model_server+"/cleanall")
    return render_template('index.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def web_upload_file():
    if request.method == 'POST':
        f = request.files['file']
        sendFile = {"file": (f.filename, f.stream, f.mimetype)}
        resp = requests.post(url=model_server+"/detect/custom", files=sendFile)
        # resp = requests.post(url=model_server+"/detect/custom", files = myfiles)
        print(resp.content)
        response = json.loads(resp.content)
        showme = 'image'
        vid = ''
        fname = response['filename']
        ctype = response['contentType']
        myext = os.path.splitext(fname)
        if myext[1] == ".m4v":
            vid = myext[0] + ".mp4"
            showme = 'video'
        dobjs = []
        try:
            dobjs = response['detectedObj']
        except Exception:
            dobjs = [{"object": "NONE", "count": 0}]
        return render_template('result.html',filename=fname, contentType=ctype, detected=dobjs, videoname=vid, showme=showme)
        
@app.route('/result')
def web_result():
    # resp = requests.post(url=model_server+"/detect/custom")
    return render_template('result.html')

@app.route('/gallery')
def web_gallery():
    detected = glob.glob("static/*")
    detected_files = []
    detected_videos = []
    for f in detected:
        fname = os.path.basename(f)
        if allowed_ext(fname):
            labels = requests.get(url=model_server+"/uploads/get/labels/" + fname)
            l = json.loads(labels.content)
            drec = {"imagename": fname, "objects_detected": l['labels']}
            detected_files.append(drec)
        elif os.path.splitext(fname)[1] == ".mp4":
            detected_videos.append(fname)

    return render_template('gallery.html',images=detected_files,videos=detected_videos)

def allowed_ext(fname):
    myext = os.path.splitext(fname)
    good2go = False
    try:
        if myext[1] in SAFE_2_PROCESS:
            good2go = True
    except Exception:
        good2go = False
    return good2go
    

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5001)
