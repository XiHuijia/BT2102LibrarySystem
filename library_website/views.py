
import datetime
import mysql.connector
from pymongo import MongoClient
import json
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from datetime import date
import time

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="xhj20010222"
)


isAdmin = 0
firstTimeOpen = 0
overdueFine = 0


# mycursorUpdateFine = mydb.cursor()
# mycursor = mydb.cursor()
# mycursor.execute("USE library")
# f = open('libbooks.json',)
# data = json.load(f)
# sqlBook = "INSERT INTO Book (bookID , title, isbn, pageCount, publishedDate, status, thumbnailUrl, shortDescription, longDescription) " \
#           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
# sqlAuthor = "INSERT INTO Author (bookID, authorName) VALUES (%s, %s)"
# sqlCategory = "INSERT INTO Category (bookID, categoryName) VALUES (%s, %s)"
# for element in data:
#     book = (element["_id"], element["title"], element["isbn"], element["pageCount"],
#             element["publishedDate"][11:21],element["status"],
#             element["thumbnailUrl"],element["shortDescription"], element["longDescription"])
#     mycursor.execute(sqlBook, book)
#     authorSplit = element["authors"][1:-1].split(", ")
#     for authorDetails in authorSplit:
#         author = (element["_id"], authorDetails)
#         mycursor.execute(sqlAuthor, author)
#     categorySplit = element["categories"][2:-2].split(", ")
#     for categoryDetail in categorySplit:
#         category = (element["_id"], categoryDetail)
#         mycursor.execute(sqlCategory, category)
# mydb.commit()




initializeNumber = 0
client = MongoClient(host="127.0.0.1", port=27017)
collection = client["library"]["test"]
bookID = ''
bookAuthor = ''
bookTitle = ''
bookPulisher = ''
bookDate = ''
bookPage = ''
bookLongDescription = ''
bookShortDescription = ''
bookCategory = ''
bookAvailable = ''
bookDueDate = ''
bookISBN = ''
userLoginName = ''
collectionForUniqueItem = []
byCategory = "byCat"
byAuthor = "byAut"
byPublisher = "byPub"
byYearOfPublication = "byYop"
byBookID = "byBid"
def findAvailable(bookID):
    mycursor1 = mydb.cursor()
    mycursor1.execute("USE library")
    sql1 = "SELECT * FROM Borrow WHERE bookID = %s"
    mycursor1.execute(sql1, ((bookID),))
    myresult = mycursor1.fetchall()

    sql2 = "SELECT * FROM Reserve WHERE bookID = %s"
    mycursor1.execute(sql2, ((bookID),))
    myresult2 = mycursor1.fetchall()
    # return myresult
    if(len(myresult) == 0 and len(myresult2) == 0):
        return "available for borrow and reserve"
    elif (len(myresult) != 0 and len(myresult2) == 0):
        return "available for reserve only"
    else:
        return "not available for borrow and reserve"

def findBookDueDate(bookID):
    mycursor16 = mydb.cursor()
    mycursor16.execute("USE library")
    sql1 = "SELECT dueDate FROM Borrow WHERE bookID = %s"
    mycursor16.execute(sql1, ((bookID),))
    myresult = mycursor16.fetchall()
    if (len(myresult) == 0):
        return ''
    else:
        return myresult[0][0]

def borrow(bookID, user):
    global mydb
    global userLoginName
    mycursor2 = mydb.cursor()
    mycursor2.execute("USE library")

    #select from borrow using memberID to see the number of books this user has borrowed
    #store the number into variable num
    sql0 = "SELECT * FROM Borrow WHERE memberID = %s"
    mycursor2.execute(sql0, (user,))
    myresult0 = mycursor2.fetchall()
    num = len(myresult0)

    #select from borrow using bookID to see whether this book has been borrowed
    #if no one borrows the book, myresult1 = [], meaning len(myresult1) = 0
    sql1 = "SELECT * FROM Borrow WHERE bookID = %s"
    mycursor2.execute(sql1, (bookID,))
    myresult1 = mycursor2.fetchall()

    sql11 = "SELECT * FROM Reserve WHERE bookID = %s"
    mycursor2.execute(sql11, (bookID,))
    myresult11 = mycursor2.fetchall()
    if (len(myresult11) != 0):
        userWhoReserveTheBook = myresult11[0][1]
        if (userWhoReserveTheBook != str(userLoginName)):
            return "The book has been reserved by someone else, You cam neither borrow or reserve it"

    #select from fine using memberID to see whether this user has unpaid fine
    #end the function if the user has unpaid fine, return String unpaidfine
    sql2 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor2.execute(sql2, (user,))
    myresult2 = mycursor2.fetchall()
    if int((myresult2)[0][0]) != 0:
        return "unpaidfine"

    #get due date after 4 weeks from today in String format
    curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    Datetime = datetime.datetime.strptime(curTime, "%Y-%m-%d %H:%M:%S")
    Datetime2 = Datetime + datetime.timedelta(days=28)
    Datetime3 = datetime.datetime.strftime(Datetime2, "%Y-%m-%d %H:%M:%S")

    if len(myresult1) == 0 and num < 4:
        #if can borrow, insert a new entry into borrow table, including the bookID, memberID, dueDate
        sql3 = "INSERT INTO borrow (bookID, memberID, dueDate) VALUES (%s, %s, %s);"
        mycursor2.execute(sql3, (bookID, user, Datetime3))
        mydb.commit()
        #select from reserve table using bookID to see whether it has been reserved
        # if the book is available and the user has previously reserved the book,
        # auto cancel the reservation after successfully borrowing
        sql4 = "SELECT * FROM Reserve WHERE bookID = %s"
        mycursor2.execute(sql4, (bookID,))
        myresult4 = mycursor2.fetchall()
        if len(myresult4) != 0 and myresult4[0][1] == user:
            cancelReserve(bookID)
        return "borrowed"

    elif num>=4:
        #if the user has borrowed more than 4 books, return cannot borrow
        return "cannot borrow"
    else:
        #if the book has been borrowed, return unavailable
        return "unavailable"

