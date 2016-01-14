# coding=utf-8
import httplib
import logging
import socket
import string

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
from mcstatus import MinecraftServer

from imgurpython import ImgurClient
from time import sleep

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

userWithCurrentChatAction = ''
urlForCurrentChatAction = ''
requestTextForCurrentChatAction = ''

def main():
    # Read keys.ini file at program start (don't forget to put your keys in there!)
    KeyConfig = ConfigParser.ConfigParser()
    KeyConfig.read("keys.ini")

    # Telegram Bot Authorization Token
    bot = telegram.Bot(KeyConfig.get('Telegram', 'TELE_BOT_ID'))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    lastUserWhoMoved = {}

    while True:
        try:
            getUpdatesLoop(bot, KeyConfig, lastUserWhoMoved)
        except telegram.TelegramError or \
                socket.timeout or socket.error or \
                urllib2.URLError or \
                httplib.BadStatusLine as e:
            bot.sendMessage(chat_id=userWithCurrentChatAction, text='I\'m sorry Dave, I suffered an error!')
            if not KeyConfig.get('HeyBoet', 'ADMIN_GROUP_CHAT_ID') == '':
                bot.sendMessage(chat_id=KeyConfig.get('HeyBoet', 'ADMIN_GROUP_CHAT_ID'), text=
                'Error: ' + e.message + '\n' +
                'Request Text: ' + requestTextForCurrentChatAction + '\n' +
                'Url: ' + urlForCurrentChatAction)
            continue


def getUpdatesLoop(bot, keyConfig, lastUserWhoMoved):
    # Keep track of the last user to receive a chat action.
    # Force all chat actions to resolve even on error.
    global userWithCurrentChatAction
    global urlForCurrentChatAction
    global requestTextForCurrentChatAction

    # Request updates after the last update_id
    allUpdates = bot.getUpdates()

    # If empty
    if len(allUpdates) <= 0:
        return

    # If reset
    for update in allUpdates:
        if update.message.text == '/reset ' + keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY'):
            lastUpdateId = allUpdates[-1].update_id + 1
            data = json.load(urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') +
                                            '/getUpdates?offset=' + str(lastUpdateId)))
            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
            userWithCurrentChatAction = update.message.chat_id
            urlForCurrentChatAction = 'Message queue reset.' if data['ok'] else 'Reset failed.'
            requestTextForCurrentChatAction = keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY')
            bot.sendMessage(chat_id=update.message.chat_id, text=urlForCurrentChatAction)
            return

    # Pop the top for processing
    update = allUpdates[0]
    # chat_id is required to reply to any message
    chat_id = update.message.chat_id
    # Offset the update queue to the next update
    urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/getUpdates?offset=' + str(update.update_id + 1))
    message = update.message.text
    user = update.message.from_user.username \
        if not update.message.from_user.username == '' \
        else update.message.from_user.first_name + (' ' + update.message.from_user.last_name) \
            if not update.message.from_user.last_name == '' \
            else ''

# -----------------------------------------------------COMMANDS LIST----------------------------------------------------
    if message:
        splitText = message.split(' ', 1)

        bitcoinType = message.lower() == '/bitcoin'  # Bitcoin Rate Command
        issPosType = message.lower() == '/iss'  # ISS Position Command
        currencyType = message.lower() == '/rand'  # Currency Command
        rocketType = message.lower() == '/launch'  # Rocket Launch Command
        spacexType = message.lower() == '/spacex'  # SpaceX Launch Schedule Command
        mcType = message.lower() == '/mc'  # Minecraft server status
        cricType = message.lower() == '/cric'  # Proteas status from Cricbuzz api

        chessBoardType = message.lower() == '/getchess' or message.lower() == '/chessmove' # Show current chess game

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
        imgurType = splitText[0].lower() == '/imgur' if ' ' in message else False # Imgur API
        chessType = splitText[0].lower() == '/chessmove' if ' ' in message else False # Riot's chess API
        quoteType = splitText[0].lower() == '/getquote' if ' ' in message else False # Wikiquote API
        showType = splitText[0].lower() == '/getshow' if ' ' in message else False # Search TV Shows with TVMaze API
        echoImgType = splitText[0].lower() == '/echoimg' if ' ' in message else False # For debugging problem photo urls

        figType = message.lower().startswith('/getfig')  # Get a picture of a fig (common /getgif typo)
        isisType = message.lower().startswith('/isis')  # Get latest isis news (common /iss typo)

        requestText = filter(lambda x: x in string.printable, splitText[1]) if ' ' in message else ''
        requestTextForCurrentChatAction = requestText
