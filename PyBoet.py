# coding=utf-8
import httplib
import logging
import telegram
import json
import urllib
import urllib2
import random
import ConfigParser
import MLStripper
import datetime
import soundcloud
import feedparser
import tungsten
import requests

from imgurpython import ImgurClient
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
                if update_id is not None:
                    update_id += 1
            elif e.message == "Could not parse file content":
                # The file in the google search result link is not accessible.
                sleep(1)
            elif e.message in ("Unknown HTTPError"):
                pass
            elif e.message in ("PHOTO_SAVE_FILE_INVALID"):
                continue
            elif e.message in ("Bad Request: text is empty"):
                continue
            else:
                raise e
        except URLError as e:
            # These are network problems on our end.
            sleep(1)
        except httplib.BadStatusLine as e:
            sleep(1)


def echo(bot, update_id, keyConfig):
    # Sense reset
    allUpdates = bot.getUpdates()
    for update in allUpdates:
        if update.message.text == '/reset ' + keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY'):
            lastUpdateId = allUpdates[-1].update_id + 1
            data = json.load(urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') +
                                            '/getUpdates?offset=' + str(lastUpdateId)))
            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Message queue reset.' if data['ok'] else 'Reset failed.')
            return lastUpdateId

    # Request updates after the last update_id
    for update in allUpdates:
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text
        user = update.message.from_user.username \
            if not update.message.from_user.username == '' \
            else update.message.from_user.first_name + (' ' + update.message.from_user.last_name) \
                if not update.message.from_user.last_name == '' \
                else ''

# -----------------------------------------------------COMMANDS LIST----------------------------------------------------
        if message:
            splitText = message.split(' ', 1)

            bcType = message.lower() == '/bitcoin'  # Bitcoin Rate Command
            issposType = message.lower() == '/iss'  # ISS Position Command
            currencyType = message.lower() == '/rand'  # Currency Command

            wType = splitText[0].lower() == '/getweather' if ' ' in message else False  # Get Weather Command
            xType = splitText[0].lower() == '/getxxx' if ' ' in message else False  # Get Porn Command
            imageType = splitText[0].lower() == '/get' if ' ' in message else False  # Fetch Random Picture Command
            gifType = splitText[0].lower() == '/getgif' if ' ' in message else False  # Fetch GIF Command
            giphyType = splitText[0].lower() == '/giphy' if ' ' in message else False  # Fetch Giphy GIF Command
            hugeType = splitText[0].lower() == '/gethuge' if ' ' in message else False  # Fetch Large Picture Command
            vidType = splitText[0].lower() == '/getvid' if ' ' in message else False  # Get Top Youtube Result Command
            hugeGifType = splitText[0].lower() == '/gethugegif' if ' ' in message else False  # Fetch Large GIF Command
            dicType = splitText[0].lower() == '/define' if ' ' in message else False  # Command To Define A Word
            urbanDicType = splitText[0].lower() == '/urban' if ' ' in message else False  # Urban Dictionary Command
            placeType = splitText[0].lower() == '/place' if ' ' in message else False  # Google Map Command
            translateType = splitText[0].lower() == '/translate' if ' ' in message else False  # Google translate Command
            torrentType = splitText[0].lower() == '/torrent' if ' ' in message else False  # Torrent Search Command
            wikiType = splitText[0].lower() == '/wiki' if ' ' in message else False  # Wiki Search Command
            issType = splitText[0].lower() == '/iss' if ' ' in message else False  # ISS Sightings Command
            soundType = splitText[0].lower() == '/getsound' if ' ' in message else False  # Get Sound from Soundcloud API Command
            bookType = splitText[0].lower() == '/getbook' if ' ' in message else False  # Get Book from Google Books API Command
            movieType = splitText[0].lower() == '/getmovie' if ' ' in message else False  # Get movie from OMDB API Command
            updateType = splitText[0].lower() == '/update' if ' ' in message else False  # Self update
            answerType = splitText[0].lower() == '/getanswer' if ' ' in message else False  # An answer from Wolfram Alpha API
            imgurType = splitText[0].lower() == '/imgur' if ' ' in message else False

            figType = message.lower().startswith('/getfig')  # Get a picture of a fig (common /getgif typo)
            isisType = message.lower().startswith('/isis')  # Get latest isis news (common /iss typo)

            requestText = splitText[1] if ' ' in message else ''
