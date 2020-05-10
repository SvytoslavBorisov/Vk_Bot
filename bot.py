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
    keyboard.add_button("Выйти", color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


def create_keyboard_out():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Мой рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Общий рейтинг", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Зайти", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


vk_session = vk_api.VkApi(token=TOKEN)

long_poll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

kb_in = create_keyboard_in()
kb_out = create_keyboard_out()
try_to_in = 0

for event in long_poll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['from_id'] in USERS:
            user_in = 1
            kb = kb_in
        else:
            user_in = 0
            kb = kb_out
        if event.message.text.lower() == 'мой рейтинг':
            try_to_in = 0
            if user_in:
                p = ID_WITH_USERS[event.obj.message["from_id"]]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'{p["nickname"]}, у вас {p["rating"]} очков рейтинга',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы не авторизованы',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)

        elif event.message.text.lower() == 'общий рейтинг':
            try_to_in = 0
            k = get('https://nothing-nowhere-nowhen.ru/api/12345/users').json()['users']
            k.sort(key=lambda x: -x['rating'])
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
                try_to_in = 1
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Введите ваш логин и пароль на сайте https://nothing-nowhere-nowhen.ru через запятую. Например: SuperMeatBoy,12345',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Вы уже авторизованы',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=kb)
        elif try_to_in:
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
            try_to_in = 0
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Неизвестная команда. Пожалуйста, воспользуйтесь кнопками',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=kb)
