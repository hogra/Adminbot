from vk_api import VkApi, exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data import db_session, users, group


tok = 'vk1.a.PjWas5ZQVRqq08J7YC8pC_AP6N8Fix4r1WYL48t5Df6B3fc2n8NWnx7AgzsABGYS0a1n-SG0y83sHVcGT0G8WAuUq7ReauMYA79bIN58Q0oI8q0WDBOPaCclOd7JP3YMKf6EV1eH5U0vxasKSGToVrgRVp-7XOjM9_brPN3pGDCeCwrJl_edSM57JKfGkhdNSbMH-ExcQyjnuzNXRgL_gQ'
vk_session = VkApi(token=tok)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 219582896)
DOMENS = ['.com', '.edu', '.fun', '.gov', '.info', '.net', '.org', '.xxx', '.dev', '.ai', '.au', '.az', '.cz', '.eu',
          '.gg', '.ru', '.рф', '.su']


def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})

def eraser(gid, mid):
    vk_session.method('messages.delete', {'peer_id': 2000000000 + gid, 'delete_for_all': 1, 'cmids': mid, 'random_id': 0})

db_session.global_init("db/users.db")
db_session.global_init("db/group.db")
db_sess = db_session.create_session()

def greg(gid, works, keys=None):
    g = group.Group()
    g.groupid = gid
    g.works = works
    db_sess = db_session.create_session()
    db_sess.add(g)
    db_sess.commit()

def grreg(a, gid):
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.greet = a
    db_sess.commit()

def ureg(a, gid, status):
    u = users.User()
    u.userid = a['id']
    u.groupid = gid
    u.surname = a['last_name']
    u.name = a['first_name']
    u.status = status
    db_sess.add(u)
    db_sess.commit()

def wreg(a, gid):
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.words = a
    db_sess.commit()

def streg(gid, uid, a):
    db_sess = db_session.create_session()
    u = db_sess.query(users.User).filter(users.User.groupid == gid, users.User.userid == uid).first()
    u.status = a
    db_sess.commit()

def lreg(a, gid):
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.links = a
    db_sess.commit()

def getadmins(gid):
    members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
    l1 = list()
    for i in members:
        try:
            if i['is_admin']:
                l1.append(i['member_id'])
        except KeyError:
            pass
        except IndexError:
            pass
    return l1


