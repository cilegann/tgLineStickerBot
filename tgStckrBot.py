from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler,Filters
import requests
import os
import uuid
import zipfile
import json
from PIL import Image
import logging
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random
from configparser import ConfigParser, SafeConfigParser
import traceback
from telegram.ext.dispatcher import run_async
import threading

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#todo: animated url https://stickershop.line-scdn.net/stickershop/v1/sticker/{stickerid}/iPhone/sticker_animation@2x.png

def randomEmoji():
    emoji="😺😂🤣😇😉😋😌😍😘👀💪🤙🐶🐱🐭🐹🐰🐻🐼🐨🐯🦁🐮🐷🐽🐸🐵🦍🐔🐧🐦🐤🐣🐺🐥🦊🐗🐴🦓🦒🦌🦄🐝🐛🦋🐌🐢🐙🦑🐓🦇🐖🐎🐑🐏🐐🦏🐘🐫🐪🐄🐂🦔🐿🐃🐅🐆🐊🐇🐈🐋🐳🐩🐕🦉🐬🦈🐡🦆🦅🐟🐠🕊🌞🌝🌕🌍🌊⛄✈🚲🛵🏎🚗🚅🌈🗻"
    return random.sample(emoji,1)[0]

def addStickerThread(bot,update,statusMsg,fid,stkId,emj):
    try:
        with zipfile.ZipFile(f"{fid}.zip",'r') as zip_ref:
            zip_ref.extractall(fid)
        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：分析貼圖包")
        info=json.load(open(f"{fid}/productInfo.meta"))
        enName=f"{info['title']['en']}"
        if 'zh-Hant' in info['title']:
            twName=f"{info['title']['zh-Hant']}"
        else:
            twName=enName
        stkName=f"line{stkId}_by_{botName}"
        try:
            stkSet=bot.getStickerSet(stkName)
            if len(stkSet.stickers)!=0:
                statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：更新貼圖集")
                for stk in stkSet.stickers:
                    bot.deleteStickerFromSet(stk.file_id)
        except telegram.error.BadRequest:
            pass
        for i,s in enumerate(info['stickers']):
            statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：處理並上傳貼圖 ({i}/{len(info['stickers'])})")
            img=Image.open(f"{fid}/{s['id']}@2x.png")
            ratio=s['width']/s['height']
            if s['width']>s['height']:
                img=img.resize((512,int(512/ratio)))
            else:
                img=img.resize((int(512*ratio),512))
            img.save(f"{fid}/{s['id']}@2x.png")
            try:
                bot.addStickerToSet(update.message.from_user.id,stkName,emj,png_sticker=open(f"{fid}/{s['id']}@2x.png",'rb'))
            except telegram.error.BadRequest:
                bot.createNewStickerSet(update.message.from_user.id,stkName,f"{twName}_@{botName}",emj,png_sticker=open(f"{fid}/{s['id']}@2x.png",'rb'))
        statusMsg.edit_text(f'好惹！')
        update.message.reply_html(f'給你 <a href="https://t.me/addstickers/{stkName}">{twName}</a> ！')
    except Exception as e:
        statusMsg.edit_text("啊ＧＧ，我有點壞掉了，你等等再試一次好嗎....\n"+str(e))
        print(traceback.format_exc())
    finally:
        try:
            import shutil
            shutil.rmtree(fid)
            os.remove(f"{fid}.zip")
        except:
            pass

@run_async
def start(bot,update):
    update.message.reply_text("/add - 新增貼圖\n/upload - 上傳Line貼圖zip\n/delete - 刪除某個貼圖\n/purge - 清除貼圖集裡的全部貼圖\n/cancel - 取消\n免責聲明：此工具目的是協助貼圖創作者方便移植貼圖，請勿侵犯原作者權益。本工具及開發者不承擔任何侵權帶來的法律責任，所有責任皆由使用者承擔。")

@run_async
def add(bot,update):
    update.message.reply_text("好的，你要移植哪個貼圖？\n請告訴我 line 貼圖集的網址！\n\n（僅限創作者使用，請勿侵權，請參考 /start 中的說明）\n\n要取消的話請叫我 /cancel")
    return 0

@run_async
def continueAdd(bot, update):
    emj=randomEmoji()
    try:
        stkUrl=update.message.text
        if "?" not in stkUrl:
            rindex=stkUrl.rfind('/')
            lindex=stkUrl.rfind('/',0,rindex)
        else:
            rindex=stkUrl.rfind("?")
            lindex=stkUrl.rfind("/")
        if rindex==-1 or lindex==-1:
            update
            return
        stkId=stkUrl[lindex+1:rindex]
        # stkId="10429834"
        statusMsg=update.message.reply_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦")
        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：抓取貼圖包")
        myfile=requests.get(f"http://dl.stickershop.line.naver.jp/products/0/0/1/{stkId}/iphone/stickers@2x.zip")
        fid=stkId
        with open(f'{fid}.zip','wb') as file:
            file.write(myfile.content)
        t=threading.Thread(target=addStickerThread,args=(bot,update,statusMsg,fid,stkId,emj))
        t.start()
    except Exception as e:
        update.message.reply_text("啊ＧＧ，我有點壞掉了，你等等再試一次好嗎....\n"+str(e))
        print(traceback.format_exc())
        try:
            import shutil
            shutil.rmtree(fid)
            os.remove(f"{fid}.zip")
        except:
            pass    
    return ConversationHandler.END