def reserve(bookID, user):
    global mydb
    mycursor3 = mydb.cursor()
    mycursor3.execute("USE library")

    #select from reserve to see whether it has been reserved
    #still use number of entry of the result
    sql1 = "SELECT * FROM Reserve WHERE bookID = %s"
    mycursor3.execute(sql1, (bookID,))
    myresult = mycursor3.fetchall()

    sql10 = "SELECT dueDate FROM Borrow WHERE bookID = %s"
    mycursor3.execute(sql10, (bookID,))
    myresult10 = mycursor3.fetchall()
    #user cannot reserve if have unpaid fine
    #terminate the function and return unpaidfine
    sql2 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor3.execute(sql2, (user,))
    myresult2 = mycursor3.fetchall()


    if int((myresult2)[0][0]) != 0:
        return "unpaidfine"
    if len(myresult) == 0:
        if len(myresult10) != 0:
            currentDueDate = myresult10[0][0]
            newDate = currentDueDate + datetime.timedelta(days=1)
            sql3 = "INSERT INTO reserve (bookID, memberID, reserve_date) VALUES (%s, %s, %s);"
            mycursor3.execute(sql3, (bookID, user, newDate))
            mydb.commit()
        else:
        #if can reserve, insert a new entry into reserve table using bookID, memberID, reserve date(today)
        #return String reserved at the end
            curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            sql3 = "INSERT INTO reserve (bookID, memberID, reserve_date) VALUES (%s, %s, %s);"
            mycursor3.execute(sql3, (bookID, user, curTime))
            mydb.commit()
        return "reserved"

    else:
        if myresult[0][1] == user:
            #if the book has been reserved by the same person, return already reserved
            return "already reserved"
        else:
            #if the book has been reserved by someone else, return cannot reserve
            return "cannot reserve"

def calculateFine():
    global userLoginName
    global mydb
    global overdueFine
    global mycursorUpdateFine
    mycursor4 = mydb.cursor()
    mycursor4.execute("USE library")
    curDate = date.today()
    ratePerDay = 1
    sql10 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor4.execute(sql10, (str(userLoginName),))
    myresult10 = mycursor4.fetchall()
    totalUnPaidfine = overdueFine
    print(overdueFine)

    #select from borrow using memberID to get the entries of borrowing by this user
    sql1 = "SELECT * FROM borrow WHERE memberID = %s"
    mycursor4.execute(sql1, (str(userLoginName), ))
    myresult1 = mycursor4.fetchall()

    #if the number of entry > 0, meaning the user hsa borrowed the book
    if len(myresult1) != 0:
        # loop through the entries, get the due dates
        for i in myresult1:
            # print(i[2].date())
            # year = int(i[2][0:4])
            # month = int(i[2][5:7])
            # day = int(i[2][8:10])
            # dueDate = date(year, month, day)
            dueDate = i[2]
            #if today's date is larger than due date
            #using today's date minus the due date and calculate the fine for this book
            #add the fine to totalUnpaidFine
            if dueDate < curDate:
                daysPassed = (curDate - dueDate).days
                fine = daysPassed * ratePerDay
                totalUnPaidfine = totalUnPaidfine + fine
                updateFine(totalUnPaidfine)
    #update fine table with memberID and total amount of unpaid fine
                # sql3 = "UPDATE fine SET total_amount = %s WHERE memberID = %s"
                # mycursorUpdateFine.execute(sql3, (totalUnPaidfine, str(userLoginName),))
                # mydb.commit()
    return "fines calculated"

def extendDueDate(bookID):
    global userLoginName
    global mydb
    mycursor5 = mydb.cursor()
    todaysDate = date.today()
    mycursor5.execute("USE library")

    #select from borrow to for updating the due date later
    sql1 = "SELECT * FROM borrow WHERE bookID = %s and memberID = %s"
    mycursor5.execute(sql1, (bookID, str(userLoginName), ))
    myresult1 = mycursor5.fetchall()
    if (len(myresult1) == 0):
        return "You have not borrow this book before!"

    #select from reserve to see whether this book is currently reserved by someone else
    #len(myresult2) == 0 means no one resevered the book
    sql2 = "SELECT * FROM reserve WHERE bookID = %s"
    mycursor5.execute(sql2, (bookID,))
    myresult2 = mycursor5.fetchall()

    if len(myresult2) == 0:
        #from myresult1 find the due date and add 28 days
        # curDueDate = myresult1[0][1]
        curDueDate = myresult1[0][2]
        numberOfDaysPassed = (curDueDate - todaysDate).days
        print(numberOfDaysPassed)
        if (numberOfDaysPassed < 0):
            return "The book is overdue, you cannot extend it anymore. Please proceed to pay the fine"
        # Datetime = datetime.datetime.strptime(curDueDate, "%Y-%m-%d %H:%M:%S")
        # Datetime2 = Datetime + datetime.timedelta(days=28)
        # Datetime3 = datetime.datetime.strftime(Datetime2, "%Y-%m-%d %H:%M:%S")
        Datetime3 = curDueDate + datetime.timedelta(days=28)
        #update the due date to the new value
        sql3 = "UPDATE borrow SET dueDate = %s WHERE memberID = %s and bookID = %s"
        mycursor5.execute(sql3, (Datetime3, str(userLoginName), bookID, ))
        mydb.commit()
        #return true if extension of due date is successful, false otherwise
        return "You have successfully extend the due date of the book"
    else:
        return "This book has been reserved by someone, so you cannot extend the due date"

#RETURN

def returnBookFunct(bookID):
    global userLoginName
    mycursor6 = mydb.cursor()
    mycursor6.execute("USE library")

    #select from borrow using memberID and bookID to see whether the user has indeed borrowed this book
    sql1 = "SELECT * FROM borrow WHERE bookID = %s and memberID = %s"
    mycursor6.execute(sql1, (bookID, str(userLoginName), ))
    myresult6 = mycursor6.fetchall()
    if len(myresult6) != 0:
        #if the person has indeed borrowed this book before
        #delete the entry from borrow table using bookID
        #return success message
        sql2 = "DELETE FROM borrow WHERE bookID = %s"
        mycursor6.execute(sql2, (bookID, ))
        mydb.commit()
        return "You have successfully return the book"
    else:
        # else return error message
        return "You have not borrowed this book before!"


