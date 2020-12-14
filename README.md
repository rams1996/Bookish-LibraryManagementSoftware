Bookish - Online Catalogue

Environment setup:

    Front end setup:
        - Install NodeJs from https://nodejs.org/en/download/

        - Install Angular CLI using the command:
          npm install -g @angular/cli. 

        - Navigate to LibraryManagementSystem/FrontEnd and issue command:
         npm install
       (This will install the necessary dependencies present in package.json file)

        - Disable CORS on Chrome by installing this extension (Allow cross origin requests on Chrome)
          https://chrome.google.com/webstore/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf?hl=en

        - In LibraryManagementSystem/FrontEnd, issue command
          npm start
         (Angular application will now run on localhost:4200)

    Postgres Setup:
        - Install Postgres from here: https://www.postgresql.org/download/ 
        - Install pgAdmin4 from here: https://www.pgadmin.org
          (GUI Client to interface with Postgres Database)
        - Restore database from the backup script LibraryManagementSystem.sql file present in the projecy   directory

    Flask setup:
        - Download the latest version of Python3 and install:
          https://www.python.org/downloads/

        - Install the Python Flask package with the command
          pip3 install flask 

        - Install the Python Postgres connection adaptor with the command
          pip3 install psycopg2

        - To run the flask server, navigate to LibraryManagementSystem/Server and issue command
          python server.py  

        - Enter username and password for the database in the connection constructor in server.py and in load data scripts

    Data setup:
        - Navigate to LibraryManagementSystem/Data

        - Open terminal in this directory and run loadBooksDataToPostgres.py 
          python loadBooksDataToPostgres
          (To fetch records from books.csv)

        - Open terminal in this directory and run loadBorrowerDataToPostgres.py 
          python loadBorrowerDataToPostgres
          (To fetch records from borrowers.csv) [ Note: Remove the row containing the headers and then import]





