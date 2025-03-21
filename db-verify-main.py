import streamlit as st
import sqlalchemy
import pymongo
import pymysql
import psycopg2
import sqlite3
import os
from urllib.parse import urlparse
from sqlalchemy.engine.url import make_url

# Configure page
st.set_page_config(
    page_title="Database Connection Checker",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("Database Connection Checker")
st.markdown("Verify connection to different database systems")

# Database type selection
db_type = st.selectbox(
    "Select Database Type",
    ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Microsoft SQL Server", "Oracle"],
    index=0
)

# Connection method tabs
conn_method = st.radio(
    "Connection Method",
    ["Connection URI", "Connection Details"],
    horizontal=True
)

# Show appropriate input fields based on selection
if conn_method == "Connection URI":
    uri = st.text_input("Connection URI", placeholder="e.g. mysql://user:password@host:port/dbname")
    
    # Display example URI format based on selected database
    if db_type == "MySQL":
        st.caption("Example URI format: mysql://username:password@hostname:3306/database_name")
    elif db_type == "PostgreSQL":
        st.caption("Example URI format: postgresql://username:password@hostname:5432/database_name")
    elif db_type == "MongoDB":
        st.caption("Example URI format: mongodb://username:password@hostname:27017/database_name")
else:
    # Connection details input fields
    col1, col2 = st.columns(2)
    
    with col1:
        host = st.text_input("Host", "localhost")
        username = st.text_input("Username")
        database = st.text_input("Database Name")
    
    with col2:
        # Set default port based on database type
        default_ports = {
            "MySQL": "3306", 
            "PostgreSQL": "5432", 
            "MongoDB": "27017",
            "SQLite": "", # SQLite doesn't use ports
            "Microsoft SQL Server": "1433",
            "Oracle": "1521"
        }
        
        port = st.text_input(
            "Port", 
            value=default_ports.get(db_type, "")
        )
        password = st.text_input("Password", type="password")
    
    # Additional security options section
    st.subheader("Security Options")
    
    # SSL/TLS options
    use_ssl = st.checkbox("Use SSL/TLS", value=False)
    
    if use_ssl:
        ssl_col1, ssl_col2 = st.columns(2)
        
        with ssl_col1:
            ssl_verify = st.selectbox(
                "SSL Verification",
                ["Verify CA", "Verify Full", "Verify None"],
                index=0
            )
            
            if ssl_verify != "Verify None":
                ca_cert = st.text_input("CA Certificate Path (optional)")
        
        with ssl_col2:
            client_cert = st.text_input("Client Certificate Path (optional)")
            client_key = st.text_input("Client Key Path (optional)")
    
    # Database-specific additional options
    if db_type == "MongoDB":
        auth_source = st.text_input("Authentication Database (optional)", "admin")
        replica_set = st.text_input("Replica Set Name (optional)")
    
    elif db_type == "SQLite":
        if conn_method == "Connection Details":
            sqlite_file = st.text_input("SQLite Database File Path", "database.db")
            create_if_not_exists = st.checkbox("Create file if it doesn't exist", value=True)
    
    elif db_type == "Oracle":
        service_name = st.text_input("Service Name (optional)")
        sid = st.text_input("SID (optional)")

# Test connection button
test_button = st.button("Test Connection", type="primary", use_container_width=True)

# Function to test MySQL connection
def test_mysql_connection(host, port, user, password, database=None, uri=None, ssl_options=None):
    try:
        if uri:
            # Add SSL options to URI if provided
            if ssl_options and ssl_options.get('use_ssl'):
                parsed_url = make_url(uri)
                query_params = parsed_url.query
                
                # Add SSL parameters
                query_params['ssl'] = 'true'
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    query_params['ssl_ca'] = ssl_options.get('ca_cert')
                if ssl_options.get('client_cert'):
                    query_params['ssl_cert'] = ssl_options.get('client_cert')
                if ssl_options.get('client_key'):
                    query_params['ssl_key'] = ssl_options.get('client_key')
                
                # Set verify mode
                if ssl_options.get('ssl_verify') == "Verify None":
                    query_params['ssl_verify_cert'] = 'false'
                
                # Rebuild the URI with SSL parameters
                uri = str(parsed_url)
            
            engine = sqlalchemy.create_engine(uri)
            conn = engine.connect()
        else:
            conn_args = {
                'host': host,
                'port': int(port),
                'user': user,
                'password': password
            }
            
            if database:
                conn_args['database'] = database
            
            # Add SSL options if provided
            if ssl_options and ssl_options.get('use_ssl'):
                ssl_context = {}
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    ssl_context['ca'] = ssl_options.get('ca_cert')
                if ssl_options.get('client_cert'):
                    ssl_context['cert'] = ssl_options.get('client_cert')
                if ssl_options.get('client_key'):
                    ssl_context['key'] = ssl_options.get('client_key')
                
                # Set verify mode
                if ssl_options.get('ssl_verify') == "Verify None":
                    ssl_context['check_hostname'] = False
                
                if ssl_context:
                    conn_args['ssl'] = ssl_context
                else:
                    conn_args['ssl_disabled'] = False
                
            conn = pymysql.connect(**conn_args)
            
        # Test the connection by executing a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True, "Successfully connected to MySQL database!"
    except Exception as e:
        return False, f"Error connecting to MySQL database: {str(e)}"

# Function to test PostgreSQL connection
def test_postgres_connection(host, port, user, password, database=None, uri=None, ssl_options=None):
    try:
        if uri:
            # Add SSL options to URI if provided
            if ssl_options and ssl_options.get('use_ssl'):
                parsed_url = make_url(uri)
                query_params = parsed_url.query
                
                # Add SSL mode
                if ssl_options.get('ssl_verify') == "Verify CA":
                    query_params['sslmode'] = 'verify-ca'
                elif ssl_options.get('ssl_verify') == "Verify Full":
                    query_params['sslmode'] = 'verify-full'
                elif ssl_options.get('ssl_verify') == "Verify None":
                    query_params['sslmode'] = 'require'
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    query_params['sslrootcert'] = ssl_options.get('ca_cert')
                if ssl_options.get('client_cert'):
                    query_params['sslcert'] = ssl_options.get('client_cert')
                if ssl_options.get('client_key'):
                    query_params['sslkey'] = ssl_options.get('client_key')
                
                # Rebuild the URI with SSL parameters
                uri = str(parsed_url)
            
            engine = sqlalchemy.create_engine(uri)
            conn = engine.connect()
        else:
            conn_args = {
                'host': host,
                'port': int(port),
                'user': user,
                'password': password
            }
            
            if database:
                conn_args['dbname'] = database
            
            # Add SSL options if provided
            if ssl_options and ssl_options.get('use_ssl'):
                if ssl_options.get('ssl_verify') == "Verify CA":
                    conn_args['sslmode'] = 'verify-ca'
                elif ssl_options.get('ssl_verify') == "Verify Full":
                    conn_args['sslmode'] = 'verify-full'
                elif ssl_options.get('ssl_verify') == "Verify None":
                    conn_args['sslmode'] = 'require'
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    conn_args['sslrootcert'] = ssl_options.get('ca_cert')
                if ssl_options.get('client_cert'):
                    conn_args['sslcert'] = ssl_options.get('client_cert')
                if ssl_options.get('client_key'):
                    conn_args['sslkey'] = ssl_options.get('client_key')
            
            conn = psycopg2.connect(**conn_args)
            
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True, "Successfully connected to PostgreSQL database!"
    except Exception as e:
        return False, f"Error connecting to PostgreSQL database: {str(e)}"

# Function to test MongoDB connection
def test_mongodb_connection(host, port, user, password, database=None, auth_source="admin", uri=None, ssl_options=None, replica_set=None):
    try:
        if uri:
            # Add SSL options to URI if provided
            if ssl_options and ssl_options.get('use_ssl'):
                # Parse the URI to check if it already contains query parameters
                if '?' in uri:
                    uri += '&ssl=true'
                else:
                    uri += '?ssl=true'
                
                # Add SSL verification option
                if ssl_options.get('ssl_verify') == "Verify None":
                    uri += '&tlsAllowInvalidCertificates=true'
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    uri += f'&tlsCAFile={ssl_options.get("ca_cert")}'
                if ssl_options.get('client_cert'):
                    uri += f'&tlsCertificateKeyFile={ssl_options.get("client_cert")}'
            
            client = pymongo.MongoClient(uri)
        else:
            # Create connection options
            conn_options = {}
            
            # Add SSL options if provided
            if ssl_options and ssl_options.get('use_ssl'):
                conn_options['ssl'] = True
                
                if ssl_options.get('ssl_verify') == "Verify None":
                    conn_options['tlsAllowInvalidCertificates'] = True
                
                # Add certificate paths if provided
                if ssl_options.get('ca_cert'):
                    conn_options['tlsCAFile'] = ssl_options.get('ca_cert')
                if ssl_options.get('client_cert'):
                    conn_options['tlsCertificateKeyFile'] = ssl_options.get('client_cert')
            
            # Add replica set if provided
            if replica_set:
                conn_options['replicaSet'] = replica_set
                
            # Create MongoDB connection string
            if user and password:
                connection_string = f"mongodb://{user}:{password}@{host}:{port}/{database or ''}?authSource={auth_source}"
            else:
                connection_string = f"mongodb://{host}:{port}/{database or ''}"
                
            client = pymongo.MongoClient(connection_string, **conn_options)
        
        # Test connection by getting server info
        server_info = client.server_info()
        
        # Close connection
        client.close()
        
        return True, "Successfully connected to MongoDB server!"
    except Exception as e:
        return False, f"Error connecting to MongoDB server: {str(e)}"

# Function to test SQLite connection
def test_sqlite_connection(database_path, create_if_not_exists=False):
    try:
        if not os.path.exists(database_path) and not create_if_not_exists:
            return False, f"SQLite database file not found: {database_path}"
        
        # Connect to SQLite database
        conn = sqlite3.connect(database_path)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True, f"Successfully connected to SQLite database (version: {version[0]})!"
    except Exception as e:
        return False, f"Error connecting to SQLite database: {str(e)}"

# Function to test Microsoft SQL Server connection
def test_mssql_connection(host, port, user, password, database=None, uri=None, ssl_options=None):
    try:
        if uri:
            # Add SSL options to URI if provided
            if ssl_options and ssl_options.get('use_ssl'):
                # Ensure we're using encrypt=true for SSL
                if '?' in uri:
                    uri += '&encrypt=true'
                else:
                    uri += '?encrypt=true'
                
                # Add trust server certificate option for Verify None
                if ssl_options.get('ssl_verify') == "Verify None":
                    uri += '&trustServerCertificate=true'
            
            engine = sqlalchemy.create_engine(uri)
            conn = engine.connect()
        else:
            # Construct the connection string
            conn_str = f"mssql+pyodbc://{user}:{password}@{host}:{port}"
            if database:
                conn_str += f"/{database}"
            
            # Add driver information
            conn_str += "?driver=ODBC+Driver+17+for+SQL+Server"
            
            # Add SSL options if provided
            if ssl_options and ssl_options.get('use_ssl'):
                conn_str += "&encrypt=true"
                
                # Add trust server certificate option for Verify None
                if ssl_options.get('ssl_verify') == "Verify None":
                    conn_str += "&trustServerCertificate=true"
            
            engine = sqlalchemy.create_engine(conn_str)
            conn = engine.connect()
        
        # Test the connection with a simple query
        result = conn.execute(sqlalchemy.text("SELECT @@VERSION"))
        version = result.scalar()
        
        # Close connection
        conn.close()
        
        return True, f"Successfully connected to Microsoft SQL Server!"
    except Exception as e:
        return False, f"Error connecting to Microsoft SQL Server: {str(e)}"

# Function to test Oracle connection
def test_oracle_connection(host, port, user, password, service_name=None, sid=None, uri=None, ssl_options=None):
    try:
        if uri:
            engine = sqlalchemy.create_engine(uri)
            conn = engine.connect()
        else:
            # Determine if we're using service name or SID
            if service_name:
                # Format for service name
                dsn = f"{host}:{port}/{service_name}"
            elif sid:
                # Format for SID
                dsn = f"{host}:{port}:{sid}"
            else:
                return False, "Either Service Name or SID must be provided for Oracle connection"
            
            # Construct the connection string
            conn_str = f"oracle+cx_oracle://{user}:{password}@{dsn}"
            
            # Add SSL options if provided
            if ssl_options and ssl_options.get('use_ssl'):
                conn_str += "?ssl=true"
                
                # Add certificate paths if provided
                if ssl_options.get('wallet_location'):
                    conn_str += f"&wallet_location={ssl_options.get('wallet_location')}"
            
            engine = sqlalchemy.create_engine(conn_str)
            conn = engine.connect()
        
        # Test the connection with a simple query
        result = conn.execute(sqlalchemy.text("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1"))
        version = result.scalar()
        
        # Close connection
        conn.close()
        
        return True, "Successfully connected to Oracle database!"
    except Exception as e:
        return False, f"Error connecting to Oracle database: {str(e)}"

# Process the connection test when button is clicked
if test_button:
    with st.spinner("Testing connection..."):
        # Create SSL options dictionary if SSL is enabled
        ssl_options = None
        if conn_method == "Connection Details" and 'use_ssl' in locals() and use_ssl:
            ssl_options = {
                'use_ssl': True,
                'ssl_verify': ssl_verify if 'ssl_verify' in locals() else "Verify CA"
            }
            
            # Add certificate paths if provided
            if 'ca_cert' in locals() and ca_cert:
                ssl_options['ca_cert'] = ca_cert
            if 'client_cert' in locals() and client_cert:
                ssl_options['client_cert'] = client_cert
            if 'client_key' in locals() and client_key:
                ssl_options['client_key'] = client_key
        
        if conn_method == "Connection URI":
            if not uri:
                st.error("Please enter a connection URI")
            else:
                # Parse URI to get database type
                parsed_uri = urlparse(uri)
                scheme = parsed_uri.scheme
                
                if db_type == "MySQL" and scheme in ["mysql", "mysql+pymysql"]:
                    success, message = test_mysql_connection(None, None, None, None, uri=uri, ssl_options=ssl_options)
                elif db_type == "PostgreSQL" and scheme in ["postgresql", "postgres"]:
                    success, message = test_postgres_connection(None, None, None, None, uri=uri, ssl_options=ssl_options)
                elif db_type == "MongoDB" and scheme == "mongodb":
                    success, message = test_mongodb_connection(None, None, None, None, uri=uri, ssl_options=ssl_options)
                elif db_type == "Microsoft SQL Server" and scheme in ["mssql", "mssql+pyodbc"]:
                    success, message = test_mssql_connection(None, None, None, None, uri=uri, ssl_options=ssl_options)
                elif db_type == "Oracle" and scheme in ["oracle", "oracle+cx_oracle"]:
                    success, message = test_oracle_connection(None, None, None, None, uri=uri, ssl_options=ssl_options)
                elif db_type == "SQLite" and (scheme == "sqlite" or parsed_uri.path):
                    db_path = parsed_uri.path
                    if db_path.startswith('/'):
                        db_path = db_path[1:]  # Remove leading slash
                    success, message = test_sqlite_connection(db_path)
                else:
                    success = False
                    message = f"URI scheme '{scheme}' does not match selected database type '{db_type}'"
                    
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:  # Connection Details
            # Special case for SQLite which doesn't require host/port
            if db_type == "SQLite":
                if 'sqlite_file' not in locals() or not sqlite_file:
                    st.error("Please enter a SQLite database file path")
                else:
                    create_if_not_exists_val = create_if_not_exists if 'create_if_not_exists' in locals() else False
                    success, message = test_sqlite_connection(sqlite_file, create_if_not_exists_val)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            # All other database types require host and port
            elif not host or (not port and db_type != "SQLite"):
                st.error("Host and port are required")
            else:
                if db_type == "MySQL":
                    success, message = test_mysql_connection(
                        host, port, username, password, database, ssl_options=ssl_options
                    )
                elif db_type == "PostgreSQL":
                    success, message = test_postgres_connection(
                        host, port, username, password, database, ssl_options=ssl_options
                    )
                elif db_type == "MongoDB":
                    auth_source_val = auth_source if 'auth_source' in locals() else "admin"
                    replica_set_val = replica_set if 'replica_set' in locals() else None
                    success, message = test_mongodb_connection(
                        host, port, username, password, database, auth_source_val, 
                        ssl_options=ssl_options, replica_set=replica_set_val
                    )
                elif db_type == "Microsoft SQL Server":
                    success, message = test_mssql_connection(
                        host, port, username, password, database, ssl_options=ssl_options
                    )
                elif db_type == "Oracle":
                    service_name_val = service_name if 'service_name' in locals() else None
                    sid_val = sid if 'sid' in locals() else None
                    success, message = test_oracle_connection(
                        host, port, username, password, service_name_val, sid_val, ssl_options=ssl_options
                    )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Display connection information section
with st.expander("Connection Information"):
    st.markdown("""
    ### Default Database Ports
    
    - **MySQL**: Default port is 3306
    - **PostgreSQL**: Default port is 5432
    - **MongoDB**: Default port is 27017
    - **Microsoft SQL Server**: Default port is 1433
    - **Oracle**: Default port is 1521
    - **SQLite**: No port required (file-based database)
    
    ### SSL/TLS Information
    
    - **Verify CA**: Verifies that the certificate presented by the server was signed by a trusted CA
    - **Verify Full**: Verifies that the certificate matches the hostname (most secure)
    - **Verify None**: Encrypted connection without certificate verification (least secure)
    
    ### Database Connection Information
    
    - Make sure you have the correct credentials (username/password)
    - Ensure the database server allows remote connections
    - Check that there are no firewall rules blocking the connection
    - Verify the database name exists on the server
    - For SSL connections, ensure certificates are properly configured
    
    ### Common Issues
    
    - **Connection Refused**: The server is not running or not accepting connections
    - **Authentication Failed**: Incorrect username or password
    - **Unknown Database**: The specified database does not exist
    - **Access Denied**: The user does not have permission to access the database
    - **SSL Certificate Error**: Certificate validation failed or certificate not found
    """)