for event in longpoll.listen():
    gid = event.chat_id
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            msg = event.object.message['text'].lower()
            a = False
            print(event.object['message'])
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None:
                forbidden = db_sess.query(group.Group.words).filter(group.Group.groupid == gid).first()[0]
                if forbidden is not None:
                    forbidden = db_sess.query(group.Group.words).filter(group.Group.groupid == gid).first()[0].split(',')
                else:
                    forbidden = []
                keylinks = db_sess.query(group.Group.links).filter(group.Group.groupid == gid).first()[0]
                try:
                    if event.object['message']['action']['type'] == 'chat_invite_user':
                        print(event.object['message'])
                        sender(gid, db_sess.query(group.Group.greet).filter(group.Group.groupid == gid).first()[0])
                        a = vk.users.get(user_id=event.object['message']['action']['member_id'])
                        ureg(a[0], gid, 'пользователь')
                except TypeError:
                    pass
                except KeyError:
                    pass
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None and len(msg) > 0:
                if msg[0] == '!' and db_sess.query(users.User.status).filter(users.User.userid == event.object.message['from_id'], users.User.groupid == gid).first()[0] == 'админ':
                    if msg[1:6] == 'админ':
                        q = event.object.message
                        fromid = q['reply_message']['from_id']
                        streg(gid, fromid, 'админ')
                        a = vk.users.get(user_id=fromid)[0]
                        sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                    elif msg[1:4] == 'кик':
                        q = event.object.message
                        if db_sess.query(users.User.status).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).first()[0] == 'админ':
                            print(db_sess.query(users.User.userid).filter(users.User.userid == q['from_id'], users.User.groupid == gid).first()[0])
                            if db_sess.query(users.User.userid).filter(users.User.userid == q['from_id'], users.User.groupid == gid).first()[0] in getadmins(gid):
                                try:
                                    db_sess.query(users.User).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).delete()
                                    db_sess.commit()
                                    vk.messages.removeChatUser(chat_id=gid, user_id=q['reply_message']['from_id'])
                                    sender(gid, 'Готово, этого парня вы больше не встретите')
                                except exceptions.ApiError:
                                    sender(gid, 'Хара-кири?')
                            else:
                                sender(gid, 'Это как вы хотите кикнуть админа?')
                        else:
                            try:
                                db_sess.query(users.User).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).delete()
                                db_sess.commit()
                                vk.messages.removeChatUser(chat_id=gid, user_id=q['reply_message']['from_id'])
                                sender(gid, 'Готово, этого парня вы больше не встретите')
                            except exceptions.ApiError:
                                sender(gid, 'Хара-кири?')
                    elif msg[1:6] == 'снять':
                        q = event.object.message
                        fromid = q['reply_message']['from_id']
                        streg(gid, fromid, 'пользователь')
                        a = vk.users.get(user_id=fromid)[0]
                        sender(gid, f"{a['first_name']} {a['last_name']} больше не админ")
                    elif msg[1:10] == 'за работу':
                        sender(gid, 'Не стройте из себя дурака, у меня уже есть ваша карточка!')
                    elif msg[1:5] == 'ключ':
                        if msg[6:11] == 'слово':
                            word = msg[11:].replace(' ', '')
                            lst = db_sess.query(group.Group.words).filter(group.Group.groupid == gid).first()[0]
                            if lst is not None:
                                lst = lst.split(',')
                                if word in lst:
                                    lst.remove(word)
                                    sender(gid, f'Я убрал слово {word} из списка запрещенных слов')
                                else:
                                    lst.append(word)
                                    sender(gid, f'Я добавил слово {word} в список запрещенных слов')
                            else:
                                lst = [word]
                                sender(gid, f'Я добавил слово {word} в список запрещенных слов')
                            fin = ','.join(lst)
                            wreg(fin, gid)
                        elif msg[6:12] == 'ссылки':
                            if keylinks == 1:
                                lreg(0, gid)
                                sender(gid, 'Ссылки теперь разрешены')
                            else:
                                lreg(1, gid)
                                sender(gid, 'Ссылки теперь запрещены')
                        elif msg[6:17] == 'приветствие':
                            a = msg[18:]
                            if a != '':
                                grreg(a, gid)
                                sender(gid, 'Приветственное сообщение изменено')
                            else:
                                sender(gid, 'Я слишком вежлив, чтобы не здороваться с новичками')
                    elif msg[1:2] == '-':
                        try:
                            eraser(gid, event.object.message['reply_message']['conversation_message_id'])
                        except exceptions.ApiError:
                            sender(gid, 'Прости, я не могу удалить это сообщение')
                    else:
                        sender(gid, 'а где комманда? вот тебе список, не волнуйся ##тут будет ссылка на html список##')
                elif msg[0] == '!' and db_sess.query(users.User.status).filter(users.User.userid == event.object.message['from_id'], users.User.groupid == gid).first()[0] == 'админ':
                    sender(gid, 'А команды могут использовать только админы, дружище')
                elif msg in forbidden:
                    try:
                        eraser(gid, event.object.message['conversation_message_id'])
                    except exceptions.ApiError:
                        pass
                elif keylinks:
                    if 'https://' in msg or 'http://' in msg or any(list(map(lambda x: x in msg, DOMENS))):
                        try:
                            eraser(gid, event.object.message['conversation_message_id'])
                        except exceptions.ApiError:
                            pass
                if msg == 'привет':
                    sender(gid, 'Здарова, заебал')
            elif msg == '!за работу':
                if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is None:
                    greg(gid, True)
                members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
                print(members)
                for i in getadmins(gid):
                    try:
                        a = vk.users.get(user_id=i)[0]
                        ureg(a, gid, 'админ')
                        sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                    except IndexError:
                        pass
                for i in members:
                    try:
                        a = vk.users.get(user_id=i['member_id'])[0]
                        print(a)
                        print(getadmins(gid))
                        if a['id'] not in getadmins(gid):
                            ureg(a, gid, 'пользователь')
                    except IndexError:
                        pass
                sender(gid, 'Регистрация окончена')
            elif len(msg) == 0:
                pass
            else:
                sender(gid, 'Товарищ, похоже эта беседа не зарегистрирована!\nЧтобы зарегистрировать беседу предоставьте '
                            'боту права администратора, доступ ко всей переписке и напишите команду "!За работу"')