# ----------------------------------------------Image Search : GCSE API-------------------------------------------------
        if imageType:
            googurl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                      'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + keyConfig.get('Google',
                                                                                              'GCSE_APP_ID') + '&q='
            realUrl = googurl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if 'items' in data and len(data['items']) >= 9:
                imagelink = data['items'][random.randint(0, 9)]['link']
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink
                bot.sendPhoto(chat_id=userWithCurrentChatAction,
                              photo=urlForCurrentChatAction.encode('utf-8'),
                              caption=(user + ': ' if not user == '' else '') +
                                      requestText.encode('utf-8').title())
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any images for ' +\
                                          requestText
                requestTextForCurrentChatAction = requestText
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction.encode('utf-8'))
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = item.link
                bot.sendDocument(chat_id=userWithCurrentChatAction,
                                 filename=requestTextForCurrentChatAction.encode('utf-8'),
                                 document=urlForCurrentChatAction.encode('utf-8'))
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink
                bot.sendDocument(chat_id=userWithCurrentChatAction,
                                 filename=requestTextForCurrentChatAction.encode('utf-8'),
                                 document=urlForCurrentChatAction.encode('utf-8'))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find a gif for ' +\
                                          requestText + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction.encode('utf-8'))
# --------------------------------------------------Giphy Search : GCSE API---------------------------------------------
        elif giphyType:
            giphyUrl = 'http://api.giphy.com/v1/gifs/search?q='
            apiKey = '&api_key=dc6zaTOxFJmzC&limit=10&offset=0'
            realUrl = giphyUrl + requestText.encode('utf-8') + apiKey
            data = json.load(urllib.urlopen(realUrl))
            if data['pagination']['total_count'] >= 1:
                imagelink = data['data'][random.randint(0, len(data['data']) - 1)]['images']['original']['url']
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink
                bot.sendDocument(chat_id=userWithCurrentChatAction,
                                 filename=requestTextForCurrentChatAction.encode('utf-8') + '.gif',
                                 document=urlForCurrentChatAction.encode('utf-8'))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find a giphy gif for '+\
                                          requestText + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction.encode('utf-8'))
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink
                bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=urlForCurrentChatAction.encode('utf-8'),
                              caption=(user + ': ' if not user == '' else '') +
                                      requestTextForCurrentChatAction.title().encode('utf-8'))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find a huge image for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink
                bot.sendDocument(chat_id=userWithCurrentChatAction,
                                 filename=requestTextForCurrentChatAction.encode('utf-8') + '.gif',
                                 document=urlForCurrentChatAction.encode('utf-8'))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any huge gifs for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -------------------------------------------Video Search : YouTube API-------------------------------------------------
        elif vidType:
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                      ', I\'m afraid I can\'t do that.\n(use @vid instead)'
            bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# --------------------------------------------------Weather : Yahoo API-------------------------------------------------
        elif wType:
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
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = ('It is currently ' + weather['text'] + ' in ' + city +
                                           ' with a temperature of ' + weather['temp'] + 'C.\nA high of ' +
                                           forecast[0]['high'] + ' and a low of ' + forecast[0]['low'] +
                                           ' are expected during the day with conditions being ' +
                                           forecast[0]['text'] + '.\nSunrise: ' + astronomy['sunrise'] +
                                           '\nSunset: ' + astronomy['sunset'])
                requestTextForCurrentChatAction = requestText
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction,
                                parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I don\'t know the place ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
