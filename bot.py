import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from requests import get, post, delete
from werkzeug.security import check_password_hash

TOKEN = '74e37cc73292c748af3aa25a6d552d69d93a7be6e10ba227c2676282098c7707e9816d6bee18927a21a8a'
GROUP_ID = 194326967
USERS = []


def create_keyboard_in():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Мой рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Общий рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Сыграть в викторину", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Выйти", color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


def create_keyboard_out():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Мой рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Общий рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Сыграть в викторину", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Зайти", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


def create_keyboard_questions_answer(p, p1, p2, p3):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(p, color=VkKeyboardColor.DEFAULT)
    keyboard.add_button(p1, color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button(p2, color=VkKeyboardColor.DEFAULT)
    keyboard.add_button(p3, color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Завершить игру', color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


vk_session = vk_api.VkApi(token=TOKEN)

long_poll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

kb_in = create_keyboard_in()
kb_out = create_keyboard_out()

all_info = {}

for event in long_poll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['from_id'] not in all_info:
            all_info[event.obj.message['from_id']] = {}
        if event.obj.message['from_id'] in USERS:
            all_info[event.obj.message['from_id']]['user_in'] = 1
            kb = kb_in
        else:
            all_info[event.obj.message['from_id']]['user_in'] = 0
            kb = kb_out
        if event.message.text.lower() == 'мой рейтинг':
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            if all_info[event.obj.message['from_id']]['user_in']:
                k = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']
                k.sort(key=lambda x: x['rating'], reverse=True)
                p = all_info[event.obj.message["from_id"]]['user']
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'{p["nickname"]}, у вас {p["rating"]} очков рейтинга. Вы находитесь на {k.index(p) + 1} месте общего зачёта.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы не авторизованы.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)

        elif event.message.text.lower() == 'общий рейтинг':
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            k = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']
            k.sort(key=lambda x: x['rating'], reverse=True)
            s = ''
            for i in range(min(len(k), 10)):
                s += f'{i + 1}) {k[i]["name"]} "{k[i]["nickname"]}" {k[i]["surname"]} - {k[i]["rating"]}\n'
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=s,
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
        elif event.message.text.lower() == 'выйти':
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            if all_info[event.obj.message['from_id']]['user_in']:
                USERS.remove(event.obj.message['from_id'])
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы успешно вышли.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb_out)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы не авторизованы.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        elif event.message.text.lower() == 'зайти':
            if not all_info[event.obj.message['from_id']]['user_in']:
                all_info[event.obj.message['from_id']]['try_to_in'] = 1
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Введите ваш логин и пароль на сайте https://nothing-nowhere-nowhen.ru через запятую. Например: SuperMeatBoy,12345.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы уже авторизованы.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        elif event.message.text.lower() == 'сыграть в викторину':
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            all_info[event.obj.message['from_id']]['flag_game'] = 1
            all_info[event.obj.message['from_id']]['number_quest'] = 0
            all_info[event.obj.message['from_id']]['right_answers'] = 0
            all_info[event.obj.message['from_id']]['right_answers'] = 0
            all_info[event.obj.message['from_id']]['def_answers'] = 0
            k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
            quest_number = random.randint(0, len(k) - 1)
            all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
            while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(all_info[event.obj.message['from_id']]['temp'][0]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][1]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][2]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][3]) >= 40:
                quest_number = random.randint(0, len(k) - 1)
                all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
            all_info[event.obj.message['from_id']]['answers'] = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Начинаем!',
                             random_id=random.randint(0, 2 ** 64))
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Вопрос №1',
                             random_id=random.randint(0, 2 ** 64))
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=k[quest_number]['text'],
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=create_keyboard_questions_answer(*all_info[event.obj.message['from_id']]['temp']))
        elif event.message.text.lower() == 'завершить игру':
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            all_info[event.obj.message['from_id']]['flag_game'] = 0
            all_info[event.obj.message['from_id']]['number_quest'] = 0
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=f'Игра закончена. Вы ответили правильно {all_info[event.obj.message["from_id"]]["right_answers"]} раз и неправильно {all_info[event.obj.message["from_id"]]["def_answers"]}',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
            all_info[event.obj.message['from_id']]['right_answers'] = 0
            all_info[event.obj.message['from_id']]['def_answers'] = 0
        elif 'flag_game' in all_info[event.obj.message['from_id']] and all_info[event.obj.message['from_id']]['flag_game']:
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            all_info[event.obj.message['from_id']]['number_quest'] += 1
            if event.message.text.lower() in set(all_info[event.obj.message['from_id']]['answers']):
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Правильно!',
                                 random_id=random.randint(0, 2 ** 64))
                k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
                quest_number = random.randint(0, len(k) - 1)
                all_info[event.obj.message['from_id']]['right_answers'] += 1
                all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(all_info[event.obj.message['from_id']]['temp'][0]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][1]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][2]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][3]) >= 40:
                    quest_number = random.randint(0, len(k) - 1)
                    all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                all_info[event.obj.message['from_id']]['flag_game'] = 1
                all_info[event.obj.message['from_id']]['answers'] = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Вопрос №{all_info[event.obj.message["from_id"]]["number_quest"] + 1}',
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=k[quest_number]['text'],
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=create_keyboard_questions_answer(*all_info[event.obj.message['from_id']]['temp']))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Неправильно! Правильный ответ:\n{all_info[event.obj.message["from_id"]]["answers"][0][0].upper() + all_info[event.obj.message["from_id"]]["answers"][0][1:]}.',
                                 random_id=random.randint(0, 2 ** 64))
                k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
                all_info[event.obj.message['from_id']]['def_answers'] += 1
                quest_number = random.randint(0, len(k) - 1)
                all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(all_info[event.obj.message['from_id']]['temp'][0]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][1]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][2]) >= 40 or len(all_info[event.obj.message['from_id']]['temp'][3]) >= 40:
                    quest_number = random.randint(0, len(k) - 1)
                    all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                all_info[event.obj.message['from_id']]['temp'] = k[quest_number]['answers'].split('!@#$%')
                flag_game = 1
                all_info[event.obj.message['from_id']]['answers'] = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Вопрос №{all_info[event.obj.message["from_id"]]["number_quest"] + 1}',
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=k[quest_number]['text'],
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=create_keyboard_questions_answer(*all_info[event.obj.message['from_id']]['temp']))
        elif 'try_to_in' in all_info[event.obj.message['from_id']] and all_info[event.obj.message['from_id']]['try_to_in']:
            try:
                nickname, password = event.message.text.lower().replace(' ', '').split(',')
                nickname = nickname.lower()
                users = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']

                good = 0
                cur_user = 0
                for x in users:
                    if x['nickname'].lower() == nickname and check_password_hash(x['password'], password):
                        good = 1
                        cur_user = x
                        break

                if good:
                    all_info[event.obj.message['from_id']]['try_to_in'] = 0
                    USERS.append(event.obj.message['from_id'])
                    all_info[event.obj.message['from_id']]['user'] = cur_user
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Вы успешно авторизовались.',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=kb_in)
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Данные некорректны, попробуйте еще раз.',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=kb)
            except Exception:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Данные некорректны, попробуйте еще раз.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        else:
            all_info[event.obj.message['from_id']]['try_to_in'] = 0
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Неизвестная команда. Пожалуйста, воспользуйтесь кнопками.',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
