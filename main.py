import os
import requests
from dotenv import load_dotenv
import telebot
from bs4 import BeautifulSoup
import urllib.parse

TOKEN = '1862922993:AAFSX9gFBXA2TRjrzEM61a6EgKkd4uxHMVU'
URL = 'http://russpeech.spbu.ru/search/trn-search.php?wf='

bot = telebot.TeleBot(TOKEN)

results_cache = []
message_cache = ''
first_word = ''


def get_string(list_to_str):
    string = '\n\n'.join(list_to_str)
    return string


def search(word):
    """Makes an http request to the corpus and gets out the search results"""
    url_word = URL + urllib.parse.quote(word.encode('cp1251'))
    request = requests.get(url_word).content
    soupik = BeautifulSoup(request, 'html.parser')
    finds = soupik.find_all('p', {'class': 'res'})
    global results_cache
    results_cache = [res.text.strip() for res in finds]


def send_results(message):
    """Sends results depending on their amount"""
    amount = len(results_cache)
    words = message.text.split()
    if amount == 0:
        msg = 'По заданному запросу результатов не найдено.'
        if len(words) > 1:
            msg += f'\nВыполнить поиск для "{words[0]}"? /confirm – выполнить поиск'
            message.text = words[0]
            global message_cache
            message_cache = message
        bot.send_message(message.chat.id, msg)
    elif amount > 5:
        msg = f'По Вашему запросу найдено {amount} результатов. /yes – распечатать все'
        bot.send_message(message.chat.id, msg)
    else:
        msg = get_string(results_cache)
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['start', 'greet'])
def greet(message):
    msg = ('Здравствуйте! Я – бот Корпуса русской устной речи.\n'
           'Для осуществления поиска отправьте нужную словоформу в сообщении')
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['yes'])
def return_long_results(message):
    global results_cache
    for i in range(0, len(results_cache), 5):
        beg = i + 1
        end = i + 5 if i + 5 < len(results_cache) else len(results_cache)
        msg = f'Результаты с {beg} по {end}\n\n'
        msg += get_string(results_cache[i:i + 5])
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['confirm'])
def get_first_word_results(message):
    search(message_cache.text.lower())
    send_results(message_cache)


@bot.message_handler(func=lambda m: True)
def return_search(message):
    search(message.text.lower())
    send_results(message)


bot.infinity_polling()