# ----------------------------------------------Image Search : GCSE API-------------------------------------------------
            if imageType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                          'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google',
                                                                                                  'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink.encode('utf-8'), caption=(user + ': ' if not user == '' else '') +
                                                                                            requestText.title()
                                  .encode('utf-8'))
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any images for ' +
                                                          requestText.encode('utf-8'))
# ------------------------------------------------Imgur Search : Imgur API----------------------------------------------
            if imgurType:
                client_id = keyConfig.get('Imgur', 'CLIENT_ID')
                client_secret = keyConfig.get('Imgur', 'CLIENT_SECRET')
                client = ImgurClient(client_id, client_secret)
                items = client.gallery_search(q=requestText.encode('utf-8'),
                                              advanced={'q_type': 'anigif'},
                                              sort='top',
                                              window='all',
                                              page=random.randint(0, 9))
                for item in items:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, filename=requestText.encode('utf-8'),
                                     document=item.link.encode('utf-8'))
                    print(item.link)
# -----------------------------------------------GIF Search : GCSE API--------------------------------------------------
            elif gifType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                          'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google',
                                                                                                  'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, filename=requestText.encode('utf-8'),
                                     document=imagelink.encode('utf-8'))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find a gif for ' +
                                                          requestText.encode('utf-8') + '.')
# --------------------------------------------------Giphy Search : GCSE API---------------------------------------------
            elif giphyType:
                giphyUrl = 'http://api.giphy.com/v1/gifs/search?q='
                apiKey = '&api_key=dc6zaTOxFJmzC&limit=10&offset=0'
                realUrl = giphyUrl + requestText.encode('utf-8') + apiKey
                data = json.load(urllib.urlopen(realUrl))
                if data['pagination']['total_count'] >= 1:
                    imagelink = data['data'][random.randint(0, len(data) - 1)]['images']['original']['url']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                    bot.sendDocument(chat_id=chat_id, filename=requestText.encode('utf-8') + '.gif',
                                     document=imagelink.encode('utf-8'))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find a giphy gif for '+
                                                          requestText.encode('utf-8') + '.')
# ------------------------------------------------Large Image Search : GCSE API-----------------------------------------
            elif hugeType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                          'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google',
                                                                                                  'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=huge"
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data:
                    imagelink = data['items'][0]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink.encode('utf-8'), caption=(user + ': ' if not user == '' else '') +
                                                                                            requestText.title().encode('utf-8'))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find a huge image for ' +
                                         requestText.encode('utf-8') + '.')
# ---------------------------------------------Large GIF Search : GCSE API----------------------------------------------
            elif hugeGifType:
                googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                          'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google',
                                                                                                  'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8') + "&imgSize=xlarge" + "&fileType=gif"
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, filename=requestText + ': ' + imagelink.encode('utf-8'),
                                     document=imagelink.encode('utf-8'))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any huge gifs for ' +
                                         requestText.encode('utf-8') + '.')
# -------------------------------------------Video Search : YouTube API-------------------------------------------------
            elif vidType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                vidurl = 'https://www.googleapis.com/youtube/v3/search?safeSearch=none&type=video&key=' + keyConfig.get \
                    ('Google', 'GCSE_APP_ID') + '&part=snippet&q='
                realUrl = vidurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 1:
                    vidlink = data['items'][0]['id']['videoId']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          'https://www.youtube.com/watch?v=' + vidlink + '&type=video')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t do that.\n(Video not found)')
# --------------------------------------------------Weather : Yahoo API-------------------------------------------------
            elif wType:  #
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                yahoourl = \
                    "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20" \
                    "in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%27" + requestText.encode(
                    'utf-8') + "%27)%20" \
                    "and%20u%3D%27c%27&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
                result = urllib.urlopen(yahoourl).read()
                data = json.loads(result)
                if data['query']['count'] == 1:
                    weather = data['query']['results']['channel']['item']['condition']
                    forecast = data['query']['results']['channel']['item']['forecast']
                    city = data['query']['results']['channel']['location']['city']
                    astronomy = data['query']['results']['channel']['astronomy']
                    bot.sendMessage(chat_id=chat_id, text=((user + ': ' if not user == '' else '') +
                                                           'It is currently ' + weather['text'] + ' in ' + city +
                                                           ' with a temperature of '
                    + weather['temp'] + 'C.\nA high of ' + forecast[0]['high'] + ' and a low of ' +
                    forecast[0]['low'] + ' are expected during the day with conditions being ' +
                    forecast[0]['text'] + '.\nSunrise: ' + astronomy['sunrise'] + '\nSunset: ' +
                    astronomy['sunset']))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I don\'t know the place ' +
                                                          requestText.encode('utf-8') + '.')
