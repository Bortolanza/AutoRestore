from dboperations import setusersbase, resetop
from requisicoes import Requisicoes
from dbinfo import getbaseoid
from threading import Thread
import subprocess
import globals
import re

errormatch = re.compile("ERROR")
donematch = re.compile("DONE.*")
killedmatch = re.compile("KILLED")
noproblem = re.compile("errors ignored on restore")
noprocess = re.compile("No such process|Illegal number")
# docpath = '/home/enzo/Desktop/restore-14/restore-14/venv/'
docpath = '/app/venv/'


def getdiskspace():
    getdiskspaceprocess = subprocess.Popen([docpath+'getdiskspace.sh'],
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
    out, error = getdiskspaceprocess.communicate()
    if len(error) > 1:
        return 'ERROR'
    string = out.decode("utf-8")
    for x in string.split('\n'):
        x = re.sub("( )+", ' ', str(x))
        arr = x.split(' ')
        if re.findall("/dev/sda2", arr[0]):
            return arr[3]


def getfiles():
    arr = []
    getfilesprocess = subprocess.Popen([docpath+'getfiles.sh'],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    out, error = getfilesprocess.communicate()
    if len(error) > 1:
        raise Exception('Pedir para o Cleimor ajustar a montagem da pasta')
    string = out.decode("utf-8")
    string = string.split('\n')
    for x in string:
        if re.findall("\\.backup|\\.bin", x):
            arr.append(x)
    return arr


def checkcopy():
    checkcopyprocess = subprocess.Popen([docpath+'checkcopy.sh'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    out, error = checkcopyprocess.communicate()
    globals.requests_list[0].setstatus('CHECKING COPY')
    if len(error) > 1:
        raise Exception(error)
    arr = (out.decode('utf-8')).strip().split("\n")
    for x in arr:
        if globals.requests_list[0].file == x:
            return True
    globals.requests_list[0].setstatus('DONE CHEKING')
    checkcopyprocess.kill()
    return False


def cleanfolder():
    getbackupsprocess = subprocess.Popen([docpath+'getbackups.sh'],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
    out, error = getbackupsprocess.communicate()
    if len(error) > 1:
        raise Exception(error)
    arr = (out.decode('utf-8')).strip().split("\n")
    if len(arr) > 5:
        cleanfolderprocess = subprocess.Popen([docpath+'cleanfolder.sh',
                                              arr[-1]],
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
        out, error = cleanfolderprocess.communicate()
        if len(error) > 1:
            raise Exception(error)
    return


def copyfile():
    copyfileprocess = subprocess.Popen([docpath+'copybase.sh',
                                       globals.requests_list[0].file],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    globals.requests_list[0].setp(copyfileprocess.pid)
    globals.requests_list[0].setstatus('COPYING')
    out, error = copyfileprocess.communicate()
    if len(error) > 0:
        raise Exception(error)
    cleanfolder()
    globals.requests_list[0].setstatus('DONE COPYING')
    return


def createbase():
    createprocess = subprocess.Popen([docpath+'createbase.sh',
                                     globals.requests_list[0].dbname,
                                     # globals.requests_list[0].user
                                     ],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    globals.requests_list[0].setp(createprocess.pid)
    globals.requests_list[0].setstatus('CREATING')
    out, error = createprocess.communicate()
    if len(error) > 0:
        globals.requests_list[0].setstatus(error.decode("utf-8"))
    else:
        globals.requests_list[0].setstatus('DONE CREATING')
    return


def restorebase():
    restoreprocess = subprocess.Popen([docpath+'restorebase.sh',
                                      globals.requests_list[0].file,
                                      globals.requests_list[0].dbname],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    globals.requests_list[0].setp(restoreprocess.pid)
    globals.requests_list[0].setstatus('RESTORING')
    out, error = restoreprocess.communicate()
    if len(error) > 0 and noproblem.search(error.decode('utf8')) is None:
        raise Exception(error)
    globals.requests_list[0].setstatus('DONE RESTORING')
    restoreprocess.kill()
    return


def dropbase():
    dropprocess = subprocess.Popen([docpath+'dropbase.sh',
                                   globals.requests_list[0].dbname],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    globals.requests_list[0].setp(dropprocess.pid)
    globals.requests_list[0].setstatus('DROPPING')
    out, error = dropprocess.communicate()
    if len(error) > 0:
        raise Exception(error)
    else:
        globals.requests_list[0].setstatus('DONE DROPPING')
    return

def getdumpfolders():
    getdumpfoldersprocess = subprocess.Popen([docpath+'getdumpdirections.sh'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    out, error = getdumpfoldersprocess.communicate()
    if len(error) > 0:
        raise Exception(error)
    string = out.decode("utf-8").strip()
    arr = string.split('\n')
    return arr


def dumpbase():
    dumpbaseprocess = subprocess.Popen([docpath+'dumpbase.sh',
                                       globals.requests_list[0].dbname,
                                       globals.requests_list[0].file,
                                       globals.requests_list[0].folder],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    globals.requests_list[0].setp(dumpbaseprocess.pid)
    globals.requests_list[0].setstatus('DUMPING')
    out, error = dumpbaseprocess.communicate()
    if len(error) > 0:
        raise Exception(error)
    globals.requests_list[0].setstatus('DONE DUMPING')
    return

def waitforprocess(nomeprocesso):
    while True or len(globals.requests_list) > 0:
        if killedmatch.search(globals.requests_list[0].status) is not None:
            return
        if errormatch.search(globals.requests_list[0].status) is not None:
            raise Exception("Processo %s falhou" % nomeprocesso)
        if donematch.search(globals.requests_list[0].status) is not None:
            return True


def requestrestore():
    try:
        if not checkcopy():
            copyfile()
            waitforprocess("copyfile")
        createbase()
        waitforprocess("createbase")
        globals.requests_list[0].setoid(getbaseoid(globals.conn, globals.requests_list[0].dbname)[0][0])
        setusersbase(globals.conn, globals.requests_list[0].oid, "RESTORING", globals.requests_list[0].userid)
        restorebase()
        waitforprocess("restorebase")
    except Exception as error:
        if error == "Processo restorebase falhou":
            requestdrop()
            return
        raise error
    else:
        setusersbase(globals.conn, globals.requests_list[0].oid, "RESTORED", globals.requests_list[0].userid)


def requestdrop():
    try:
        dropbase()
        waitforprocess("dropbase")
    except Exception as error:
        resetop(globals.conn, globals.requests_list[0].oid, "RESTORED")
        raise error
    else:
        return

def requestdump():
    try:
        dumpbase()
        waitforprocess("requestdump")
    except Exception as error:
        raise error
    else:
        return



def databasethread():
    globals.runningthread.acquire()
    while len(globals.requests_list) > 0:
        if globals.requests_list[0].type == 'RESTORE':
            requestrestore()
        elif globals.requests_list[0].type == 'DROP':
            requestdrop()
        elif globals.requests_list[0].type == 'DUMP':
            requestdump()
        globals.rmvlistlock.acquire()
        globals.requests_list.pop(0)
        globals.rmvlistlock.release()
    globals.runningthread.release()
    globals.ongoingthread = None


def startdatabasethread():
    ongoingthread = Thread(target=databasethread)
    ongoingthread.start()


def killprocess(pid):
    getfilesprocess = subprocess.Popen([docpath+'killprocess.sh',
                                       pid],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    out, error = getfilesprocess.communicate()
    if globals.requests_list[0].p == pid:
        globals.requests_list[0].status = "KILLED"
    if len(error) > 1:
        if noprocess.search(error.decode('utf8')) is not None:
            return False
        raise Exception(error.decode('utf8'))
    return True
