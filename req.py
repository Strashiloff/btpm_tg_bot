import requests, os, json, utils.parser as parser
from utils.logger import traceError
from flask import jsonify
from mcrcon import MCRcon, MCRconException

ip='192.168.31.162'
PASS_SERV = os.environ.get('RCON_PASS')
mcron = None

def updateIp(ip_new):
  DEST_IP = os.environ.get('DEST_IP', '')
  if(DEST_IP != ip_new):
    os.environ.setdefault('DEST_IP', ip_new)
    ip = ip_new
  
def checkStatus (id_user):
  global ip
  error, response = sendCommand()
  DEST_IP = os.environ.get('DEST_IP', ip)
  rigth, level = checkAdminRigthts(id_user)
  text = ''
  
  if response.find('перегружен') != -1:
    text = """IP сервера: {0}
Майнкрафт сервер: <code>{1}</code>
""".format(renderIP(id_user, DEST_IP), 'offline')
    if level > 1:
      text += '\n' + response
    return text
  
  if error:
    text = """Последний IP сервера: {0}
Майнкрафт сервер: <code>{1}</code>
""".format(renderIP(id_user, DEST_IP), 'offline')
    if level > 0:
      text += '\n' + response
    return text

  online, players = parser.parsePlayers(response)
  
  return """IP сервера: {0}
Майнкрафт сервер: <code>{1}</code>
Игроков онлайн: <b>{2}</b>
Ники игроков онлайн: <b>{3}</b>
""".format(renderIP(id_user, DEST_IP), 'online', online, players)

def renderIP (id_user, ip):
  rigth, level = checkAdminRigthts(id_user)
  if rigth:
    return ip
  return "у вас не доступа к этой информации"

def sendAdminCommand(command, id_user):
  global ip
  DEST_IP = os.environ.get('DEST_IP', ip)
  rigth, level = checkAdminRigthts(id_user)
  error, response = sendCommand(command)
  
  if error:
    text = 'Майнкрафт не запущен'
    if level > 1:
      text += '\n' + response
    return text
  return response

def checkAdminRigthts(id_user):
  target = os.path.abspath('.')  + '/stickers/admin.txt'
  fileRigths = open(target, 'r')
  strings = fileRigths.readlines()
  for line in strings:
    words = line.split(' ')
    if int(words[0]) == int(id_user):
      return True, int(words[2].replace('\n', ''))
  return False, -1

def sendCommand (command = 'list'):
  global ip, PASS_SERV
  IP_SERV = os.environ.get('DEST_IP', ip)
  response = ''
  mcron = MCRcon(IP_SERV, PASS_SERV)
  try:
    mcron.connect()
    response = mcron.command(command)
    mcron.disconnect()
  except ConnectionRefusedError as e:
    traceError(sendCommand, e)
    return True, 'Хост доступен, майнкрафт не запущен'
  except Exception as e:
    traceError(sendCommand, e)
    return True, 'Сервер выключен'
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
    list_admins_new = list()
    for line in list_string:
      list_admins_new.append(line.replace('\n', '') + '\n')
      str_row = line.split(' ')
      if int(str_row[0]) == int(string_args[0]):
        return '{0} уже является администратором'.format(string_args[1])
      
    file_admin.close()
    list_admins_new.append(string_admin)
    file_admin = open(target, 'w')
    file_admin.writelines(list_admins_new)
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