def getuser(conn, username, pword):
    return conn.executequery("SELECT users.usersid, users.nome, users.privilege FROM users WHERE "
                                             "users.username = '%s' AND users.password = md5('%s');"
                                             % (username, pword), 1)

def getbaseoid(conn, dbname):
    return conn.executequery("SELECT pg_database.oid "
                             "  FROM pg_catalog.pg_database "
                             " WHERE datname = '%s'" % dbname, 1)


def getuserstats(conn):
    return conn.executequery("WITH cte AS( SELECT pg_database.oid"
                             "                  , datname, pg_database_size(datname)"
                             "                  , usersid "
                             "               FROM pg_catalog.pg_database "
                             "               JOIN databases ON databases.dataoid = pg_database.oid "
                             "              WHERE datistemplate = FALSE "
                             "                    AND pg_database.datname NOT IN ('template0', 'template1', 'postgres')"
                             ")SELECT count(*)"
                             "      , pg_size_pretty(sum(pg_database_size)) AS sum"
                             "      , users.nome, foo.datname"
                             "      , pg_size_pretty(foo.max) "
                             "      , sum(pg_database_size) sum2"
                             "   FROM cte "
                             "   JOIN users USING(usersid) "
                             "   JOIN LATERAL(SELECT datname"
                             "                     , pg_database_size max "
                             "                  FROM cte "
                             "                 WHERE oid = cte.oid "
                             "                 ORDER BY pg_database_size DESC "
                             "                 LIMIT 1) AS foo ON TRUE "
                             "  GROUP BY users.usersid"
                             "         , foo.datname"
                             "         , foo.max "
                             "  ORDER BY sum2", 1)


def getuserbases(conn, userid, status="'RESTORED'"):
    return conn.executequery("WITH cte AS ("
                             "  SELECT databases.restoredt  as time"
                             "       , pg_database_size(datname) size"
                             "       , pg_database.datname"
                             "       , status"
                             "    FROM public.databases"
                             "    JOIN pg_catalog.pg_database ON pg_database.oid = dataoid"
                             "   WHERE databases.usersid = %i"
                             "     AND databases.status in (%s)" 
                             "   ORDER BY size DESC"
                             " )SELECT date_trunc('seconds', time)::TEXT as time"
                             "       , pg_size_pretty(size) pt_size"
                             "       , datname"
                             "       , status::TEXT"
                             "    FROM cte"
                             "   UNION ALL"
                             "  SELECT ''"
                             "       , pg_size_pretty(SUM(size))"
                             "       , 'Total'"
                             "       , ''"
                             "    FROM cte"
                             "   ORDER BY time desc nulls last" % (userid, status), 1)


def getuserhistory(conn, userid):
    return conn.executequery("SELECT date_trunc('seconds', coalesce(dropdt, restoredt))::TEXT as time"
                             "       , COALESCE(dbname, datname)"
                             "       , status::TEXT"
                             "    FROM public.databases"
                             "    LEFT JOIN pg_database ON databases.dataoid = pg_database.oid"
                             "   WHERE usersid = %i"
                             "   ORDER BY restoredt" % userid, 1)


def getallbases(conn):
    return conn.executequery("SELECT pg_database.datname"
                             "  FROM pg_database"
                             " WHERE datistemplate = FALSE "
                             "       AND pg_database.datname NOT IN ('template0', 'template1', 'postgres')", 1)


def getfunctionalities(conn, functionalityid):
    if functionalityid is None:
        functionalityid = 'NULL'
    return conn.executequery("SELECT functionalityid"
                             "     , description"
                             "  FROM functionality"
                             " WHERE functionalityid != coalesce(%s::int, 0)" % functionalityid, 1)


def getfunctionalitiesperiods(conn, functionalityid):
    return conn.executequery("SELECT initialhour::text"
                             "     , finalhour::text"
                             "     , functionalityperiodid"
                             "  FROM functionalityperiod"
                             " WHERE functionalityid = (%s)::int" % functionalityid, 1)


def checkperiods(conn, functionalityid):
    return conn.executequery("SELECT TRUE"
                            "   FROM functionalityperiod"
                             " WHERE now()::time BETWEEN initialhour AND finalhour"
                             "   AND functionalityid = %s::int"
                             " LIMIT 1" % functionalityid, 1)