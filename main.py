from vk_api import VkApi, exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data import db_session, users, group


tok = 'vk1.a.PjWas5ZQVRqq08J7YC8pC_AP6N8Fix4r1WYL48t5Df6B3fc2n8NWnx7AgzsABGYS0a1n-SG0y83sHVcGT0G8WAuUq7ReauMYA79bIN58Q0oI8q0WDBOPaCclOd7JP3YMKf6EV1eH5U0vxasKSGToVrgRVp-7XOjM9_brPN3pGDCeCwrJl_edSM57JKfGkhdNSbMH-ExcQyjnuzNXRgL_gQ'
vk_session = VkApi(token=tok)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 219582896)



def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


db_session.global_init("db/users.db")
db_session.global_init("db/group.db")
db_sess = db_session.create_session()

def greg(gid, works, keys=None):
    g = group.Group()
    g.groupid = gid
    g.keys = 'None'
    g.works = works
    db_sess = db_session.create_session()
    db_sess.add(g)
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
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            gid = event.chat_id
            msg = event.object.message['text'].lower()
            a = False
            print(event.chat_id)
            try:
                dey = event.message.action['type']
                invite_id = event.message.action['member_id']
            except:
                dey = ''
                invite_id = -100
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None and len(msg) > 0:
                print(dey)
                gr = db_sess.query(group.Group.greet).filter(group.Group.groupid == gid).first()[0]
                if dey == 'chat_invite_user':
                    print(db_sess.query(group.Group.greet).filter(group.Group.groupid == gid).first()[0])
                    sender(gid, gr)
                if msg[0] == '!':
                    if msg[1:6] == 'админ':
                        q = event.object.message
                        fromid = q['reply_message']['from_id']
                        try:
                            if db_sess.query(users.User.status).filter(users.User.userid == fromid, users.User.groupid == gid).first()[0] == 'админ':
                                sender(gid, 'А он уже')
                            else:
                                    a = vk.users.get(user_id=fromid)[0]
                                    ureg(a, gid, 'админ')
                                    sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                        except TypeError:
                            sender(gid, f"Да я и так админ")
                    elif msg[1:4] == 'кик':
                        q = event.object.message
                        print(q)
                        print(db_sess.query(users.User).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).first())
                        if db_sess.query(users.User.status).filter(users.User.userid == q['from_id'], users.User.groupid == gid).first()[0] == 'админ':
                            if q['from_id'] in getadmins(gid):
                                try:
                                    vk.messages.removeChatUser(chat_id=gid, user_id=q['reply_message']['from_id'])
                                    sender(gid, 'Готово, этого парня вы больше не встретите')
                                except exceptions.ApiError:
                                    sender(gid, 'Хара-кири?')
                            try:
                                if db_sess.query(users.User.status).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).first()[0] != 'админ':
                                    vk.messages.removeChatUser(chat_id=gid, user_id=q['reply_message']['from_id'])
                                    sender(gid, 'Готово, этого парня вы больше не встретите')
                                if db_sess.query(users.User.status).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).first()[0] == '' or db_sess.query(users.User.status).filter(users.User.userid == q['reply_message']['from_id'], users.User.groupid == gid).first()[0] == 'отсутствует':
                                    sender(gid, 'Это как вы хотите кикнуть админа?')
                            except TypeError:
                                pass
                            else:
                                sender(gid, 'Разбирайтесь со своими проблемами сами, или позовите организатора. Админ не '
                                       'может кикать админа')
                        else:
                            sender(gid, 'У вас нет прав админа для этого действия')
                    elif msg[1:6] == 'снять':
                        q = event.object.message
                        fromid = q['reply_message']['from_id']
                        a = vk.users.get(user_id=fromid)[0]
                        user = db_sess.query(users.User).filter(users.User.userid == fromid, users.User.groupid == gid).first()
                        print(user)
                        user.status = "отсутствует"
                        db_sess.commit()
                    elif msg[1:10] == 'за работу':
                        sender(gid, 'Не стройте из себя дурака, у меня уже есть ваша карточка!')
                    else:
                        sender(gid, 'а где комманда? вот тебе список, не волнуйся ##тут будет ссылка на html список##')
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
                        print(i, a)
                        ureg(a, gid, 'админ')
                        sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                    except IndexError:
                        pass
                sender(gid, 'Регистрация окончена')
            elif len(msg) == 0:
                pass
            else:
                sender(gid, 'Товарищ, похоже эта беседа не зарегистрирована!\nЧтобы зарегистрировать беседу предоставьте '
                            'боту права администратора, доступ ко всей переписке и напишите команду "!За работу"')