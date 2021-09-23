#Модуль погоды для ядра BAB
#Версия: 2.1
#Авторы: https://vk.com/edwardfuchs
#Git: https://github.com/EdwardFuchs/weather_module


#Настройка:
graphic = True #Использовать ли графику


#Код
from PIL import Image, ImageFont, ImageDraw #Для создания и редактирования изображений
import requests #Для запросов на сайт
import datetime #Для получения времени
from io import BytesIO #Для сохранения файла в оперативную память
import os.path #Для проверки существования файла


#Функция для получения погоды
def get_weather(city):
    weather = requests.get('http://api.openweathermap.org/data/2.5/weather', params={
        'lang':'ru',
        'units': 'metric',
        'APPID': 'ef23e5397af13d705cfb244b33d04561',
        'q': city
    }).json()
    if weather["cod"] == "404" or weather["cod"] == 404:
        raise Exception(f"404: Город {city} не найден.")
    elif weather["cod"] != "200" and weather["cod"] != 200:
        raise Exception(f"200: {weather['message']}")
    icon = weather["weather"][0]["icon"]
    temp = weather["main"]["temp"]
    temp_min = weather["main"]["temp_min"]
    temp_max = weather["main"]["temp_max"]
    utc = weather["timezone"]
    country = weather['sys']['country']
    weather_desc = weather["weather"][0]["description"]
    wind_speed = weather["wind"]["speed"]
    clouds = weather["clouds"]["all"]
    humidity = weather["main"]["humidity"]
    time_update = datetime.datetime.fromtimestamp(weather["dt"]).strftime('%H:%M')
    return city, country, icon, temp, temp_min, temp_max, utc, weather_desc, wind_speed, clouds, humidity, time_update


#исполение команды
def weather(event):
    if len(event.splited) < 3:
        event.message_send("Ошибка! В команде нужно указывать город.")
        return False
    city = event.args
    try:
        city, country, icon, temp, temp_min, temp_max, utc, weather_desc, wind_speed, clouds, humidity, time_update = get_weather(city)
    except Exception as error:
        event.message_send(error)
    if graphic:
        #Графика
        # Иконка
        icon_url = f"http://openweathermap.org/img/wn/{icon}@4x.png"
        icon = Image.open(requests.get(icon_url, stream=True).raw)
        icon = icon.resize([300, 300], resample=Image.LANCZOS)
        #Проверка наличия шрифта
        if not os.path.isfile("Files/Fonts/NotoSansCJKsc-Regular.otf"):
            event.message_send("Похоже вы в певый раз запустили графический плагин. Скачиваем нужный шрифт и помещаем его в нужное место...")
            if not os.path.exists("Files"):
                event.message_send("Создаем папку Files/Fonts/")
                os.makedirs("Files/Fonts/")
            fnt = requests.get("https://github.com/googlefonts/noto-cjk/raw/master/NotoSansCJKsc-Regular.otf")
            with open("Files/Fonts/NotoSansCJKsc-Regular.otf", "wb") as f:
                f.write(fnt.content)
            event.message_send("Шрифт скачан и помещен в нужное место.")
        # Задаем шрифт
        small = ImageFont.truetype('Files/Fonts/NotoSansCJKsc-Regular.otf', 48)
        big = ImageFont.truetype('Files/Fonts/NotoSansCJKsc-Regular.otf', 128)
        # Создаем изображение
        img = Image.new("RGB", (1080, 400), "#000000")
        draw = ImageDraw.Draw(img)
        # Текст по центру
        w, h = draw.textsize(f"{country}/{city}", font=small)
        draw.text((((1080 - w) / 2), 20), f"{country}/{city}", font=small, fill=(255, 255, 255))
        # Часы
        offset = datetime.timedelta(seconds=utc)  # отступ по UTC
        tz = datetime.timezone(offset, name=city)
        dt = datetime.datetime.now(tz=tz)
        time = dt.strftime("%H:%M")
        draw.text((205, 70), time, font=big, fill=(255, 255, 255))
        draw.text((530, 60), "|", font=big, fill=(255, 255, 255))
        data = dt.strftime("%A, %d %B")
        # на русский
        data = data.replace("Monday", "Понедельник").replace("Tuesday", "Вторник").replace("Wednesday", "Среда").replace("Thursday", "Четверг").replace("Friday", "Пятница").replace("Saturday", "Суббота").replace("Sunday", "Воскресенье")
        data = data.replace("January", "Января").replace("February", "Февраля").replace("March", "Марта").replace("April", "Апреля").replace("May", "Мая").replace("June", "Июня").replace("July", "Июля").replace("August", "Августа").replace("September", "Сентября").replace("October", "Октября").replace("November", "Ноября").replace("December", "Декабря")
        # Текст по центру
        w, h = draw.textsize(data, font=small)
        draw.text((((1080 - w) / 2), 300), data, font=small, fill=(255, 255, 255))
        # ставим значёк погоды
        img.paste(icon, (520, 20), icon)
        # температуры
        draw.text((800, 100), f"{int(temp)}°", font=small, fill=(255, 255, 255))
        draw.text((800, 160), f"{int(temp_min)}°/{int(temp_max)}°", font=small, fill=(255, 255, 255))
        temp = BytesIO()
        img.save(temp, format="png")
        files = [{'type': "photo", 'data': temp.getvalue(), 'name': "weather.png"}]
        event.bot.upload_files(files, event.peer_id)
        temp.close()
        img.close()
    else:
        #без графики
        current_weather = f"""Погода в {country}/{city}:
        &#8195;•Температура: {temp}°C
        &#8195;•Состояние: {weather_desc}
        &#8195;•Скорость ветра: {wind_speed} м/с
        &#8195;•Облачность: {clouds}%
        &#8195;•Влажность: {humidity}%
        &#8195;•Время обновления: {time_update} UTC{f'+{utc / 3600}' if utc >= 0 else utc / 3600}"""
        event.message_send(f"{current_weather}")

    
HandleCmd('погода', 0, weather)