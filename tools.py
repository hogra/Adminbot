from vk_api import VkApi

from data import db_session
from data import group
from data import users
from datetime import datetime

TOK = 'vk1.a.PjWas5ZQVRqq08J7YC8pC_AP6N8Fix4r1WYL48t5Df6B3fc2n8NWnx7AgzsABGYS0a1n-SG0y83sHVcGT0G8WAuUq7ReauMYA79bIN58Q0oI8q0WDBOPaCclOd7JP3YMKf6EV1eH5U0vxasKSGToVrgRVp-7XOjM9_brPN3pGDCeCwrJl_edSM57JKfGkhdNSbMH-ExcQyjnuzNXRgL_gQ'
vk_session = VkApi(token=TOK)
vk = vk_session.get_api()
db_session.global_init("db/users.db")
db_session.global_init("db/group.db")
db_sess = db_session.create_session()

# Модуль с константами и функциями бота

def sender(id, text): # Отправление сообщения в чат
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


def eraser(gid, mid): # Удаление сообщения из чата
    vk_session.method('messages.delete',
                      {'peer_id': 2000000000 + gid, 'delete_for_all': 1, 'cmids': mid, 'random_id': 0})


def preg(gid, uid, key): # Регистрация предупреждения
    db_sess = db_session.create_session()
    u = db_sess.query(users.User).filter(users.User.groupid == gid, users.User.userid == uid).first()
    if key == '+':
        u.pred += 1
    elif key == 0:
        u.pred = 0
    elif key == '-':
        if u.pred > 0:
            u.pred -= 1
    db_sess.commit()


def cpreg(a, gid): # Регистрация максимального допустимого количества предупреждений
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.pred = a
    db_sess.commit()


def greg(gid, works): # Регистрация группы
    g = group.Group()
    g.groupid = gid
    g.works = works
    db_sess = db_session.create_session()
    db_sess.add(g)
    db_sess.commit()
    print(f'Группа {gid} зарегистрирована')


def grreg(a, gid): # Регистрация приветственного сообщения
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.greet = a
    db_sess.commit()


def ureg(a, gid, status): # Регистрация участника
    u = users.User()
    u.userid = a['id']
    u.groupid = gid
    u.surname = a['last_name']
    u.name = a['first_name']
    u.date = (datetime.now()).strftime("%d.%m.%Y")
    u.status = status
    db_sess.add(u)
    db_sess.commit()
    print(f'    Пользователь {u.surname} {u.name} был внесен в базу данных, как {status}')


def wreg(a, gid): # Регистрация запрещенного слова
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.words = a
    db_sess.commit()


def streg(gid, uid, a): # Регистрация статуса
    db_sess = db_session.create_session()
    u = db_sess.query(users.User).filter(users.User.groupid == gid, users.User.userid == uid).first()
    u.status = a
    db_sess.commit()
    print(f'    Статус пользователя {u.surname} {u.name} изменен на "{u.status}"')


def lreg(a, gid): # Регистрация флага ссылок
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.links = a
    db_sess.commit()

def ssyms(gid, uid, n):
    db_sess = db_session.create_session()
    u = db_sess.query(users.User).filter(users.User.groupid == gid, users.User.userid == uid).first()
    u.symbols += n
    db_sess.commit()




def getadmins(gid): # Получение всех организаторов чата
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
