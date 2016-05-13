# coding=utf-8
import httplib
import logging
import socket
import string

from dateutil import tz

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

#reverse image search imports:
from bs4 import BeautifulSoup
from StringIO import StringIO
import pycurl, json
import certifi

from mcstatus import MinecraftServer

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

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    lastUserWhoMoved = {}

    while True:
        getUpdatesLoop(bot, KeyConfig, lastUserWhoMoved)


def getUpdatesLoop(bot, keyConfig, lastUserWhoMoved):

# Request updates after the last update_id
    allUpdates = []
    try:
        allUpdates = bot.getUpdates()
    except URLError or telegram.error.TelegramError as e:
        print e.message

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
            bot.sendMessage(chat_id=update.message.chat_id, text='Message queue reset.' if data['ok'] else 'Reset failed.')
            return

# Pop the top for processing
    update = allUpdates[0]
# chat_id is required to reply to any message
    chat_id = update.message.chat_id
    message = update.message.text
    user = update.message.from_user.username \
        if not update.message.from_user.username == '' \
        else update.message.from_user.first_name + (' ' + update.message.from_user.last_name) \
            if not update.message.from_user.last_name == '' \
            else ''

# -----------------------------------------------------COMMANDS LIST----------------------------------------------------
    if message:
        message = message.replace(bot.name, "")

        splitText = message.split(' ', 1)

        bitcoinType = message.lower() == '/bitcoin'  # Bitcoin Rate Command
        issPosType = message.lower() == '/iss'  # ISS Position Command
        currencyType = message.lower() == '/rand'  # Currency Command
        rocketType = message.lower() == '/launch'  # Rocket Launch Command
        spacexType = message.lower() == '/spacex'  # SpaceX Launch Schedule Command
        mcType = message.lower() == '/mc'  # Minecraft server status
        cricType = message.lower() == '/cric'  # Proteas status from Cricbuzz api
        rgetType = message.lower() == '/get'  # Random get from setsetgo api

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
        lyricsType = splitText[0].lower() == '/getlyrics' if ' ' in message else False # Get lyrics from musix api
        reverseImageType = splitText[0].lower() == '/reverseimage' if ' ' in message else False # Get reverse image results from google
        steamGameType = splitText[0].lower() == '/getgame' if ' ' in message else False # Get game details from steam

        figType = message.lower().startswith('/getfig')  # Get a picture of a fig (common /getgif typo)
        isisType = message.lower().startswith('/isis')  # Get latest isis news (common /iss typo)

        requestText = filter(lambda x: x in string.printable, splitText[1]) if ' ' in message else ''
        requestTextForCurrentChatAction = requestText

# Ashley: Added a try catch here-
# For weird 'Unautherized' error when sending photos.
# Keeps track of the last user to receive a chat action.
# Satisfies pending chat actions with a message instead of a photo.
        userWithCurrentChatAction = ''
        urlForCurrentChatAction = ''
        requestTextForCurrentChatAction = ''
        try:
