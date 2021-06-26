import telebot, requests, os, glob
from api import API_TOKEN
from PIL import Image
from telebot import types

last_cancel_menu = None # Сообщение с кнопкой отмены
main_keyboard = None

bot = telebot.TeleBot(API_TOKEN)

def removeImages():
  filelist = glob.glob(os.path.join(os.path.abspath('./stickers'), '*'))
  for f in filelist:
    os.remove(f)

@bot.message_handler(commands=['start'])
def start_message(message):
  global main_keyboard
  types.ReplyKeyboardRemove()
  
  main_keyboard = types.ReplyKeyboardMarkup()
  key_start = types.KeyboardButton(text='Рестарт')
  key_help = types.KeyboardButton(text='Помощь')
  key_sticker = types.KeyboardButton(text='Конвертация')
  # main keyboard (bot menu)
  main_keyboard.row(key_start, key_help)
  main_keyboard.row(key_sticker)
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
""", parse_mode="HTML")

@bot.message_handler(commands=['sticker'])
def stickerMessage(message):
  global last_cancel_menu
  keyboard = types.InlineKeyboardMarkup()
  key_cancel = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
  keyboard.add(key_cancel)
  last_cancel_menu = bot.send_message(message.chat.id, 'Конвертация стикеров. Отправь мне стикер который хочешь отсканировать и подожди некоторое время:', reply_markup=keyboard)
  bot.register_next_step_handler(message, convertSticker)
  
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
  global last_cancel_menu
  if call.data == 'cancel':
    bot.clear_step_handler(call.message)
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, 'Вы отменили действие')

@bot.message_handler(content_types=['text'])
def textMessage(message):
  if message.text == 'Рестарт':
    start_message(message)
  elif message.text == 'Помощь':
    help_message(message)
  elif message.text == 'Конвертация':
    stickerMessage(message)
  else:
    bot.send_message(message.chat.id, 'Поговорить? Это не ко мне а к @alexstrashiloff')
  
def convertSticker (message):
  global last_cancel_menu
  if message.content_type == 'sticker':
    file_info = bot.get_file(message.sticker.file_id)
    try:
      file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    except requests.RequestException as e:
      print(e)
      bot.send_message(message.chat.id, 'Извините, нет связи с серверами telegram, повторите попытку позже.')
      return
      
    open(file_info.file_path, 'wb').write(file.content)
    if file_info.file_path.find('.webp') != -1:
      image = Image.open(file_info.file_path)
      # image = image.convert('RGB')
      new_images = file_info.file_path.replace('.webp', '.png')
      image.save(new_images, 'png')
    elif file_info.file_path.find('.tgs') != -1:
      new_images = file_info.file_path.replace('.tgs', '.gif')
      os.system('lottie_convert.py --gif-skip-frames 4 {0} {1}'.format(file_info.file_path, new_images))
    else:
      bot.send_message(message.chat.id, 'Что это?? Я с таким не работаю')
      return
    bot.edit_message_reply_markup(last_cancel_menu.chat.id, last_cancel_menu.message_id, reply_markup=None)
    try:
      bot.send_document(message.chat.id, open(new_images, 'rb'))
    except Exception:
      print ('Ошибка при отправке файла /sticker')
      bot.send_message(message.chat.id, 'Произошла внутренняя ошибка, приносим свои извинения!')
    removeImages()
  else:
    bot.send_message(message.chat.id, 'Извините это не стикер, повторите')
    bot.register_next_step_handler(message, convertSticker)

bot.polling(none_stop=True)