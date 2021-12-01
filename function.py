import psycopg2

def SQL_add(URL,id):            # 友達追加時にデータベースに登録
    id = "'"+id+"'"
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

def ChangeContent(URL,id,text):
    id = "'"+id+"'"
    text = "'"+text+"'"
    conn = psycopg2.connect(URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('UPDATE Informations set content = %s where userid = %s' %(text,id))
    conn.commit()