# ----------------------------------------------Image Search : GCSE API-------------------------------------------------
            if imageType:
                googurl = 'https://www.googleapis.com/customsearch/v1'
                args = {'cx': keyConfig.get('Google', 'GCSE_SE_ID'),
                        'key': keyConfig.get('Google', 'GCSE_APP_ID'),
                        'searchType': "image",
                        'safe': "off",
                        'q': requestText,
                        'searchType': "image"}
                realUrl = googurl + '?' + urllib.urlencode(args)
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 9:
                    imagelink = 'x-raw-image:///'
                    offset = 0
                    randint = random.randint(0, 9)
                    while imagelink.startswith('x-raw-image:///') and \
                                    offset < 10 and \
                                    randint + offset < len(data['items']):
                        imagelink = data['items'][randint + offset]['link']
                        offset = offset+1
                    if not imagelink.startswith('x-raw-image:///') and not imagelink == '':
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                        userWithCurrentChatAction = chat_id
                        urlForCurrentChatAction = imagelink
                        bot.sendPhoto(chat_id=userWithCurrentChatAction,
                                      photo=urlForCurrentChatAction.encode('utf-8'),
                                      caption=(user + ': ' if not user == '' else '') +
                                              string.capwords(requestText.encode('utf-8')) +
                                              (' ' + imagelink if len(imagelink) < 100 else ''))
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        userWithCurrentChatAction = chat_id
                        urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                  ', I\'m afraid I can\'t find any images for ' +\
                                                  string.capwords(requestText.encode('utf-8'))
                        requestTextForCurrentChatAction = requestText
                        bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction.encode('utf-8'))
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find any images for ' +\
                                              string.capwords(requestText.encode('utf-8'))
                    requestTextForCurrentChatAction = requestText
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction.encode('utf-8'))
# ------------------------------------------------Imgur Search : Imgur API----------------------------------------------
            if imgurType:
                client_id = keyConfig.get('Imgur', 'CLIENT_ID')
                client_secret = keyConfig.get('Imgur', 'CLIENT_SECRET')
                client = ImgurClient(client_id, client_secret)
                items = client.gallery_search(q=string.capwords(requestText.encode('utf-8')),
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
                                              string.capwords(requestText.encode('utf-8')) + '.'
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
                                              string.capwords(requestText.encode('utf-8')) + '.'
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
                    imagelink = 'x-raw-image:///'
                    offset = 0
                    while imagelink.startswith('x-raw-image:///') and offset < 10 and offset < len(data['items']):
                        imagelink = data['items'][offset]['link']
                        offset = offset+1
                    if not imagelink.startswith('x-raw-image:///'):
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                        userWithCurrentChatAction = chat_id
                        urlForCurrentChatAction = imagelink
                        bot.sendPhoto(chat_id=userWithCurrentChatAction, photo=urlForCurrentChatAction.encode('utf-8'),
                                      caption=(user + ': ' if not user == '' else '') +
                                              requestTextForCurrentChatAction.title().encode('utf-8') +
                                              (' ' + imagelink if len(imagelink) < 100 else ''))
                    else:
                        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                        userWithCurrentChatAction = chat_id
                        urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                  ', I\'m afraid I can\'t find a huge image for ' +\
                                                  string.capwords(requestText.encode('utf-8')) + '.'
                        bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find a huge image for ' +\
                                              string.capwords(requestText.encode('utf-8')) + '.'
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
                                              string.capwords(requestText.encode('utf-8')) + '.'
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -------------------------------------------Video Search : YouTube API-------------------------------------------------
            elif vidType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                vidurl = 'https://www.googleapis.com/youtube/v3/search?safeSearch=none&type=video&key=' + keyConfig.get \
                    ('Google', 'GCSE_APP_ID') + '&part=snippet&q='
                realUrl = vidurl + requestText.encode('utf-8')
                data = json.load(urllib.urlopen(realUrl))
                if 'items' in data and len(data['items']) >= 1:
                    vidlink = data['items'][0]['id']['videoId']
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                          'https://www.youtube.com/watch?v=' + vidlink + '&type=video')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid I can\'t do that.\n(Video not found)')
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
                                and 'xvideos.com/favorite/' not in xlink \
                                and 'xvideos.com/?k=' not in xlink \
                                and 'xvideos.com/tags' not in xlink \
                                and 'pornhub.com/users/' not in xlink \
                                and 'pornhub.com/video/search?search=' not in xlink \
                                and 'xvideos.com/profiles/' not in xlink \
                                and 'xnxx.com/?' not in xlink \
                                and 'xnxx.com/tags/' not in xlink \
                                and 'xhamster.com/stories_search' not in xlink \
                                and 'redtube.com/pornstar/' not in xlink \
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
                if 'list' in data and len(data['list']) >= 1:
                    resultNum = data['list'][random.randint(0, len(data['list']) - 1)]
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
                                              'Urban Definition For ' + string.capwords(requestText.encode('utf-8')) + ":\n" + resultNum['definition'] +\
                                              '\n\nExample:\n' + resultNum['example']
                    bot.sendMessage(chat_id=userWithCurrentChatAction,
                                    text=urlForCurrentChatAction)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction ='I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                             ', I\'m afraid I can\'t find any urban definitions for ' +\
                                             string.capwords(requestText.encode('utf-8')) + '.'
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
                if 'totalItems' in data and data['totalItems'] >= 1:
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
                                          (' ' + imagelink if len(imagelink) < 100 else ''))
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
                    moveUrl = 'http://riot.so/cgi-bin/chessbot/chess?time=30&move='
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
                                movesUrl = 'http://riot.so/cgi-bin/chessbot/chess?move=moves'
                                movesList = (urllib.urlopen(movesUrl)).read()[len('validmoves'):]
                                if not movesList == '':
                                    boardUrl = 'http://riot.so/cgi-bin/chessbot/chess?move=board'
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
                                    urllib.urlopen('http://riot.so/cgi-bin/chessbot/chess?move=reset')
                                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                                    userWithCurrentChatAction = chat_id
                                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                                              ', I\'m afraid the chess game is over.'
                                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
                            else:
                                movesUrl = 'http://riot.so/cgi-bin/chessbot/chess?move=moves'
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
# -------------------------------------View the current state of the chess game-----------------------------------------
            elif chessBoardType:
                movesUrl = 'http://riot.so/cgi-bin/chessbot/chess?move=moves'
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
                boardUrl = 'http://riot.so/cgi-bin/chessbot/chess?move=board'
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
                utc_zone = tz.tzutc()
                local_zone = tz.tzlocal()
                blast1UtcTime = datetime.datetime.strptime(b1['net'], '%B %d, %Y %H:%M:%S %Z')
                if blast1UtcTime.hour >= '22' or blast1UtcTime.hour == 0:
                    blast1UtcTime = blast1UtcTime + datetime.timedelta(days=1)
                blast1UtcTime = blast1UtcTime.replace(tzinfo=utc_zone)
                blast1LocalString = str(blast1UtcTime.astimezone(local_zone))
                blast1LocalTime = datetime.datetime.strptime(blast1LocalString, '%Y-%m-%d %H:%M:%S+02:00')
                blast2UtcTime = datetime.datetime.strptime(b2['net'], '%B %d, %Y %H:%M:%S %Z')
                if blast2UtcTime.hour >= '22' or blast2UtcTime.hour == 0:
                    blast2UtcTime = blast2UtcTime + datetime.timedelta(days=1)
                blast2UtcTime = blast2UtcTime.replace(tzinfo=utc_zone)
                blast2LocalString = str(blast2UtcTime.astimezone(local_zone))
                blast2LocalTime = datetime.datetime.strptime(blast2LocalString, '%Y-%m-%d %H:%M:%S+02:00')
                blast3UtcTime = datetime.datetime.strptime(b3['net'], '%B %d, %Y %H:%M:%S %Z')
                if blast3UtcTime.hour >= '22' or blast3UtcTime.hour == 0:
                    blast3UtcTime = blast3UtcTime + datetime.timedelta(days=1)
                blast3UtcTime = blast3UtcTime.replace(tzinfo=utc_zone)
                blast3LocalString = str(blast3UtcTime.astimezone(local_zone))
                blast3LocalTime = datetime.datetime.strptime(blast3LocalString, '%Y-%m-%d %H:%M:%S+02:00')
                blast4UtcTime = datetime.datetime.strptime(b4['net'], '%B %d, %Y %H:%M:%S %Z')
                if blast4UtcTime.hour >= '22' or blast4UtcTime.hour == 0:
                    blast4UtcTime = blast4UtcTime + datetime.timedelta(days=1)
                blast4UtcTime = blast4UtcTime.replace(tzinfo=utc_zone)
                blast4LocalString = str(blast4UtcTime.astimezone(local_zone))
                blast4LocalTime = datetime.datetime.strptime(blast4LocalString, '%Y-%m-%d %H:%M:%S+02:00')
                blast5UtcTime = datetime.datetime.strptime(b5['net'], '%B %d, %Y %H:%M:%S %Z')
                if blast5UtcTime.hour >= '22' or blast5UtcTime.hour == 0:
                    blast5UtcTime = blast5UtcTime + datetime.timedelta(days=1)
                blast5UtcTime = blast5UtcTime.replace(tzinfo=utc_zone)
                blast5LocalString = str(blast5UtcTime.astimezone(local_zone))
                blast5LocalTime = datetime.datetime.strptime(blast5LocalString, '%Y-%m-%d %H:%M:%S+02:00')
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = 'Upcoming Rocket Launches:\n\n' +\
                                          str(blast1LocalTime) + \
                                          '\n*' + b1['name'] + \
                                          '*\nLaunching from [' + b1['location']['pads'][0]['name'] + '](' + b1['location']['pads'][0]['mapURL'] + ')' + \
                                          ('\nWatch live at ' + b1['vidURL'] if 'vidURL' in b1 else '') + '\n\n' +\
                                          str(blast2LocalTime) + \
                                          '\n*' + b2['name'] + \
                                          '*\nLaunching from [' + b2['location']['pads'][0]['name'] + '](' + b2['location']['pads'][0]['mapURL'] + ')' + \
                                          ('\nWatch live at ' + b2['vidURL'] if 'vidURL' in b2 else '') + '\n\n' +\
                                          str(blast3LocalTime) + \
                                          '\n*' + b3['name'] + \
                                          '*\nLaunching from [' + b3['location']['pads'][0]['name'] + '](' + b3['location']['pads'][0]['mapURL'] + ')' + \
                                          ('\nWatch live at ' + b3['vidURL'] if 'vidURL' in b3 else '') + '\n\n' +\
                                          str(blast4LocalTime) + \
                                          '\n*' + b4['name'] + \
                                          '*\nLaunching from [' + b4['location']['pads'][0]['name'] + '](' + b4['location']['pads'][0]['mapURL'] + ')' + \
                                          ('\nWatch live at ' + b4['vidURL'] if 'vidURL' in b4 else '') + '\n\n' +\
                                          str(blast5LocalTime) + \
                                          '\n*' + b5['name'] + \
                                          '*\nLaunching from [' + b5['location']['pads'][0]['name'] + '](' + b5['location']['pads'][0]['mapURL'] + ')' + \
                                          ('\nWatch live at ' + b5['vidURL'] if 'vidURL' in b5 else '')
                bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
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
# --------------------------------------------------Current Proteas match-----------------------------------------------
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
# --------------------------------------------Search TV Shows with TVMaze API-------------------------------------------
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
# ------------------------------------Debug send photo with certain urls------------------------------------------------
            elif echoImgType:
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = requestText
                bot.sendPhoto(chat_id=chat_id, photo=urlForCurrentChatAction)
