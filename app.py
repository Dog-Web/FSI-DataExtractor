from flask import Flask
from flask import render_template
import json
import time
import getopt
import sys
import os
from requests import get, post
import urllib
app = Flask(__name__)
def runAnalysis(input_file='artdoc.pdf', output_file='', file_type='application/json'):
    # Endpoint URL
    endpoint = r"https://fsiformrecognizer.cognitiveservices.azure.com/"
    # Subscription Key
    apim_key = "b1786032cc014d0f9c4cd24530e3fb6d"
    # Model ID
    model_id = "ca9bb8ab-a0ff-42a5-99e8-6ba5efe2f1e8"
    # API version
    API_version = "v2.1"

    post_url = endpoint + "/formrecognizer/%s/custom/models/%s/analyze" % (API_version, model_id)
    params = {
        "includeTextDetails": True
    }

    headers = {
        # Request headers
        'Content-Type': file_type,
        'Ocp-Apim-Subscription-Key': apim_key,
    }
    try:
        filej = urllib.request.Request('https://fsi2.blob.core.windows.net/trainimages/newtestdensa.pdf')
        with urllib.request.urlopen(filej) as responsee:
            data_bytes = responsee.read()
    except IOError:
        print("Inputfile not accessible.")
        sys.exit(2)

    try:
        print('Initiating analysis...')
        resp = post(url = post_url, data = data_bytes, headers = headers, params = params)
        if resp.status_code != 202:
            print("POST analyze failed:\n%s" % json.dumps(resp.json()))
            quit()
        print("POST analyze succeeded:\n%s" % resp.headers)
        print
        get_url = resp.headers["operation-location"]
    except Exception as e:
        print("POST analyze failed:\n%s" % str(e))
        quit()

    n_tries = 15
    n_try = 0
    wait_sec = 5
    max_wait_sec = 60
    print()
    print('Getting analysis results...')
    while n_try < n_tries:
        try:
            resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": apim_key})
            resp_json = resp.json()
            if resp.status_code != 200:
                print("GET analyze results failed:\n%s" % json.dumps(resp_json))
                quit()
            status = resp_json["status"]
            if status == "succeeded":
                if output_file:
                    with open(output_file, 'w') as outfile:
                        json.dump(resp_json, outfile, indent=2, sort_keys=True)
                print("Analysis succeeded:\n%s" % json.dumps(resp_json["analyzeResult"]["documentResults"][0]["fields"], indent=2, sort_keys=True))
                quit()
            if status == "failed":
                print("Analysis failed:\n%s" % json.dumps(resp_json))
                quit()
            # Analysis still running. Wait and retry.
            time.sleep(wait_sec)
            n_try += 1
            wait_sec = min(2*wait_sec, max_wait_sec)     
        except Exception as e:
            msg = "GET analyze results failed:\n%s" % str(e)
            print(msg)
            quit()
    print("Analyze operation did not complete within the allocated time.")


@app.route("/")
def hello():
    runAnalysis()
    return render_template("index.html")
