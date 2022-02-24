from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler,Filters
import requests
import os
import uuid
import zipfile
import json
import logging
import telegram
import random
from configparser import SafeConfigParser
import traceback
from telegram.ext.dispatcher import run_async
import threading
import re
from imageHdl import apng2webm, tryResizePng

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def randomEmoji():
    emoji = "😺😂🤣😇😉😋😌😍😘👀💪🤙🐶🐱🐭🐹🐰🐻🐼🐨🐯🦁🐮🐷🐵🦍🐔🐧🐦🐤🐣🐺🐥🦊🐗🐴🦓🦒🦌🦄🐌🐢🐓🐖🐎🐑🐏🐐🦏🐘🐫🐪🐄🐂🦔🐃🐅🐆🐊🐇🐈🐋🐳🐩🐕🦉🐬🦈🐡🦆🦅🐟🐠🕊🌞🌝🌕🌍🌊⛄✈🚲🛵🏎🚗🚅🌈🗻"
    return random.sample(emoji, 1)[0]

def addStickerThread(bot, update, statusMsg, fid, stkId, emj, isAnimated=False):
    try:
        with zipfile.ZipFile(f"{fid}.zip", 'r') as zip_ref:
            zip_ref.extractall(fid)

        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：分析貼圖包")
        info = json.load(open(f"{fid}/productInfo.meta", encoding='UTF-8'))
        enName = f"{info['title']['en']}"
        twName = f"{info['title']['zh-Hant']}" if 'zh-Hant' in info['title'] else enName
        stkName = f"line{stkId}_animated_by_{botName}" if isAnimated else f"line{stkId}_by_{botName}"

        try:
            stkSet = bot.getStickerSet(stkName)
            if len(stkSet.stickers) != 0:
                statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：更新貼圖集")
                for stk in stkSet.stickers:
                    bot.deleteStickerFromSet(stk.file_id)
        except telegram.error.BadRequest:
            pass

        for i, s in enumerate(info['stickers']):
            statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：處理並上傳貼圖 ({i}/{len(info['stickers'])})")
            pngFile = f"{fid}/animation@2x/{s['id']}@2x.png" if isAnimated else f"{fid}/{s['id']}@2x.png"
            wh, fps = tryResizePng(pngFile)
            if isAnimated:
                try:
                    bot.addStickerToSet(update.message.from_user.id, stkName, emj, webm_sticker=open(apng2webm(pngFile, wh, fps), 'rb'))
                except telegram.error.BadRequest as e:
                    logging.error(e)
                    bot.createNewStickerSet(update.message.from_user.id, stkName, f"{twName}_@{botName}", emj, webm_sticker=open(apng2webm(pngFile, wh, fps),'rb'))
            else:
                try:
                    bot.addStickerToSet(update.message.from_user.id, stkName,emj, png_sticker=open(pngFile,'rb'))
                except telegram.error.BadRequest as e:
                    logging.error(e)
                    bot.createNewStickerSet(update.message.from_user.id, stkName, f"{twName}_@{botName}", emj, png_sticker=open(pngFile,'rb'))

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

def start(update, context):
    update.message.reply_text("/add - 新增貼圖\n/upload - 上傳Line貼圖zip\n/delete - 刪除某個貼圖\n/purge - 清除貼圖集裡的全部貼圖\n/cancel - 取消\n免責聲明：此工具目的是協助貼圖創作者方便移植貼圖，請勿侵犯原作者權益。本工具及開發者不承擔任何侵權帶來的法律責任，所有責任皆由使用者承擔。")

def add(update, context):
    update.message.reply_text("好的，你要移植哪個貼圖？\n請告訴我 line 貼圖集的網址！\n\n（僅限創作者使用，請勿侵權，請參考 /start 中的說明）\n\n要取消的話請叫我 /cancel")
    return 0

def continueAdd(update, context):
    emj = randomEmoji()
    try:
        stkUrl=update.message.text
        r = re.compile("[0-9]{2,}")
        result = r.search(stkUrl)
        stkId = result.group(0)
        statusMsg = update.message.reply_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦")
        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：抓取貼圖包")
        dlFile = requests.get(f"https://stickershop.line-scdn.net/stickershop/v1/product/{stkId}/iphone/stickerpack@2x.zip")
        try:
            isAnimated = "404 Not Found" not in dlFile.content.decode()
        except UnicodeDecodeError:
            isAnimated = True
        if not isAnimated:
            dlFile = requests.get(f"http://dl.stickershop.line.naver.jp/products/0/0/1/{stkId}/iphone/stickers@2x.zip")
        fid=stkId
        with open(f'{fid}.zip','wb') as file:
            file.write(dlFile.content)
        t = threading.Thread(target=addStickerThread, args=(context.bot, update, statusMsg, fid, stkId, emj, isAnimated))
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