# ----------------------------------------------Porn Search : GCSE API--------------------------------------------------
            elif xType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                googurl = 'https://www.googleapis.com/customsearch/v1?&num=10&safe=off&cx=' + keyConfig.get\
                    ('Google', 'GCSE_XSE_ID') + '&key=' + keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = googurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= '1':
                    for item in data['items']:
                        xlink = item['link']
                        if  \
                                    'xvideos.com/tags/' not in xlink \
                                and 'pornhub.com/users/' not in xlink \
                                and 'pornhub.com/video/search?search=' not in xlink \
                                and 'xvideos.com/profiles/' not in xlink \
                                and 'xnxx.com/?' not in xlink \
                                and 'xnxx.com/tags/' not in xlink \
                                and 'xhamster.com/stories_search' not in xlink \
                                and 'xvideos.com/tags' not in xlink \
                                and 'redtube.com/pornstar/' not in xlink \
                                and 'xvideos.com/favorite/' not in xlink \
                                :
                            bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') + xlink)
                            break
                else:
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', you\'re just too filthy.')
# -------------------------------------------Dictionary : DictionaryAPI.net---------------------------------------------
            elif dicType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                dicUrl = 'http://dictionaryapi.net/api/definition/'
                realUrl = dicUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data) >= 1:
                    partOfSpeech = data[random.randint(0, len(data) - 1)]
                    if len(partOfSpeech['Definitions']) >= 1:
                        definitionText = partOfSpeech['Definitions'][0]
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                              requestText.title() + ":\n" + partOfSpeech[
                                                              'PartOfSpeech'] + ".\n\n" + definitionText)
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id,
                                        text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                             ', I\'m afraid I can\'t find any definitions for the word ' +
                                             requestText + '.')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any definitions for the word ' +
                                         requestText + '.')
# -----------------------------------------------Urban Dictionary : Urban API-------------------------------------------
            elif urbanDicType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                dicurl = 'http://api.urbandictionary.com/v0/define?term='
                realUrl = dicurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['list']) >= 1:
                    resultNum = data['list'][random.randint(0, len(data['list']) - 1)]
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text=(user + ': ' if not user == '' else '') +
                                         'Urban Definition For ' + requestText.title() + ":\n" + resultNum['definition'] +
                                         '\n\nExample:\n' + resultNum['example'])
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any urban definitions for ' +
                                         requestText.encode('utf-8') + '.')
# ---------------------------------------------Google Maps Places API---------------------------------------------------
            elif placeType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.FIND_LOCATION)
                mapsUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + \
                          keyConfig.get('Google', 'GCSE_APP_ID') + '&location=-30,30&radius=50000&query='
                realUrl = mapsUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['results']) >= 1:
                    latNum = data['results'][0]['geometry']['location']['lat']
                    lngNum = data['results'][0]['geometry']['location']['lng']
                    bot.sendLocation(chat_id=chat_id, latitude=latNum, longitude=lngNum)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any places for ' +
                                         requestText.encode('utf-8') + '.')
# --------------------------------------------------Google Translate API------------------------------------------------
            elif translateType:
                translateUrl = 'https://www.googleapis.com/language/translate/v2?key=' + \
                               keyConfig.get('Google', 'GCSE_APP_ID') + '&target=en&q='
                realUrl = translateUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['data']['translations']) >= 1:
                    translation = data['data']['translations'][0]['translatedText']
                    detectedLanguage = data['data']['translations'][0]['detectedSourceLanguage']
                    languagesList = json.load(urllib.urlopen(
                        'https://www.googleapis.com/language/translate/v2/languages?target=en&key=' + keyConfig.get(
                            'Google', 'GCSE_APP_ID')))['data']['languages']
                    detectedLanguageSemanticName = [lang for lang in languagesList
                                                    if lang['language'] == detectedLanguage][0]['name']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          "Detected language: " + detectedLanguageSemanticName +
                                                          "\nMeaning: " + translation.title())
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any translations for ' +
                                         requestText.encode('utf-8') + '.')
