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
import base64
import io

model_server = "http://ocpedge:5001"
SAFE_2_PROCESS = [".jpg",".jpeg",".png",".m4v",".mov",".mp4"]

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
        fname = response['filename']
        ctype = response['contentType']
        dobjs = response['detectedObj']
        return render_template('result.html',filename=fname, contentType=ctype, detected=dobjs)
        
@app.route('/result')
def web_result():
    # resp = requests.post(url=model_server+"/detect/custom")
    return render_template('result.html')

@app.route('/gallery')
def web_gallery():
    originals = glob.glob("/data/docker_vols/uploaded-files/*")
    detected = glob.glob("/data/docker_vols/detected-files/exp/*")
    original_files = []
    detected_files = []
    for c in originals:
        iname = os.path.basename(c)
        if allowed_ext(iname):
            original_files.append(iname)
    for f in detected:
        fname = os.path.basename(f)
        if allowed_ext(fname):
            labels = requests.get(url=model_server+"/uploads/get/labels/" + fname)
            print(labels)
            detected_files.append(fname)
    return render_template('gallery.html',images=detected_files)

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
    serve(app, host='0.0.0.0', port=5002)
