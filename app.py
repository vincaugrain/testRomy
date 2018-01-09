#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen, Request


app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def parseRes(data):
	i = 1
	ret = {1:0, 2:0, 3:0}
	for element in data:
	    ret[i] = element.get('name')
	    i = i + 1
	return ret


def processRequest(req):
    if req.get("result").get("action") != "get_prescription":
        return {}
    baseurl = "https://staging-app.api.romy-paris.com/google/api/prescription"
    url = baseurl + "&format=json"
    result = urlopen(url).read()
    last = result.get_json(silent=True, force=True)
    print(print(json.dumps(last, indent=4)))
    data = json.loads(result)
    cost = parseRes(data)
    res = makeWebhookResult(data, cost)
    return res

def makeWebhookResult(req, cost):
    if req.get("result").get("action") != "get_prescription":
        return {}
    result = req.get("result")

    speech = "Votre prescription est composée des capsules " + str(cost[1]) + ", " 
    if cost[2] != 0:
    	speech = speech + str(cost['prescription2'])
    if cost[3] != 0:
    	speech = speech + " et " + str(cost['prescription3']) + "."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-romyTestPrescription"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