# ----------------------------------------------Porn Search : GCSE API--------------------------------------------------
        elif xType:
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
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        userWithCurrentChatAction = chat_id
                        urlForCurrentChatAction = (user + ': ' if not user == '' else '') + xlink
                        requestTextForCurrentChatAction = requestText
                        bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                        break
            else:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', you\'re just too filthy.')
# -------------------------------------------Dictionary : DictionaryAPI.net---------------------------------------------
        elif dicType:
            dicUrl = 'http://dictionaryapi.net/api/definition/'
            realUrl = dicUrl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if len(data) >= 1:
                partOfSpeech = data[random.randint(0, len(data) - 1)]
                if len(partOfSpeech['Definitions']) >= 1:
                    definitionText = partOfSpeech['Definitions'][0]
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                              requestText.title() + ":\n" + \
                                              partOfSpeech['PartOfSpeech'] + ".\n\n" + definitionText
                    bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find any definitions for the word ' +\
                                              requestText + '.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any definitions for the word ' +\
                                          requestText + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -----------------------------------------------Urban Dictionary : Urban API-------------------------------------------
        elif urbanDicType:
            dicurl = 'http://api.urbandictionary.com/v0/define?term='
            realUrl = dicurl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if len(data['list']) >= 1:
                resultNum = data['list'][random.randint(0, len(data['list']) - 1)]
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                          'Urban Definition For ' + requestText.title() + ":\n" + resultNum['definition'] +\
                                          '\n\nExample:\n' + resultNum['example']
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction ='I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                         ', I\'m afraid I can\'t find any urban definitions for ' +\
                                         requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction)
# ---------------------------------------------Google Maps Places API---------------------------------------------------
        elif placeType:
            mapsUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + \
                      keyConfig.get('Google', 'GCSE_APP_ID') + '&location=-30,30&radius=50000&query='
            realUrl = mapsUrl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if len(data['results']) >= 1:
                latNum = data['results'][0]['geometry']['location']['lat']
                lngNum = data['results'][0]['geometry']['location']['lng']
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.FIND_LOCATION)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'lat=' + str(latNum) + ' long=' + str(lngNum)
                bot.sendLocation(chat_id=chat_id, latitude=latNum, longitude=lngNum)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any places for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction)
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                          "Detected language: " + detectedLanguageSemanticName +\
                                          "\nMeaning: " + translation.title()
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any translations for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -----------------------------------------Current Bitcoin Price - CoinDesk API-----------------------------------------
        elif bitcoinType:
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
                            text='The Current Price of 1 Bitcoin:\n\n' + priceUS['rate'] +
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
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'Torrent Name: ' + tTitle + \
                                          '\nDownload Link: ' + downloadUrl + \
                                          '\nSeeds: ' + seeds + \
                                          '\nLeechers: ' + leechs
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction, disable_web_page_preview=True)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I can\'t find any torrents for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
# ----------------------------------------------------Wikipedia API-----------------------------------------------------
        elif wikiType:
            wikiUrl = \
                'https://simple.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
            realUrl = wikiUrl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if len(data[2]) >= 1:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                          data[2][0] + '\nLink: ' + data[3][0]
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction, disable_web_page_preview=True)
            else:
                wikiUrl = \
                    'https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
                realUrl = wikiUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data[2]) >= 1 and not data[2][0] == '':
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                              data[2][0] + '\nLink: ' + data[3][0]
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction,
                                    disable_web_page_preview=True)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find any wiki articles for ' +\
                                              requestText.encode('utf-8') + '.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction,
                                    text=urlForCurrentChatAction)
