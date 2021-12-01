import psycopg2

def SQL_add(URL,id):            # 友達追加時にデータベースに登録
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("INSERT INTO Informations(userid,status,reason_time,name,remarks) values (%s,'連絡待ち','なし','なし','なし');" %(id))
    con.commit()

def SQL_delete(URL,id):         # 友達削除時にデータベースから削除
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("DELETE FROM Informations WHERE userid = %s;" %(id))
    con.commit()

def CheckStatus(URL,id):
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    status = cursor.execute("SELECT status FROM Informations where userid = %s" %(id))
    con.commit()
    return(status)