# -----------------------------------------------Get lyrics From musix match--------------------------------------------
            elif lyricsType:
                trackUrl = 'http://api.musixmatch.com/ws/1.1/track.search?apikey='
                data = json.load(urllib.urlopen(trackUrl + keyConfig.get('MusixMatch', 'APP_ID') + '&q=' + requestText))
                if 'message' in data and \
                                'body' in data['message'] and \
                                'track_list' in data['message']['body'] and \
                                len(data['message']['body']['track_list']) >= 1 and \
                                'track' in data['message']['body']['track_list'][0] and \
                                'artist_name' in data['message']['body']['track_list'][0]['track'] and \
                                'track_name' in data['message']['body']['track_list'][0]['track']:
                    artist_name = data['message']['body']['track_list'][0]['track']['artist_name']
                    track_name = data['message']['body']['track_list'][0]['track']['track_name']
                    track_soundcloud_id = str(data['message']['body']['track_list'][0]['track']['track_soundcloud_id'])
                    trackId = str(data['message']['body']['track_list'][0]['track']['track_id'])
                    lyricsUrl = 'http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey='
                    data = json.load(urllib.urlopen(lyricsUrl + keyConfig.get('MusixMatch', 'APP_ID') + '&track_id=' + trackId))
                    lyrics_body = ''
                    if 'message' in data and \
                                    'body' in data['message'] and \
                                    'lyrics' in data['message']['body'] and \
                                    len(data['message']['body']['lyrics']) >= 1 and \
                                    'lyrics_body' in data['message']['body']['lyrics']:
                        lyrics_body = data['message']['body']['lyrics']['lyrics_body'].replace('******* This Lyrics is NOT for Commercial use *******','')
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = ((user + ': ') if not user == '' else '') + track_name + ' by ' + artist_name +\
                                              (('\nListen at: https://api.soundcloud.com/tracks/' + track_soundcloud_id) if not track_soundcloud_id =='0' else '') +\
                                              (('\n' + lyrics_body) if not lyrics_body=='' else '')
                    bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find any tracks for the lyrics ' +\
                                              requestText.encode('utf-8')
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -------------------------------------------Perform google reverse image search----------------------------------------
            elif reverseImageType:
                code = retrieve_google_image_search_results(requestText)
                jsonResults = json.loads(google_image_results_parser(code))
                resultsText = ''
                if 'result_qty' in jsonResults and len(jsonResults['result_qty']) > 0:
                    for jsonResult in jsonResults['result_qty']:
                        resultsText += jsonResult + '\n'
                if 'title' in jsonResults and len(jsonResults['title']) > 0:
                    for jsonResult in jsonResults['title']:
                        resultsText += jsonResult + '\n'
                if 'description' in jsonResults and len(jsonResults['description']) > 0:
                    for jsonResult in jsonResults['description']:
                        resultsText += (jsonResult[jsonResult.index('-')+2:] + '\n' if '-' in jsonResult else '')
                if 'links' in jsonResults and len(jsonResults['links']) > 0:
                    for jsonResult in jsonResults['links']:
                        resultsText += jsonResult + '\n'
                resultLinks = code[code.index('Search Results'):].split('href=')
                for resultLink in resultLinks[1:]:
                    resultLink = resultLink[1:]
                    foundLink = resultLink[:resultLink.index('"')]
                    if foundLink != '#' and \
                                    foundLink != 'javascript:;' and \
                                    foundLink != 'javascript:void(0)' and \
                                    foundLink != '//www.google.com/intl/en/policies/privacy/?fg=1' and \
                                    foundLink != '//www.google.com/intl/en/policies/terms/?fg=1' and \
                                    len(foundLink) < 50:
                        resultsText += foundLink + '\n'
                bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                userWithCurrentChatAction = chat_id
                urlForCurrentChatAction = resultsText
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# -------------------------------------------Perform google reverse image search----------------------------------------
            elif steamGameType:
                code = urllib.urlopen("http://store.steampowered.com/search/?term=" + requestText).read()
                appId = steam_results_parser(code)
                if appId:
                    steamGameLink = "http://store.steampowered.com/app/" + appId
                    bypassAgeGate = urllib2.build_opener()
                    bypassAgeGate.addheaders.append(('Cookie', 'birthtime=578390401'))
                    code = bypassAgeGate.open(steamGameLink).read()
                    #code = urllib.urlopen(steamGameLink).read()
                    gameResults = steam_game_parser(code, steamGameLink)
                else:
                    gameResults = ""
                if gameResults:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = gameResults
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction,
                                    disable_web_page_preview=True, parse_mode='Markdown')
                else:
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    userWithCurrentChatAction = chat_id
                    urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
                                              ', I\'m afraid I can\'t find the steam game ' +\
                                              requestText.encode('utf-8')
                    bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
