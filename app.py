from flask import Flask,request
from flask import render_template
import json
import time
import getopt
import sys
import os
from requests import get, post
import urllib
from urllib.request import urlopen
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv()

####################Storage Setup###############################################
account = "files121"   # Azure account name 
connect_str = os.environ['STORAGE_CONN_STR']
container = "uploads"
allowed_ext = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])
max_length =  500 * 1024 * 1024  
blob_service_client = BlobServiceClient.from_connection_string(connect_str)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_ext
###############################################################################

###########for Default page based on Densa-Shark example#######################
endpoint = "https://fsiformrecognizer.cognitiveservices.azure.com/"
key = os.environ['RECOG_KEY']
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
formUrl="https://fsi2.blob.core.windows.net/trainimages/FSI%20-%20DENSA%20SHARK%20-%2020.07.2020.pdf?sp=r&st=2021-05-15T07:46:30Z&se=2022-05-15T15:46:30Z&spr=https&sv=2020-02-10&sr=b&sig=j6Hfe9DeLN5eaLjMxDcMu6l8kQzciglHRcm4NOlUswI%3D"
poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id="42ef222f-7a31-4045-833c-09c8d4d688a5", form_url=formUrl)
result = poller.result()
tags=[]
values=[]
for recognized_form in result:
    print("Form type: {}".format(recognized_form.form_type))
    for name, field in recognized_form.fields.items():
        #print("Field '{}' has value '{}' and a confidence score of {}".format(
        #    name,
        #   field.value,
        #    field.confidence
        #))
        tags.append(name)
        values.append(field.value)
data=tuple(zip(tags,values))   
ans=dict(zip(tags,values))

################################################################################### 


@app.route("/input")
def abc():
    return render_template("home.html")

@app.route("/upload",methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        if request.form.get("upload"):
            img = request.files['file']
            if img and allowed_file(img.filename):
                filename = secure_filename(img.filename)
                img.save(filename)
                blob_client = blob_service_client.get_blob_client(container = container, blob = filename)
                with open(filename, "rb") as data:
                    try:
                        blob_client.upload_blob(data, overwrite=True)
                        msg = ""+filename+" Upload Done ! "
                        fileurl="https://files121.blob.core.windows.net/uploads/"+filename

                    except:
                        pass
                os.remove(filename)
            return render_template("upload_page.html", msg=msg,fileurl=fileurl)
        

             

    else:
        return render_template("upload_page.html",fileurl="")
    

        


@app.route("/")
def default():
    return render_template("index.html",rows=data,ans=ans)

@app.route("/reading")
def read():
    return render_template("loading.html")



#https://files121.blob.core.windows.net/uploads/16.jpg

@app.route("/analysisresults", methods=["GET","POST"])
def hello():
    if request.method=="POST":
        reporturl=request.form.get("inputurl")
        formUrl=reporturl
        if(formUrl==""):
            return render_template("index.html",rows=data,ans=ans)
        endpoint = "https://fsiformrecognizer.cognitiveservices.azure.com/"
        key = os.environ['RECOG_KEY']
        form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
        form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
        poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id = "42ef222f-7a31-4045-833c-09c8d4d688a5", form_url=formUrl)
        result = poller.result()
        tags=[]
        values=[]
        for recognized_form in result:
            for name, field in recognized_form.fields.items():
                tags.append(name)
                values.append(field.value)
        data=tuple(zip(tags,values))   
        ans=dict(zip(tags,values))
        filename=ans["Name of the ship"] +"_Dated_"+ ans["Date of FSI"]
        filename = secure_filename(filename)
        print(filename)
        with open(filename+".json", 'w') as fp:
                    json.dump(ans, fp)
        blob_client_2 = blob_service_client.get_blob_client(container = "saveddata", blob = filename+".json")
        with open(filename+".json", "rb") as asdf:
            try:
                blob_client_2.upload_blob(asdf, overwrite=True)
                
                

            except:
                pass
        os.remove(filename+".json")
        #To read the saved JSON from saveddata
        #fileurl="https://files121.blob.core.windows.net/saveddata/"+filename+".json"
        #data_json=json.loads(urlopen(fileurl).read())
        #print(data_json)




        
       
    return render_template("index.html",rows=data,ans=ans)

if __name__ == '__main__':
    app.run(debug=True)