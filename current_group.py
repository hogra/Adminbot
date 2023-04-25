from tools import db_sess, group

# Класс чата

class CurGroup:
    def __init__(self, gid):
        self.gid = gid
        forbidden = db_sess.query(group.Group.words).filter(group.Group.groupid == gid).first()[0]
        if forbidden is not None:
            self.forbidden = db_sess.query(group.Group.words).filter(group.Group.groupid == gid).first()[0].split(',')
        else:
            self.forbidden = []
        self.pred = db_sess.query(group.Group.pred).filter(group.Group.groupid == gid).first()[0]
        self.greet = db_sess.query(group.Group.greet).filter(group.Group.groupid == gid).first()[0]
        self.links = db_sess.query(group.Group.links).filter(group.Group.groupid == gid).first()[0]
