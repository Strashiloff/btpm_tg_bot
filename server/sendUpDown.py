import sys, requests, json, time

def sendStatus(flag):
  string = None
  time_ = time.strftime('%m/%d/%Y %H:%M:%S GMT%Z')
  if flag == 0:
    string = 'Сервер выключен (' + time_ + ')'
  elif flag == 1:
    string = 'Сервер запущен (' + time_ + ')'
  try:
    print(string)
    data = json.dumps({'status': string})
    requests.post('https://btpm-bot.herokuapp.com/status', data)
  except Exception as e:
    print(sendStatus, e)

if __name__ == '__main__':
  if len (sys.argv) > 1:
    sendStatus(int(sys.argv[1]))