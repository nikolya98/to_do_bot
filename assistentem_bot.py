import os
import datetime
import pickle


def check_user(user_id):
    """
    Функция проверяет известен ли нам пользователь или нет.

    Если пользователь новый, то функция создаст для него папку и файл, и вернёт False...
    Если пользователь уже известен (т.е. для него уже была создана папка), то функция вернёт True.
    """
    users = os.listdir('users/')
    user_id = str(user_id)
    if user_id in users:
        user_path = f'users/{user_id}/'
        return True, user_path
    else:
        os.mkdir(f'users/{user_id}')
        os.mkdir(f'users/{user_id}/photos')
        user_path = f'users/{user_id}/'
        metadata_processing(user_path, mode='create')
        return False, user_path


def metadata_processing(path, case=None, mode='update'):
    """
    Функция обрабатывает файл с метаданными пользователя.

    Метаданные - список пар ('Задача', дата_добавления).
    Если выбран mode='create', то функция создаст файл с метаданными для пользователя.
    Если выбран mode='update', то функция обновляет файл с метаданными.
    """
    if mode == 'create':
        metadata_file = open(f'{path}/metadata.pickle', 'wb')
        metadata_file.close()
    elif mode == 'update':
        with open(f'{path}/metadata.pickle', 'rb+') as metadata_file:
            if check_metadata(path):
                metadata = list()
                initial_data = (case['case_name'], case['case_date'])
                metadata.append(initial_data)
                pickle.dump(metadata, metadata_file)
                return
            else:
                metadata = pickle.load(metadata_file)
        with open(f'{path}/metadata.pickle', 'wb') as metadata_file:
            case_info = (case['case_name'], case['case_date'])
            metadata.append(case_info)
            pickle.dump(metadata, metadata_file)


def give_help(file='help'):
    """
    Функция возвращает текст документации бота.
    """
    with open(f'help/{file}.txt', 'r', encoding='utf-8') as docs:
        message_text = docs.read()
    return message_text


def check_metadata(path):
    return os.path.getsize(f'{path}/metadata.pickle') == 0


def case_save(path, case):
    """
    Функция добавляет запись в файл.

    Функция принимает задачу от пользователя (в виде словаря), сериализирует её и записывает в файл.
    """
    with open(f'{path}/{case["case_date"]}.pickle', 'wb') as file_with_case:
        pickle.dump(case, file_with_case)
    metadata_processing(path, case, mode='update')


def date_processing(date, mode='straight'):
    if mode == 'straight':
        res = datetime.datetime.fromtimestamp(date)
        return res.strftime('%d-%m-%Y %H:%M:%S')
    elif mode == 'reverse':
        res = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        return int(res.timestamp())
