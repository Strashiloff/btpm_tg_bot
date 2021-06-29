import requests
# from flask import Flask, request, jsonify
# from flask_cors import CORS
from utils.logger import traceError

# app = Flask(__name__)
# CORS(app)
ip='192.168.31.76'

def checkStatus ():
  try:
    response = requests.post('http://localhost:8081/', timeout = 4)
  except requests.ConnectionError as e:
    traceError(checkStatus, e)
    return 'Не удается подключиться к серверу, скорее всего он не доступен'
  except requests.Timeout or requests.ReadTimeout as e:
    traceError(checkStatus, e)
    return 'Сервер не доступен или перегружен'
  # response = requests.get('http://{0}:8081'.format(ip))
  return response.content