from dbinfo import getuserstats, getuserbases, getbaseoid, getuserhistory, getallbases, getuser, getfunctionalities, getfunctionalitiesperiods, checkperiods
from osfunctions import getdiskspace, getfiles, startdatabasethread, killprocess, dropbase as osdropbase, getdumpfolders
from flask import Flask, render_template, send_file, request, redirect, Response, url_for, session
from dboperations import updinfodelbase, newperiod, removeperiod
from sessioncheks import checksessioninfo
from flask_bootstrap import Bootstrap5
from requisicoes import Requisicoes
from flask_session import Session
from dbconn import Connection
from datetime import datetime
import globals
import time
import ast


try:
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    app.secret_key = 'ifoeflefkergier'
except Exception as error:
    raise Exception(error)
else:
    @app.route('/')
    def index():
        if 'userid' not in session or not checksessioninfo(session['userid']):
            session['userid'] = None
            return render_template('index.html', login=request.args.get('login'))
        return redirect('/home')


    @app.route('/favicon.ico')
    def icon():
        return send_file('static/images/icon.png')


    @app.post('/login')
    def login():
        user = getuser(globals.conn, request.form['username'], request.form['pword'])
        if len(user) != 1:
            return redirect(url_for('index', login='failed'))
        session['userid'] = user[0][0]
        session['nome'] = user[0][1]
        session['privilege'] = user[0][2]
        return redirect('/home')


    @app.route('/home')
    def home():
        if 'userid' not in session or not checksessioninfo(session['userid']):
            return redirect('/')
        else:
            if globals.userstats is None or (datetime.now() - globals.lastgetuserstats).seconds > 300:
                globals.lastgetuserstats = datetime.now()
                globals.userstats = getuserstats(globals.conn)
            return render_template('home.html',
                                   nome_usuario=session['nome'],
                                   disk_space=getdiskspace(),
                                   userstatslen=len(globals.userstats),
                                   userstats=globals.userstats,
                                   privilege=session['privilege'])


    @app.route('/subirbase')
    def subirbase():
        if 'userid' not in session or not checksessioninfo(session['userid']) or not (checkperiods(globals.conn, 1)):
            return redirect('/')
        else:
            try:
                filelist = getfiles()
            except Exception as err:
                print(err)
                return redirect('404')
            return render_template('subirbase.html',
                                   nome_usuario=session['nome'],
                                   disk_space=getdiskspace(),
                                   bases_avaliable=filelist,
                                   requestrepeat=request.args.get('requestrepeat'),
                                   privilege=session['privilege'])


    @app.post('/subir')
    def subir():
        if not (checkperiods(globals.conn, 1)):
            return redirect(url_for('home'))
        skip = 0
        requisitado = Requisicoes(request.form['dbname'], request.form['file'], session['userid'], session['nome'], "RESTORE", None)
        for x in globals.requests_list:
            if requisitado.dbname == x.dbname:
                skip = 1
                break
        if not skip:
            globals.addlistlock.acquire()
            globals.requests_list.append(requisitado)
            globals.addlistlock.release()
            if not globals.runningthread.locked():
                startdatabasethread()
            return redirect(url_for('subirbase', requestrepeat=0))
        return redirect(url_for('subirbase', requestrepeat=1))


    @app.route('/dumpbase')
    def dumpbase():
        if 'userid' not in session or not checksessioninfo(session['userid']) or not (checkperiods(globals.conn, 2)):
            return redirect('/')
        else:
            try:
                baselist = getallbases(globals.conn)
                lenbaselist = len(baselist)
            except Exception as err:
                print(err)
                return redirect('404')
            return render_template('dumpbase.html',
                                   nome_usuario=session['nome'],
                                   disk_space=getdiskspace(),
                                   lenbaselist = lenbaselist,
                                   bases_avaliable=baselist,
                                   folders_avaliable=getdumpfolders(),
                                   requestrepeat=request.args.get('requestrepeat'),
                                   privilege=session['privilege'])


    @app.post('/dump')
    def dump():
        if not checkperiods(globals.conn, 2):
            return redirect(url_for('home'))
        requisitado = Requisicoes(request.form['dumpname'], request.form['file'], session['userid'], session['nome'], "DUMP", request.form['directory'])
        globals.addlistlock.acquire(timeout=3)
        if globals.addlistlock.locked():
            globals.requests_list.append(requisitado)
            globals.addlistlock.release()
        else:
            return redirect(url_for('dumpbase', requestrepeat=1))
        if not globals.runningthread.locked():
            startdatabasethread()
        return redirect(url_for('dumpbase', requestrepeat=0))




    @app.route('/historico')
    def historico():
        if 'userid' not in session or not checksessioninfo(session['userid']):
            return redirect('/')
        else:
            userstats = getuserhistory(globals.conn, session['userid'])
            return render_template('historico.html',
                                   nome_usuario=session['nome'],
                                   disk_space=getdiskspace(),
                                   userstatslen=len(userstats),
                                   userstats=userstats,
                                   privilege=session['privilege'])

    @app.route('/minhasbases')
    def minhasbases():
        if 'userid' not in session or not checksessioninfo(session['userid']):
            return redirect('/')
        else:
            listaprocesso = []
            userstats = getuserbases(globals.conn, session['userid'])
            for x in globals.requests_list:
                if x.userid == session['userid']:
                    listaprocesso.append(x)
            return render_template('minhasbases.html',
                                   nome_usuario=session['nome'],
                                   disk_space=getdiskspace(),
                                   userstatslen=len(userstats),
                                   userstats=userstats,
                                   listaprocesso=listaprocesso,
                                   listaprocessolen=len(listaprocesso),
                                   privilege=session['privilege'])


    @app.post('/dropbase')
    def dropbase():
        requisitado = Requisicoes(request.form['dropbase'], None, session['userid'], session['nome'], "DROP")
        globals.addlistlock.acquire(timeout=3)
        if globals.addlistlock.locked():
            globals.requests_list.append(requisitado)
            globals.requests_list[-1].setoid(getbaseoid(globals.conn, globals.requests_list[-1].dbname)[0][0])
            globals.addlistlock.release()
            updinfodelbase(globals.conn, globals.requests_list[-1].dbname, globals.requests_list[-1].oid)
        else:
            return redirect('/minhasbases')
        if not globals.runningthread.locked():
            startdatabasethread()
        return redirect('/minhasbases')


    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')


    @app.route('/functionsetup')
    def functionsetup():
        if 'userid' not in session or \
        not checksessioninfo(session['userid']) or \
        session['privilege'] not in ["MASTER", "ADMIN"]:
            return redirect('/')
        chosen = [None]
        arrtimes = None
        timeslen = None
        if request.args.get('chosen') is not None:
            chosen = ast.literal_eval(request.args.get('chosen'))
            if request.args.get('times'):
                arrtimes = ast.literal_eval(request.args.get('times'))
                timeslen = len(arrtimes)
        functionalities = getfunctionalities(globals.conn, chosen[0])
        return render_template('setuptimes.html',
                               nome_usuario=session['nome'],
                               disk_space=getdiskspace(),
                               requestrepeat=request.args.get('requestrepeat'),
                               privilege=session['privilege'],
                               funcionalities=functionalities,
                               times=arrtimes,
                               timeslen=timeslen,
                               chosen=chosen)


    @app.post('/function')
    def functions():
        functid = ast.literal_eval(request.form['functid'])
        funstr = request.form['functid']
        if request.form['requesttype'] == "1":
            initime = request.form['inihour'] + ":" + request.form['inimin']
            fimtime = request.form['fimhour'] + ":" + request.form['fimmin']
            newperiod(globals.conn, initime, fimtime, functid[0])
        elif request.form['requesttype'] == "3":
            removeperiod(globals.conn, request.form['functperiodid'])
        times = str(getfunctionalitiesperiods(globals.conn, functid[0]))
        return redirect(url_for('functionsetup', times=times, chosen=funstr))


    @app.post('/addperiod')
    def addperiod():
        funstr = request.form['functid']
        functid = ast.literal_eval(request.form['functid'])
        times = getfunctionalitiesperiods(globals.conn, functid[0])
        return redirect(url_for('functionsetup', times=times, chosen=funstr))


    @app.post('/cancelprocess')
    def cancelprocess():
        globals.rmvlistlock.acquire()
        selectedpid = request.form['cancelprocess']
        for x, obj in enumerate(globals.requests_list):
            if selectedpid == str(obj.p):
                if not killprocess(str(obj.p)):
                    globals.requests_list.pop(x)
                    return redirect('/minhasbases')
                if obj.status != "IN QUEUE":
                    osdropbase()
                    updinfodelbase(globals.conn, globals.requests_list[0].dbname, globals.requests_list[0].oid)
                globals.requests_list.pop(x)
        globals.rmvlistlock.release()
        return redirect('/minhasbases')


    @app.errorhandler(404)
    def handle_bad_direction(e):
        print(request.url)
        return render_template('404handler.html')


    app.run(host='0.0.0.0', port=8081, debug=True)