@run_async
def upload(bot,update):
    update.message.reply_text("好的，請上傳 line 貼圖集的 zip！\n\n（僅限創作者使用，請勿侵權，請參考 /start 中的說明）\n\n要取消的話請叫我 /cancel")
    return 0

@run_async
def continueUpload(bot, update):
    emj=randomEmoji()
    try:
        statusMsg=update.message.reply_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦")
        fid=str(uuid.uuid1())
        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：取得貼圖包")
        zipFile=update.message.document.get_file()
        zipFile.download(f"{fid}.zip")
        stkId=""
        with zipfile.ZipFile(f"{fid}.zip",'r') as zip_ref:
            zip_ref.extractall(fid)
        # statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：分析貼圖包")
        if not os.path.exists(f"{fid}/productInfo.meta"):
            update.message.reply_text("你上傳的東西好像不是Line的標準貼圖包哦，抱歉啦不能幫你了")
            return ConversationHandler.END
        info=json.load(open(f"{fid}/productInfo.meta"))
        stkId=info['packageId']
        t=threading.Thread(target=addStickerThread,args=(bot,update,statusMsg,fid,stkId,emj))
        t.start()
    except Exception as e:
        update.message.reply_text("啊ＧＧ，我有點壞掉了，你等等再試一次好嗎....\n"+str(e))
        print(traceback.format_exc())
        try:
            import shutil
            shutil.rmtree(fid)
            os.remove(f"{fid}.zip")
        except:
            pass  
    return ConversationHandler.END

@run_async
def delete(bot,update):
    if update.message.from_user.id not in adminId:
        update.message.reply_text("泥素隨？？？？你不能做這件事餒")
        return ConversationHandler.END
    update.message.reply_text("把你要刪掉的貼圖傳給我吧！\n要取消的話請叫我 /cancel")
    return 0

@run_async
def continueDelete(bot,update):
    stickerToDelete=update.message.sticker.file_id
    try:
        bot.deleteStickerFromSet(stickerToDelete)
        update.message.reply_text("好惹，我把他從貼圖集移除了")
    except:
        update.message.reply_text("抱歉....能力所及範圍外")
    finally:
        return ConversationHandler.END

@run_async
def purge(bot,update):
    if update.message.from_user.id not in adminId:
        update.message.reply_text("泥素隨？？？？你不能做這件事餒")
        return ConversationHandler.END
    update.message.reply_text("把你要清空的貼圖集中的一個貼圖傳給我吧！\n要取消的話請叫我 /cancel")
    return 0
    
@run_async
def continuePurge(bot,update):
    stickerToDelete=update.message.sticker.set_name
    try:
        stkSet=bot.getStickerSet(stickerToDelete)
        if len(stkSet.stickers)!=0:
            for stk in stkSet.stickers:
                bot.deleteStickerFromSet(stk.file_id)
        update.message.reply_text("好惹，我把貼圖集清空了")
    except:
        update.message.reply_text("抱歉....能力所及範圍外")
    finally:
        return ConversationHandler.END

@run_async
def cancel(bot,update):
    update.message.reply_text("好的 已經取消動作")
    return ConversationHandler.END

if __name__=="__main__":
    if os.path.exists('secret.cfg'):
        cfg=SafeConfigParser(os.environ)
        cfg.read('secret.cfg')
        botName=cfg.get('DEFAULT','botName')
        botToken=cfg.get('DEFAULT','botToken')
        adminId=json.loads(cfg.get('DEFAULT','adminId'))
    else:
        botName=os.environ.get('botName')
        botToken=os.environ.get('botToken')
        adminId=json.loads(os.environ.get('adminId',"{}"))

    updater = Updater(botToken)
    cancelHandler=CommandHandler('cancel',cancel)
    #updater.dispatcher.add_handler(cancelHandler,group=0)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    addHandler=ConversationHandler(
        entry_points=[ CommandHandler('add',add)],
        states={
            0:[
                MessageHandler(Filters.text,continueAdd)
            ]
        },fallbacks=[]
    )
    uploadHandler=ConversationHandler(
        entry_points=[ CommandHandler('upload',upload)],
        states={
            0:[
                MessageHandler(Filters.document.mime_type("multipart/x-zip"),continueUpload)
            ]
        } ,fallbacks=[]
    )
    deleteHandler=ConversationHandler(
        entry_points=[ CommandHandler('delete',delete)],
        states={
            0:[
                MessageHandler(Filters.sticker,continueDelete)
            ]
        } ,fallbacks=[]
    )
    purgeHandler=ConversationHandler(
        entry_points=[ CommandHandler('purge',purge)],
        states={
            0:[
                MessageHandler(Filters.sticker,continuePurge)
            ]
        } ,fallbacks=[]
    )

    updater.dispatcher.add_handler(addHandler)
    updater.dispatcher.add_handler(uploadHandler)
    updater.dispatcher.add_handler(deleteHandler)
    updater.dispatcher.add_handler(purgeHandler)
    if os.path.exists('secret.cfg'):
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",port=int(os.environ.get('PORT', '8443')))
        updater.bot.set_webhook("https://linestkr2tg.herokuapp.com/")
    updater.idle()
