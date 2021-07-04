import requests, os, json
from utils.logger import traceError
from flask import jsonify

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
  url = 'http://{0}:8081/'.format(DEST_IP)
  error, response = sendRequest(url)
  if error:
    return response
  data = response.json()
  return """IP сервера: {0}
Текущий статус сервера: <code>{1}</code>
Майнкрафт: <code>{2}</code>
Игроков онлайн: <b>{3}</b>
Ники игроков онлайн: <b>{4}</b>
""".format(data['ip'], data['status'], data['minecraft'], data['online'], data['players'])

def sendAdminCommand(command):
  global ip
  DEST_IP = os.environ.get('DEST_IP', ip)
  url = 'http://{0}:8081/command'.format(DEST_IP)
  error, response = sendRequest(url, json.dumps({"command": command}))
  if error:
    return response
  data = response.json()
  return data['text']

def checkAdminRigthts(id_user):
  target = os.path.abspath('.')  + '/stickers/admin.txt'
  fileRigths = open(target, 'r')
  strings = fileRigths.readlines()
  for line in strings:
    words = line.split(' ')
    if int(words[0]) == int(id_user):
      return True, int(words[2].replace('\n', ''))
  return False

def sendRequest (url, data = ''):
  try:
    response = requests.post(url, data, timeout = 15)
  except requests.ConnectionError as e:
    traceError(checkStatus, e)
    return True, 'Не удается подключиться к серверу, скорее всего он не доступен'
  except requests.Timeout or requests.ReadTimeout as e:
    traceError(checkStatus, e)
    return True, 'Сервер не доступен или перегружен'
  return False, response

def setNewAdmin (string_admin):
  target = os.path.abspath('.') + '/stickers/admin.txt'
  string_args = string_admin.split(' ')
  if len(string_args) != 3 or not string_args[0].isdigit() or not string_args[2].isdigit():
    return 'Ошибка в команде'
  
  if int(string_args[2]) > 2 and int(string_args[2]) < 1:
    return 'Чи шо, не таких прав доступа... есть только 1 и 2'
  
  try:
    file_admin = open(target)
    list_string = file_admin.readlines()
    for line in list_string:
      str_row = line.split(' ')
      if int(str_row[0]) == int(string_args[0]):
        return '{0} уже является администратором'.format(string_args[1])
      
    file_admin.close()
    file_admin = open(target, 'a')
    file_admin.write(string_admin)
    file_admin.close()
  except Exception as e:
    print(setNewAdmin, e)
    return 'Произошла ошибка'
    
  return 'Новый администратор добавлен'

def showListAdmins ():
  target = os.path.abspath('.') + '/stickers/admin.txt'
  try:
    file_admins = open(target)
    list_admins = file_admins.readlines()
    file_admins.close()
  except Exception as e:
    print(setNewAdmin, e)
    return 'Произошла ошибка'
  return ''.join(list_admins)

def deleteAdmin(id_admin, your_id):
  target = os.path.abspath('.') + '/stickers/admin.txt'
  
  if not id_admin.isdigit():
    return 'Ошибка, id неверен'
  try:
    file_admins = open(target)
    list_admins = file_admins.readlines()
    file_admins.close()
    find = None
    for line in list_admins:
      line_text = line.split(' ')
      if int(line_text[0]) == int(id_admin):
        find = line
        if int(line_text[2]) == 2 and int(your_id) != 93812289:
          return 'Этого администратора нельзя удалить'
      
    if find == None:
      return 'Такого администратора нет'
    
    list_admins.remove(find)
    file_admins = open(target, 'w')
    file_admins.writelines(list_admins)
    file_admins.close()
  except Exception as e:
    print(setNewAdmin, e)
    return 'Произошла ошибка'
  return 'Администратор удален'