from flask import Flask
from flask import jsonify
from flask import request
import psycopg2
from psycopg2.extras import RealDictCursor
import errorCodes
import datetime

app = Flask(__name__)

def openConnection():
    psqlConnection = psycopg2.connect(user='postgres', password='', database='lms')
    return psqlConnection

@app.route("/searchBook", methods=['GET', 'POST'])
def searchBook():
    psqlConnection = openConnection()
    searchString = request.args.get('searchString')
    resultSet = []
    query1 = 'select b.isbn from book b left outer join book_authors ba on b.isbn = ba.isbn left outer join authors a on ba.author_id = a.author_id where b.isbn like %s or b.title like %s or a.name like %s'
    isbnList = []
    try:
        cursor = psqlConnection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query1, ("%" + searchString + "%", "%" + searchString + "%", "%" + searchString + "%"))
        for row in cursor:
            isbnList.append(row['isbn'])
        if len(isbnList) > 0:
            uniqueIsbnList = list(set(isbnList))
            stringFormat = '(' + ','.join(['%s'] * len(uniqueIsbnList)) + ')'
            query2 = 'select b.isbn,b.title,array_agg(a.name), b.is_checked_out from book b left outer join book_authors ba on b.isbn = ba.isbn left outer join authors a on ba.author_id = a.author_id where b.isbn IN ' + stringFormat + ' group by b.isbn'
            cursor.execute(query2, tuple(uniqueIsbnList))
            for row in cursor:
                resultSet.append(row)
            response = {'searchResult': resultSet, 'message': 'search success', 'success': True}
        else:
            response = {'searchResult': None, 'message': 'search success', 'success': True}
    except psycopg2.Error as err:
        response = {'searchResult': None, 'message': 'search failed', 'success': False, 'errorCode': err.pgcode}
    finally:
        if psqlConnection is not None:
            psqlConnection.close()

    return jsonify(response)


@app.route("/checkoutBook", methods=['GET', 'POST'])
def checkoutBook():
    psqlConnection = openConnection()
    data = request.json
    cardId = data["cardId"]
    isbn = data["isbn"]
    response = None
    try:
        cursor = psqlConnection.cursor()
        query = 'select 1 from borrower where card_id = %s'
        cursor.execute(query, (cardId,))
        isBorrower = 0
        for row in cursor:
            isBorrower = row[0]
        if isBorrower:
            query = 'select is_checked_out from book where isbn = %s'
            isCheckedOut = 1
            cursor.execute(query, (isbn,))
            for row in cursor:
                isCheckedOut = row[0]
            query = 'select count(*) >= 3 from book_loans where card_id = %s and date_in is null'
            isCountExceeded = 1
            cursor.execute(query, (cardId,))
            for row in cursor:
                isCountExceeded = row[0]
            if isCheckedOut:
                response = {'message': 'Sorry, selected book is already checked out!', 'success': False}
            elif isCountExceeded:
                response = {'message': 'Sorry, a borrower is permitted a maximum of 3 book loans!', 'success': False}
            else:
                query1 = 'Insert into book_loans(isbn, card_id, date_out, due_date, date_in) values(%s,%s,%s,%s,null)'
                query2 = 'update book set is_checked_out = true where isbn = %s'
                dateOut = datetime.date.today()
                dueDate = dateOut + datetime.timedelta(days=14)
                cursor.execute(query1, (isbn, cardId, dateOut, dueDate))
                cursor.execute(query2, (isbn,))
                psqlConnection.commit()
                response = {'message': 'book checked out', 'success': True}
        else:
            response = {'message': 'Borrower with entered card id does not exist', 'success': False}
    except psycopg2.Error as err:
            response = {'message': 'Borrower creation failed', 'success': False, 'errorCode': err.pgcode}
    finally:
        if psqlConnection is not None:
            psqlConnection.close()
    return jsonify(response)


@app.route("/searchBookLoan", methods=['GET', 'POST'])
def searchBookLoan():
    psqlConnection = openConnection()
    searchString = request.args.get('searchString')
    resultSet = []
    query = 'select bl.loan_id,bl.isbn,bl.card_id,b.bname,bl.date_out,bl.due_date from book_loans bl join borrower b on bl.card_id = b.card_id where (bl.isbn like %s or bl.card_id = %s or b.bname like %s) and date_in is null'
    try:
        cursor = psqlConnection.cursor(cursor_factory=RealDictCursor)
        if searchString.isdigit():
            cursor.execute(query, ("%" + searchString + "%", searchString, "%" + searchString + "%"))
        else:
            cursor.execute(query, ("%" + searchString + "%", 0, "%" + searchString + "%"))
        for row in cursor:
            resultSet.append(row)
        response = {'searchResult': resultSet, 'message': 'search success', 'success': True}
    except psycopg2.Error as err:
        response = {'searchResult': None, 'message': 'searchFailed', 'success': False, 'errorCode': err.pgcode}
    finally:
        if psqlConnection is not None:
            psqlConnection.close()
    return jsonify(response)


