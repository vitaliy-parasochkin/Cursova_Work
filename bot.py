import config #імпорт токена
import logging
import random
from aiogram import Bot, Dispatcher, executor, types #імпорт бота

"""
asdasfasfasfasd
"""

logging.basicConfig(level=logging.INFO)
#ініціалізація бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

#функція яка перебирає кожне слово
def normalize_city_name(name):
    return name.strip().lower()
#робимо із нашого файлу з містами України масив
cities = [normalize_city_name(x) for x in open("Cities.txt", "r" ,encoding="utf-8").readlines() if x.strip()]
cities_cache = {}
#обробник події коли користувач нажтискає команду /start
@dp.message_handler(commands=['start'])
async def start_message(message:types.Message):
    await message.answer('Привіт!\nЦе гра міста в українські міста, українською мовою.\nЩоб розпочати гру,вам просто потрібно натиснути команду "/play", '
                         'і тоді я підберу місто :).\nНехай щастить!')

#обробник події коли користувач нажтискає команду /start
@dp.message_handler(commands=['play'])
async def play_message(message:types.Message):
    id_user = message.from_user.id
    if id_user in cities_cache:
        cities_cache[id_user].clear()
    await message.answer('Гра почалась!\n')
    await message.answer(first_city(id_user))
@dp.message_handler(text = ['Здаюсь']) #Обробник події, для того коли користувач пропише "Здаюсь"
async def answer(message:types.Message):
    await message.answer('Ви визнали поразку\nДля того,щоб знову грати, пропишіть команду /play')
@dp.message_handler(commands=['info'])#Обробник події, для того коли користувач захоче дізнатись інформацію про бота
async def show_info(message:types.Message):
    await message.answer("Вся інформація про міста взяти з сторінки в вікіпедії, ось посилання https://uk.m.wikipedia.org/wiki/%D0%9C%D1%96%D1%81%D1%82%D0%B0_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8_(%D0%B7%D0%B0_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D1%96%D1%82%D0%BE%D0%BC)\n"
                         "Бот створений тільки для українських міст, і українською мовою.\n"
                         "В базі даних бота є лише населенні пункти, які мають статус 'Місто'\n"
                         "Бот може місцями працювати некоректно, з всіма питаннями звертатись до розробників :) ")
@dp.message_handler(commands=['rules'])#Обробник події, для того коли користувач захоче дізнатись правила гри
async def show_info(message:types.Message):
    await message.answer('Щоб почати гру, необхідно написати боту команду - "/play". Після цього,бот генерує місто, на останню букву якого, користувач повинен написати нове місто.\n'
                         'Якщо остання букви міста "ь", "й", "и", то ця буква заміняється на попередню перед нею, тобто якщо місто Глиняни, то користувачу потрібно ввести місто на букву "н".\n'
                         'Гра завершується тоді коли в базі даних бота закінчаться міста, або коли користувач визнає поразку і напише боту текст - "Здаюсь".'
                         'Вдалої гри!')
#обробник події коли користувач відповідає
@dp.message_handler()
async def main(message:types.Message):
    id_user = message.from_user.id
    city_user = message.text.lower()
    last_letter_for_user = last_char(cities_cache[id_user][-1])
    last_letter_for_bot = last_char(city_user)
    if check_city(city_user):
        if check_letter_city(city_user,last_letter_for_user):
            if (check_city_in_cache(city_user,id_user)==False):
                add_city_in_cache(city_user,id_user)
                await message.answer(new_city(last_letter_for_bot,id_user))
            else:
                await message.answer('Це місто вже було назване. Подумайте над іншим варіантом')
        else:
            await message.answer("Місто повинне починатись з літери " + last_letter_for_user)
    else:
        await message.answer("Я такого міста не знаю :(")

def normalize_city(city): #переводимо слова в нижній регістр,щоб було простіше працювати
    return city.lower()

def first_city(id_user):#Генератор першого міста
    city = random.choice(cities)
    cities_cache[id_user] = [city]
    return city.capitalize()

def check_city(city): #перевірка на те,чи є таке місто в нашій базі
    if city in cities:
        return True
    else:
        return False

def check_letter_city(city,letter): #Перевірка останньої літери
    if city.startswith(letter[-1]):
        return True
    else:
        return False

def generate_city(arr,letter): #обробник події для перемоги
    for i in cities:
        if i.startswith(letter):
            arr.append(i)
    if arr == []:
        return 'Гру закінчено,ви перемогли!'
    return random.choice(arr)

def new_city(letter,id_user): #ГЕнератор нового міста від лиця бота
    cities_temp=[]
    bot_city = generate_city(cities_temp,letter)
    while(bot_city in cities_cache[id_user]):
        bot_city = generate_city(cities_temp, letter)
    cities_cache[id_user].append(bot_city)
    return bot_city.capitalize()

def check_city_in_cache(city,id_user): #Перевірка чи не називали таке місто
    if city in cities_cache[id_user]:
        return True
    else:
        return False

def add_city_in_cache(city,id_user): #Добавляємо місто в кеш вже названих міст
    cities_cache[id_user].append(city)

def last_char(city): #Заміна букв в кінці слова на попередні перед ним
    wrong_char = ['ь',"и","й"]
    for i in wrong_char:
        if (i==city[-1]):
            return city[-2]
    return city[-1]

def win(arr):# обробник події перемоги
    if len(cities_cache) == len(cities):
        return 'Гру закінчено,ви перемогли!'

#Запуск бота
if __name__=='__main__':
    executor.start_polling(dp,skip_updates=True)