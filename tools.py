from vk_api import VkApi

from data import db_session
from data import group
from data import users

TOK = 'vk1.a.PjWas5ZQVRqq08J7YC8pC_AP6N8Fix4r1WYL48t5Df6B3fc2n8NWnx7AgzsABGYS0a1n-SG0y83sHVcGT0G8WAuUq7ReauMYA79bIN58Q0oI8q0WDBOPaCclOd7JP3YMKf6EV1eH5U0vxasKSGToVrgRVp-7XOjM9_brPN3pGDCeCwrJl_edSM57JKfGkhdNSbMH-ExcQyjnuzNXRgL_gQ'
vk_session = VkApi(token=TOK)
vk = vk_session.get_api()
db_session.global_init("db/users.db")
db_session.global_init("db/group.db")
db_sess = db_session.create_session()


def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


def eraser(gid, mid):
    vk_session.method('messages.delete',
                      {'peer_id': 2000000000 + gid, 'delete_for_all': 1, 'cmids': mid, 'random_id': 0})


def preg(gid, uid, key):
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


def cpreg(a, gid):
    db_sess = db_session.create_session()
    g = db_sess.query(group.Group).filter(group.Group.groupid == gid).first()
    g.pred = a
    db_sess.commit()


def greg(gid, works):
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