# -----------------------------------------Current Bitcoin Price - CoinDesk API-----------------------------------------
            elif bcType:
                bcurl = 'https://api.coindesk.com/v1/bpi/currentprice/ZAR.json'
                data = json.load(urllib.urlopen(bcurl))
                bcurl2 = 'https://api.coindesk.com/v1/bpi/currentprice.json'
                data2 = json.load(urllib.urlopen(bcurl2))
                updateTime = data['time']['updated']
                priceUS = data['bpi']['USD']
                priceZA = data['bpi']['ZAR']
                priceGB = data2['bpi']['GBP']
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                bot.sendMessage(chat_id=chat_id,
                                text=(user + ': ' if not user == '' else '') +
                                     'The Current Price of 1 Bitcoin:\n\n' + priceUS['rate'] +
                                     ' USD\n' + priceGB['rate'] +
                                     ' GBP\n' + priceZA['rate'] + ' ZAR' + '\n\nTime Updated: ' + updateTime)
# --------------------------------Torrent Search + Fetch : Strike + TorrentProject API----------------------------------
            elif torrentType:
                tor1Url = 'https://torrentproject.se/?s='
                searchUrl = tor1Url + requestText.encode('utf-8') + '&out=json'
                data = json.load(urllib.urlopen(searchUrl))
                torrageUrl = 'http://torrage.info/torrent.php?h='
                if data['total_found'] >= 1 and '1' in data:
                    torrent = data['1']['torrent_hash']
                    tTitle = data['1']['title']
                    seeds = str(data['1']['seeds'])
                    leechs = str(data['1']['leechs'])
                    downloadUrl = torrageUrl + torrent.upper()
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text=(user + ': ' if not user == '' else '') +
                                         'Torrent Name: ' + tTitle + '\nDownload Link: ' + downloadUrl + '\nSeeds: ' +
                                         seeds + '\nLeechers: ' + leechs, disable_web_page_preview=True)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I can\'t find any torrents for ' +
                                                          requestText.encode('utf-8') + '.')
# ----------------------------------------------------Wikipedia API-----------------------------------------------------
            elif wikiType:
                wikiUrl = \
                    'https://simple.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
                realUrl = wikiUrl + requestText.encode('utf-8')
                print realUrl
                data = json.load(urllib.urlopen(realUrl))
                if len(data[2]) >= 1:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          'Description: ' + data[2][0] + '\nLink: ' + data[3][0],
                                    disable_web_page_preview=True)
                else:
                    wikiUrl = \
                        'https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
                    realUrl = wikiUrl + requestText.encode('utf-8')
                    data = json.load(urllib.urlopen(realUrl))
                    if len(data[2]) >= 1 and not data[2][0] == '':
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') + data[2][0])
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id,
                                        text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                             ', I\'m afraid I can\'t find any wiki articles for ' +
                                             requestText.encode('utf-8') + '.')
# -----------------------------------# ISS Spotting : Open Notify + Google Maps API-------------------------------------
            elif issType:
                mapsUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + \
                          keyConfig.get('Google', 'GCSE_APP_ID') + '&location=-30,30&radius=50000&query='
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
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                              'The next ISS sighting in ' + requestText.encode(
                            'utf-8').title() + ' starts at ' + startDateTime.strftime(
                            '%H:%M:%S on %d-%m-%Y') + ' for ' + str(
                            divmod(durationSeconds, 60)[0]) + ' minutes and ' + str(
                            divmod(durationSeconds, 60)[1]) + ' seconds.')
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id,
                                        text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                             ', I\'m afraid I can\'t find the next ISS sighting for ' +
                                             requestText.encode('utf-8') + '.')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any places for ' +
                                         requestText.encode('utf-8') + '.')
# -----------------------------------------------------Soundcloud API---------------------------------------------------
            elif soundType:
                client = soundcloud.Client(client_id=keyConfig.get('Soundcloud', 'SC_CLIENT_ID'))
                track = client.get('/tracks', q=requestText.encode('utf-8'), sharing='public')
                if len(track) >= 1:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          track[0].permalink_url)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find the sound of ' +
                                         requestText.encode('utf-8') + '.')
# ----------------------------------------------------ISS Position------------------------------------------------------
            elif issposType:
                 bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                 bot.sendPhoto(chat_id=chat_id,
                       photo='http://www.heavens-above.com/orbitdisplay.aspx?icon=iss&width=400&height=400&satid=25544',
                       caption=(user + ': ' if not user == '' else '') + 'Current Position of the ISS')
