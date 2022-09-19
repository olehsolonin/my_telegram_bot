
"""
Задача:
Соеденить два скрипта, которые уже есть. 
Нужно прикрутить скрипт, ищущий предложения на английском, которые содержат слово, 
введенное юзером и подбирают предложение на английском, где содержится это слово, 
и которое подохдит юзеру по уровню. 
Что уже имеем: 
1. Простой эхо-бот для Телеги, который пулит последние сообщения, через ТелеграмБотАПИ и шлет 
    в ответ копию того, что юзер ему написал.
2. Скрипт, который принимает слово и юзера (дикт, где указан юзернейм и уровень английского) 
   и возыращает строчку, которая содержит одно или несколько предложений, либо сообщение о том,
    что ничего не найдено.
Соответвенно, нужно сделать так, чтоб бот в телеге читал сообщение от юзера, 
и, если это слово на английском, возвращал сообщение с результатом.
Для практической мы используем очень примитивный флоу, 
без большинства нужных проверок, т.к. на них можно сильно застрять. Они остануться на домашки.
Норимальный флоу должен быть такой:
- Принимаем сообщение.
- Смотрим на ID юзера и проверяем, есть у нас такой или нет. 
- Если нет, тосоздаем нового, забиваем туда ID и шлем юзеру в ответ сообщение:
  "Выбери свой уровень английского"
- Принимаем его и записыаем к юзеру.
- Теперь можем обратывать его сообщения - слова на английском.
- На каждон из этих сообщений делаем такие проверки:
     - если сообщение не начинаеися со / (служебные команды), 
     - не число, 
     - не кирилица 
    то это просто слово на английском, и мы его кидаем в функцию, 
    которая выдает предложения с этим словом и отправляемю юзеру ответ.
Для практической сделаем более примитивный.
- Юзера захардкодим в виде словаря {"username": str, "level"; int}
- Будем исходить из того, что мы всегда шлем только корректные сообщения: 
  одно словo на английском.
- Поэтому, все что нужно, это прокидывать слово из телеграм-сообщения в скрипт, 
 получать результат и отсылать обратно.
- еще было бы неплохо добавить логирование, пока просто принтами.
"""

import requests

token = "5483119869:AAG8mx7aV3FeM2IV9rZSAyCOVY95uHFbc4Q"
root_url = "https://api.telegram.org/bot"

ok_codes = 200, 201, 202, 203, 204

user = {"username" : "Egor",
          "level" : 1} 

sentences = [
    {"text": "When my time comes \n Forget the wrong that I’ve done.", 
    "level": 1},
    {"text": "In a hole in the ground there lived a hobbit.", 
    "level": 2},
    {"text": "The sky the port was the color of television, tuned to a dead channel.", 
    "level": 1},
    {"text": "I love the smell of napalm in the morning.", 
    "level": 0},
    {"text": "The man in black fled across the desert, and the gunslinger followed.", 
    "level": 0},
    {"text": "The Consul watched as Kassad raised the death wand.", 
    "level": 1},
    {"text": "If you want to make enemies, try to change something.", 
    "level": 2},
    {"text": "We're not gonna take it. \n Oh no, we ain't gonna take it \nWe're not gonna take it anymore", 
    "level": 1},
    {"text":"I learned very early the difference between knowing the name of something and knowing something.", 
    "level": 2}
]


def fill_matched_sentences(message, user = user, sentences = sentences)->list:
    matched_sentences = []
    for sentence in sentences:
        user_lvl = user.get("level")
        sentences_lvl = sentence.get("level")
        sentences_txt = sentence.get("text")
        if  sentences_lvl == user_lvl:
            if message in sentences_txt:
                matched_sentences.append(sentences_txt)
    return matched_sentences


def create_result_message(matched_sentences:list)->str:
    result_message = ""
    if not matched_sentences:
        result_message = "Sorry, not found sentences for your request"
    if len(matched_sentences) == 1:
        result_message = matched_sentences[0]
    if len(matched_sentences) > 1:
            for x in matched_sentences:
                result_message += x + "\n...\n"
    return result_message

def send_message(token, chat_id, message):
    url = f"{root_url}{token}/sendMessage"
    res = requests.post(url, data={'chat_id': chat_id, "text": message})
    if res.status_code in ok_codes:
        return True
    else:
        print(f"Request failed with status_code {res.status_code}")
        return False

def get_updates(token):
    url = f"{root_url}{token}/getUpdates"
    res = requests.get(url)
    if res.status_code in ok_codes:
        updates = res.json()
        return updates

def process_message(message:str)->str:

    if message[0] == '/':
        message = 'системная команда'
    else:
        matched_sentences = fill_matched_sentences(message)
        message = create_result_message(matched_sentences)
    
    return message


updates = get_updates(token)

last_message_id = 0
while True:
    updates = get_updates(token)
    last_message = updates["result"][-1]    
    message_id = last_message["message"]["message_id"]
    
    last_message_text = last_message["message"]["text"]
    chat_id = last_message["message"]["chat"]["id"] 
    
    if message_id > last_message_id:
        message_to_user = process_message(last_message_text)
        send_message(token, chat_id, message_to_user)
        last_message_id = message_id


# add lower case check
# change level
# numbers and kirilica
# error if don't have a new message