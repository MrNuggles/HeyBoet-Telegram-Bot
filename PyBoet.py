import logging
import telegram
import json
import urllib
import urllib2
import random
import ConfigParser

from time import sleep

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2


def main():
    # Read keys.ini file at program start (don't forget to put your keys in there!)
    KeyConfig = ConfigParser.ConfigParser()
    KeyConfig.read("keys.ini")

    # Telegram Bot Authorization Token
    bot = telegram.Bot(KeyConfig.get('Telegram', 'TELE_BOT_ID'))

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            update_id = echo(bot, update_id, KeyConfig)
        except telegram.TelegramError as e:
            # These are network problems with Telegram.
            if e.message in ("Bad Gateway", "Timed out"):
                sleep(1)
            elif e.message == "Unauthorized":
                # The user has removed or blocked the bot.
                update_id += 1
            else:
                raise e
        except URLError as e:
            # These are network problems on our end.
            sleep(1)


def echo(bot, update_id, keyConfig):

    # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text

        if message:
            splitText = message.split(' ', 1)
            if len(splitText) <= 1:
                continue

            wType = splitText[0] == '/getweather'
            xType = splitText[0] == '/getx'
            imageType = splitText[0] == '/get'
            gifType = splitText[0] == '/getgif'
            hugeType = splitText[0] == '/gethuge'
            vidType = splitText[0] == '/getvid'
            hugeGifType = splitText[0] == '/gethugegif'
            dicType = splitText[0] == '/dict'
            urbanDicType = splitText[0] == '/define'

            requestText = splitText[1]  # imagetext is input text

            if imageType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink, caption=requestText + ': ' +  (imagelink[:100] + '...' if len(imagelink) > 100 else imagelink))
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')
            elif gifType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendDocument(chat_id=chat_id, filename=requestText + ': ' + imagelink, document=imagelink)
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Gif not found)')
            elif hugeType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=huge"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink, caption=requestText + ': ' +  (imagelink[:100] + '...' if len(imagelink) > 100 else imagelink))
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')
            elif hugeGifType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=xlarge" + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendDocument(chat_id=chat_id, filename=requestText + ': ' + imagelink, document=imagelink)
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')
            elif vidType:
                vidurl = 'https://www.googleapis.com/youtube/v3/search?safeSearch=none&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&part=snippet&q='
                realUrl = vidurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['items']) >= 1:
                    vidlink = data['items'][0]['id']['videoId']
                    bot.sendMessage(chat_id=chat_id, text='https://www.youtube.com/watch?v=' + vidlink + '&type=video')
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Video not found)')
            elif wType:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(weather coming soon!)')
            elif xType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_XSE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    for item in data['items']:
                        xlink = item['link']
                        if not 'xvideos.com/tags/' in xlink \
                                and not 'xvideos.com/profiles/' in xlink \
                                and not 'pornhub.com/users/' in xlink \
                                and not 'pornhub.com/video/search?search=' in xlink \
                                and not 'xnxx.com/tags/' in xlink:
                            bot.sendMessage(chat_id=chat_id, text=xlink)
                            break
                else:
                    # Reply to the message
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do this:\n' + realUrl)
            elif dicType:
                dicurl = 'http://dictionaryapi.net/api/definition/'
                realUrl = dicurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data) >= 1:
                    partOfSpeech = data[random.randint(0, len(data)-1)]
                    if len(partOfSpeech['Definitions']) >= 1:
                        definitionText = partOfSpeech['Definitions'][random.randint(0, len(partOfSpeech['Definitions'])-1)]
                        bot.sendMessage(chat_id=chat_id, text=requestText.title() + ": " + partOfSpeech['PartOfSpeech'] + ". " + definitionText)
                    else:
                        bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any definitions here:\n' + realUrl)
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any definitions here:\n' + realUrl)
            elif urbanDicType:
                dicurl = 'http://api.urbandictionary.com/v0/define?term='
                realUrl = dicurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['list']) >= 1:
                    bot.sendMessage(chat_id=chat_id, text=requestText.title() + ":\n" + data['list'][random.randint(0, len(data['list'])-1)]['definition'])
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any urban definitions here:\n' + realUrl)
            else:
                pass  # bot.sendMessage(chat_id=chat_id, text='Hey Boet! Use a valid command next time...')

    return update_id

if __name__ == '__main__':
    main()