def upload(update,context):
    update.message.reply_text("好的，請上傳 line 貼圖集的 zip！\n\n（僅限創作者使用，請勿侵權，請參考 /start 中的說明）\n\n要取消的話請叫我 /cancel")
    return 0

def continueUpload(update,context):
    emj = randomEmoji()
    try:
        statusMsg = update.message.reply_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦")
        fid = str(uuid.uuid1())
        statusMsg.edit_text(f"好窩我試試看！給我一點時間不要急～～\n不要做其他動作哦\n目前進度：取得貼圖包")
        zipFile = update.message.document.get_file()
        zipFile.download(f"{fid}.zip")
        stkId = ""
        with zipfile.ZipFile(f"{fid}.zip", 'r') as zip_ref:
            zip_ref.extractall(fid)

        if not os.path.exists(f"{fid}/productInfo.meta"):
            update.message.reply_text("你上傳的東西好像不是Line的標準貼圖包哦，抱歉啦不能幫你了")
            return ConversationHandler.END

        info = json.load(open(f"{fid}/productInfo.meta"))
        stkId = info['packageId']
        t = threading.Thread(target=addStickerThread, args=(context.bot, update, statusMsg, fid, stkId, emj))
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

def delete(update, context):
    if update.message.from_user.id not in adminId:
        update.message.reply_text("泥素隨？？？？你不能做這件事餒")
        return ConversationHandler.END
    update.message.reply_text("把你要刪掉的貼圖傳給我吧！\n要取消的話請叫我 /cancel")
    return 0

def continueDelete(update, context):
    stickerToDelete = update.message.sticker.file_id
    try:
        context.bot.deleteStickerFromSet(stickerToDelete)
        update.message.reply_text("好惹，我把他從貼圖集移除了")
    except:
        update.message.reply_text("抱歉....能力所及範圍外")
    finally:
        return ConversationHandler.END

def purge(update, context):
    if update.message.from_user.id not in adminId:
        update.message.reply_text("泥素隨？？？？你不能做這件事餒")
        return ConversationHandler.END
    update.message.reply_text("把你要清空的貼圖集中的一個貼圖傳給我吧！\n要取消的話請叫我 /cancel")
    return 0

def continuePurge(update, context):
    stickerToDelete=update.message.sticker.set_name
    try:
        stkSet = context.bot.getStickerSet(stickerToDelete)
        if len(stkSet.stickers)!=0:
            for stk in stkSet.stickers:
                context.bot.deleteStickerFromSet(stk.file_id)
        update.message.reply_text("好惹，我把貼圖集清空了")
    except:
        update.message.reply_text("抱歉....能力所及範圍外")
    finally:
        return ConversationHandler.END

def cancel(update,context):
    update.message.reply_text("好的 已經取消動作")
    return ConversationHandler.END

if __name__ == "__main__":
    if os.path.exists('secret.cfg'):
        cfg = SafeConfigParser(os.environ)
        cfg.read('secret.cfg')
        botName = cfg.get('DEFAULT','botName')
        botToken = cfg.get('DEFAULT','botToken')
        adminId = json.loads(cfg.get('DEFAULT','adminId'))
    else:
        botName = os.environ.get('botName')
        botToken = os.environ.get('botToken')
        adminId = json.loads(os.environ.get('adminId',"{}"))

    updater = Updater(botToken)
    cancelHandler = CommandHandler('cancel',cancel, run_async=True)
    updater.dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    addHandler = ConversationHandler(
        entry_points=[ CommandHandler('add', add)],
        states={
            0:[
                MessageHandler(Filters.text, continueAdd)
            ]
        },fallbacks=[], run_async=True
    )
    uploadHandler=ConversationHandler(
        entry_points=[ CommandHandler('upload', upload)],
        states={
            0:[
                MessageHandler(Filters.document.mime_type("multipart/x-zip"), continueUpload)
            ]
        } ,fallbacks=[], run_async=True
    )
    deleteHandler=ConversationHandler(
        entry_points=[ CommandHandler('delete', delete)],
        states={
            0:[
                MessageHandler(Filters.sticker, continueDelete)
            ]
        } ,fallbacks=[], run_async=True
    )
    purgeHandler=ConversationHandler(
        entry_points=[ CommandHandler('purge', purge)],
        states={
            0:[
                MessageHandler(Filters.sticker, continuePurge)
            ]
        } ,fallbacks=[], run_async=True
    )

    updater.dispatcher.add_handler(addHandler)
    updater.dispatcher.add_handler(uploadHandler)
    updater.dispatcher.add_handler(deleteHandler)
    updater.dispatcher.add_handler(purgeHandler)
    if os.path.exists('secret.cfg'):
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",port=int(os.environ.get('PORT', '8443')), webhook_url="https://linestkr2tg.herokuapp.com/")
    updater.idle()
