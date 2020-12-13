import psycopg2
import csv

# Enter your username and password for your database
postgresConnection = psycopg2.connect(
    user='postgres', password='', database='lms')
cursor = postgresConnection.cursor()

with open('borrowers.csv') as csvfile:
    borrowerData = csv.reader(csvfile, delimiter=',')
    for row in borrowerData:
        query = 'insert into borrower(ssn,bname,address,phone) values(%s,%s,%s,%s)'
        ssn = ''.join(row[1].split()).replace(
            '-', '').replace('(', '').replace(')', '')
        name = row[2] + ' ' + row[3]
        address = row[5] + ',' + row[6] + ',' + row[7]
        phone = ''.join(row[8].split()).replace(
            '-', '').replace('(', '').replace(')', '')
        cursor.execute(query, (ssn, name, address, phone))

postgresConnection.commit()
cursor.close()
postgresConnection.close()