def cancelReserve(bookID):
    global userLoginName
    global mydb
    mycursor7 = mydb.cursor()
    mycursor7.execute("USE library")

    # select from reserve using memberID and bookID to see whether the user has indeed reserved this book
    sql1 = "SELECT * FROM reserve WHERE bookID = %s and memberID = %s"
    mycursor7.execute(sql1, (bookID, str(userLoginName),))
    myresult7 = mycursor7.fetchall()
    if len(myresult7) != 0:
        # if the person has indeed reserved this book before
        # delete the entry from reserve table using bookID
        # return success message
        sql2 = "DELETE FROM reserve WHERE bookID = %s"
        mycursor7.execute(sql2, (bookID,))
        mydb.commit()
        return "You have successfully cancelled the reservation of the book"
    else:
        # else return error message
        return "You have not reserved this book before!"

fineCount = 40
def updateFine(amount):
    global fineCount
    mycursor4 = mydb.cursor()
    mycursor4.execute("USE library")
    sql2 = "UPDATE fine SET total_amount = %s WHERE memberID = %s"
    mycursor4.execute(sql2, (str(amount), str(userLoginName), ))
    mydb.commit()
    return "Fines updated"

def payFine(amount, method):
    global userLoginName
    global mydb
    global mycursorUpdateFine
    mycursor8 = mydb.cursor()
    mycursor8.execute("USE library")

    #find the current unpaidfine
    sql1 = "SELECT * FROM fine WHERE memberID = %s"
    mycursor8.execute(sql1, (str(userLoginName), ))
    curFine = mycursor8.fetchall()[0][1]
    curFine = int(curFine)
    totalFineRemaing = 0
    #if unpaid fine is 0, return no need to pay message
    if curFine == 0:
        return "You have no unpaid fines!"
    else:
        #if needs to pay
        #if entered a number larger than unpaid fine, return too much message
        if amount > curFine:
            return "Your current unpaid fine is less than the number you have entered"
        elif amount < curFine:
            return "You need to pay the full amount of the fine"
        else:
            #if can pay
            #upate the fine table and set the fine amount to (curFine - amount)
            remainingFine = curFine - amount
            totalFineRemaing = remainingFine
            print(type(totalFineRemaing))
            updateFine(int(totalFineRemaing))
            # mycursor18 = mydb.cursor()
            # mycursorUpdateFine.execute("USE library")
            # sql2 = "UPDATE fine SET total_amount = %s WHERE memberID = %s "
            # mycursorUpdateFine.execute(sql2, (str(totalFineRemaing), str(userLoginName), ))
            # # mycursorUpdateFine.execute(sql2)
            # mydb.commit()
            # insert entry into payment table
            curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            sql3 = "INSERT INTO payment (paymentMemberID, transactionTime, total_amount,fineMemberID, memberId,  paymentMethod) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor8.execute(sql3, (str(userLoginName), curTime, int(amount),str(userLoginName),str(userLoginName), method, ))
            mydb.commit()

    return int(totalFineRemaing)


def searchFromMongo(input, filterResult):
    global initializeNumber
    if (initializeNumber == 0):
        f = open('libbooks.json')
        data = json.load(f)
        collection.insert_many(data)
        initializeNumber = initializeNumber + 1
    if (initializeNumber > 0):
        allTheListOfResult = []
        regularExpResult = ".*data.*".format(input)
        global collectionForUniqueItem
        interResult = list(collection.find({filterResult: {'$regex': str(input), "$options": 'i'}}).sort("title"))
        testing = list(collection.find({filterResult: (input)}).sort("title"))
        finalResult = []
        if (len(interResult) >= len(testing)):
            finalResult = interResult
        else:
            finalResult = testing

        if (len(finalResult) == 1):
            collectionForUniqueItem = finalResult
            return finalResult
        for response in finalResult:
            intermediateRow = []
            intermediateRow.append(response['_id'])
            intermediateRow.append(response['title'])
            intermediateRow.append(response['authors'][1: -1])
            allTheListOfResult.append(intermediateRow)
        return allTheListOfResult
    return None

def directToOneSingleDetailsPage(request, result):
    global firstTimeOpen
    firstTimeOpen = 0
    global bookID
    global bookAuthor
    global bookTitle
    global bookPulisher
    global bookDate
    global bookPage
    global bookLongDescription
    global bookShortDescription
    global bookCategory
    global bookAvailable
    global bookDueDate
    global bookISBN
    bookDetailsPage_name = 'library_website/BOOK_DETAILSMAIN.html'
    bookID = result[0]['_id']
    bookAuthor = result[0]['authors'][1: -1]
    bookTitle = result[0]['title']
    bookDate = result[0]['publishedDate'][11:21]
    bookPage = result[0]['pageCount']
    bookLongDescription = result[0]['longDescription']
    bookShortDescription = result[0]['shortDescription']
    bookCategory = result[0]['categories'][2:-2]
    bookAvailable = findAvailable((bookID))
    bookDueDate = findBookDueDate(bookID)
    bookISBN = result[0]['isbn']
    if (userLoginName == ''):
        bookDetailsPage_name = 'library_website/BOOK_DETAILSBorrowMain.html'
    return render(request, bookDetailsPage_name,
                  {'bookID': bookID,
                   'author': bookAuthor,
                   'title': bookTitle,
                   'publisher': bookPulisher,
                   'DateOfPublication': bookDate,
                   'numberOfPages': bookPage,
                   'shortDescription': bookShortDescription,
                   'longDescription': bookLongDescription,
                   'category': bookCategory,
                   'availability': bookAvailable,
                   'dueDate': bookDueDate,
                   'isbn': bookISBN,
                   'resultOfBorrowing': ' '})



