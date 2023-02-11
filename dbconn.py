import psycopg2
from psycopg2 import pool


class Connection:
    def __init__(self, user, password, host, port, database):
        self.user = user,
        self.password = password,
        self.host = host,  
        self.port = port,  
        self.database = database  
        self.pool = psycopg2.pool.ThreadedConnectionPool(1, 5, user=user, password=password, host=host,
                                                         port=port, database=database)
        self.connection = None

    def getconnection(self):
        try:
            self.connection = self.pool.getconn()
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        except (Exception, psycopg2.Error) as error:
            raise Exception(error)
        else:
            if self.connection:
                cursor = self.connection.cursor()
                return cursor

    def executequery(self, statement, querytype):
        cursor = self.getconnection()
        try:
            cursor.execute(statement)
        except (Exception, psycopg2.Error) as error:
            raise Exception(error)
        else:
            if querytype == 1:
                values = cursor.fetchall()
            else:
                values = 1
        cursor.close()
        self.pool.putconn(self.connection)
        return values


