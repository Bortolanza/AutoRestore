def setusersbase(conn, oid, status, userid):
    return conn.executequery("INSERT INTO public.databases(dataoid, status, usersid, restoredt) "
                             "VALUES(%s::oid, '%s', %i, now()) ON CONFLICT (dataoid) "
                             "DO UPDATE SET status = '%s'"
                             "            , usersid = %i"
                             "            , restoredt = NOW()"
                             % (oid, status, userid, status, userid), 0)


def resetop(conn, oid, status):
    return conn.executequery("UPDATE public.databases"
                             "   SET status = '%s'"
                             " WHERE dataoid = %s::oid" % (status, oid), 0)


def updinfodelbase(conn, dbname, oid):
    return conn.executequery("UPDATE public.databases"
                             "   SET dbname = '%s'"
                             "     , status = 'DELETED'"
                             "     , dropdt = NOW()"
                             " WHERE dataoid = %s::oid " % (dbname, oid), 0)
