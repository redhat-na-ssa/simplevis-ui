#!/usr/bin/env python3.8
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from flask_restful import reqparse, abort, Api, Resource
from waitress import serve, logging
import requests
import os
import json
from bs4 import BeautifulSoup
from html import unescape

model_server = "http://localhost:8000"

app = Flask(__name__,template_folder='templates')
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
        resp = requests.get(url=model_server+"/uploads/get/" + fname)
        myimage = resp.content
        return render_template('result.html',filename=fname, contentType=ctype, detected=dobjs, imagedata=myimage)
        
@app.route('/result')
def web_result():
    # resp = requests.post(url=model_server+"/detect/custom")
    return render_template('result.html')

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5001)
