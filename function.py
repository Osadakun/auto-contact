def SQL_add(URL,id):
    con = psycopg2.connect(URL, sslmode='require')
    cursor = con.cursor()
    cursor.execute("INSERT INTO Informations(userid,status,reason_title,name,reamrks) values (%s,'なし','なし','なし','なし');" %(id))
    con.commit()
    print("--------------------------")
