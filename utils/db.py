import sqlite3

dbName = 'main.sqlite'
tableAvisos = 'avisos'
tableMensagens = 'mensagens'
tablePermissoes = 'permissoes'
tableScoreboard = 'scoreboard'
tableWR = 'wr'
tableRPG = 'rpg'

def returnTable(tableUsada):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM {tableUsada}')
    mensagens = cursor.fetchall()
    cursor.close()
    db.close()
    return mensagens

def dbExecute(query):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()

def dbReturn(query):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(query)
    val = cursor.fetchall()
    cursor.close()
    db.close()
    return val

def dbReturnDict(query):
    db = sqlite3.connect(dbName)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(query)
    val = [dict(row) for row in cursor.fetchall()]
    db.close()
    return val