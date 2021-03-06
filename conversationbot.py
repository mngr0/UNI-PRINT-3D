#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import telegram
import linuxcnc
from machinekit import hal
import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from subprocess import check_output


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

err = hal.Pin("edge.out")

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [['bianca']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

try:
    import cv2
    cv2_cap = cv2.VideoCapture(0)
    if not cv2_cap.isOpened():
        cv2_cap = cv2.VideoCapture(1)
        if not cv2_cap.isOpened():
            print ("Camera not found!")
            cv2_cap = None

except ImportError:
    print ("working without videocamera")

if not cv2_cap is None:
    cv2_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1);

users=[153740336,419019135]

s = linuxcnc.stat()
warning_sent=0

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def periodic_check(context):
    global warning_sent
    s.poll()
    #print("immalive")
    #context.bot.send_message(chat_id=users[0], text="bianca in pausa", reply_markup=markup)
    if (err.get() ):
        if warning_sent == 0:
            print("sending msg")
            for user in users:
                context.bot.send_message(chat_id=user, text="bianca in pausa", reply_markup=markup)
            warning_sent= warning_sent+1
    else:
        warning_sent= 0
#check also for program ended

def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])

def start(update, context):
    print("received status request by ", update.message.chat_id)
    s.poll()
    state=""
    f=s.file
    l=s.motion_line + 1
    if os.path.isfile(f):
        n=wc(f)
    else:
        n=l
        f= "no file"
    state = "Bianca:\nExecuting file: %s\nLinea %s di %s, stato=%s per cento"%(f,str(l),str(n),(l*100/n))
    print(state)
    context.bot.send_message(chat_id=update.message.chat_id, text=state,reply_markup=markup)

    if not cv2_cap is None :
        #flushing the buffer, that should be 1 image, but let's consume 4 just to be sure
        ret , img = cv2_cap.read()
        ret , img = cv2_cap.read()
        ret , img = cv2_cap.read()
        ret , img = cv2_cap.read()
        if ret == False:
            context.bot.send_message(chat_id=update.message.chat_id, text="Unable to capture photo")
            print ("Error reading image")
            return
        cv2.resize(img, (640, 480))
        img_name="test.png"
        cv2.imwrite(img_name,cv2.resize(img, (640, 480)))
        p=open(img_name,"rb")
        context.bot.send_photo(chat_id=update.message.chat_id, photo=p )
        p.close()
        os.remove(os.path.abspath(img_name))

    return CHOOSING


def welcome(update, context):
    update.message.reply_text("Welcome!", reply_markup=markup)
    return CHOOSING

def main():
    updater = Updater("224391427:AAEc0CvVN4SM_FZ0vi0anlCEuKptRysQSa0", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.regex("^bianca$"),start))
    updater.job_queue.run_repeating(periodic_check,5,context=users[0])
    dp.add_error_handler(error)

    print("Telegram bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