# --------------------------------------------Get a quote from WikiQuote------------------------------------------------
        elif quoteType:
            wikiUrl = \
                'https://simple.wikiquote.org/w/api.php?action=query&list=search&srlimit=1&namespace=0&format=json&srsearch='
            realUrl = wikiUrl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if len(data['query']['search']) >= 1:
                formattedQuoteSnippet = MLStripper.strip_tags(
                    data['query']['search'][0]['snippet'].replace('<span class="searchmatch">', '*').replace(
                        '</span>', '*'))
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') + formattedQuoteSnippet + \
                              '\nhttps://simple.wikiquote.org/wiki/' + \
                              urllib.quote(data['query']['search'][0]['title'].encode('utf-8'))
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction,
                                disable_web_page_preview=True, parse_mode='Markdown')
            else:
                wikiUrl = \
                    'https://en.wikiquote.org/w/api.php?action=query&list=search&srlimit=1&namespace=0&format=json&srsearch='
                realUrl = wikiUrl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if len(data['query']['search']) >= 1:
                    formattedQuoteSnippet = MLStripper.strip_tags(
                        data['query']['search'][0]['snippet'].replace('<span class="searchmatch">', '*').replace(
                            '</span>', '*'))
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') + formattedQuoteSnippet + \
                                  '\nhttps://en.wikiquote.org/wiki/' + \
                                  urllib.quote(data['query']['search'][0]['title'].encode('utf-8'))
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction,
                                    disable_web_page_preview=True, parse_mode='Markdown')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find any quotes for ' +\
                                              requestText.encode('utf-8') + '.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
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
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                              'The next ISS sighting in ' + requestText.encode('utf-8').title() + \
                                              ' starts at ' + startDateTime.strftime('%H:%M:%S on %d-%m-%Y') + \
                                              ' for ' + str(divmod(durationSeconds, 60)[0]) + \
                                              ' minutes and ' + str(divmod(durationSeconds, 60)[1]) + ' seconds.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find the next ISS sighting for ' +\
                                              requestText.encode('utf-8') + '.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any places for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=requestTextForCurrentChatAction)
# -----------------------------------------------------Soundcloud API---------------------------------------------------
        elif soundType:
            client = soundcloud.Client(client_id=keyConfig.get('Soundcloud', 'SC_CLIENT_ID'))
            track = client.get('/tracks', q=requestText.encode('utf-8'), sharing='public')
            if len(track) >= 1:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                          track[0].permalink_url
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find the sound of ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
# ----------------------------------------------------ISS Position------------------------------------------------------
        elif issPosType:
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = 'http://www.heavens-above.com/orbitdisplay.aspx?icon=iss&width=400&height=400&satid=25544'
            bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=urlForCurrentChatAction,
                           caption='Current Position of the ISS')
