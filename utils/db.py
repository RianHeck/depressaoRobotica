import sqlite3

dbName = 'main.sqlite'
tableAvisos = 'avisos'
tableMensagens = 'mensagens'

async def returnTable(tableUsada):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM {tableUsada}')
    mensagens = cursor.fetchall()
    cursor.close()
    db.close()
    return mensagens

async def dbExecute(query):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()

async def dbReturn(query):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(query)
    val = cursor.fetchone()
    cursor.close()
    db.close()
    return val