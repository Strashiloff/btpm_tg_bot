import psycopg2, sys, os
from services import requestdb
# sys.path.insert(0, '..') # Костыль, стыдно...
# import api
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import Error

DATABASE_URL = os.environ.get('DATABASE_URL')

def connectDb ():
  conn = None
  try:
    if DATABASE_URL == None:
      return None
      # conn = psycopg2.connect(database=api.DB_NAME, user=api.DB_USER, password=api.DB_USER_PASSWORD, port=api.DB_PORT, host=api.DB_HOST)
    else:
      conn = psycopg2.connect(DATABASE_URL, sslmode='require')
      
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return None
  
  return conn

def InitDb ():
  try:
    conn = connectDb()
    cursor = conn.cursor()
    # cursor.execute(requestdb.SELECT_DB_NAMES)
    # data = cursor.fetchall()
    # check = checkExistDb(data)
    # if not check:
    #   cursor.execute(requestdb.CREATE_DB_BOT)

    cursor.execute(requestdb.SELECT_TABLES_NAMES)
    listTb = cursor.fetchall()
    check = checkExistTable(listTb, 'admins')
    
    if not check:
      cursor.execute(requestdb.CREATE_TABLE_ADMINS)
      cursor.execute(requestdb.ADD_ADMIN.format(93812289, 'alexstrashiloff', 2))
      
    check1 = checkExistTable(listTb, 'ip_last')
    
    if not check1:
      cursor.execute(requestdb.CREATE_TABLE_IP)
      cursor.execute(requestdb.ADD_IP.format(os.environ.get('DESP_IP', '0.0.0.0')))

  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return False
  
  finally:
    if conn:
      cursor.close()
      conn.close()
      
  return True

def checkExistDb (data):
  for elem in data:
    if elem[0] == 'bot':
      return True
  return False

def checkExistTable (data, table):
  for elem in data:
    if elem[0] == table:
      return True
  return False

def checkExistAdmin (data, _id):
  for elem in data:
    if int(elem[0]) == _id:
      return True
  return False

def getListAdmins():
  try:
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(requestdb.SELECT_ALL_ADMINS)
    data = cursor.fetchall()
    
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return False
  
  finally:
    if conn:
      cursor.close()
      conn.close()
      
  return formatAdminsList(data)

def addNewAdmin(_id, username, level):
  try:
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(requestdb.SELECT_ALL_ADMINS)
    data = cursor.fetchall()
    check = checkExistAdmin(data, _id)
    if check:
      return False
    
    text = requestdb.ADD_ADMIN.format(_id, username, level)
    cursor.execute(text)
    
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return False
  
  finally:
    if conn:
      cursor.close()
      conn.close()
  
  return True

def formatAdminsList(arr):
  new_arr = list()
  for _trust in arr:
    _admin = ''
    for i, string in enumerate(_trust):
      if i < len(_trust) - 1:
        _admin += str(string) + ' '
      else:
        _admin += str(string) + '\n'
    new_arr.append(_admin)
    
  return new_arr

def deleteAdmin(_id):
  try:
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(requestdb.SELECT_ALL_ADMINS)
    data = cursor.fetchall()
    check = checkExistAdmin(data, _id)
    if check:
      return False
    
    text = requestdb.DELETE_ADMIN.format(_id)
    cursor.execute(text)
    
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return False
  
  finally:
    if conn:
      cursor.close()
      conn.close()

  return True

def getIp ():
  try:
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(requestdb.SELECT_IP)
    data = cursor.fetchone()
    
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return None
  
  finally:
    if conn:
      cursor.close()
      conn.close()

  return data[0]

def updateIp(_ip):
  try:
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(requestdb.UPDATE_IP.format(_ip))
    
  except (Exception, Error) as e:
    print('POSTGRES:', e)
    return False
  
  finally:
    if conn:
      cursor.close()
      conn.close()

  return True