import requests
# from time import sleep
from flask import Flask, request, jsonify
from flask_cors import CORS

server = Flask(__name__)
CORS(server)

@server.route('/', methods=['GET', 'POST'])
def requestFromVps():
  if request.method == 'GET':
    return 'Hello kollegi'
  else: # request.method == 'POST':
    # sleep(5)
    return jsonify(
      ip = '0.0.0.0',
      status = 'offline',
      minecraft = 'not running',
      online = '0',
      players = ''
    )