def homePage(request):
    global userLoginName
    if (str(userLoginName) == '' or str(userLoginName) == None):
        logout(request)
   # mongoDB.write_database()
    data = request.POST.get('search')
    # result = ''
    data = str(data)
    filterResult = "title"
    if (data != None):
        if data[0:5].lower() == byCategory.lower():
            filterResult = "categories"
            data = str(data[6:])
        elif data[0:5].lower() == byAuthor.lower():
            filterResult = "authors"
            data = str(data[6:])
        elif data[0:5].lower() == byYearOfPublication.lower():
            filterResult = "publishedDate"
            data = str(data[6:])
        elif data[0:5].lower() == byBookID.lower():
            filterResult = '_id'
            try:
                 data = int(data[6:])
            except:
                errorMessage = "You have enter an invalid book or invalid filter"
                return render(request, 'library_website/HOME.html', {'data': errorMessage})
    result = searchFromMongo(data,filterResult)
    #print(data)
    ddd = {'s': 'hey'}
    homePage_name = 'library_website/HOME.html'

    bookDetailsPage_name = 'library_website/BOOK_DETAILSMAIN2.html'
    visitorDetails_name = 'library_website/VISITOR_BOOKDETAILS.html'
    # idExtracted = result['_id']

    # mycursor = mydb.cursor()
    # mycursor.execute("USE library")
    # a = "SELECT * FROM Book WHERE id = %s"
    # mycursor.execute(a, (data, ))
    # myresult = mycursor.fetchall()
    # print(myresult[0][0])
    # for row in myresult:
    #     print(row)
    # if (data == "2"):
    #    return render(request, 'library_website/bookDetails.html')


    global bookID
    global bookAuthor
    global bookTitle
    global bookPulisher
    global bookDate
    global bookPage
    global bookLongDescription
    global bookShortDescription
    global bookCategory
    global bookAvailable
    global bookDueDate
    global bookISBN
    global firstTimeOpen
    message = ''
    listOfInstruction = ''
    if (userLoginName == ''):
        bookDetailsPage_name = 'library_website/BOOK_DETAILSMAINBorrowed.html'
    if len(result) != 0:
        if (len(result) == 1):
            firstTimeOpen = 0
            return directToOneSingleDetailsPage(request, collectionForUniqueItem)
        finalInput = result
        firstTimeOpen = 0
        return render(request, bookDetailsPage_name,
                      {"inputData": finalInput})


    firstTimeOpen = firstTimeOpen + 1
    if firstTimeOpen > 1:
        if (len(result) == 0):
            message = "The book you searched does not exist, you can try to use filter to find the book \n"
            searchByAuthor = "Search book by Author, use byAut as prefix, eg: byAut Charlie Collins \n"
            searchByCategory = "Search book by Category, use byCat as prefix, eg: byCat Java \n"
            searchByYearOfPublication = "Search book by Year Of Publication, use byYop as prefix, eg: byYop 2009 \n"
            searchByBookID = "Search book by Book ID, use byBid as prefix, eg: byBid 54 \n"
            listOfInstruction = []
            listOfInstruction.append(searchByAuthor)
            listOfInstruction.append(searchByCategory)
            listOfInstruction.append(searchByYearOfPublication)
            listOfInstruction.append(searchByBookID)
    return render(request, homePage_name, {'data': message, 'listOfFilter': listOfInstruction})

def signUp(id, password, confirm):
    if password != confirm:
        return "Please check your password again."
    else:
        mycursor9 = mydb.cursor()
        mycursor9.execute("USE library")

        #insert entry into memberuser table
        #insert entry into fine table, set default fine to be 0
        sql1 = "INSERT INTO User(memberID, password) VALUES (%s, %s);"
        sql2 = "INSERT INTO fine(fineMemberID, total_amount, memberID) VALUES (%s, %s, %s);"

        user = (id, password)
        mycursor9.execute(sql1, user)
        mycursor9.execute(sql2, (id, 0, id))
        mydb.commit()
        return "Signed up successfully!"

def adminSignUp(id, password, confirm):
    if password != confirm:
        return "Please check your password again."
    else:
        mycursor10 = mydb.cursor()
        mycursor10.execute("USE library")

        # insert entry into adminuser table
        sql = "INSERT INTO adminUser(adminID, password) VALUES (%s, %s);"

        adminUser = (id, password)
        mycursor10.execute(sql, adminUser)
        mydb.commit()
        return "Sign up successfully!"

def signUpPage(request):
    global userLoginName
    global isAdmin
    global firstTimeOpen
    firstTimeOpen = 0
    if request.method == "POST":
        usercreationform = UserCreationForm(request.POST)
        if usercreationform.is_valid():
            user = usercreationform.save()
            # log the user in
            username = usercreationform.cleaned_data.get("username")
            password = usercreationform.cleaned_data.get("password1")
            confirm = usercreationform.cleaned_data.get("password2")
            userLoginName = username
            containAdmin = str(userLoginName)[0:5]


            if (containAdmin == "admin"):
                isAdmin = 1
                adminSignUp(username, password, confirm)
                login(request, user)
                return redirect(
                    "library_adminAccountPage"  # this should be the NAME of the url from the urlpattern
                )  # redirect to homePage
            else:
                signUp(username, password, confirm)
                login(request, user)
                return redirect(
                    "library_homePage"  # this should be the NAME of the url from the urlpattern
                  )  # redirect to homePage

    else:
        usercreationform = UserCreationForm()
    return render(request, "library_website/signUp3.html", {"signUpForm": usercreationform})
    #return render(request, 'library_website/signUpUpdated.html')

def autoCancelReservation():
    global userLoginName
    global mydb
    mycursor11 = mydb.cursor()
    mycursor11.execute("USE library")

    #select from fine table to see the total unpaid fine of the user
    sql1 = "SELECT * FROM fine WHERE memberID = %s"
    mycursor11.execute(sql1, (str(userLoginName), ))
    myresult1 = mycursor11.fetchall()

    #if total unpaid fine is not 0, cancel all the reservations
    if myresult1[0][1] != 0:
        sql2 = "DELETE FROM reserve WHERE memberID = %s"
        mycursor11.execute(sql2, (str(userLoginName), ))
        mydb.commit()

