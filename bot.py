# -*- coding: utf-8 -*-
from flask import *
#Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage, \
    SuggestedResponseKeyboard, TextResponse, StartChattingMessage, ScanDataMessage

from kik.messages.responses import SuggestedResponse

import bs4
from urllib.request import urlopen as ureq
import requests
import re

class Imdb:
    @staticmethod
    def searchtitle(search,x=0):
        details = []
        print(search,x)
        keyword = []

        for letter in search:
            if letter == ' ':
                keyword.append('+')
            else:
                keyword.append(letter)
        title = ''.join(keyword)
        myurl = "https://www.imdb.com/search/title/?title=" + title + "&count=10"

        response = requests.get(myurl)

        soup_obj = bs4.BeautifulSoup(response.text,'lxml')
        soup_obj.prettify()
        item = soup_obj.find_all('div', class_ = 'lister-item mode-advanced')

        length = len(item)

        if x < length:

            name = item[x].h3.a.text
            details.append(name)
            yr = item[x].h3.find('span', class_ = 'lister-item-year text-muted unbold')
            year = yr.text
            details.append(year)
            if item[x].find('div', class_ = 'ratings-imdb-rating') is not None:
                imdb_rating = float(item[x].strong.text)
                details.append("\n\U00002B50")
                details.append(imdb_rating)
                details.append("\\10\n")
            if item[x].find('div', class_ = 'ratings-metascore') is not None:
                metascore = item[x].find('span', class_ = 'metascore').text
                details.append("Metascore: ")
                details.append(metascore)
                details.append("\n")
            if item[x].p.find('span', class_ = 'runtime') is not None:
                rt = item[x].p.find('span', class_ = 'runtime')
                runtime = rt.text
                details.append(runtime)
            if item[x].p.find('span', class_ = 'genre') is not None:
                gen = item[x].p.find('span', class_ = 'genre')
                genre = gen.text
                details.append(genre)
            ptag = item[x].find_all('p', class_ = 'text-muted')
            plot = ptag[1].text
            details.append(plot)
            detailss = ''.join(str(e) for e in details)
            return detailss
        else:
            return "No search result found."

    @staticmethod
    def searchposter(search,x=0):
        details = []
        print(search,x)
        keyword = []
        for letter in search:
            if letter == ' ':
                keyword.append('+')
            else:
                keyword.append(letter)
        title = ''.join(keyword)
        myurl = "https://www.imdb.com/search/title/?title=" + title + "&count=10"
        response = requests.get(myurl)
        soup_obj = bs4.BeautifulSoup(response.text,'lxml')
        soup_obj.prettify()
        item = soup_obj.find_all('div', class_ = 'lister-item mode-advanced')
        length = len(item)
        if x < length:
            if item[x].find('div', class_ = 'lister-item-image float-left') is not None:
                posterurl = item[x].find('div', class_ = 'lister-item-image float-left').a.img.get('loadlate')
                print("1."+posterurl)
                posterurl = posterurl[:-29]
                print("2."+posterurl)
                posterurl += ".jpg"
                print("3."+posterurl)
                return posterurl
            else:
                return "No poster found."
        else:
            return None

bot = Imdb()

class KikBot(Flask):
    """ Flask kik bot application class"""

    def __init__(self, kik_api, import_name, static_path=None, static_url_path=None, static_folder="static",
                 template_folder="templates", instance_path=None, instance_relative_config=False,
                 root_path=None):

        self.kik_api = kik_api

        super(KikBot, self).__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                                     instance_path, instance_relative_config, root_path)

        self.route("/", methods=["POST"])(self.incoming)


    def incoming(self):
        # verify that this is a valid request
        if not self.kik_api.verify_signature(request.headers.get("X-Kik-Signature"), request.get_data()):
            return Response(status=403)

        messages = messages_from_json(request.json["messages"])
        i=0

        response_messages = []

        for message in messages:
            user = self.kik_api.get_user(message.from_user)
            # Check if its the user's first message. Sent only once.
            if isinstance(message, StartChattingMessage):
                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Hey {}, This bot performs the search for any title you type and shows the info from IMDb website.".format(user.first_name),
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Help")])]))
            
            elif isinstance(message, ScanDataMessage):
                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Hey {}, This bot performs the search for any title you type and shows the info from IMDb website.".format(user.first_name),
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Help")])]))

            # Check if the user has sent a text message.
            elif isinstance(message, TextMessage):
                user = self.kik_api.get_user(message.from_user)
                message_body_lower = message.body.lower()
                message_body = message.body

                if message_body in ['']:
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body="Type any title you want and this bot will show the info from IMDb website of that title.\nIf you need further help, please join #moviesNshows.",
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Help")])]))

                elif message_body in ["!Help"]:
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body="Type any title you want and this bot will show the info from IMDb website of that title.\nIf you need further help, please join #moviesNshows",
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Help")])]))

                elif message_body.split()[0] in ["!Next"]:
                    newtitle = message_body.strip("!Next")
                    print(newtitle)

                    if bot.searchposter(newtitle) is not None:
                        response_messages.append(PictureMessage(
                            to=message.from_user,
                            chat_id=message.chat_id,
                            pic_url=bot.searchposter(newtitle,x=i+1)
                        ))
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=bot.searchtitle(newtitle,x=i+1),
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Next "+newtitle), TextResponse("!Help")] )]
                        )
                    )

                else:
                    if bot.searchposter(message_body_lower) is not None:
                        response_messages.append(PictureMessage(
                            to=message.from_user,
                            chat_id=message.chat_id,
                            pic_url=bot.searchposter(message_body_lower)
                        ))
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=bot.searchtitle(message_body_lower),
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Next "+message_body_lower), TextResponse("!Help")])]
                        )
                    )

            # If its not a text message
            else:

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Type any title you want and this bot will show the info from IMDb website of that title.",
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("!Help")])]))

            self.kik_api.send_messages(response_messages)

        return Response(status=200)


kik = KikApi('imdb.bot', '56a9320d-84cb-4b4c-9ec9-4c7f714ab0ea')
kik.set_configuration(Configuration(webhook='https://myimdbbot.herokuapp.com'))
app = KikBot(kik, __name__)

if __name__ == "__main__":
    """ Main program """
    app.run(port=8080, host='127.0.0.1', debug=True)