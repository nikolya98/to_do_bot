import telebot
import assistentem_bot
import os
import pickle


TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    if assistentem_bot.check_user(message.from_user.id)[0]:
        bot.send_message(message.from_user.id, 'С возвращением!')
    else:
        bot.send_message(message.from_user.id, 'Приветствую!')
        bot.send_message(message.from_user.id, assistentem_bot.give_help(file='help'))


@bot.message_handler(commands=['help'])
def doc(message):
    bot.send_message(message.from_user.id, assistentem_bot.give_help(file='help'))


@bot.message_handler(content_types=['photo'])
def save_photo(message):
    user_path = assistentem_bot.check_user(message.from_user.id)[1]
    photo = message.photo[-1]
    file_id = photo.file_id
    file_path = bot.get_file(file_id).file_path
    downloaded_file = bot.download_file(file_path)
    with open(f'{user_path}/photos/' + f'{message.date}.jpg', mode='wb') as directory:
        directory.write(downloaded_file)
    new_case(message)


@bot.message_handler(commands=['new_case'])
def new_case(message):
    if message.content_type == 'photo':
        message_text = message.caption.replace('/new_case', '').strip().split(':', maxsplit=1)
    else:
        message_text = message.text.replace('/new_case', '').strip().split(':', maxsplit=1)
    message_text = [i.strip() for i in message_text]
    case = {
        'case_name': message_text[0],
        'case_description': message_text[1],
        'case_photo': None,
        'case_date': message.date
    }
    if message.content_type == 'photo':
        case['case_photo'] = message.photo[-1].file_id
    assistentem_bot.case_save(assistentem_bot.check_user(message.from_user.id)[1], case)


@bot.message_handler(commands=['show_case'])
def show_case(message):
    path = assistentem_bot.check_user(message.from_user.id)[1]
    case_name = message.text.replace('/show_case', '').strip()
    case_dates = list()
    if assistentem_bot.check_metadata(path):
        bot.send_message(message.from_user.id, 'Задача не найдена! Вы ещё не добавили ни одной задачи.')
        return
    with open(f'{path}/metadata.pickle', 'rb') as metadata_file:
        all_cases = pickle.load(metadata_file)
    for i in range(len(all_cases)):
        if case_name.lower() == all_cases[i][0].lower():
            case_dates.append(all_cases[i][1])
    if not case_dates:
        bot.send_message(message.from_user.id, 'Задача не найдена!')
        return
    buffer = list()
    for i in case_dates:
        case_file = open(f'{path}{i}.pickle', 'rb')
        buffer.append(pickle.load(case_file))

    if len(buffer) > 1:
        warning_text = assistentem_bot.give_help(file='show_case')
        same_cases = '\n'
        for case in buffer:
            same_cases += f'Название: {case["case_name"]}. ' \
                          f'Дата создания: {assistentem_bot.date_processing(case["case_date"])}\n'
        bot.send_message(message.from_user.id, warning_text + same_cases)
        return
    else:
        case = buffer[0]
        if case['case_photo']:
            with open(f'{path}photos/{case["case_photo"]}.jpg', 'rb') as photo:
                bot.send_photo(message.from_user.id, photo,
                               f'{case["case_name"]}. {case["case_description"]}')
            return
        message_text = f'{case["case_name"]}.\n' + f'{case["case_description"]}'
        bot.send_message(message.from_user.id, message_text)


@bot.message_handler(commands=['show_this'])
def show_this(message):
    path = assistentem_bot.check_user(message.from_user.id)[1]
    if assistentem_bot.check_metadata(path):
        bot.send_message(message.from_user.id, 'Задача не найдена! Вы ещё не добавили ни одной задачи.')
        return
    date = message.text.replace('/show_this', '').strip()
    try:
        date_processed = assistentem_bot.date_processing(date, mode='reverse')
    except ValueError:
        bot.send_message(message.from_user.id, 'Некорректный ввод. Воспользуйтесь командой /help')
        return
    if f'{date_processed}.pickle' not in os.listdir(path):
        bot.send_message(message.from_user.id, 'Задача не найдена! Используйте команду /show_all')
        return
    with open(f'{path}{date_processed}.pickle', 'rb') as file_case:
        case = pickle.load(file_case)
        if case['case_photo']:
            with open(f'{path}photos/{case["case_photo"]}.jpg', 'rb') as photo:
                bot.send_photo(message.from_user.id, photo,
                               f'{case["case_name"]}. {case["case_description"]}')
            return
        message_text = f'{case["case_name"]}.\n' + f'{case["case_description"]}'
        bot.send_message(message.from_user.id, message_text)