# ----------------------------------------Currency Converter : fixer.io API---------------------------------------------
        elif currencyType:
            usdurl = 'http://api.fixer.io/latest?base=USD'
            gbpurl = 'http://api.fixer.io/latest?base=GBP'
            eururl = 'http://api.fixer.io/latest?base=EUR'
            data1 = json.load(urllib.urlopen(usdurl))
            data2 = json.load(urllib.urlopen(gbpurl))
            data3 = json.load(urllib.urlopen(eururl))
            zarusd = float(data1['rates']['ZAR'])
            zargbp = float(data2['rates']['ZAR'])
            zareur = float(data3['rates']['ZAR'])
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = '1 USD = ' + str(zarusd) + ' ZAR\n1 GBP = ' + str(zargbp) +\
                                      ' ZAR\n1 EUR = ' + str(zareur) + ' ZAR'
            bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
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
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'Photo= ' + bookData['imageLinks']['thumbnail'] + \
                                              ' Caption= ' + (user + ': ' if not user == '' else '') + googleBooksUrl
                    bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=bookData['imageLinks']['thumbnail'],
                                  caption=(user + ': ' if not user == '' else '') + googleBooksUrl)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') + googleBooksUrl
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any books for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ----------------------------------------------Fig Search : GCSE API---------------------------------------------------
        elif figType:
            realUrl = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&safe=off&' \
                      'cx=' + keyConfig.get('Google', 'GCSE_SE_ID') + '&key=' + \
                      keyConfig.get('Google', 'GCSE_APP_ID') + '&q=fig'
            data = json.load(urllib.urlopen(realUrl))
            if data['searchInformation']['totalResults'] >= 1:
                imagelink = data['items'][random.randint(0, 9)]['link']
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = imagelink.encode('utf-8')
                bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=urlForCurrentChatAction,
                              caption=(user if not user == '' else '') +
                                      ('' if len(imagelink.encode('utf-8')) > 100 else ': ' +
                                                                                       imagelink.encode('utf-8')))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any figs.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ----------------------------------------------ISIS news RSS feed------------------------------------------------------
        elif isisType:
            realUrl = 'http://isis.liveuamap.com/rss'
            data = feedparser.parse(realUrl)
            if len(data.entries) >= 1:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                          data.entries[random.randint(0, 9)].link
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any ISIS news.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ---------------------------------------------Movie from  OMDB API-----------------------------------------------------
        elif movieType:
            movieUrl = 'http://www.omdbapi.com/?plot=short&r=json&y=&t='
            realUrl = movieUrl + requestText.encode('utf-8')
            data = json.load(urllib.urlopen(realUrl))
            if 'Error' not in data:
                if 'Poster' in data and not data['Poster'] == 'N/A':
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = data['Poster']
                    bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=urlForCurrentChatAction,
                                  caption=(user if not user == '' else '') + data['Title'] + ':\n' + data['Plot'])
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                              data['Title'] + ':\n' + data['Plot']
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any movies for ' +\
                                          requestText.encode('utf-8') + '.'
                bot.sendMessage(chat_id=userWithCurrentChatAction,
                                text=urlForCurrentChatAction)
