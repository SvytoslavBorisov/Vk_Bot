import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random


def main():
    vk_session = vk_api.VkApi(
        token='74e37cc73292c748af3aa25a6d552d69d93a7be6e10ba227c2676282098c7707e9816d6bee18927a21a8a')

    longpoll = VkBotLongPoll(vk_session, '194326967')

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            print(f'Печатает {event.obj.from_id} для {event.obj.to_id}')

        if event.type == VkBotEventType.GROUP_JOIN:
            print(f'{event.obj.user_id} вступил в группу!')

        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()

            print(event)
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])

            user = vk.users.get(user_id=event.obj.message['from_id'])
            fullname = user[0]['first_name'] + ' ' + user[0]['last_name']

            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=f"Привет, { fullname }! Спасибо, что написали нам. Мы обязательно ответим",
                             random_id=random.randint(0, 2 ** 64))


main()