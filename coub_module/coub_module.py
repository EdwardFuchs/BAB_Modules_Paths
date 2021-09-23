#Модуль поиска coub для ядра BAB
#Версия: 1.0
#Авторы: https://vk.com/edwardfuchs
#Git: https://github.com/EdwardFuchs/coub_module


#Настройка:
max_count = 1 #Максимальное кол. коубов ( до 10 )
use_random = True #Испльзовать рандом

#Код
import requests
import random
def get_coubs(text):
    res = []
    coubs = requests.get(f"https://coub.com/api/v2/search?q={text}").json()["coubs"]
    count = max_count if len(coubs) >= max_count else len(coubs)
    if use_random:
        coubs = random.choices(coubs, k=count)
    else:
        coubs = coubs[:max_count]
    for coub in coubs:
        res.append("https://coub.com/view/" + coub["permalink"])
    return res
    
    
    
def coub(event):
    if event.bot.is_group():
        bot = event.bot.getBot("page")
        save = 0
    else:
        bot = event.bot
        save = 1
    if not bot:
        return event.message_send('Для работы необходим хотябы один бот-страница')
    if len(event.splited) < 3:
        event.message_send("Ошибка! В команде нужно указывать название коуба.")
        return False
    text = event.args
    coubs = get_coubs(text)
    videos = ""
    for coub in coubs:
        res = bot.method("video.save", link = coub)
        if "response" in res:
            upload_url = res["response"]["upload_url"]
            requests.get(upload_url)
            video_id = res["response"]["video_id"]
            owner_id = res["response"]["owner_id"]
            access_key = res["response"]["access_key"]
            videos += f"video{owner_id}_{video_id}_{access_key},"
    videos[:-1]
    if not videos:
        event.message_send(f'Коубы по запросу {event.args} не найдены')
    else:
        event.message_send(f'Коубы по запросу {event.args}', attachment = videos)
    


HandleCmd('коуб', 0, coub)
