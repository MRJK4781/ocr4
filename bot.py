# ©️ @Deccan_Botz 

from telegram import ChatAction,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackQueryHandler,PicklePersistence
import logging
import os
from functools import wraps
import requests

API_KEY = os.environ.get("API_KEY","") 

TOKEN = os.environ.get("BOT_TOKEN","")

OWNER = os.environ.get("OWNER", "")

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@run_async     
@send_typing_action
def start(update,context):
    """Send a message when the command /start is issued."""
    global first
    first=update.message.chat.first_name
    update.message.reply_text('Hi! '+str(first)+' \n\nWelcome to OCR Bot.\n\nJust send a clear image to me and i will recognize the text in the image and send it as a message!\n\nCheck /help for more...')

def help(update,context):
    """Send a message when the command /help is issued."""
    global first
    first=update.message.chat.first_name
    update.message.reply_text('Hi! '+str(first)+' \n\nFollow these steps...\n➥ First Send me a Clear Image to me \n➥ Extracted Text is Uploaded as Message!')


@run_async
@send_typing_action
def convert_image(update,context):
        file_id = update.message.photo[-1].file_id
        newFile=context.bot.get_file(file_id)
        file= newFile.file_path
        context.user_data['filepath']=file
        keyboard =  [[
                      InlineKeyboardButton("English", callback_data='eng'),
		      InlineKeyboardButton("Chinese", callback_data='chs')
                     ],     
                     ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Select the Language Here 👇", reply_markup=reply_markup)

@run_async
def button(update,context):
    filepath=context.user_data['filepath']
    query = update.callback_query
    query.answer()
    query.edit_message_text("Extracting Text....")
    data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={filepath}&language=eng&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
    data=data.json()
    if data['IsErroredOnProcessing']==False:
        message=data['ParsedResults'][0]['ParsedText']
        query.edit_message_text(f"{message}")
    else:
        query.edit_message_text(text="⚠️ Something went wrong")

persistence=PicklePersistence('userdata')
def main():
    token=TOKEN 
    updater = Updater(token,use_context=True,persistence=persistence)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(MessageHandler(Filters.photo, convert_image))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling(clean=True)
    updater.idle()
 
	
if __name__=="__main__":
	main()
