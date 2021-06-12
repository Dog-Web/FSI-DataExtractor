from flask import Flask,request
from flask import render_template
import json
import time
import getopt
import sys
import os
from requests import get, post
import urllib
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
app = Flask(__name__)
endpoint = "https://fsiformrecognizer.cognitiveservices.azure.com/"
key = "b1786032cc014d0f9c4cd24530e3fb6d"
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
formUrl="https://fsi2.blob.core.windows.net/trainimages/FSI%20-%20DENSA%20SHARK%20-%2020.07.2020.pdf?sp=r&st=2021-05-15T07:46:30Z&se=2022-05-15T15:46:30Z&spr=https&sv=2020-02-10&sr=b&sig=j6Hfe9DeLN5eaLjMxDcMu6l8kQzciglHRcm4NOlUswI%3D"
poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id="ff78f398-3064-4a08-8866-cea29f5b4a50", form_url=formUrl)
result = poller.result()
tags=[]
values=[]
for recognized_form in result:
    print("Form type: {}".format(recognized_form.form_type))
    for name, field in recognized_form.fields.items():
        print("Field '{}' has value '{}' and a confidence score of {}".format(
            name,
            field.value,
            field.confidence
        ))
        tags.append(name)
        values.append(field.value)
data=tuple(zip(tags,values))   
ans=dict(zip(tags,values))
 


@app.route("/input")
def abc():
    return render_template("home.html")

@app.route("/")
def default():
    return render_template("index.html",rows=data,ans=ans)




@app.route("/analysisresults", methods=["GET","POST"])
def hello():
    if request.method=="POST":
        reporturl=request.form.get("inputurl")
        formUrl=reporturl
        if(formUrl==""):
            return render_template("index.html",rows=data,ans=ans)
        endpoint = "https://fsiformrecognizer.cognitiveservices.azure.com/"
        key = "b1786032cc014d0f9c4cd24530e3fb6d"
        form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
        form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
        poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id = "ff78f398-3064-4a08-8866-cea29f5b4a50", form_url=formUrl)
        result = poller.result()
        tags=[]
        values=[]
        for recognized_form in result:
            for name, field in recognized_form.fields.items():
                tags.append(name)
                values.append(field.value)
        data=tuple(zip(tags,values))   
        ans=dict(zip(tags,values))

        
       
    return render_template("index.html",rows=data,ans=ans)
