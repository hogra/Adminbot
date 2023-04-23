from datetime import datetime, timedelta

from vk_api import exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from current_group import CurGroup
from current_user import CurUser
from tools import *

longpoll = VkBotLongPoll(vk_session, 219582896)
DOMENS = ['.com', '.edu', '.fun', '.gov', '.info', '.net', '.org', '.xxx', '.dev', '.ai', '.au', '.az', '.cz', '.eu',
          '.gg', '.ru', '.рф', '.su']

for event in longpoll.listen():
    gid = event.chat_id
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            msg = event.object.message['text'].lower()
            a = False
            print(event.object['message'])
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None:
                cgr = CurGroup(gid)
                forbidden = cgr.forbidden
                keylinks = cgr.links
                try:
                    if event.object['message']['action']['type'] == 'chat_invite_user':
                        print(event.object['message'])
                        sender(gid, cgr.greet)
                        a = vk.users.get(user_id=event.object['message']['action']['member_id'])
                        ureg(a[0], gid, 'пользователь')
                except TypeError:
                    pass
                except KeyError:
                    pass
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None and len(msg) > 0:
                cru = CurUser(event.object.message['from_id'], gid)
                try:
                    ans = CurUser(event.object.message['reply_message']['from_id'], gid)
                except KeyError:
                    ans = False
                if cru.stat[:3] == 'мут':
                    dto = datetime.strptime(cru.stat[4:], '%Y-%m-%d %H:%M:%S')
                    dtn = datetime.now()
                    print(dto)
                    print(datetime.now())
                    if dto <= datetime.now():
                        streg(gid, cru.uid, 'пользователь')
                    else:
                        eraser(gid, event.object.message['conversation_message_id'])
                if msg[0] == '!' and cru.stat == 'админ':
                    if msg[1:6] == 'админ':
                        if ans is not False:
                            q = event.object.message
                            streg(gid, ans.uid, 'админ')
                            sender(gid, f"{ans.name} {ans.sname} назначен админом")
                        else:
                            sender(gid,
                                   'Кого назначать-то? Напишите вашу команду в ответ на сообщение этого ответственного '
                                   'господина')
                    elif msg[1:4] == 'кик':
                        if ans is not False:
                            if ans.stat == 'админ':
                                if cru.uid in getadmins(gid):
                                    try:
                                        db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                         users.User.groupid == gid).delete()
                                        db_sess.commit()
                                        vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid)
                                        sender(gid, 'Готово, этого парня вы больше не встретите')
                                    except exceptions.ApiError:
                                        sender(gid, 'Хара-кири?')
                                else:
                                    sender(gid, 'Это как вы хотите кикнуть админа?')
                            else:
                                try:
                                    db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                     users.User.groupid == gid).delete()
                                    db_sess.commit()
                                    vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid)
                                    sender(gid, 'Готово, этого парня вы больше не встретите')
                                except exceptions.ApiError:
                                    sender(gid, 'Хара-кири?')
                        else:
                            sender(gid, 'Кого кикать-то? Напишите вашу команду в ответ на сообщение этого негодяя')
                    elif msg[1:6] == 'снять':
                        if ans is not False:
                            if ans.stat == 'админ':
                                if cru.uid in getadmins(gid):
                                    streg(gid, ans.uid, 'пользователь')
                                    sender(gid, f"{ans.name} {ans.sname} больше не админ")
                                else:
                                    sender(gid, 'Разбирайтесь со своими проблемами сами, или позовите главного админа')
                            else:
                                sender(gid, f"Куда ему падать еще ниже?")
                        else:
                            sender(gid, 'Кого снимать-то? Напишите вашу команду в ответ на сообщение провинившегося')
                    elif msg[1:10] == 'за работу':
                        sender(gid, 'Не стройте из себя дурака, у меня уже есть ваша карточка!')
                    elif msg[1:5] == 'ключ':
                        if msg[6:11] == 'слово':
                            word = msg[11:].replace(' ', '')
                            lst = forbidden
                            if len(lst) > 0:
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
                        elif msg[6:11] == "преды":
                            try:
                                a = int(msg.split(' ')[-1])
                                if a > 0:
                                    cpreg(a, gid)
                                    sender(gid, f'Максимальное количество предупреждений: {a}')
                                else:
                                    sender(gid, 'Лучше введите число больше нуля')
                            except ValueError:
                                sender(gid, 'Введите чило пожалуйста')
                    elif msg[1:2] == '-':
                        try:
                            eraser(gid, event.object.message['reply_message']['conversation_message_id'])
                        except exceptions.ApiError:
                            sender(gid, 'Прости, я не могу удалить это сообщение')
                    elif msg[1:4] == 'мут':
                        if ans is not False:
                            mes = msg.split(' ')
                            time = False
                            print(mes)
                            if len(mes) == 3:
                                if 'ч' in mes[-1]:
                                    time = timedelta(hours=int(mes[1]))
                                elif 'м' in mes[-1]:
                                    time = timedelta(minutes=int(mes[1]))
                                elif 'д' in mes[-1]:
                                    time = timedelta(days=int(mes[1]))
                                else:
                                    sender(gid, 'Уточните время, будьте добры')
                            else:
                                sender(gid, 'Можно пожалуйста по подробнее')
                            if time is False:
                                pass
                            else:
                                streg(gid, ans.uid, f'мут:{(datetime.now() + time).strftime("%Y-%m-%d %H:%M:%S")}')
                                sender(gid,
                                       f'{ans.name} {ans.sname} теперь в муте '
                                       f'до {(datetime.now() + time).strftime("%Y-%m-%d %H:%M:%S")}')
                        else:
                            sender(gid, 'Кого мутить-то? Напишите вашу команду в ответ на сообщение этого болтуна')
                    elif msg[1:6] == 'пред-':
                        if ans is not False:
                            if ans.stat == 'админ':
                                if cru.uid in getadmins(gid):
                                    try:
                                        preg(gid, ans.uid, '-')
                                        if ans.pred > 0:
                                            sender(gid,
                                                   f'Предупреждения: {ans.name} {ans.sname} теперь '
                                                   f'имеет {ans.pred - 1}.')
                                        else:
                                            sender(gid, f'Предупреждения: {ans.name} {ans.sname} теперь имеет 0.')
                                    except exceptions.ApiError:
                                        sender(gid, 'Меня-то?')
                                else:
                                    sender(gid, 'Кто тут кого предупреждает?')
                            else:
                                try:
                                    preg(gid, ans.uid, '-')
                                    if ans.pred > 0:
                                        sender(gid,
                                               f'Предупреждения: {ans.name} {ans.sname} теперь имеет {ans.pred - 1}.')
                                    else:
                                        sender(gid, f'Предупреждения: {ans.name} {ans.sname} теперь имеет 0.')
                                except exceptions.ApiError:
                                    sender(gid, 'Меня-то?')

                        else:
                            sender(gid, 'Кого прощать-то? Напишите вашу команду в ответ на сообщение этого бедолагу')
                    elif msg[1:6] == 'пред+' or msg[1:5] == 'пред':
                        if ans is not False:
                            if ans.stat == 'админ':
                                if cru.uid in getadmins(gid):
                                    try:
                                        preg(gid, ans.uid, '+')
                                        if ans.pred + 1 >= cgr.pred:
                                            db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                             users.User.groupid == gid).delete()
                                            db_sess.commit()
                                            vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid)
                                            sender(gid, 'Вот, что бывает с нарушителями')
                                        else:
                                            sender(gid,
                                                   f'Предупреждения: {ans.name} {ans.sname} теперь '
                                                   f'имеет {ans.pred + 1}. \n Если он получит {cgr.pred}, мне '
                                                   f'придется его выгнать')
                                    except exceptions.ApiError:
                                        sender(gid, 'Меня-то?')
                                else:
                                    sender(gid, 'Кто тут кого предупреждает?')
                            else:
                                try:
                                    preg(gid, ans.uid, '+')
                                    print(ans.pred, cgr.pred)
                                    if ans.pred + 1 >= cgr.pred:
                                        db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                         users.User.groupid == gid).delete()
                                        db_sess.commit()
                                        vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid)
                                        sender(gid, 'Вот, что бывает с нарушителями')
                                    else:
                                        sender(gid,
                                               f'Предупреждения: {ans.name} {ans.sname} теперь имеет {ans.pred + 1}. \n '
                                               f'Если он получит {cgr.pred}, мне придется его выгнать')
                                except exceptions.ApiError:
                                    sender(gid, 'Меня-то?')

                        else:
                            sender(gid,
                                   'Кого предупреждать-то? Напишите вашу команду в ответ на сообщение этого нарушителя')
                    elif msg[1:7] == 'размут':
                        if ans is not False:
                            if ans.stat[:3] == 'мут':
                                streg(gid, ans.uid, f'пользователь')
                                sender(gid, f'{ans.name} {ans.sname} больше не в муте')
                            else:
                                sender(gid, f'Он и так не из молчеливых')
                        else:
                            sender(gid, 'Кого размутить-то? Напишите вашу команду в ответ на сообщение этого молчуна')
                    elif msg[1:12] == 'всепрощение':
                        members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
                        for i in members:
                            try:
                                preg(gid, i['member_id'], 0)
                            except AttributeError:
                                pass
                        sender(gid, 'Все предупреждения сняты')
                    else:
                        sender(gid, 'А где комманда? вот тебе список, не волнуйся ##тут будет ссылка на html список##')
                elif msg[0] == '!' and cru.stat != 'админ':
                    sender(gid, 'А команды могут использовать только админы, дружище')
                elif msg in forbidden:
                    try:
                        eraser(gid, event.object.message['conversation_message_id'])
                    except exceptions.ApiError:
                        pass
                elif keylinks == 1:
                    if 'https://' in msg or 'http://' in msg or any(list(map(lambda x: x in msg, DOMENS))):
                        try:
                            eraser(gid, event.object.message['conversation_message_id'])
                        except exceptions.ApiError:
                            pass
            elif msg == '!за работу':
                try:
                    if db_sess.query(group.Group).filter(
                            group.Group.groupid == str(gid)).first() is None and -219582896 in getadmins(gid):
                        greg(gid, True)
                    members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
                    for i in members:
                        if i['member_id'] in getadmins(gid):
                            try:
                                a = vk.users.get(user_id=i['member_id'])[0]
                                ureg(a, gid, 'админ')
                                sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                            except IndexError:
                                pass
                        else:
                            try:
                                a = vk.users.get(user_id=i['member_id'])[0]
                                ureg(a, gid, 'пользователь')
                            except IndexError:
                                pass
                    sender(gid, 'Регистрация окончена')
                except exceptions.ApiError:
                    sender(gid,
                           'Товарищ, похоже эта беседа не зарегистрирована!\nЧтобы зарегистрировать беседу '
                           'предоставьте боту права администратора, доступ ко всей переписке и напишите команду '
                           '"!За работу"')
            elif len(msg) == 0:
                pass
            else:
                sender(gid,
                       'Товарищ, похоже эта беседа не зарегистрирована!\nЧтобы зарегистрировать беседу предоставьте '
                       'боту права администратора, доступ ко всей переписке и напишите команду "!За работу"')