def adminAutoCancellation():
    global userLoginName
    global mydb
    mycursor11 = mydb.cursor()
    mycursor11.execute("USE library")
    todaysDate = date.today()
    sql1 = "SELECT memberID FROM fine WHERE total_amount > 0"
    mycursor11.execute(sql1)
    myresult1 = mycursor11.fetchall()

    for members in myresult1:
        print(members)
        sql2 = "DELETE FROM reserve WHERE memberID = %s"
        mycursor11.execute(sql2, members)
        mydb.commit()

    sql3 = "SELECT bookID, reserve_date FROM Reserve"
    mycursor11.execute(sql3)
    myresult2 = mycursor11.fetchall()

    for details in myresult2:
        print(details[0])
        print(details[1])
        print(type(details[0]))
        reserDate = details[1]
        numbersOfDaysPassed = (todaysDate - reserDate).days
        if (numbersOfDaysPassed) > 1:
            sql4 = "DELETE FROM reserve WHERE reserve_date = %s"
            mycursor11.execute(sql4, (str(details[1]), ))
            mydb.commit()



def cancelOverdueReserveBook():
    global userLoginName
    global mydb
    curDate = date.today()
    mycursor11 = mydb.cursor()
    mycursor11.execute("USE library")

    # select from fine table to see the total unpaid fine of the user
    sql1 = "SELECT * FROM Reserve WHERE memberID = %s"
    mycursor11.execute(sql1, (str(userLoginName),))
    myresult1 = mycursor11.fetchall()

    for result in myresult1:
        reservedDate = result[2]
        numberOfDaysPassed = (curDate - reservedDate).days
        if (numberOfDaysPassed > 1):
            reserveBook =  result[0]
            sql2 = "DELETE FROM reserve WHERE memberID = %s and bookID = %s"
            mycursor11.execute(sql2, (str(userLoginName), reserveBook, ))
            mydb.commit()

    # if total unpaid fine is not 0, cancel all the reservations
    # if myresult1[0][1] != 0:
    #     sql2 = "DELETE FROM reserve WHERE memberID = %s"
    #     mycursor11.execute(sql2, (str(userLoginName),))
    #     mydb.commit()


def memberLogInPage(request):
    global userLoginName
    global firstTimeOpen
    global overdueFine
    firstTimeOpen = 0
    if request.method == "POST":
        authenticationform = AuthenticationForm(data=request.POST)
        if authenticationform.is_valid():
            # log the user in
            user = authenticationform.get_user()
            userUsername = str(user)
            userNameLen = len(userUsername)
            if (userUsername[0:5] == "admin"):
                message = "You are admin user, please use log in via admin log in page"
                return render(request, 'library_website/HOME.html', {'data': message})
            login(request, user)
            userLoginName = user
            mycursor4 = mydb.cursor()
            mycursor4.execute("USE library")
            sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
            mycursor4.execute(sql1, (str(userLoginName),))
            myresult = mycursor4.fetchall()
            overdueFine = int(myresult[0][0])
            calculateFine()
            sql10 = "SELECT total_amount FROM fine WHERE memberID = %s"
            mycursor4.execute(sql10, (str(userLoginName),))
            myresult10 = mycursor4.fetchall()
            if (int(myresult10[0][0]) > 0):
                autoCancelReservation()
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                userLoginName = user
                return redirect("library_homePage")  # redirect to homePage

    else:
        authenticationform = AuthenticationForm()
    return render(request, "library_website/memberLogin3.html", {"loginForm": authenticationform})
    #return render(request, 'library_website/memberLogin3.html')

def bookDetailsPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    global bookID
    global bookAuthor
    global bookTitle
    global bookPulisher
    global bookDate
    global bookPage
    global bookLongDescription
    global bookShortDescription
    global bookCategory
    global bookAvailable
    global bookDueDate
    global bookISBN
    return render(request, 'library_website/BOOK_DETAILS.html',
                  {'bookID': bookID,
                   'author': bookAuthor,
                   'title': bookTitle,
                   'publisher': bookPulisher,
                   'DateOfPublication': bookDate,
                   'numberOfPages': bookPage,
                   'shortDescription': bookShortDescription,
                   'longDescription': bookLongDescription,
                   'category': bookCategory,
                   'availability': bookAvailable,
                   'dueDate': bookDueDate,
                   'isbn': bookISBN,
                   'resultOfBorrowing': ' '})

def findTitleFromID(bookID):
    global mydb
    mycursor5 = mydb.cursor()
    mycursor5.execute("USE library")
    sql1 = "SELECT title FROM Book where bookID = %s"
    mycursor5.execute(sql1, (int(bookID),))
    myresult = mycursor5.fetchall()
    return myresult[0][0]

