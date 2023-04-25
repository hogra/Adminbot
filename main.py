from datetime import datetime, timedelta

from vk_api import exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from current_group import CurGroup
from current_user import CurUser
from tools import *

print('Начинаю работу')
for event in VkBotLongPoll(vk_session, 219582896).listen(): # Бот отслеживает лонгпол
    gid = event.chat_id # ID чата относительно бота
    print('Событие в чате', gid)
    if event.type == VkBotEventType.MESSAGE_NEW:
        # Если бот получает сообщение (т.е. если в каком-либо из чатов новое сообщение)
        if event.from_chat:
            msg = event.object.message['text'].lower() # Он сохраняет текст сообщения
            a = False # Временная переменная, в которую я сохраняю запросы в вк
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None:
                # Если чат есть в базе данных:
                cgr = CurGroup(gid) # Сохраняю параметры данного чата
                forbidden = cgr.forbidden # Лист запрещенных слов
                keylinks = cgr.links # Флаг ссылок
                try:
                    if event.object['message']['action']['type'] == 'chat_invite_user': # Если в чате новый участник
                        print('     Новый участник')
                        sender(gid, cgr.greet) # Отправляет приветственное сообщение
                        a = vk.users.get(user_id=event.object['message']['action']['member_id'])
                        try:
                            ureg(a[0], gid, 'пользователь') # Регистрирует пользователя в базу
                        except IndexError: # Если это не бот
                            pass # Тогда - не регистрирует
                except TypeError:
                    pass
                except KeyError:
                    pass
            if db_sess.query(group.Group).filter(group.Group.groupid == str(gid)).first() is not None and len(msg) > 0:
                # Если сообщение является текстом:
                cru = CurUser(event.object.message['from_id'], gid) # Сохраняю параметры отправителя (того, кто пишет)
                print(f'    Новое сообщение от пользователя {cru.name} {cru.sname}: {msg}')
                try:
                    ans = CurUser(event.object.message['reply_message']['from_id'], gid)
                    # И сохраняю параметры получателя (того, кому пишут), если таковой имеется
                except KeyError:
                    ans = False # Иначе - не сохраняю
                if cru.stat[:3] == 'мут': # Если отправитель в муте
                    if datetime.strptime(cru.stat[4:], '%Y-%m-%d %H:%M:%S') <= datetime.now(): # Если время мута истекло
                        streg(gid, cru.uid, 'пользователь')  # Отправителю снова присваивается статус "пользователь"
                        print(f'    Срок мута пользователя {cru.name, cru.sname} окончен')
                    else: # Если не истекло
                        eraser(gid, event.object.message['conversation_message_id']) # удаляю сообщение
                        print(f'    Пользователь {cru.name, cru.sname} пишет сообщение "{msg}", находясь в муте')
                if msg[0] == '!' and cru.stat == 'админ':
                    # Команды начинаются с "!". Только админы могут использовать команды
                    if msg[1:6] == 'админ': # Команда "админ"
                        if ans is not False: # Если есть получатель
                            streg(gid, ans.uid, 'админ') # Он назначается админом
                            sender(gid, f"{ans.name} {ans.sname} назначен админом")
                        else:
                            sender(gid,
                                   'Кого назначать-то? Напишите вашу команду в ответ на сообщение этого ответственного '
                                   'господина')
                    elif msg[1:4] == 'кик': # Команда "кик"
                        if ans is not False:
                            if ans.stat == 'админ': # Если получатель - админ
                                if cru.uid in getadmins(gid): # Проверяется, является ли отправитель организатором
                                    try:
                                        print(f'    Пользователь {ans.name} {ans.sname} кикнут из чата')
                                        db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                         users.User.groupid == gid).delete()
                                        # Пользователь удаляется из базы данных
                                        db_sess.commit()
                                        vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid) # И удаляется из чата
                                        sender(gid, 'Готово, этого парня вы больше не встретите')
                                    except exceptions.ApiError:
                                        sender(gid, 'Хара-кири?') # А бота кикнуть нельзя
                                else:
                                    sender(gid, 'Это как вы хотите кикнуть админа?') # Как и админа
                            else: # Если получатель не админ - проблем нет
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
                    elif msg[1:6] == 'снять': # Команда "снять"
                        if ans is not False:
                            if ans.stat == 'админ': # Если получатель - админ
                                if cru.uid in getadmins(gid): # И отправитель - организатор
                                    streg(gid, ans.uid, 'пользователь') # Получатель - снова пользователь
                                    sender(gid, f"{ans.name} {ans.sname} больше не админ")
                                else:
                                    sender(gid, 'Разбирайтесь со своими проблемами сами, или позовите главного админа')
                            else:
                                sender(gid, f"Куда ему падать еще ниже?")
                        else:
                            sender(gid, 'Кого снимать-то? Напишите вашу команду в ответ на сообщение провинившегося')
                    elif msg[1:10] == 'за работу': # Об этом будет ниже
                        sender(gid, 'Не стройте из себя дурака, у меня уже есть ваша карточка!')
                    elif msg[1:5] == 'ключ': # Ключи позволяют изменить настройки чата
                        if msg[6:11] == 'слово': # Добавление запрещенного слова
                            word = msg[11:].replace(' ', '')
                            lst = forbidden
                            if len(lst) > 0: # Если запрещенные слова уже есть
                                if word in lst: # И указанное слово есть в списке
                                    lst.remove(word) # Оно убирается из него
                                    sender(gid, f'Я убрал слово {word} из списка запрещенных слов')
                                else:
                                    lst.append(word) # Иначе - добавляется
                                    sender(gid, f'Я добавил слово {word} в список запрещенных слов')
                            else:
                                lst = [word]
                                sender(gid, f'Я добавил слово {word} в список запрещенных слов')
                            wreg(','.join(lst), gid)
                        elif msg[6:12] == 'ссылки': # Запрет ссылок
                            if keylinks == 1: # Если ссылки запрещены
                                lreg(0, gid)
                                sender(gid, 'Ссылки теперь разрешены') # Они разрешаются
                            else: # И наоборот
                                lreg(1, gid)
                                sender(gid, 'Ссылки теперь запрещены')
                        elif msg[6:17] == 'приветствие': # Приветственное сообщение
                            a = msg[18:]
                            if a != '':
                                grreg(a, gid)
                                sender(gid, 'Приветственное сообщение изменено')
                            else:
                                sender(gid, 'Я слишком вежлив, чтобы не здороваться с новичками')
                        elif msg[6:11] == "преды": # Допустимое количество предупреждений
                            try:
                                a = int(msg.split(' ')[-1])
                                if a > 0:
                                    cpreg(a, gid)
                                    sender(gid, f'Максимальное количество предупреждений: {a}')
                                else:
                                    sender(gid, 'Лучше введите число больше нуля')
                            except ValueError:
                                sender(gid, 'Введите чило пожалуйста')
                    elif msg[1:2] == '-': # Обратно к командам - удаление сообщения
                        try:
                            eraser(gid, event.object.message['reply_message']['conversation_message_id'])
                        except exceptions.ApiError:
                            sender(gid, 'Прости, я не могу удалить это сообщение')
                    elif msg[1:4] == 'мут': # Мут
                        if ans is not False: # Мут и его время ставится в статус, как он работает описывалось выше
                            mes = msg.split(' ')
                            time = False
                            print(mes)
                            if len(mes) == 3:
                                if 'ч' in mes[-1]:
                                    time = timedelta(hours=int(mes[1])) # Можно дать мут на часы
                                elif 'м' in mes[-1]:
                                    time = timedelta(minutes=int(mes[1])) # Минуты
                                elif 'д' in mes[-1]:
                                    time = timedelta(days=int(mes[1])) # Или дни
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
                    elif msg[1:6] == 'пред-': # Преды. Преды можно снимать
                        if ans is not False:
                            if ans.stat == 'админ': # Если отправитель - админ
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
                    elif msg[1:6] == 'пред+' or msg[1:5] == 'пред': # Или давать
                        if ans is not False:
                            if ans.stat == 'админ':
                                if cru.uid in getadmins(gid):
                                    try:
                                        preg(gid, ans.uid, '+')
                                        if ans.pred + 1 >= cgr.pred:
                                            # При достижении максимального количества предов, пользователя кикает
                                            print(f'    Пользователь {cru.name, cru.sname} был кикнут из-за достижения '
                                                  f'максимального количества предупреждений')
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
                                        print(f'    Пользователь {cru.name, cru.sname} был кикнут из-за достижения '
                                              f'максимального количества предупреждений')
                                        db_sess.query(users.User).filter(users.User.userid == ans.uid,
                                                                         users.User.groupid == gid).delete()
                                        db_sess.commit()
                                        vk.messages.removeChatUser(chat_id=gid, user_id=ans.uid)
                                        sender(gid, 'Вот, что бывает с нарушителями')
                                    else:
                                        sender(gid,
                                               f'Предупреждения: {ans.name} {ans.sname} '
                                               f'теперь имеет {ans.pred + 1}. \n Если он получит {cgr.pred}, '
                                               f'мне придется его выгнать')
                                except exceptions.ApiError:
                                    sender(gid, 'Меня-то?')

                        else:
                            sender(gid,
                                   'Кого предупреждать-то? Напишите вашу команду в ответ на сообщение этого нарушителя')
                    elif msg[1:7] == 'размут': # Из мута можно вывести
                        if ans is not False:
                            if ans.stat[:3] == 'мут':
                                streg(gid, ans.uid, f'пользователь')
                                sender(gid, f'{ans.name} {ans.sname} больше не в муте')
                            else:
                                sender(gid, f'Он и так не из молчеливых')
                        else:
                            sender(gid, 'Кого размутить-то? Напишите вашу команду в ответ на сообщение этого молчуна')
                    elif msg[1:12] == 'всепрощение': # И снять преды со всех пользователей
                        members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
                        for i in members:
                            try:
                                preg(gid, i['member_id'], 0)
                            except AttributeError:
                                pass
                        sender(gid, 'Все предупреждения сняты')
                    else: # Если пользователь ввел команду, которой не существует, бот направит его в список команд
                        sender(gid, 'А где комманда? вот тебе список, не волнуйся ##тут будет ссылка на html список##')
                elif msg[0] == '!' and cru.stat != 'админ':
                    sender(gid, 'А команды могут использовать только админы, дружище')
                elif msg in forbidden and cru.stat != 'админ': # Если в сообщении есть запрещенное слово
                    try:
                        eraser(gid, event.object.message['conversation_message_id']) # Оно удаляется
                    except exceptions.ApiError: # Если это не организатор
                        pass
                elif keylinks == 1 and cru.stat != 'админ':
                    if 'https://' in msg or 'http://' in msg or any(list(map(lambda x: x in msg,
                                                                             ['.com', '.edu', '.fun', '.gov', '.info',
                                                                              '.net', '.org', '.xxx', '.dev', '.ai',
                                                                              '.au', '.az', '.cz', '.eu', '.gg', '.ru',
                                                                              '.рф', '.su']))):
                        # Если в сообщении есть ссылки (проверяются по доменам)
                        try: # Он тоже стирается
                            eraser(gid, event.object.message['conversation_message_id'])
                        except exceptions.ApiError:
                            pass
            elif msg == '!за работу': # Если чата нет в базе данных, его нужно ввести этой командой
                try:
                    if db_sess.query(group.Group).filter(
                            group.Group.groupid == str(gid)).first() is None and -219582896 in getadmins(gid):
                        # Перед регистрацией проверяется, назначен ли бот админом
                        greg(gid, True) # Если да - группа регистрируется в бд
                    members = vk.messages.getConversationMembers(peer_id=2000000000 + gid)['items']
                    for i in members: # Бот проходит по всем участникам
                        if i['member_id'] in getadmins(gid): # Если участник - организатор, он вносится как админом
                            try:
                                a = vk.users.get(user_id=i['member_id'])[0]
                                ureg(a, gid, 'админ')
                                sender(gid, f"{a['first_name']} {a['last_name']} назначен админом")
                            except IndexError:
                                pass
                        else: # Иначе - как участник
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
