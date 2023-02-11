from subprocess import Popen


class Requisicoes:
    def __init__(self, dbname, file, userid, nome, type, folder=None):
        self.dbname = dbname
        self.file = file
        self.userid = userid
        self.nome = nome
        self.type = type
        self.p = None
        self.status = 'IN QUEUE'
        self.oid = None
        self.folder = folder

    def setp(self, pid):
        self.p = pid

    def setstatus(self, status):
        self.status = status

    def setoid(self, oid):
        self.oid = oid
