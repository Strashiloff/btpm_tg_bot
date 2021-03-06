import requests, subprocess, json
# from time import sleep
from flask import Flask, request, jsonify
from flask_cors import CORS

server = Flask(__name__)
# CORS(server)

def sendMyIpToHost():
  my_ip = subprocess.Popen(['curl', '-s', 'ifconfig.me/ip'], stdout=subprocess.PIPE)
  try:
    data = json.dumps({"ip": my_ip.stdout.readline().decode('utf-8')})
    requests.post('https://btpm-bot.herokuapp.com/setip', data)
  except Exception as e:
    print(sendMyIpToHost, e)
    
sendMyIpToHost()

@server.route('/', methods=['GET', 'POST'])
def requestFromVps():
  if request.method == 'GET':
    return 'Hello kollegi'
  else: # request.method == 'POST':
    online = '0'
    players = ''
    minecraft = 'Not running'
    result, ip, arr = getServerStatus()
    if result != 'No screen session found.':
      online, players = parsePlayers(arr)
      minecraft = 'Running'
    
    if online == 0:
      players = 'никого нет('
    # sleep(11)
    return jsonify(
      ip = ip,
      status = 'Online',
      minecraft = minecraft,
      online = online,
      players = players
    )
    
@server.route('/command', methods=['POST'])
def requestFromVpsCommand ():
  try:
    json_data = json.loads(request.data)
  except Exception as e:
    print ('|||___|||', e)

  text = executeCommand(json_data['command'])
  return jsonify(text=text)
    
def getServerStatus ():
  proc = subprocess.Popen(['./status.sh'], stdout=subprocess.PIPE)
  arr = list()
  while True:
    line = proc.stdout.readline().decode('utf-8')
    if not line:
      break
    arr.append(line.rstrip().replace('\n', ''))
  return arr[0], arr[1], arr

def parsePlayers (array):
  array.reverse()
  find = ''
  for param in array:
    if param.find(' of a max of ') != -1:
      find = param
      break
  
  arr = find.split(' ')
  players = ''
  try:
    online = int(arr[5])
  except Exception as e:
    return 0, ''
  if online > 0:
    for i in range(13, len(arr)):
      players += arr[i]
      
  return online, players

def executeCommand (command):
  proc = subprocess.Popen(['./command.sh', command], stdout=subprocess.PIPE)
  text = ''
  while True:
    line = proc.stdout.readline().decode('utf-8')
    text += line
    if not line:
      break
  
  return text