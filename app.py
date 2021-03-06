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
    firstname = data.get('firstname')
    caps = data.get('capsules')
    i = 1
    ret = {1:0, 2:0, 3:0}
    for element in caps:
        ret[i] = element.get('name')
        i = i + 1
    return ret

def processRequest(req):
    if req.get("result").get("action") != "get_prescription":
        return {}
    url = "https://staging-app.api.romy-paris.com/google/api/prescription"
    accessToken = req.get('originalRequest').get('data').get('user').get('accessToken')
    token = "Bearer " + accessToken
    
    request = urllib.request.Request(url, headers={"Authorization" : token})
    result = urllib.request.urlopen(request).read()
    data = json.loads(result)
    cost = parseRes(data)
    res = makeWebhookResult(data, cost)
    return res

def makeWebhookResult(data, cost):
    print(json.dumps(data, indent=4))
    if cost[1] == 0:
    	speech = "Votre prescription n'est pas prête pour le moment. Merci de réessayer ulterieurement."
    else:
	    speech = "Votre prescription est composée des capsules " + str(cost[1])
	    if cost[2] != 0:
	        if cost[3] != 0:
	        	speech = speech + ", " + str(cost[2]) + " et " + str(cost[3]) + "."
	        else:
	        	speech = speech + " et " + str(cost[2])
	    else:
	    	speech = "Votre prescription est composée de la capsule " + str(cost[1]) + "." 
    

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
