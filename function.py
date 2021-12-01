import psycopg2

def SQL_add(URL,id):
    id = "'"+id+"'"
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("INSERT INTO Informations(userid,status,reason_time,name,remarks) values (%s,'なし','なし','なし','なし');" %(id))
    con.commit()
    print("--------------------------")
