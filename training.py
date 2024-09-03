import telebot
import sqlite3
import datetime
import os

bot = telebot.TeleBot("Token")

@bot.message_handler(commands=['add_workout'])
def add_workout(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Введите название упражнения:")
    bot.register_next_step_handler(message, get_exercise)

def get_exercise(message):
    chat_id = message.chat.id
    exercise = message.text

    bot.send_message(chat_id, "Укажите вес:")
    bot.register_next_step_handler(message, get_weight, exercise=exercise)

def get_weight(message, exercise):
    chat_id = message.chat.id
    weight = message.text

    bot.send_message(chat_id, "Укажите количество подходов:")
    bot.register_next_step_handler(message, get_sets, exercise=exercise, weight=weight)

def get_sets(message, exercise, weight):
    chat_id = message.chat.id
    sets = message.text

    bot.send_message(chat_id, "Укажите количество повторений:")
    bot.register_next_step_handler(message, get_reps, exercise=exercise, weight=weight, sets=sets)

def get_reps(message, exercise, weight, sets):
    chat_id = message.chat.id
    reps = message.text
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect('training_diary.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO workouts (exercise, weight, sets, reps, date) VALUES (?, ?, ?, ?, ?)', (exercise, weight, sets, reps, date))

    bot.send_message(chat_id, "Новая тренировка успешно добавлена в дневник.")

@bot.message_handler(commands=['view_workouts_date'])
def view_workouts_date(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Введите дату в формате ГГГГ-ММ-ДД:")
    bot.register_next_step_handler(message, get_date)

def get_date(message):
    chat_id = message.chat.id
    date = message.text

    with sqlite3.connect('training_diary.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM workouts WHERE date LIKE ?', (f"{date}%",))
        workouts = cursor.fetchall()

    if workouts:
        workout_list = " ".join([f"Дата: {workout[5]}, Упражнение: {workout[1]}, Вес: {workout[2]}, Подходы: {workout[3]}, Повторения: {workout[4]} " for workout in workouts])
        bot.send_message(chat_id, f"Тренировки на {workout_list}: ")

    else:
            bot.send_message(chat_id, f"На дату {date} тренировок не найдено.")

@bot.message_handler(func=lambda message: True)
def send_exercise_info(message):
    exercise_name = message.text

    with sqlite3.connect('exercises.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, description, image_path, gif_url FROM exercises WHERE name = ?', (exercise_name,))
        exercise = cursor.fetchone()

    if exercise:
        name, description, image_path, gif_url = exercise
        name = str(name)  # Преобразуем значение в строку, если оно не строка

        # Отправляем описание упражнения
        bot.send_message(message.chat.id, f"Описание упражнения {name}: {description}")
        
        # Получаем абсолютный путь к файлу изображения
        image_full_path = os.path.abspath(os.path.join(os.getcwd(), image_path))
        
        try:
            with open(image_full_path, 'rb') as image_file:
                bot.send_photo(message.chat.id, photo=image_file, caption="Картинка упражнения")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Файл изображения не найден.")
        
        if gif_url:
            with open(gif_url, 'rb') as gif_file:
                bot.send_document(message.chat.id, document=gif_file, caption="Гифка упражнения")
        else:
            bot.send_message(message.chat.id, "Ссылка на гифку упражнения не найдена.")
    else:
        bot.send_message(message.chat.id, "Упражнение не найдено.") 

bot.polling()
