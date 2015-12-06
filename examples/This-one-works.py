import logging
import telegram
import urllib
import json
import random


bot = telegram.Bot('151051910:AAERVg5H2dcyHQWH05UvFTdXw4XUBQZjL5s')

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        for update in bot.getUpdates(offset=update_id, timeout=10):
            text = update.message.text
            chat_id = update.message.chat.id
            update_id = update.update_id

            if text:
                roboed = ed(text)  # Ask something
                bot.sendMessage(chat_id=chat_id, text=roboed)
                update_id = update_id + 1


def ed(text):
    url = 'https://www.googleapis.com/customsearch/v1?&searchType=image&num=10&cx=011897561310453504822:g-xqrhezi3e&key=AIzaSyBmrK9xQUoX6xFZWYZ5jRWWK4B2ETkweWc&q=' + text.encode('utf-8')
    data = json.load(urllib.urlopen(url))
    if text.startswith('/img '):
        if data['searchInformation']['totalResults'] >= '1':
            imagelink = data['items'][random.randint(0, 9)]['link']
            return imagelink
        else:
            return 'I\'m sorry Dave, I\'m afraid I can\'t do that.\n(Image not found)'
    else:
        pass


if __name__ == '__main__':
    main()
