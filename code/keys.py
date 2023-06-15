import os
import json
import requests

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_KEY = os.environ.get("API_KEY")

def getSessionKey():
  # Define the request payload
  payload = { "request-json": json.dumps({"apikey": API_KEY}) }

  # Make the POST request
  response = requests.post('http://nova.astrometry.net/api/login',
                           data=payload)

  if response.status_code == 'error':
    raise Exception("Error. " + response.message)

  return response.json()['session']



