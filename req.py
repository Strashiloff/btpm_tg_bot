import requests, os, json, utils.parser as parser, services.db as db
from utils.logger import traceError
from flask import jsonify
from mcrcon import MCRcon, MCRconException

PASS_SERV = os.environ.get('RCON_PASS')
mcron = None

def updateIp(ip_new):
  ip = db.getIp()
  if(ip != ip_new):
    check = db.updateIp(ip_new)
  
def checkStatus (id_user):
  error, response = sendCommand()
  DEST_IP = db.getIp()
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
  return 'у вас не доступа к этой информации'

def sendAdminCommand(command, id_user):
  DEST_IP = db.getIp()
  rigth, level = checkAdminRigthts(id_user)
  if level > 0:
    error, response = sendCommand(command)
  else:
    return 'у вас недостаточно прав'
  
  if error:
    text = 'Майнкрафт не запущен'
    if level > 1:
      text += '\n' + response
    return text
  return response

def checkAdminRigthts(id_user):
  strings = db.getListAdmins()
  for line in strings:
    words = line.split(' ')
    if int(words[0]) == int(id_user):
      return True, int(words[2].replace('\n', ''))
  return False, -1

def sendCommand (command = 'list'):
  global PASS_SERV
  IP_SERV = db.getIp()
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

def setNewAdmin (string_admin, id_user):
  target = os.path.abspath('.') + '/stickers/admin.txt'
  string_args = string_admin.split(' ')
  
  rights, level = checkAdminRigthts(id_user)
  
  if (level < 2):
    return 'У вас недостаточно прав доступа.'
  
  resp = checkErrorAdmin(string_admin)
  if resp != None:
    return resp
  
  try:
    list_string = db.getListAdmins()
    check = checkExistAdmin(list_string, string_admin)
    if check != None:
      return check
    
    new_admin_param = string_admin.split(' ')
    check = db.addNewAdmin(new_admin_param[0], new_admin_param[1], new_admin_param[2])
    
  except Exception as e:
    print(setNewAdmin, e)
    return 'Произошла ошибка.'
    
  return 'Новый администратор добавлен.'

def checkExistAdmin (list_string, admins):
  list_admins = admins.split('\n')
  for admin in list_admins:
    string_args = admin.split(' ')
    for line in list_string:
      str_row = line.split(' ')
      if int(str_row[0]) == int(string_args[0]):
        return '{0} (id:{1}) уже является администратором.'.format(string_args[1], string_args[0])
      
  return None

def checkErrorAdmin(admins):
  arr_str = admins.split('\n')
  for i, string in enumerate(arr_str):
    string_args = string.split(' ')
    if len(string_args) != 3 or not string_args[0].isdigit() or not string_args[2].isdigit():
      return 'Ошибка в команде (строка ' + (i+1) + ')'
  
    if int(string_args[2]) > 2 and int(string_args[2]) < 1:
      return 'Чи шо, не таких прав доступа... есть только 0, 1 и 2 (строка ' + (i+1) + ')'
    
  return None

def addAdminList (list_admins, id_user):
  rights, level = checkAdminRigthts(id_user)
  
  if (level < 2):
    return 'У вас недостаточно прав доступа.'
  
  resp = checkErrorAdmin(list_admins)
  if resp != None:
    return resp
  
  list_string = db.getListAdmins()
  check = checkExistAdmin(list_string, list_admins)
  if check != None:
    return check
  
  list_string_admins = list_admins.split('\n')
  try:
    for admin in list_string_admins:
      param_admin = admin.split(' ')
      check = db.addNewAdmin(param_admin[0], param_admin[1], param_admin[2])
      
  except Exception as e:
    print(addAdminList, e)
    return 'Произошла ошибка.'
    
  return 'Список администраторов обновлен.'

def showListAdmins ():
  try:
    list_admins = db.getListAdmins()
  except Exception as e:
    print(showListAdmins, e)
    return 'Произошла ошибка.'
  if (list_admins == False):
    return 'Произошла ошибка.'
  
  return ''.join(list_admins)

def deleteAdmin(id_admin, id_user):
  rights, level = checkAdminRigthts(id_user)
  
  if (level < 2):
    return 'У вас недостаточно прав допступа.'
  
  if not id_admin.isdigit():
    return 'Ошибка, id неверен.'
  
  try:
    list_admins = db.getListAdmins()
    
    if list_admins == False: 
      return 'Произошла ошибка.'
    
    find = None
    for line in list_admins:
      line_text = line.split(' ')
      if int(line_text[0]) == int(id_admin):
        find = line
        if int(line_text[2]) == 2 and int(id_user) != 93812289:
          return 'Этого администратора нельзя удалить.'
      
    if find == None:
      return 'Такого администратора нет.'
    
    check = db.deleteAdmin(id_admin)
    
  except Exception as e:
    print(deleteAdmin, e)
    return 'Произошла ошибка.'
  return 'Администратор удален.'