# ---------------------------------------------------Self update Service------------------------------------------------
        elif updateType and requestText == keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY'):
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
                            fullAnswer += answer.encode('ascii', 'ignore')
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (user + ': ' if not user == '' else '') + fullAnswer
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I can\'t find any answers for ' +\
                                          requestText.encode('utf-8')
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ------------------------------------------------Play Chess Against HeyBoet--------------------------------------------
        elif chessType:
            if not user == '':
                adminOverride = False
                if len(requestText.split(' ', 1)) > 1:
                    adminOverride = requestText.split(' ', 1)[1] == keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY')
                    requestText = requestText.replace(' ' + keyConfig.get('HeyBoet', 'ADMIN_COMMAND_KEY'), '')
                moveUrl = 'http://riot.so/cgi-bin/chess?time=30&move='
                formatedRequestText = requestText.lower()\
                    .replace('1', 'i')\
                    .replace('2', 'j')\
                    .replace('3', 'k')\
                    .replace('4', 'l')\
                    .replace('5', 'm')\
                    .replace('6', 'n')\
                    .replace('7', 'o')\
                    .replace('8', 'p')
                formatedRequestText = formatedRequestText\
                    .replace('i', '8')\
                    .replace('j', '7')\
                    .replace('k', '6')\
                    .replace('l', '5')\
                    .replace('m', '4')\
                    .replace('n', '3')\
                    .replace('o', '2')\
                    .replace('p', '1')
                realUrl = moveUrl + formatedRequestText.encode('utf-8')
                moveResponse = (urllib.urlopen(realUrl)).read()
                isMoveValid = not moveResponse.startswith('invalid')
                if requestText not in ['clear', 'back', 'wwyd', 'history', 'status', 'moves', 'fen', 'board'] or adminOverride:
                    userRestricted = False
                    if update.message.chat.type == 'group' and not adminOverride and isMoveValid:
                        if update.message.chat.id in lastUserWhoMoved and lastUserWhoMoved[update.message.chat.id] == user:
                            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                            userWithCurrentChatAction = chat_id
                            urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                      ', I\'m afraid I can\'t let you make more than one sequential chess move in a group.'
                            bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                            userRestricted = True
                        else:
                            lastUserWhoMoved[update.message.chat.id] = user
                    if not userRestricted or adminOverride:
                        if isMoveValid:
                            movesUrl = 'http://riot.so/cgi-bin/chess?move=moves'
                            movesList = (urllib.urlopen(movesUrl)).read()[len('validmoves'):]
                            if not movesList == '':
                                boardUrl = 'http://riot.so/cgi-bin/chess?move=board'
                                boardResponse = (urllib.urlopen(boardUrl)).read()
                                boardImageUrl = str(boardResponse.split(' ', 1)[1])
                                boardUrlImageBase = 'http://www.eddins.net/steve/chess/ChessImager/ChessImager.php?fen='
                                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                                userWithCurrentChatAction = chat_id
                                urlForCurrentChatAction = boardUrlImageBase +\
                                                          urllib.quote(boardImageUrl[len(boardUrlImageBase):])
                                bot.sendPhoto(chat_id=userWithCurrentChatAction,
                                              photo=urlForCurrentChatAction,
                                              caption='+ A B C D E F G H\n1\n2\n3\n4\n5\n6\n7\n8')
                            else:
                                urllib.urlopen('http://riot.so/cgi-bin/chess?move=reset')
                                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                                userWithCurrentChatAction = chat_id
                                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                          ', I\'m afraid the chess game is over.'
                                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                        else:
                            movesUrl = 'http://riot.so/cgi-bin/chess?move=moves'
                            movesList = (urllib.urlopen(movesUrl)).read()
                            formatedmovesList = movesList\
                                .replace('1', 'i')\
                                .replace('2', 'j')\
                                .replace('3', 'k')\
                                .replace('4', 'l')\
                                .replace('5', 'm')\
                                .replace('6', 'n')\
                                .replace('7', 'o')\
                                .replace('8', 'p')
                            formatedmovesList = formatedmovesList\
                                .replace('i', '8')\
                                .replace('j', '7')\
                                .replace('k', '6')\
                                .replace('l', '5')\
                                .replace('m', '4')\
                                .replace('n', '3')\
                                .replace('o', '2')\
                                .replace('p', '1')
                            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                            userWithCurrentChatAction = chat_id
                            urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                      ', I\'m afraid that chess move is invalid. List of valid moves:\n' +\
                                                      formatedmovesList[len('validmoves'):]
                            bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry whoever you are, I\'m afraid' +\
                                          ' you must have a username to be trusted' +\
                                          ' enough to make chess moves.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ---------------------------------View the current state of the chess game---------------------------------------------
        elif chessBoardType:
            movesUrl = 'http://riot.so/cgi-bin/chess?move=moves'
            movesList = (urllib.urlopen(movesUrl)).read()
            formatedmovesList = movesList\
                .replace('1', 'i')\
                .replace('2', 'j')\
                .replace('3', 'k')\
                .replace('4', 'l')\
                .replace('5', 'm')\
                .replace('6', 'n')\
                .replace('7', 'o')\
                .replace('8', 'p')
            formatedmovesList = formatedmovesList\
                .replace('i', '8')\
                .replace('j', '7')\
                .replace('k', '6')\
                .replace('l', '5')\
                .replace('m', '4')\
                .replace('n', '3')\
                .replace('o', '2')\
                .replace('p', '1')
            boardUrl = 'http://riot.so/cgi-bin/chess?move=board'
            boardResponse = (urllib.urlopen(boardUrl)).read()
            boardImageUrl = str(boardResponse.split(' ', 1)[1])
            boardUrlImageBase = 'http://www.eddins.net/steve/chess/ChessImager/ChessImager.php?fen='
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = boardUrlImageBase +\
                                      urllib.quote(boardImageUrl[len(boardUrlImageBase):])
            bot.sendPhoto(chat_id=userWithCurrentChatAction,
                          photo=urlForCurrentChatAction,
                          caption='+ A B C D E F G H\n1\n2\n3\n4\n5\n6\n7\n8\nValid moves: ' +
                                  formatedmovesList[len('validmoves'):])