# ----------------------------------------Currency Converter : fixer.io API---------------------------------------------
            elif currencyType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                usdurl = 'http://api.fixer.io/latest?base=USD'
                gbpurl = 'http://api.fixer.io/latest?base=GBP'
                eururl = 'http://api.fixer.io/latest?base=EUR'
                data1 = json.load(urllib.urlopen(usdurl))
                data2 = json.load(urllib.urlopen(gbpurl))
                data3 = json.load(urllib.urlopen(eururl))
                zarusd = float(data1['rates']['ZAR'])
                zargbp = float(data2['rates']['ZAR'])
                zareur = float(data3['rates']['ZAR'])
                bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                      '1 USD = ' + str(zarusd) + ' ZAR\n1 GBP = ' + str(zargbp) +
                                                      ' ZAR\n1 EUR = ' + str(zareur) + ' ZAR')
# ---------------------------------------------------Google Books API---------------------------------------------------
            elif bookType:
                booksUrl = 'https://www.googleapis.com/books/v1/volumes?maxResults=1&key=' + \
                           keyConfig.get('Google', 'GCSE_APP_ID') + '&q='
                realUrl = booksUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if data['totalItems'] >= 1:
                    bookData = data['items'][0]['volumeInfo']
                    googleBooksUrl = data['items'][0]['accessInfo']['webReaderLink']
                    if 'imageLinks' in bookData:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                        bot.sendPhoto(chat_id=chat_id, photo=bookData['imageLinks']['thumbnail'],
                                      caption=(user + ': ' if not user == '' else '') + googleBooksUrl)
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') + googleBooksUrl)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any books for ' +
                                                          requestText.encode('utf-8') + '.')
# ----------------------------------------------Fig Search : GCSE API---------------------------------------------------
            elif figType:
                realUrl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                          'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + \
                          keyConfig.get('Google', 'GCSE_APP_ID') + '&q=fig'
                data = json.load(urllib.urlopen(realUrl))
                if data['searchInformation']['totalResults'] >= 1:
                    imagelink = data['items'][random.randint(0, 9)]['link']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    bot.sendPhoto(chat_id=chat_id, photo=imagelink.encode('utf-8'),
                                  caption=(user if not user == '' else '') +
                                          ('' if len(imagelink.encode('utf-8')) > 100 else ': ' +
                                                                                           imagelink.encode('utf-8')))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any figs.')
# ----------------------------------------------ISIS news RSS feed------------------------------------------------------
            elif isisType:
                realUrl = 'http://isis.liveuamap.com/rss'
                data = feedparser.parse(realUrl)
                if len(data.entries) >= 1:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          data.entries[random.randint(0, 9)].link)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t find any ISIS news.')
# ---------------------------------------------Movie from  OMDB API-----------------------------------------------------
            elif movieType:
                movieUrl = 'http://www.omdbapi.com/?plot=short&r=json&y=&t='
                realUrl = movieUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if 'Error' not in data:
                    if 'Poster' in data and not data['Poster'] == 'N/A':
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                        print data['Poster']
                        bot.sendPhoto(chat_id=chat_id, photo=data['Poster'],
                                      caption=(user if not user == '' else '') + data['Title'] + ':\n' + data['Plot'])
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                              data['Title'] + ':\n' + data['Plot'])
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any movies for ' +
                                         requestText.encode('utf-8') + '.')
# ---------------------------------------------------Self update Service------------------------------------------------
            elif updateType and requestText == keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY'):  #
                urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') +
                               '/getUpdates?offset=' + str(update_id))
                import subprocess
                import os
                import sys
                subprocess.call(["git", "pull"])
                os.execv(sys.executable, sys.argv)
# --------------------------------------------Get Answers From Wolfram Alpha API----------------------------------------
            elif answerType:
                client = tungsten.Tungsten(keyConfig.get('Wolfram', 'WOLF_APP_ID'))
                result = client.query(requestText)
                if len(result.pods) >= 1:
                    fullAnswer = ''
                    for pod in result.pods:
                        for answer in pod.format['plaintext']:
                            if not answer == None:
                                fullAnswer += answer.encode('utf-8')
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          fullAnswer)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    bot.sendMessage(chat_id=chat_id,
                                    text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                         ', I\'m afraid I can\'t find any answers for ' +
                                         requestText.encode('utf-8'))
# ----------------------------------------------------------------------------------------------------------------------
            else:
                pass

    if not update_id == None and len(allUpdates) >= 1:
        urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') +
                       '/getUpdates?offset=' + str(update_id))
    return update_id


if __name__ == '__main__':
    main()