# ----------------------------------------------------------------------------------------------------------------------
            elif rgetType:
                pass
# ----------------------------------------------------------------------------------------------------------------------
            else:
                pass
        except telegram.TelegramError or \
                socket.timeout or socket.error or \
                urllib2.URLError or \
                httplib.BadStatusLine as e:
            adminGroupId = keyConfig.get('HeyBoet', 'ADMIN_GROUP_CHAT_ID')
            if not str(userWithCurrentChatAction) == adminGroupId:
                bot.sendMessage(chat_id=userWithCurrentChatAction, text=requestTextForCurrentChatAction + ': ' +
                                                                        urlForCurrentChatAction)
            if not adminGroupId == '':
                bot.sendMessage(chat_id=adminGroupId, text=
                'Error: ' + e.message + '\n' +
                'Request Text: ' + requestTextForCurrentChatAction + '\n' +
                'Url: ' + urlForCurrentChatAction)
# Offset the update queue to the next update
    urllib.urlopen('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/getUpdates?offset=' + str(update.update_id + 1))

# retrieves reverse search html for processing. This actually does reverse image lookups
def retrieve_google_image_search_results(image_url):
    returned_code = StringIO()
    full_url = "https://www.google.com/searchbyimage?&image_url=" + image_url
    conn = pycurl.Curl()
    conn.setopt(conn.URL, str(full_url))
    conn.setopt(conn.CAINFO, certifi.where())
    conn.setopt(conn.FOLLOWLOCATION, 1)
    conn.setopt(conn.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11")
    conn.setopt(conn.WRITEFUNCTION, returned_code.write)
    conn.perform()
    conn.close()
    return returned_code.getvalue()

# Parses reverse search html and assigns to array using beautifulsoup
def google_image_results_parser(code):
    soup = BeautifulSoup(code, "html.parser")

    # initialize 2d array
    whole_array = {"links":[],
                   "description":[],
                   "title":[],
                   "result_qty":[]}

    # Links for all the search results
    for li in soup.findAll("li", attrs={"class":"g"}):
        sLink = li.find("a")
        whole_array["links"].append(sLink["href"])

    # Search Result Description
    for desc in soup.findAll("span", attrs={"class":"st"}):
        whole_array["description"].append(desc.get_text())

    # Search Result Title
    for title in soup.findAll("h3", attrs={"class":"r"}):
        whole_array["title"].append(title.get_text())

    # Number of results
    for result_qty in soup.findAll("div", attrs={"id":"resultStats"}):
        whole_array["result_qty"].append(result_qty.get_text())

    return json.dumps(whole_array)

def steam_results_parser(code):
    soup = BeautifulSoup(code, "html.parser")
    resultList = []
    for resultRow in soup.findAll("a", attrs={"class":"search_result_row"}):
        if "data-ds-appid" in resultRow.attrs:
            resultList.append(resultRow["data-ds-appid"])
        if "data-ds-bundleid" in resultRow.attrs:
            resultList.append(resultRow["data-ds-bundleid"])
    if len(resultList) > 0:
        return resultList[0]
    return ""

def steam_game_parser(code, link):
    soup = BeautifulSoup(code, "html.parser")
    AllGameDetailsFormatted = ""

    titleDiv = soup.find("div", attrs={"class":"apphub_AppName"})
    if titleDiv:
        gameTitle = titleDiv.string
        AllGameDetailsFormatted += "*" + gameTitle + "*" + "\n"

    descriptionDiv = soup.find("div", attrs={"class":"game_description_snippet"})
    if descriptionDiv:
        descriptionSnippet = descriptionDiv.string.replace("\r", "").replace("\n", "").replace("\t", "")
        AllGameDetailsFormatted += descriptionSnippet + "\n"

    if AllGameDetailsFormatted:
        AllGameDetailsFormatted += link + "\n"

    dateSpan = soup.find("span", attrs={"class":"date"})
    if dateSpan:
        releaseDate = dateSpan.string
        AllGameDetailsFormatted += "Release Date: " + releaseDate + "\n"

    featureList = ""
    featureLinks = soup.findAll("a", attrs={"class":"name"})
    if len(featureLinks) > 0:
        for featureLink in featureLinks:
            featureList += "     " + featureLink.string.replace("Seated", "Will make you shit yourself") + "\n"
        AllGameDetailsFormatted += "Features:\n" + featureList

    reviewRows = ""
    reviewDivs = soup.findAll("div", attrs={"class":"user_reviews_summary_row"})
    if len(reviewDivs) > 0:
        for reviewRow in reviewDivs:
            reviewSubtitleDiv = reviewRow.find("div", attrs={"class":"subtitle column"}).string
            reviewSummaryDiv = reviewRow.find("div", attrs={"class":"summary column"}).string
            if not reviewSummaryDiv:
                reviewSummaryDiv = reviewRow.find("span", attrs={"class":"nonresponsive_hidden responsive_reviewdesc"}).string
            reviewSummaryDiv = reviewSummaryDiv.replace("\r", "").replace("\n", "").replace("\t", "")
            if reviewSummaryDiv != "No user reviews":
                reviewRows += "     " + reviewSubtitleDiv + reviewSummaryDiv.replace("-", "").replace(" user reviews", "").replace(" of the ", " of ") + "\n"
        if reviewRows:
            AllGameDetailsFormatted += "Reviews:\n" + reviewRows
        if AllGameDetailsFormatted.endswith("\n"):
            AllGameDetailsFormatted = AllGameDetailsFormatted[:AllGameDetailsFormatted.rfind("\n")]

    tagList = ""
    tagLinks = soup.findAll("a", attrs={"class":"app_tag"})
    if len(tagLinks) > 0:
        for tagLink in tagLinks:
            tagList += tagLink.string.replace("\r", "").replace("\n", "").replace("\t", "") + ", "
        AllGameDetailsFormatted += "\n" + "Tags:\n`" + tagList
    if AllGameDetailsFormatted.endswith(", "):
        AllGameDetailsFormatted = AllGameDetailsFormatted[:AllGameDetailsFormatted.rfind(", ")]
        AllGameDetailsFormatted += "`"

    return AllGameDetailsFormatted

if __name__ == '__main__':
    main()