def myAccountPage(request):
    global mydb
    global firstTimeOpen
    global userLoginName
    firstTimeOpen = 0
    cancelOverdueReserveBook()
    if (str(userLoginName) == '' or str(userLoginName) == None):
        logout(request)
        return memberLogInPage(request)
    mycursor24 = mydb.cursor()
    mycursor24.execute("USE library")
    sql5 = "SELECT bookID FROM Reserve where memberID = %s"
    mycursor24.execute(sql5, (str(userLoginName),))
    myReservationResult = mycursor24.fetchall()
    reservedIDList = []
    reservationBookList = []
    for result in myReservationResult:
        reservedIDList.append(result[0])
        booktitle = findTitleFromID(result[0])
        reservationBookList.append(booktitle)

    sql6 = "SELECT bookID FROM Borrow where memberID = %s"
    mycursor24.execute(sql6, (str(userLoginName),))
    myBorrowResult = mycursor24.fetchall()
    borrowIDList = []
    borrowBookList = []
    for result in myBorrowResult:
        borrowIDList.append((result[0]))
        booktitle = findTitleFromID(result[0])
        borrowBookList.append(booktitle)

    sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor24.execute(sql1, (str(userLoginName),))
    myresult = mycursor24.fetchall()
    print(myresult)
    listOfUnPiadFine = []
    listOfUnPiadFine.append(myresult[0][0])
    if (int(myresult[0][0]) > 0):
        autoCancelReservation()
    aggregateList = []
    lengthBetweenTwoBooks = max(len(borrowBookList), len(reservationBookList))
    maximumLen = max(lengthBetweenTwoBooks, len(listOfUnPiadFine))
    for t in range(0, maximumLen):
        intermediate = []
        if (t >= (len(reservedIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservedIDList[t])
        if (t >= (len(reservationBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservationBookList[t])
        if (t >= (len(borrowIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowIDList[t])
        if (t >= (len(borrowBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowBookList[t])
        if (t >= (len(listOfUnPiadFine))):
            intermediate.append(' ')
        else:
            intermediate.append(listOfUnPiadFine[t])
        aggregateList.append(intermediate)
    return render(request, 'library_website/myAccount2.html', {
        'inputData': aggregateList
    })

def tryyy(request):
    global firstTimeOpen
    firstTimeOpen = 0
    return render(request, 'library_website/website.html')

def adminLogInPage(request):
    global userLoginName
    global isAdmin
    global firstTimeOpen
    firstTimeOpen = 0
    if request.method == "POST":
        authenticationform = AuthenticationForm(data=request.POST)
        if authenticationform.is_valid():
            # log the user in
            user = authenticationform.get_user()
            userUsername = str(user)
            userNameLen = len(userUsername)
            if (userNameLen < 5):
                message = "You are not admin user, please log in via member login page"
                return render(request, 'library_website/HOME.html', {'data': message})
            elif (userUsername[0:5] != "admin"):
                message = "You are not admin user, please log in via member login page"
                return render(request, 'library_website/HOME.html', {'data': message})
            login(request, user)
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                userLoginName = user
                adminAutoCancellation()
                return redirect("library_adminAccountPage")  # redirect to homePage

    else:
        authenticationform = AuthenticationForm()
    return render(request, 'library_website/adminLogin.html', {"loginForm": authenticationform})

def adminAccountPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    return render(request, 'library_website/adminAccount.html')


def adminBorrowPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    mycursor11 = mydb.cursor()
    mycursor11.execute("USE library")

    sql11 = "SELECT bookID FROM Borrow"
    mycursor11.execute(sql11)
    myresult = mycursor11.fetchall()
    titleList = []
    for i in myresult:
        bookid = i[0]
        booktile = findTitleFromID(bookid)
        titleList.append(booktile)
    return render(request, 'library_website/adminBorrowings.html', {'inputData': titleList})

def adminReservationPage(request):
    global mydb
    mycursor7 = mydb.cursor()
    mycursor7.execute("USE library")

    sql1 = "SELECT bookID FROM Reserve"
    result = 'reserved'
    mycursor7.execute(sql1)
    myresult = mycursor7.fetchall()
    titleList = []
    for i in myresult:
        bookid = i[0]
        booktile = findTitleFromID(bookid)
        titleList.append(booktile)
    return render(request, 'library_website/adminReservations.html', {'inputData': titleList})

def adminFinesPage(request):
    global mydb
    mycursor9 = mydb.cursor()
    mycursor9.execute("USE library")

    sql1 = "SELECT memberID, total_amount FROM fine WHERE total_amount != 0"
    mycursor9.execute(sql1)
    myresult = mycursor9.fetchall()
    titleList = []
    for i in myresult:
        intermediate = []
        userid = i[0]
        userUnpaidFine = i[1]
        intermediate.append(userid)
        intermediate.append(userUnpaidFine)
        titleList.append(intermediate)
    return render(request, 'library_website/adminFines.html', {'inputData': titleList})

def memberPayFinesPage(request):
    global mydb
    global firstTimeOpen
    firstTimeOpen = 0
    mycursor6 = mydb.cursor()
    mycursor6.execute("USE library")
    message = ''
    sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor6.execute(sql1, (str(userLoginName),))
    myresult = mycursor6.fetchall()
    listOfUnPiadFine = []
    listOfUnPiadFine.append(myresult[0][0])
    totalUnpaidFine = myresult[0][0]
    visaPayment = request.POST.get('visaPayment')
    print(type(visaPayment))
    if (visaPayment == None):
        visaPayment = '0'
    elif (visaPayment == ''):
        message = "Please enter the amount you want to pay"
        return render(request, 'library_website/payFines.html',
                      {'totalFines': totalUnpaidFine, 'paymentMessage': message})
    else:
        remainingFineVisa = payFine(float(visaPayment), "Visa")
        if (remainingFineVisa == "You have no unpaid fines!"):
            message = "You have no unpaid fines!"
        elif (remainingFineVisa == "You need to pay the full amount of the fine"):
            message = "You need to pay the full amount of the fine"
        elif (remainingFineVisa == "Your current unpaid fine is less than the number you have entered"):
            message = "The amount you enter is more than the overdue amount, please enter only the amount you own"
        else:
            return render(request, 'library_website/finesPaid.html', {'totalFines': remainingFineVisa})

    masterCardPayment = request.POST.get('mastercardPayment')
    if (masterCardPayment == None):
        masterCardPayment = '0'
    elif (masterCardPayment == ''):
        message = "Please enter the amount you want to pay"
        return render(request, 'library_website/payFines.html',
                      {'totalFines': totalUnpaidFine, 'paymentMessage': message})
    else:
        remainingFineMastercard = payFine(float(masterCardPayment), "Mastercard")
        if (remainingFineMastercard == "You have no unpaid fines!"):
            message = "You have no unpaid fines!"
        elif (remainingFineMastercard == "You need to pay the full amount of the fine"):
            message = "You need to pay the full amount of the fine"
        elif (remainingFineMastercard == "Your current unpaid fine is less than the number you have entered"):
            message = "The amount you enter is more than the overdue amount, please enter only the amount you own"
        else:
            return render(request, 'library_website/finesPaid.html', {'totalFines': remainingFineMastercard})
    return render(request, 'library_website/payFines.html', {'totalFines': totalUnpaidFine, 'paymentMessage': message})

def memberFinesPaidPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    return render(request, 'library_website/finesPaid.html')

def reservedBookPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    global bookID
    global bookAuthor
    global bookTitle
    global bookPulisher
    global bookDate
    global bookPage
    global bookLongDescription
    global bookShortDescription
    global bookCategory
    global bookAvailable
    global bookDueDate
    global bookISBN
    global userLoginName
    if (userLoginName == ''):
        return render(request, 'library_website/BOOK_DETAILSMAINReserved2.html',
                      {'bookID': bookID,
                       'author': bookAuthor,
                       'title': bookTitle,
                       'publisher': bookPulisher,
                       'DateOfPublication': bookDate,
                       'numberOfPages': bookPage,
                       'shortDescription': bookShortDescription,
                       'longDescription': bookLongDescription,
                       'category': bookCategory,
                       'availability': bookAvailable,
                       'dueDate': bookDueDate,
                       'isbn': bookISBN,
                       'resultOfBorrowing': 'You need to sign in to reserve the book'})
    else:
        reserveResult = reserve(bookID, str(userLoginName))
        if (reserveResult == "reserved"):
            return render(request, 'library_website/BOOK_DETAILSMAINReserved.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': 'You have successfully reserved the book'})
        elif (reserveResult == "already reserved"):
            return render(request, 'library_website/BOOK_DETAILSMAINReserved.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': 'You have already reserved the book previous'})
        else:
            reserveBookmessage = 'Reserved unsuccessful, the book has been reserved by someone else'
            if (reserveResult == "unpaidfine"):
                reserveBookmessage = "You have unpaid fines, please pay the fines before borrow or reserve the book"
            return render(request, 'library_website/BOOK_DETAILSMAINReserved.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': reserveBookmessage})


def borrowBookPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    global bookID
    global bookAuthor
    global bookTitle
    global bookPulisher
    global bookDate
    global bookPage
    global bookLongDescription
    global bookShortDescription
    global bookCategory
    global bookAvailable
    global bookDueDate
    global bookISBN
    global userLoginName
    if (userLoginName == ''):
        return render(request, 'library_website/BOOK_DETAILSMAINBorrow2.html',
                      {'bookID': bookID,
                       'author': bookAuthor,
                       'title': bookTitle,
                       'publisher': bookPulisher,
                       'DateOfPublication': bookDate,
                       'numberOfPages': bookPage,
                       'shortDescription': bookShortDescription,
                       'longDescription': bookLongDescription,
                       'category': bookCategory,
                       'availability': bookAvailable,
                       'dueDate': bookDueDate,
                       'isbn': bookISBN,
                       'resultOfBorrowing': 'You need to sign in to borrow the book'})
    else:

        borrowBookResult = borrow(bookID, str(userLoginName))
        if (borrowBookResult == "You have reserved the book before, Do you want to borrow it instead?"):
            borrowBookmessage = "You have reserved the book before, Do you want to borrow it instead?"
            return render(request, 'library_website/BOOK_DETAILSMAINBorrow.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': borrowBookmessage})

        if (borrowBookResult == "The book has been reserved by someone else, You cam neither borrow or reserve it"):
            borrowBookmessage = "The book has been reserved by someone else, You can neither borrow or reserve it"
            return render(request, 'library_website/BOOK_DETAILSMAINBorrow.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': borrowBookmessage})
        if (borrowBookResult == "borrowed"):
            return render(request, 'library_website/BOOK_DETAILSMAINBorrow.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': 'You have successfully borrowed the book'})
        elif (borrowBookResult == "cannot borrow"):
            return render(request, 'library_website/BOOK_DETAILSMAINBorrow.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': 'You cannot borrow more than four books'})
        else:
            borrowBookmessage = 'The book is unavailable for borrow, Do you want to reserve it instead?'
            if (borrowBookResult == "unpaidfine"):
                borrowBookmessage = "You have unpaid fines, please pay the fines before borrowing or reserving the book"
            return render(request, 'library_website/BOOK_DETAILSMAINBorrow.html',
                          {'bookID': bookID,
                           'author': bookAuthor,
                           'title': bookTitle,
                           'publisher': bookPulisher,
                           'DateOfPublication': bookDate,
                           'numberOfPages': bookPage,
                           'shortDescription': bookShortDescription,
                           'longDescription': bookLongDescription,
                           'category': bookCategory,
                           'availability': bookAvailable,
                           'dueDate': bookDueDate,
                           'isbn': bookISBN,
                           'resultOfBorrowing': borrowBookmessage})



def visitorBookDetailsPage(request):
    global firstTimeOpen
    firstTimeOpen = 0
    return render(request, 'library_website/BOOK_DETAILSMAINBorrowed.html')

def returnBook(request):
    data = request.POST.get('returnBook')
    returnBookMessage = "You have successfully returned the book"
    if (data == ''):
        returnBookMessage = "Please enter a valid Book ID to return the book"
    else:
        returnBookMessage = returnBookFunct(int(data))

    mycursor4 = mydb.cursor()
    mycursor4.execute("USE library")
    sql5 = "SELECT bookID FROM Reserve where memberID = %s"
    mycursor4.execute(sql5, (str(userLoginName),))
    myReservationResult = mycursor4.fetchall()
    reservedIDList = []
    reservationBookList = []
    for result in myReservationResult:
        reservedIDList.append(result[0])
        booktitle = findTitleFromID(result[0])
        reservationBookList.append(booktitle)

    sql6 = "SELECT bookID FROM Borrow where memberID = %s"
    mycursor4.execute(sql6, (str(userLoginName),))
    myBorrowResult = mycursor4.fetchall()
    borrowIDList = []
    borrowBookList = []
    for result in myBorrowResult:
        borrowIDList.append((result[0]))
        booktitle = findTitleFromID(result[0])
        borrowBookList.append(booktitle)

    sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor4.execute(sql1, (str(userLoginName),))
    myresult = mycursor4.fetchall()
    listOfUnPiadFine = []
    listOfUnPiadFine.append(myresult[0][0])

    aggregateList = []
    lengthBetweenTwoBooks = max(len(borrowBookList), len(reservationBookList))
    maximumLen = max(lengthBetweenTwoBooks, len(listOfUnPiadFine))
    for t in range(0, maximumLen):
        intermediate = []
        if (t >= (len(reservedIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservedIDList[t])
        if (t >= (len(reservationBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservationBookList[t])
        if (t >= (len(borrowIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowIDList[t])
        if (t >= (len(borrowBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowBookList[t])
        if (t >= (len(listOfUnPiadFine))):
            intermediate.append(' ')
        else:
            intermediate.append(listOfUnPiadFine[t])
        aggregateList.append(intermediate)
    return render(request, 'library_website/myAccount2.html', {'inputData': aggregateList,
                                                               'replyMessage': returnBookMessage})

def cancelReservation(request):
    data = request.POST.get('cancelReservation')
    cancelMessage = "You have successfully cancelled your reservation of the book"
    if (data == ''):
        cancelMessage = "Please enter a valid Book ID to cancel the reservation"
    else:
        cancellationID = int(data)
        cancelMessage = cancelReserve(cancellationID)

    mycursor4 = mydb.cursor()
    mycursor4.execute("USE library")
    sql5 = "SELECT bookID FROM Reserve where memberID = %s"
    mycursor4.execute(sql5, (str(userLoginName),))
    myReservationResult = mycursor4.fetchall()
    reservedIDList = []
    reservationBookList = []
    for result in myReservationResult:
        reservedIDList.append(result[0])
        booktitle = findTitleFromID(result[0])
        reservationBookList.append(booktitle)

    sql6 = "SELECT bookID FROM Borrow where memberID = %s"
    mycursor4.execute(sql6, (str(userLoginName),))
    myBorrowResult = mycursor4.fetchall()
    borrowIDList = []
    borrowBookList = []
    for result in myBorrowResult:
        borrowIDList.append((result[0]))
        booktitle = findTitleFromID(result[0])
        borrowBookList.append(booktitle)

    sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor4.execute(sql1, (str(userLoginName),))
    myresult = mycursor4.fetchall()
    listOfUnPiadFine = []
    listOfUnPiadFine.append(myresult[0][0])

    aggregateList = []
    lengthBetweenTwoBooks = max(len(borrowBookList), len(reservationBookList))
    maximumLen = max(lengthBetweenTwoBooks, len(listOfUnPiadFine))
    for t in range(0, maximumLen):
        intermediate = []
        if (t >= (len(reservedIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservedIDList[t])
        if (t >= (len(reservationBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservationBookList[t])
        if (t >= (len(borrowIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowIDList[t])
        if (t >= (len(borrowBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowBookList[t])
        if (t >= (len(listOfUnPiadFine))):
            intermediate.append(' ')
        else:
            intermediate.append(listOfUnPiadFine[t])
        aggregateList.append(intermediate)
    return render(request, 'library_website/myAccount2.html', {'inputData': aggregateList,
                                                               'replyMessage': cancelMessage})
def extendReturn(request):
    data = request.POST.get('extendReturn')
    cancelMessage = "You have successfully extended the due date of the book"
    if (data == ''):
        cancelMessage = "Please enter a valid Book ID to extend the reservation"
    else:
        cancellationID = int(data)
        cancelMessage = extendDueDate(cancellationID)

    mycursor4 = mydb.cursor()
    mycursor4.execute("USE library")
    sql5 = "SELECT bookID FROM Reserve where memberID = %s"
    mycursor4.execute(sql5, (str(userLoginName),))
    myReservationResult = mycursor4.fetchall()
    reservedIDList = []
    reservationBookList = []
    for result in myReservationResult:
        reservedIDList.append(result[0])
        booktitle = findTitleFromID(result[0])
        reservationBookList.append(booktitle)

    sql6 = "SELECT bookID FROM Borrow where memberID = %s"
    mycursor4.execute(sql6, (str(userLoginName),))
    myBorrowResult = mycursor4.fetchall()
    borrowIDList = []
    borrowBookList = []
    for result in myBorrowResult:
        borrowIDList.append((result[0]))
        booktitle = findTitleFromID(result[0])
        borrowBookList.append(booktitle)

    sql1 = "SELECT total_amount FROM fine WHERE memberID = %s"
    mycursor4.execute(sql1, (str(userLoginName),))
    myresult = mycursor4.fetchall()
    listOfUnPiadFine = []
    listOfUnPiadFine.append(myresult[0][0])

    aggregateList = []
    lengthBetweenTwoBooks = max(len(borrowBookList), len(reservationBookList))
    maximumLen = max(lengthBetweenTwoBooks, len(listOfUnPiadFine))
    for t in range(0, maximumLen):
        intermediate = []
        if (t >= (len(reservedIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservedIDList[t])
        if (t >= (len(reservationBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(reservationBookList[t])
        if (t >= (len(borrowIDList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowIDList[t])
        if (t >= (len(borrowBookList))):
            intermediate.append(' ')
        else:
            intermediate.append(borrowBookList[t])
        if (t >= (len(listOfUnPiadFine))):
            intermediate.append(' ')
        else:
            intermediate.append(listOfUnPiadFine[t])
        aggregateList.append(intermediate)
    return render(request, 'library_website/myAccount2.html', {'inputData': aggregateList,
                                                               'replyMessage': cancelMessage})

def logoutView(request):
    global firstTimeOpen
    firstTimeOpen = 0
    global userLoginName
    if request.method == "POST":
        userLoginName = ''
        logout(request)  # this logs the user out
        return redirect(
            "library_homePage"
        )  # this redirects the user to the welcome page
