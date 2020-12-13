import psycopg2
import csv

# Enter your username and password for your Postgres database
postgresConnection = psycopg2.connect(
    user='postgres', password='', database='lms')
cursor = postgresConnection.cursor()

with open('books.csv') as csvfile:
    booksCsv = csv.reader(csvfile, delimiter='	')
    authorId = 0
    for row in booksCsv:
        query = 'insert into book values(%s,%s,%s)'
        isbn = row[0]
        title = row[2]
        authors = row[3]
        cursor.execute(query, (isbn, title, False))
        authorList = authors.split(",")
        for author in authorList:
            query1 = 'insert into authors values(%s,%s)'
            authorId = authorId+1
            cursor.execute(query1, (authorId, author))
            query2 = 'insert into book_authors values(%s,%s)'
            cursor.execute(query2, (isbn, authorId))

postgresConnection.commit()
cursor.close()
postgresConnection.close()
