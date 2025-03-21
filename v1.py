import streamlit as st
import psycopg2
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import urllib.parse
import time

def verify_postgres_connection(host, port, database, user, password, ssl_mode=False):
    try:
        if ssl_mode:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                sslmode='require'
            )
        else:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
        return True, "Successfully connected to PostgreSQL database"
    except Exception as e:
        return False, f"Failed to connect to PostgreSQL database: {str(e)}"

def verify_mysql_connection(host, port, database, user, password, ssl_mode=False):
    try:
        if ssl_mode:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                ssl_ca='path_to_ssl_ca',
                ssl_cert='path_to_ssl_cert',
                ssl_key='path_to_ssl_key',
            )
        else:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
        return True, "Successfully connected to MySQL database"
    except Error as e:
        return False, f"Failed to connect to MySQL database: {e}"

def verify_mongodb_connection(host, port, database, user=None, password=None):
    try:
        if user and password:
            uri = f"mongodb://{urllib.parse.quote(user)}:{urllib.parse.quote(password)}@{host}:{port}/"
            client = MongoClient(uri)
            db = client[database]
            db.command('ping')
            return True, "Successfully connected to MongoDB database"
        else:
            client = MongoClient(host, port)
            db = client[database]
            db.command('ping')
            return True, "Successfully connected to MongoDB database"
    except Exception as e:
        return False, f"Failed to connect to MongoDB database: {str(e)}"

def parse_database_uri(uri, database_type):
    try:
        parsed = urllib.parse.urlparse(uri)
        if database_type == 'PostgreSQL':
            credentials = parsed.username and parsed.password
            if not credentials:
                return False, "Missing username or password in URI"
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.strip('/')
            if not database:
                return False, "Database name is required"
            ssl_mode = 'sslmode' in parsed.query and parsed.query.split('sslmode=')[1] == 'require'
            return True, {
                'host': host,
                'port': port,
                'database': database,
                'user': parsed.username,
                'password': parsed.password,
                'ssl_mode': ssl_mode
            }
        elif database_type == 'MySQL':
            credentials = parsed.username and parsed.password
            if not credentials:
                return False, "Missing username or password in URI"
            host = parsed.hostname
            port = parsed.port or 3306
            database = parsed.path.strip('/')
            if not database:
                return False, "Database name is required"
            return True, {
                'host': host,
                'port': port,
                'database': database,
                'user': parsed.username,
                'password': parsed.password
            }
        elif database_type == 'MongoDB':
            credentials = parsed.username and parsed.password
            host = parsed.hostname
            port = parsed.port or 27017
            database = parsed.path.strip('/')
            if not database:
                return False, "Database name is required"
            return True, {
                'host': host,
                'port': port,
                'database': database,
                'user': parsed.username if credentials else None,
                'password': parsed.password if credentials else None
            }
        else:
            return False, f"Unsupported database type: {database_type}"
    except Exception as e:
        return False, f"Failed to parse URI: {str(e)}"

def main():
    st.title("Database Connection Verifier")
    
    st.markdown("### Select the database type:")
    database_type = st.selectbox("Choose your database type", ['PostgreSQL', 'MySQL', 'MongoDB'])
    
    st.markdown("### Database Connection Settings:")
    
    input_method = st.selectbox("Input Method", ["Manual", "URI"])
    
    if input_method == "Manual":
        if database_type == 'PostgreSQL':
            host = st.text_input("Host", placeholder="localhost")
            port = st.text_input("Port", placeholder="5432")
            database = st.text_input("Database name", placeholder="mydatabase")
            user = st.text_input("User")
            password = st.text_input("Password", type="password")
            ssl_mode = st.checkbox("Use SSL?")
            
            if st.button("Verify Connection"):
                with st.spinner("Verifying PostgreSQL connection..."):
                    success, message = verify_postgres_connection(host, port, database, user, password, ssl_mode)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        elif database_type == 'MySQL':
            host = st.text_input("Host", placeholder="localhost")
            port = st.text_input("Port", placeholder="3306")
            database = st.text_input("Database name", placeholder="mydatabase")
            user = st.text_input("User")
            password = st.text_input("Password", type="password")
            ssl_mode = st.checkbox("Use SSL?")
            
            if st.button("Verify Connection"):
                with st.spinner("Verifying MySQL connection..."):
                    success, message = verify_mysql_connection(host, int(port), database, user, password, ssl_mode)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        elif database_type == 'MongoDB':
            host = st.text_input("Host", placeholder="localhost")
            port = st.text_input("Port", placeholder="27017")
            database = st.text_input("Database name", placeholder="mydatabase")
            user = st.text_input("User (optional)")
            password = st.text_input("Password (optional)", type="password")
            
            if st.button("Verify Connection"):
                with st.spinner("Verifying MongoDB connection..."):
                    success, message = verify_mongodb_connection(host, int(port) if port else 27017, database, user, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    elif input_method == "URI":
        uri = st.text_input("Database Connection URI", placeholder="e.g., postgres://user:password@host:port/database?sslmode=require")
        if uri:
            with st.spinner("Parsing URI..."):
                success, details = parse_database_uri(uri, database_type)
                if not success:
                    st.error(details)
                else:
                    st.write("Parsed Details:")
                    for key, value in details.items():
                        st.write(f"{key}: {value}")
                    
                    verify_button = st.button("Verify Connection from URI")
                    if verify_button:
                        with st.spinner("Verifying connection from URI..."):
                            if database_type == 'PostgreSQL':
                                success, message = verify_postgres_connection(details['host'], details['port'], details['database'], details['user'], details['password'], details['ssl_mode'])
                            elif database_type == 'MySQL':
                                success, message = verify_mysql_connection(details['host'], details['port'], details['database'], details['user'], details['password'])
                            elif database_type == 'MongoDB':
                                success, message = verify_mongodb_connection(details['host'], details['port'], details['database'], details['user'], details['password'])
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

if __name__ == "__main__":
    main()