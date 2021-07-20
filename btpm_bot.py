import telebot, requests, os, glob, req
from PIL import Image
from telebot import types
from utils.logger import traceError
from flask import Flask, request

last_cancel_menu = None # Сообщение с кнопкой отмены
main_keyboard = None

API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)
channel_id_test = -1001205501799
channel_id = -1001544057022
 
def removeImages():
  filelist = glob.glob(os.path.join(os.path.abspath('./stickers'), '*'))
  for f in filelist:
    os.remove(f)

@bot.message_handler(commands=['start'])
def start_message(message):
  global main_keyboard
  if message.chat.type != 'private':
    bot.send_message(message.chat.id, 'Команда не работает в групповых чатах.')
    return
  types.ReplyKeyboardRemove()
  main_keyboard = types.ReplyKeyboardMarkup()
  key_start = types.KeyboardButton(text='Рестарт')
  key_help = types.KeyboardButton(text='Помощь')
  key_sticker = types.KeyboardButton(text='Конвертация')
  key_server = types.KeyboardButton(text='Статус сервера')
  key_time = types.KeyboardButton(text='Расписание')
  key_admin = types.KeyboardButton('/admin')
  rigths, level = req.checkAdminRigthts(message.from_user.id)
  main_keyboard.row(key_sticker, key_server, key_time)
  if rigths:
    main_keyboard.row(key_start, key_help, key_admin)
  else:
    main_keyboard.row(key_start, key_help)
  bot.send_message(message.chat.id, 'Привет дружок. Бот предназначен для вывода статуса сервера по майнкрафту команды Boston tea-party.', reply_markup=main_keyboard)

@bot.message_handler(commands=['help'])
def help_message(message):
  bot.send_message(message.chat.id, """
<code>BostonTeaParty-Alpha-bot</code> создан для целей самообразования и развлечения.

<b>Основное назначение</b> бота - это вывод статуса сервера по майнкрафту для крутых ребят из Boston tea-party и дополнительно для конвертации стикеров из форматов ТГ в более унифицированные (анимированные стикеры конвертируются с визуальными деффектами из-за сторонней библиотеки)

По всем вопросам, предложениям и за получением ip сервера обращаться к @alexstrashiloff

<b>Основые команды</b>:
/start - запуск бота
/help - помощь по работе с ботом
/sticker - конвертация стикеров. После ввода команды отправляете боту любой стикер, он конвертирует его формат <code>png</code> или <code>gif</code>. 
/server - вывода статуса сервера по майнкрафту
/time - время работы сервера
/keyboard - удалить кнопочную клавиатуру, вернуть её можно с помощью команды /start.
""", parse_mode="HTML")

@bot.message_handler(commands=['sticker'])
def stickerMessage(message):
  global last_cancel_menu
  if message.chat.type != 'private':
    bot.send_message(message.chat.id, 'Конвертация доступна только в личном чате с ботом @BTPMAlphaBot')
    return
  else:
    keyboard = types.InlineKeyboardMarkup()
    key_cancel = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
    keyboard.add(key_cancel)
  last_cancel_menu = bot.send_message(message.chat.id, 'Конвертация стикеров. Отправь мне стикер который хочешь отсканировать и подожди некоторое время:', reply_markup=keyboard)
  bot.register_next_step_handler(message, convertSticker)
  
@bot.message_handler(commands=['keyboard'])
def deleteKeyboard(message):
  bot.send_message(message.chat.id, 'Клавиатура удалена.', reply_markup=types.ReplyKeyboardRemove())
  
@bot.message_handler(content_types='new_chat_members')
def newMember(message):
  if message.chat.id == -1001221265428:
    if message.json['new_chat_member']['id'] == 1765237381:
      bot.send_message(message.chat.id, 'Здарова пидоры! Can I join your club?')
    else:
      bot.send_message(message.chat.id, 'welcome to the club buddy!')
      video = open('./videoplayback.mp4', 'rb')
      bot.send_video(message.chat.id, video)
  else:
    bot.send_message(message.chat.id, 'Привет!')

@bot.message_handler(commands=['server'])
def serverStatus (message):
  send = bot.send_message(message.chat.id, 'Ожидание информации с сервера...')
  status = req.checkStatus(message.from_user.id)
  bot.edit_message_text(status, chat_id = message.chat.id, message_id = send.message_id, parse_mode='HTML')
  # bot.send_message(message.chat.id,  status, parse_mode='HTML')

@bot.message_handler(commands=['time'])
def serverTime (message):
  time_string = """Режим работы:
Пн - Вс
С 10:00 - 12:00 (МСК)
До 21:00 - 23:00 (МСК)
"""
  bot.send_message(message.chat.id, time_string, parse_mode='HTML')

