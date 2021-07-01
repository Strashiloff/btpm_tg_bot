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

def removeImages():
  filelist = glob.glob(os.path.join(os.path.abspath('./stickers'), '*'))
  for f in filelist:
    os.remove(f)

@bot.message_handler(commands=['start'])
def start_message(message):
  global main_keyboard
  if message.chat.type != 'private':
    bot.send_message(message.chat.id, 'Команда не работает в групповых чатах')
    return
  types.ReplyKeyboardRemove()
  main_keyboard = types.ReplyKeyboardMarkup()
  key_start = types.KeyboardButton(text='Рестарт')
  key_help = types.KeyboardButton(text='Помощь')
  key_sticker = types.KeyboardButton(text='Конвертация')
  key_server = types.KeyboardButton(text='Статус сервера')
  # main keyboard (bot menu)
  main_keyboard.row(key_start, key_help)
  main_keyboard.row(key_sticker, key_server)
  bot.send_message(message.chat.id, 'Привет дружок. Это тестовая версия бота. Он предназначен для вывода статуса сервера по майнкрафту команды Boston tea-party', reply_markup=main_keyboard)

@bot.message_handler(commands=['help'])
def help_message(message):
  bot.send_message(message.chat.id, """
<code>BostonTeaParty-Alpha-bot</code> создан для целей самообразования и развлечения.

<b>Основной задачей</b> бота будет вывод статуса сервера по майнкрафту для крутых ребят из Boston tea-party (в разработке) 
и дополнительно для конвертации стикеров из форматов ТГ в более унифицированные (анимированные стикеры конвертируются с визуальными деффектами из-за сторонней библиотеки)

По всем вопросам и предложениям @alexstrashiloff

<b>Основые команды</b>:
/start - запуск бота
/help - помощь по работе с ботом
/sticker - конвертация стикеров. После ввода команды отправляете боту любой стикер, он конвертирует его формат <code>png</code> или <code>gif</code>. 
/server - вывода статуса сервера по майнкрафту
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
  
@bot.message_handler(content_types='new_chat_members')
def newMember(message):
  if message.json['new_chat_member']['id'] == 1765237381:
    bot.send_message(message.chat.id, 'Здарова пидоры! Can I join your club?')
  else:
    bot.send_message(message.chat.id, 'welcome to the club buddy!')
    video = open('./videoplayback.mp4', 'rb')
    bot.send_video(message.chat.id, video)

@bot.message_handler(commands=['server'])
def serverStatus (message):
  send = bot.send_message(message.chat.id, 'Ожидание информации с сервера...')
  status = req.checkStatus()
  bot.edit_message_text(status, chat_id = message.chat.id, message_id = send.message_id, parse_mode='HTML')
  # bot.send_message(message.chat.id,  status, parse_mode='HTML')
  
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
  if call.data == 'cancel':
    bot.clear_step_handler(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.json['message_id'], reply_markup=None)
    bot.send_message(call.message.chat.id, 'Вы отменили действие')

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
  else:
    bot.send_message(message.chat.id, 'Поговорить? Это не ко мне а к @alexstrashiloff')
  
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
      bot.send_message(message.chat.id, 'Что это?? Я с таким не работаю')
      return
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
    try:
      bot.send_document(message.chat.id, open(new_images, 'rb'))
    except Exception:
      traceError ('Ошибка при отправке файла /sticker')
      bot.send_message(message.chat.id, 'Произошла внутренняя ошибка, приносим свои извинения!')
    # removeImages()
  else:
    bot.send_message(message.chat.id, 'Извините это не стикер, повторите')
    bot.register_next_step_handler(message, convertSticker)
    
@server.route('/setip', methods=['POST'])
def setIp ():
  json_string = request.get_data().decode('utf-8')
  req.updateIp(json_string)

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
  