import psycopg2

def SQL_add(URL,id):            # 友達追加時にデータベースに登録
    id = "'"+id+"'"             # これがないとSQL文に引っかからない
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("INSERT INTO Informations(userid,status,content,reason_time,name,remarks) values (%s,'連絡待ち','なし','なし','なし','なし');" %(id))
    con.commit()

def SQL_delete(URL,id):         # 友達削除時にデータベースから削除
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("DELETE FROM Informations WHERE userid = %s;" %(id))
    con.commit()

def CheckStatus(URL,id):        # 状態チェック
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("SELECT status FROM Informations where userid = %s;" %(id))
    res = cursor.fetchone()
    con.commit()
    return res[0] if res != None else None

def ChangeStatus(URL,id,tmp):   # 状態の更新
    id = "'"+id+"'"
    tmp = "'"+tmp+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set status = %s where userid = %s;' %(tmp,id))
    conn.commit()

def ChangeContent(URL,id,text): # 連絡内容の更新
    id = "'"+id+"'"
    text = "'"+text+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set content = %s where userid = %s;' %(text,id))
    conn.commit()

def ChangeReason(URL,id,text):  # 欠席理由or到着予定時間を記入
    id = "'"+id+"'"
    text = "'"+text+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set reason_time = %s where userid = %s;' %(text,id))
    conn.commit()

def ChangeName(URL,id,text):
    id = "'"+id+"'"
    text = "'"+text+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set name = %s where userid = %s;' %(text,id))
    conn.commit()

def ChangeRemarks(URL,id,text):
    id = "'"+id+"'"
    text = "'"+text+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set remarks = %s where userid = %s;' %(text,id))
    conn.commit()

def CheckInfo(URL,id):
    id = "'"+id+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Informations WHERE userid = %s;' %(id))
    conn.commit()