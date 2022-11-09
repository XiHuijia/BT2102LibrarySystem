import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="xhj20010222"
)

def signUp(id, password, confirm, isAdmin):
    if password != confirm:
        return "Please check your password again."
    else:
        mycursor = mydb.cursor()
        mycursor.execute("USE library")
        tableName = "User" + str(id)
        sql1 = "CREATE TABLE {}(bookID VARCHAR(255), dueDate VARCHAR(255), unpaidFine VARCHAR(255));".format(tableName)
        sql2 = "INSERT INTO user(id, password, numOfBooksBorrowed, unpaidFines, isAdmin) VALUES (%s, %s, %s, %s, %s);"

        user = (id, password, 0, 0, isAdmin)
        mycursor.execute(sql1)
        mycursor.execute(sql2, user)
        mydb.commit()
        return "Sign up successfully!"