# --------------------------------------------------Next Rocket Launch--------------------------------------------------
        elif rocketType:
            rocketUrl = urllib2.Request('https://launchlibrary.net/1.1/launch/next/5', headers={'User-Agent' : "Magic Browser"})
            rocketData = json.load(urllib2.urlopen(rocketUrl))
            blast = rocketData['launches']
            b1 = blast[0]
            b2 = blast[1]
            b3 = blast[2]
            b4 = blast[3]
            b5 = blast[4]
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = 'Upcoming Rocket Launches:\n\n' +\
                                      b1['net'] + '\n*' + b1['name'] + '*\nLaunching from [' + b1['location']['pads'][0]['name'] + '](' + b1['location']['pads'][0]['mapURL'] + ')\n\n' +\
                                      b2['net'] + '\n*' + b2['name'] + '*\nLaunching from [' + b2['location']['pads'][0]['name'] + '](' + b2['location']['pads'][0]['mapURL'] + ')\n\n' +\
                                      b3['net'] + '\n*' + b3['name'] + '*\nLaunching from [' + b3['location']['pads'][0]['name'] + '](' + b3['location']['pads'][0]['mapURL'] + ')\n\n' +\
                                      b4['net'] + '\n*' + b4['name'] + '*\nLaunching from [' + b4['location']['pads'][0]['name'] + '](' + b4['location']['pads'][0]['mapURL'] + ')\n\n' +\
                                      b5['net'] + '\n*' + b5['name'] + '*\nLaunching from [' + b5['location']['pads'][0]['name'] + '](' + b5['location']['pads'][0]['mapURL'] + ')'
            bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction, parse_mode=telegram.ParseMode.MARKDOWN)
# --------------------------------------------------Next Rocket Launch--------------------------------------------------
        elif mcType:
            mcServer = keyConfig.get('Minecraft', 'SVR_ADDR')
            mcPort = int(keyConfig.get('Minecraft', 'SVR_PORT'))
            dynmapPort = keyConfig.get('Minecraft', 'DYNMAP_PORT')
            status = MinecraftServer(mcServer, mcPort).status()
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = ('The server at {0} has {1} players and replied in {2} ms' +
                                       ('' if dynmapPort == '' else '\nSee map: ' + mcServer + ':' + dynmapPort))\
                .format(mcServer + ':' + str(mcPort), status.players.online, status.latency)
            bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# --------------------------------------------------Current Proteas match--------------------------------------------------
        elif cricType:
            allMatchesUrl = 'http://cricscore-api.appspot.com/csa'
            allMatches = json.load(urllib.urlopen(allMatchesUrl))
            proteasMatchId = None
            for match in allMatches:
                if match['t1'] == 'South Africa' or match['t2'] == 'South Africa':
                    proteasMatchId = match['id']
            if proteasMatchId == None:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid the Proteas are not playing right now.'
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
            else:
                matchesUrl = 'http://cricscore-api.appspot.com/csa?id=' + str(proteasMatchId)
                match = json.load(urllib.urlopen(matchesUrl))
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = (match[0]['si'] + '\n' + match[0]['de'])
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# --------------------------------------------------Search TV Shows with TVMaze API--------------------------------------------------
        elif showType:
            showsUrl = 'http://api.tvmaze.com/search/shows?q='
            data = json.load(urllib.urlopen(showsUrl + requestText))
            if len(data) >= 1:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = data[0]['show']['image']['original']
                bot.sendPhoto(chat_id=chat_id,
                              photo=urlForCurrentChatAction,
                              caption=MLStripper.strip_tags(data[0]['show']['summary'].replace('\\','')[:125]))
            else:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                          ', I\'m afraid I cannot find the TV show ' +\
                                          requestText.title()
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
# --------------------------------------------------Debug send photo with certain urls--------------------------------------------------
        elif echoImgType:
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            userWithCurrentChatAction = chat_id
            urlForCurrentChatAction = requestText
            bot.sendPhoto(chat_id=chat_id, photo=urlForCurrentChatAction)
# ----------------------------------------------------------------------------------------------------------------------
        else:
            pass


if __name__ == '__main__':
    main()
