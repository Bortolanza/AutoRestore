from requisicoes import Requisicoes
from threading import Thread, Lock
from dbconn import Connection
from datetime import datetime

global conn
global requests_list
global addlistlock
global rmvlistlock
global runningthread
global userstats
global lastgetuserstats

conn = Connection("postgres", "postgres", "172.17.0.2", "5432", "postgres")
requests_list = []
addlistlock = Lock()
rmvlistlock = Lock()
runningthread = Lock()
ongoingthread = Thread()
userstats = None
lastgetuserstats = datetime.now()
