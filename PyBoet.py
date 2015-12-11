import logging

import datetime

import telegram
import json
import urllib
import urllib2
import random
import ConfigParser
import MLStripper
import simplejson
from mcstatus import MinecraftServer

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
            elif e.message == "Could not parse file content":
                # The file in the google search result link is not accessible.
                sleep(1)
            elif e.message in ("Unknown HTTPError"):
                pass
            elif e.message in ("PHOTO_SAVE_FILE_INVALID"):
                continue
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
            mcType = message.lower() == '/mcstatus'  # Minecraft Server Status Command
            bcType = message.lower() == '/bitcoin'  # Bitcoin Rate Command
            if ' ' in message:
                splitText = message.split(' ', 1)

                wType = splitText[0].lower() == '/getweather'  # Get Weather Command
                xType = splitText[0].lower() == '/getxxx'  # Get Porn Command
                imageType = splitText[0].lower() == '/get'  # Fetch Random Picture Command
                gifType = splitText[0].lower() == '/getgif'  # Fetch GIF Command
                hugeType = splitText[0].lower() == '/gethuge'  # Fetch Large Picture Command
                vidType = splitText[0].lower() == '/getvid'  # Get Top Youtube Result Command
                hugeGifType = splitText[0].lower() == '/gethugegif'  # Fetch Large GIF Command
                dicType = splitText[0].lower() == '/define'  # Command To Define A Word
                urbanDicType = splitText[0].lower() == '/urban'  # Urban Dictionary Command
                placeType = splitText[0].lower() == '/place'  # Google Map Command
                translateType = splitText[0].lower() == '/translate'  # Google translate Command
                torrentType = splitText[0].lower() == '/torrent'  # Torrent Search Command

                requestText = splitText[1]

            if imageType:  # Image Search - GCSE API
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink.encode('utf-8'), caption=requestText + ('' if len(imagelink.encode('utf-8')) > 100 else ': ' + imagelink.encode('utf-8')))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')

            elif gifType:  # GIF Search - GCSE API
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, filename=requestText + ': ' + imagelink.encode('utf-8'), document=imagelink.encode('utf-8'))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Gif not found)')

            elif hugeType:  # Large Image Search - GCSE API
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=huge"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink.encode('utf-8'), caption=requestText + ('' if len(imagelink.encode('utf-8')) > 100 else ': ' + imagelink.encode('utf-8')))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')

            elif hugeGifType:  # Large GIF Search - GCSE API
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                 'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=xlarge" + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, filename=requestText + ': ' + imagelink.encode('utf-8'), document=imagelink.encode('utf-8'))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)')

            elif vidType:  # Video Search - YouTube API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                vidurl = 'https://www.googleapis.com/youtube/v3/search?safeSearch=none&type=video&key=' + keyConfig.get\
                    ('Google', 'GCSE_APP_ID') + '&part=snippet&q='
                realUrl = vidurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['items']) >= 1:
                    vidlink = data['items'][0]['id']['videoId']
                    bot.sendMessage(chat_id=chat_id, text='https://www.youtube.com/watch?v=' + vidlink + '&type=video')
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Video not found)')

            elif wType:  # Weather - Yahoo API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                yahoourl = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20" \
                           "in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%27" + requestText.encode('utf-8') + "%27)%20" \
                           "and%20u%3D%27c%27&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
                result = urllib.urlopen(yahoourl).read()
                data = json.loads(result)
                if data['query']['count'] == 1:
                    weather = data['query']['results']['channel']['item']['condition']
                    forecast = data['query']['results']['channel']['item']['forecast']
                    city = data['query']['results']['channel']['location']['city']
                    astronomy = data['query']['results']['channel']['astronomy']
                    bot.sendMessage(chat_id=chat_id, text=('It is currently ' + weather['text'] + ' in ' + city + ' with a temperature of '
                                                           + weather['temp'] + 'C.\nA high of ' + forecast[0]['high'] + ' and a low of ' +
                                                           forecast[0]['low'] + ' are expected during the day with conditions being ' +
                                                           forecast[0]['text'] + '.\nSunrise: ' + astronomy['sunrise'] + '\nSunset: ' +
                                                           astronomy['sunset']))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I don\'t know that place.')

            elif xType:  # Porn Search - GCSE API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                googurl = 'https://www.googleapis.com/customsearch/v1?&num=10&safe=off&cx=' + keyConfig.get\
                    ('Google', 'GCSE_XSE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    for item in data['items']:
                        xlink = item['link']
                        if not 'xvideos.com/tags/' in xlink \
                                and not 'xvideos.com/profiles/' in xlink \
                                and not 'pornhub.com/users/' in xlink \
                                and not 'pornhub.com/video/search?search=' in xlink \
                                and not 'xnxx.com/tags/' in xlink \
                                and not 'xhamster.com/stories_search/' in xlink:
                            bot.sendMessage(chat_id=chat_id, text=xlink)
                            break
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, you\'re just too filthy.')

            elif dicType:  # Dictionary - DictionaryAPI.net
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                dicUrl = 'http://dictionaryapi.net/api/definition/'
                realUrl = dicUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data) >= 1:
                    partOfSpeech = data[random.randint(0, len(data)-1)]
                    if len(partOfSpeech['Definitions']) >= 1:
                        definitionText = partOfSpeech['Definitions'][0]
                        bot.sendMessage(chat_id=chat_id, text=requestText.title() + ":\n" + partOfSpeech['PartOfSpeech'] + ".\n\n" + definitionText)
                    else:
                        bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any definitions for the word ' + requestText + '.')
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any definitions for the word ' + requestText + '.')

            elif urbanDicType:  # Urban Dictionary - Urban API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                dicurl = 'http://api.urbandictionary.com/v0/define?term='
                realUrl = dicurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['list']) >= 1:
                    resultNum = data['list'][random.randint(0, len(data['list'])-1)]
                    bot.sendMessage(chat_id=chat_id, text='Urban Definition For ' + requestText.title() + ":\n" + resultNum['definition'] + '\n\nExample:\n' + resultNum['example'])
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any urban definitions for ' + requestText)

            elif placeType:  # Google Maps Places API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.FIND_LOCATION)
                mapsUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&location=-30,30&radius=50000&query='
                realUrl = mapsUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['results']) >= 1:
                    latNum = data['results'][0]['geometry']['location']['lat']
                    lngNum = data['results'][0]['geometry']['location']['lng']
                    bot.sendLocation(chat_id=chat_id, latitude=latNum, longitude=lngNum)
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any places for ' + requestText)

            elif translateType:  # Google Translate API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.FIND_LOCATION)
                translateUrl = 'https://www.googleapis.com/language/translate/v2?key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&target=en&q='
                realUrl = translateUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['data']['translations']) >= 1:
                    translation = data['data']['translations'][0]['translatedText']
                    detectedLanguage = data['data']['translations'][0]['detectedSourceLanguage']
                    languagesList = json.load(urllib.urlopen('https://www.googleapis.com/language/translate/v2/languages?target=en&key=' + keyConfig.get('Google', 'GCSE_APP_ID')))['data']['languages']
                    detectedLanguageSemanticName = [lang for lang in languagesList
                                                    if lang['language'] == detectedLanguage][0]['name']

                    bot.sendMessage(chat_id=chat_id, text="Detected language: " + detectedLanguageSemanticName + "\nMeaning: " + translation.title())
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any translations for ' + requestText)

            elif bcType:  # Current Bitcoin Price - CoinDesk API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                bcurl = 'https://api.coindesk.com/v1/bpi/currentprice/ZAR.json'
                data = json.load(urllib.urlopen(bcurl))
                bcurl2 = 'https://api.coindesk.com/v1/bpi/currentprice.json'
                data2 = json.load(urllib.urlopen(bcurl2))
                updateTime = data['time']['updated']
                priceUS = data['bpi']['USD']
                priceZA = data['bpi']['ZAR']
                priceGB = data2['bpi']['GBP']
                bot.sendMessage(chat_id=chat_id, text='The Current Price of 1 Bitcoin:\n\n' + priceUS['rate'] + ' USD\n' +
                                                      priceGB['rate'] + ' GBP\n' + priceZA['rate'] + ' ZAR' + '\n\nTime Updated: ' + updateTime)


            elif torrentType:  # Torrent Search + Fetch - Strike API

                tor1Url = 'https://torrentproject.se/?s='
                searchUrl = tor1Url + requestText.encode('utf-8') + '&out=json'
                tor2Url = 'https://getstrike.net/api/v2/torrents/download/?hash='
                downloadUrl = tor2Url + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(searchUrl))
                if data['total_found'] >= 1 and '1' in data:
                    torrent = data['1']['torrent_hash']
                    tTitle = data['1']['title']
                    seeds = str(data['1']['seeds'])
                    leechs = str(data['1']['leechs'])
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='Torrent Name: ' + tTitle + '\nTorrent Hash: ' + torrent + '\nSeeds: ' + seeds + '\nLeechers: ' + leechs)
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I can\'t find any torrents for ' + requestText.encode('utf-8'))


            elif mcType:  # mcstatus API
              #  bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
              #  mcurl = 'https://mcapi.us/server/status?ip=41.86.100.15&port=10050'
              #  data = json.load(urllib.urlopen(mcurl))
              #  status = data['online']
              #  players = data['players']['now']
              #  if status == 'true':
              #      realstatus = 'Online'
              #      bot.sendMessage(chat_id=chat_id, text='Minecraft Server Details:\nServer Status: ' + realstatus + '\nPlayer Online: ' + players)
              #  else:
              #      realstatus = 'Offline'
              #      bot.sendMessage(chat_id=chat_id, text='Minecraft Server Details:\nServer Status: ' + realstatus + '\nPlayer Online: ' + players)

            elif wikiType:  # Wiki API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                wikiUrl = 'https://en.wikipedia.org//w/api.php?action=query&list=search&format=json&titles=Main%20Page&srlimit=1&srsearch='
                realUrl = wikiUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['query']['search']) >= 1:
                    titleText = data['query']['search'][0]['title']
                    snippetText = data['query']['search'][0]['snippet']
                    bot.sendMessage(chat_id=chat_id, text=titleText + ": " + MLStripper.strip_tags(snippetText))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any wiki articles for ' + requestText + '.')

            elif issType:  # ISS API
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                mapsUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&location=-30,30&radius=50000&query='
                realUrl = mapsUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['results']) >= 1:
                    latNum = data['results'][0]['geometry']['location']['lat']
                    lngNum = data['results'][0]['geometry']['location']['lng']
                    issSightingsUrl = 'http://api.open-notify.org/iss-pass.json?lat='
                    realUrl = issSightingsUrl + str(latNum) + '&lon=' + str(lngNum)
                    data = json.load(urllib.urlopen(realUrl))
                    if len(data['response']) >= 1:
                        timeStamp = data['response'][0]['risetime']
                        durationSeconds = data['response'][0]['duration']
                        startDateTime = datetime.datetime.fromtimestamp(timeStamp)
                        bot.sendMessage(chat_id=chat_id, text='The next ISS sighting in ' + requestText.encode('utf-8').title() + ' starts at ' + startDateTime.strftime('%H:%M:%S on %d-%m-%Y') + ' for ' + str(divmod(durationSeconds, 60)[0]) + ' minutes and ' + str(divmod(durationSeconds, 60)[1]) + ' seconds.')
                    else:
                        bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find the next ISS sighting for ' + requestText)
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any places for ' + requestText)
            else:
                pass  # bot.sendMessage(chat_id=chat_id, text='Hey Boet! Use a valid command next time...')

    return update_id

if __name__ == '__main__':
    main()