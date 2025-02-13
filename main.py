import psycopg2
from psycopg2 import OperationalError
from urllib.parse import urlparse
import streamlit as st


def validate_postgres_url(url: str):
    try:
        # Parse the PostgreSQL URL
        result = urlparse(url)

        if result.scheme != "postgres" and result.scheme != "postgresql":
            raise ValueError("Invalid URL scheme. Use a PostgreSQL URL.")

        # Extract connection parameters
        username = result.username
        password = result.password
        hostname = result.hostname
        port = result.port
        database = result.path.lstrip('/')

        # Attempt connection
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            connect_timeout=5
        )
        conn.close()
        return "Link is Valid"

    except OperationalError as e:
        return f"Invalid Link: {e}"
    except Exception as e:
        return f"Error: {e}"


st.title("PostgreSQL URL Validator")
postgres_url = st.text_input("Enter PostgreSQL URL:")
if st.button("Validate"):
    result = validate_postgres_url(postgres_url)
    st.write(result)
