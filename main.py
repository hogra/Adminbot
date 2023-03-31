from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

tok = 'vk1.a.PjWas5ZQVRqq08J7YC8pC_AP6N8Fix4r1WYL48t5Df6B3fc2n8NWnx7AgzsABGYS0a1n-SG0y83sHVcGT0G8WAuUq7ReauMYA79bIN58Q0oI8q0WDBOPaCclOd7JP3YMKf6EV1eH5U0vxasKSGToVrgRVp-7XOjM9_brPN3pGDCeCwrJl_edSM57JKfGkhdNSbMH-ExcQyjnuzNXRgL_gQ'
vk_session = VkApi(token=tok)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 219582896)

def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            id = event.chat_id
            msg = event.object.message['text'].lower()
            if msg == 'привет':
                sender(id, 'Здарова, заебал')