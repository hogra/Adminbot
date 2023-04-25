from tools import vk, db_sess, users

# Класс пользователя

class CurUser:
    def __init__(self, uid, gid):
        self.uid = uid
        self.gid = gid
        a = vk.users.get(user_id=uid)[0]
        self.name = a['first_name']
        self.sname = a['last_name']
        self.stat = db_sess.query(users.User.status).filter(users.User.userid == uid, users.User.groupid == gid).first()[0]
        self.pred = db_sess.query(users.User.pred).filter(users.User.userid == uid, users.User.groupid == gid).first()[0]
        self.date = db_sess.query(users.User.date).filter(users.User.userid == uid, users.User.groupid == gid).first()[0]
        self.sym = db_sess.query(users.User.symbols).filter(users.User.userid == uid, users.User.groupid == gid).first()[0]