@bot.message_handler(commands=['show_all'])
def show_all(message):
    path = assistentem_bot.check_user(message.from_user.id)[1]
    if assistentem_bot.check_metadata(path):
        bot.send_message(message.from_user.id, 'Задач не найдено! Добавьте новую задачу...')
        return
    with open(f'{path}/metadata.pickle', 'rb') as metadata_file:
        message_text = 'Список задач:\n\n'
        cases_list = pickle.load(metadata_file)
        for i in cases_list:
            message_text += f'{cases_list.index(i) + 1}. {i[0]}\n' +\
                            f'Дата создания: {assistentem_bot.date_processing(i[1])}\n\n'
    bot.send_message(message.from_user.id, message_text)


@bot.message_handler(commands=['delete_case'])
def delete_case(message):
    path = assistentem_bot.check_user(message.from_user.id)[1]
    if assistentem_bot.check_metadata(path):
        bot.send_message(message.from_user.id, 'Вы не добавили ни одной задачи. Нет доступных для удаления задач!')
        return
    need_to_delete = message.text.replace('/delete_case', '').strip()
    buffer = list()
    with open(f'{path}metadata.pickle', 'rb') as metadata_file:
        all_cases = pickle.load(metadata_file)
    for case in all_cases:
        if need_to_delete.lower() == case[0].lower():
            buffer.append(case)
    if len(buffer) == 0:
        bot.send_message(message.from_user.id, 'Задача не найдена! Используйте команду /show_all')
        return
    elif len(buffer) > 1:
        warning_text = assistentem_bot.give_help(file='delete')
        find_cases = '\n'
        for i in buffer:
            find_cases += f'Название: {i[0]}. Дата создания: {assistentem_bot.date_processing(i[1])}\n'
        bot.send_message(message.from_user.id, warning_text + find_cases)
        return
    else:
        if f'{buffer[0][1]}.jpg' in os.listdir(f'{path}photos'):
            os.remove(f'{path}photos/{buffer[0][1]}.jpg')
        os.remove(f'{path}{buffer[0][1]}.pickle')
        all_cases.remove(buffer[0])
        with open(f'{path}metadata.pickle', 'wb') as metadata_file:
            pickle.dump(all_cases, metadata_file)


@bot.message_handler(commands=['delete_this'])
def delete_this(message):
    path = assistentem_bot.check_user(message.from_user.id)[1]
    if assistentem_bot.check_metadata(path):
        bot.send_message(message.from_user.id, 'Задача не найдена! Вы ещё не добавили ни одной задачи.')
        return
    date = message.text.replace('/delete_this', '').strip()
    try:
        date_processed = assistentem_bot.date_processing(date, mode='reverse')
    except ValueError:
        bot.send_message(message.from_user.id, 'Некорректный ввод. Воспользуйтесь командой /help')
        return
    if f'{date_processed}.pickle' not in os.listdir(path):
        bot.send_message(message.from_user.id, 'Задача не найдена! Используйте команду /show_all')
        return
    if f'{date_processed}.jpg' in os.listdir(f'{path}photos'):
        os.remove(f'{path}photos/{date_processed}.jpg')
    os.remove(f'{path}{date_processed}.pickle')
    with open(f'{path}metadata.pickle', 'rb') as metadata:
        all_cases = pickle.load(metadata)
        for case in all_cases:
            if case[1] == date_processed:
                all_cases.remove(case)
    with open(f'{path}metadata.pickle', 'wb') as metadata:
        pickle.dump(all_cases, metadata)


bot.polling()