@app.route("/checkinBook", methods=['GET', 'POST'])
def checkinBook():
    data = request.json
    loanId = data["loanId"]
    response = None
    stringFormat = ','.join(['%s'] * len(loanId))
    query1 = 'update book_loans set date_in = current_date where loan_id in (%s)'
    query2 = 'update book set is_checked_out = false where isbn in (select isbn from book_loans where loan_id in (%s))'
    psqlConnection = openConnection()
    try:
        cursor = psqlConnection.cursor()
        cursor.execute(query1 % stringFormat, tuple(loanId))
        cursor.execute(query2 % stringFormat, tuple(loanId))
        psqlConnection.commit()
        response = {'message': 'Checked in successfully', 'success': True}
    except psycopg2.connector.Error as err:
        response = {'message': 'Failed to check in', 'success': False, 'errorCode': err.pgcode}
    finally:
        if psqlConnection is not None:
            psqlConnection.close()
    return jsonify(response)


@app.route('/addBorrower', methods=['POST'])
def addBorrower():
    psqlConnection = openConnection()
    data = request.json
    query = "insert into borrower(ssn,bname,address,phone) values(%s,%s,%s,%s)"
    response = None
    try:
        cursor = psqlConnection.cursor()
        cursor.execute(query, (data["ssn"], data["name"], data["address"], data["phone"]))
        response = {'message': 'Borrower added successfully', 'success': True}
        psqlConnection.commit()
    except psycopg2.Error as err:
        if err.pgcode == '23505':
            response = {'message': 'Borrower already exists', 'success': False, 'errorCode': err.pgcode}
        else:
            response = {'message': 'Failed to create borrower', 'success': False, 'errorCode': err.pgcode}
    finally:
        if psqlConnection is not None:
            psqlConnection.close()
    return jsonify(response)


def updateFineInfo():
    query = 'select loan_id, due_date, date_in from book_loans where date_in > due_date or current_date > due_date and date_in is null'
    psqlConnection = openConnection()
    cursor = psqlConnection.cursor()
    cursor.execute(query)
    today = datetime.date.today()
    rows = cursor.fetchall()
    for row in rows:
        if row[2] is None:
            dateDifference = today - row[1]
            fine = round(dateDifference.days * 0.25, 2)
        else:
            dateDifference = row[2] - row[1]
            fine = round(dateDifference.days * 0.25, 2)
        query = 'select count(*) from fines where loan_id = %s'
        cursor.execute(query, [row[0]])
        rowCount = 0
        for r in cursor:
            rowCount = r[0]
        if rowCount == 0:
            try:
                query = 'insert into fines values(%s,%s,%s)'
                cursor.execute(query, (row[0], fine, False))
                psqlConnection.commit()
            except psycopg2.Error as err:
                print(err)
        else:
            try:
                query = 'update fines set fine_amt = %s where loan_id = %s and paid = false'
                cursor.execute(query, (fine, row[0]))
                psqlConnection.commit()
            except psycopg2.Error as err:
                print(err)
    query = 'select loan_id from book_loans where current_date <= due_date and date_in is null'
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        try:
            query = 'delete from fines where loan_id = %s and paid = false'
            cursor.execute(query, [row[0]])
            psqlConnection.commit()
        except psycopg2.Error as err:
            print(err)
    psqlConnection.close()


@app.route("/fetchFines", methods=['GET', 'POST'])
def fetchFines():
    updateFineInfo()
    psqlConnection = openConnection()
    try:
        cursor = psqlConnection.cursor(cursor_factory=RealDictCursor)
        query = 'select b.card_id,b.bname,SUM(f.fine_amt) from fines f join book_loans bl on f.loan_id = bl.loan_id join borrower b on bl.card_id = b.card_id where f.paid=false group by b.card_id'
        cursor.execute(query)
        rows = cursor.fetchall()
        resultSet = []
        childMap = {}
        for row in rows:
            query = 'select bl.loan_id,b.bname,f.fine_amt,bl.date_in from fines f join book_loans bl on f.Loan_id = bl.Loan_id join borrower b on bl.card_id = b.Card_id where f.paid=false and b.card_id=%s'
            cardId = row['card_id']
            cursor.execute(query, (cardId,))
            childSet = []
            for childRow in cursor:
                childSet.append(childRow)
            childMap[cardId] = childSet
            resultSet.append(row)
        response = {'aggregateTable': resultSet, 'childTable': childMap, 'message': 'fines update',
                    'success': True}
    except psycopg2.Error as err:
        response = {'message': 'Failed to fetch fines', 'success': False, 'errorCode': err.pgcode}
    return jsonify(response)


@app.route("/settleFines", methods=['GET', 'POST'])
def settleFines():
    data = request.json
    loanId = data["loanId"]
    response = None
    stringFormat = ','.join(['%s'] * len(loanId))
    query = 'update fines set paid = true where loan_id in (%s)'
    psqlConnection = openConnection()
    try:
        cursor = psqlConnection.cursor()
        cursor.execute(query % stringFormat, tuple(loanId))
        psqlConnection.commit()
        response = {'message': 'fine settled', 'success': True}
    except psycopg2.Error as err:
        response = {'message': 'Fine settlement failed', 'success': False, 'errorCode': err.pgcode}
    return jsonify(response)


if __name__ == "__main__":
    app.run()
