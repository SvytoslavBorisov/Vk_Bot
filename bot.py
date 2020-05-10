import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from requests import get, post, delete
from werkzeug.security import check_password_hash

TOKEN = '74e37cc73292c748af3aa25a6d552d69d93a7be6e10ba227c2676282098c7707e9816d6bee18927a21a8a'
GROUP_ID = 194326967
USERS = []
ID_WITH_USERS = {}


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
    keyboard.add_button('Завершить игру!', color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


vk_session = vk_api.VkApi(token=TOKEN)

long_poll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

kb_in = create_keyboard_in()
kb_out = create_keyboard_out()
try_to_in = 0
try_to_in_for_open = 0
flag_game = 0
answers = []
number_quest = 0
right_answers = 0
def_answers = 0

for event in long_poll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['from_id'] in USERS:
            user_in = 1
            kb = kb_in
        else:
            user_in = 0
            kb = kb_out
        if event.message.text.lower() == 'мой рейтинг':
            if user_in:
                k = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']
                k.sort(key=lambda x: x['rating'], reverse=True)
                p = ID_WITH_USERS[event.obj.message["from_id"]]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'{p["nickname"]}, у вас {p["rating"]} очков рейтинга. Вы находитесь на {k.index(p) + 1} месте общего зачёта.',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы не авторизованы',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)

        elif event.message.text.lower() == 'общий рейтинг':
            k = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']
            k.sort(key=lambda x: x['rating'], reverse=True)
            s = ''
            for i in range(min(len(k), 10)):
                s += f'{i + 1}) {k[i]["surname"]} "{k[i]["nickname"]}" {k[i]["name"]} - {k[i]["rating"]}\n'
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=s,
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
        elif event.message.text.lower() == 'выйти':
            try_to_in = 0
            if user_in:
                USERS.remove(event.obj.message['from_id'])
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы успешно вышли',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb_out)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы не авторизованы',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        elif event.message.text.lower() == 'зайти':
            if not user_in:
                try_to_in_for_open = 1
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Введите ваш логин и пароль на сайте https://nothing-nowhere-nowhen.ru через запятую. Например: SuperMeatBoy,12345',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы уже авторизованы',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        elif event.message.text.lower() == 'сыграть в викторину':
            k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
            quest_number = random.randint(0, len(k))
            temp = k[quest_number]['answers'].split('!@#$%')
            while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(temp[0]) >= 40 or len(temp[1]) >= 40 or len(temp[2]) >= 40 or len(temp[3]) >= 40:
                quest_number = random.randint(0, len(k))
                temp = k[quest_number]['answers'].split('!@#$%')
            flag_game = 1
            answers = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Начинаем!',
                             random_id=random.randint(0, 2 ** 64))
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=k[quest_number]['text'],
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=create_keyboard_questions_answer(*temp))
        elif event.message.text.lower() == 'завершить игру!':
            quest_number = 0
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=f'Игра закончена. Вы ответили правильно {right_answers} раз и неправильно {def_answers}',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
            right_answers = 0
            def_answers = 0
        elif flag_game:
            number_quest += 1
            if event.message.text.lower() in set(answers):
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Правильно!',
                                 random_id=random.randint(0, 2 ** 64))
                k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
                quest_number = random.randint(0, len(k))
                right_answers += 1
                temp = k[quest_number]['answers'].split('!@#$%')
                while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(temp[0]) >= 40 or len(temp[1]) >= 40 or len(temp[2]) >= 40 or len(temp[3]) >= 40:
                    quest_number = random.randint(0, len(k))
                    temp = k[quest_number]['answers'].split('!@#$%')
                temp = k[quest_number]['answers'].split('!@#$%')
                flag_game = 1
                answers = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Вопрос №{number_quest + 1}',
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=k[quest_number]['text'],
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=create_keyboard_questions_answer(*temp))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Неправильно! Правильный ответ: {answers[0]}',
                                 random_id=random.randint(0, 2 ** 64))
                k = get('https://nothing-nowhere-nowhen.ru/api/questions').json()['questions']
                def_answers += 1
                quest_number = random.randint(0, len(k))
                temp = k[quest_number]['answers'].split('!@#$%')
                while k[quest_number]['type'] == 'write' or k[quest_number]['images'] != ' ' or len(temp[0]) >= 40 or len(temp[1]) >= 40 or len(temp[2]) >= 40 or len(temp[3]) >= 40:
                    quest_number = random.randint(0, len(k))
                    temp = k[quest_number]['answers'].split('!@#$%')
                temp = k[quest_number]['answers'].split('!@#$%')
                flag_game = 1
                answers = [x.lower().strip() for x in k[quest_number]['right_answer'].split('!@#$%')]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Вопрос №{number_quest + 1}',
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=k[quest_number]['text'],
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=create_keyboard_questions_answer(*temp))
        elif try_to_in_for_open:
            try:
                try_to_in_for_open = 0
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
                    try_to_in = 0
                    USERS.append(event.obj.message['from_id'])
                    ID_WITH_USERS[event.obj.message['from_id']] = cur_user
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Вы успешно авторизовались',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=kb_in)
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Данные некорректны, попробуйте еще раз',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=kb)
            except Exception:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Данные некорректны, попробуйте еще раз',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        else:
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Неизвестная команда. Пожалуйста, воспользуйтесь кнопками',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