@bot.message_handler(commands=['admin'])
def adminCommand (message):
  global last_cancel_menu
  if message.chat.type != 'private':
    return
  ascess, rights = req.checkAdminRigthts(message.from_user.id)
  if not ascess:
    send = bot.send_message(message.chat.id, 'У вас не хватает прав')
  else:  
    keyboard = types.InlineKeyboardMarkup()
    key_cancel = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
    keyboard.add(key_cancel)
    last_cancel_menu = bot.send_message(message.chat.id, """Отправьте команду (<i>Ваш уровень доступа</i>: <b>{0}</b>)
<code>command 'команда на сервер'</code> - выполнить команду на сервере майнкрафт (<i>уровень доступа</i> 1)
<code>add 'id_user' 'username' 'rigth'</code> - добавить админа (rigth = [0-2]) (<i>уровень доступа</i> 2)
<code>rewrite 'список администраторов'</code> - полностью перезаписать список администарторов (<i>уровень доступа</i> 2)
<code>list</code> - список администраторов (<i>уровень доступа</i> 0)
<code>delete 'id_user'</code> - удалить админа (<i>уровень доступа</i> 2)
""".format(rights), parse_mode='HTML', reply_markup=keyboard)
    bot.register_next_step_handler(message, getAdminCommand)
  
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
  if call.data == 'cancel':
    bot.clear_step_handler(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.json['message_id'], reply_markup=None)
    bot.send_message(call.message.chat.id, 'Вы отменили действие.')

@bot.message_handler(content_types=['text'])
def textMessage(message):
  if message.text == 'Рестарт':
    start_message(message)
  elif message.text == 'Помощь':
    help_message(message)
  elif message.text == 'Конвертация':
    stickerMessage(message)
  elif message.text == 'Статус сервера':
    serverStatus(message)
  elif message.text == 'Расписание':
    serverTime(message)
  else:
    print(message.forward_from_chat)
  #   bot.send_message(message.chat.id, 'Поговорить? Это не ко мне а к @alexstrashiloff')
def convertSticker (message):
  global last_cancel_menu
  if message.content_type == 'sticker':
    file_info = bot.get_file(message.sticker.file_id)
    path = os.path.abspath('.') + '/stikers'
    print(path)
    if not os.path.exists(path):
      os.mkdir(path)
      
    try:
      file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    except requests.RequestException as e:
      traceError(e)
      bot.send_message(message.chat.id, 'Извините, нет связи с серверами telegram, повторите попытку позже.')
      return

    target = os.path.abspath('.')  + '/stickers/'
    
    if file_info.file_path.find('.webp') != -1:
      open(target+'sticker.webp', 'wb').write(file.content)
      image = Image.open(target+'sticker.webp')
      image.save(target+'sticker.png', 'png')
      new_images = target+'sticker.png'
    elif file_info.file_path.find('.tgs') != -1:
      open(target+'sticker.tgs', 'wb').write(file.content)
      # print ('lottie_convert.py --gif-skip-frames 4 {0} {1}'.format(target+'sticker.tgs', target+'sticker.gif'))
      os.system('lottie_convert.py {0} {1}'.format(target+'sticker.tgs', target+'sticker.gif'))
      new_images = target+'sticker.gif'
    else:
      bot.send_message(message.chat.id, 'Что это?? Я с таким не работаю.')
      return
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
    try:
      bot.send_document(message.chat.id, open(new_images, 'rb'))
    except Exception:
      traceError ('Ошибка при отправке файла /sticker.')
      bot.send_message(message.chat.id, 'Произошла внутренняя ошибка, приносим свои извинения!')
    # removeImages()
  else:
    bot.send_message(message.chat.id, 'Извините это не стикер, повторите.')
    bot.register_next_step_handler(message, convertSticker)
    
def getAdminCommand(message):
  global last_cancel_menu
  text = str(message.text)
  command = text.replace(' ', '|', 1).split('|', maxsplit=1)
  if command[0] == 'command':
    text = req.sendAdminCommand(command[1], message.from_user.id)
    bot.send_message(message.chat.id, text)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
  elif command[0] == 'add':
    text = req.setNewAdmin(command[1], message.from_user.id)
    bot.send_message(message.chat.id, text)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
  elif command[0] == 'list':
    text = req.showListAdmins()
    bot.send_message(message.chat.id, text)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
  elif command[0] == 'delete':
    text = req.deleteAdmin(command[1], message.from_user.id)
    bot.send_message(message.chat.id, text)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
  elif command[0] == 'rewrite':
    text = req.addAdminList(command[1], message.from_user.id)
    bot.send_message(message.chat.id, text)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
  else:
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
    bot.send_message(message.chat.id, 'Команда не распознана.')
  
@server.route('/setip', methods=['POST'])
def setIp ():
  json_string = request.get_data().decode('utf-8')
  req.updateIp(json_string)
  return '!', 200

@server.route('/status', methods=['POST'])
def updateStatusChannel():
  global channel_id
  json_string = request.get_data().decode('utf-8')
  bot.send_message(channel_id, json_string['status'])
  return '!', 200

@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
  json_string = request.get_data().decode('utf-8')
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return '!', 200

@server.route('/')
def webhook():
  bot.remove_webhook()
  bot.set_webhook(url='https://btpm-bot.herokuapp.com/' + API_TOKEN)
  return '!', 200

if __name__ == '__main__':
  # server.debug = True
  # bot.polling(none_stop=True)
  server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
  