import requests, os
from utils.logger import traceError

ip='192.168.31.76'

def updateIp(ip_new):
  DEST_IP = os.environ.get('DEST_IP', '')
  if(DEST_IP != ip_new):
    os.environ.setdefault('DEST_IP', ip_new)
    ip = ip_new
  
def checkStatus ():
  global ip
  #
  DEST_IP = os.environ.get('DEST_IP', ip)
  try:
    response = requests.post('http://{0}:8081/'.format(DEST_IP), timeout = 15)
  except requests.ConnectionError as e:
    traceError(checkStatus, e)
    return 'Не удается подключиться к серверу, скорее всего он не доступен'
  except requests.Timeout or requests.ReadTimeout as e:
    traceError(checkStatus, e)
    return 'Сервер не доступен или перегружен'
  data = response.json()
  return """IP сервера: {0}
Текущий статус сервера: <code>{1}</code>
Майнкрафт: <code>{2}</code>
Игроков онлайн: <b>{3}</b>
Ники игроков онлайн: <b>{4}</b>
""".format(data['ip'], data['status'], data['minecraft'], data['online'], data['players'])