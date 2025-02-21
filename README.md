# dburl-verify
================

A tool for verifying database connections.

## Overview
------------

`dburl-verify` is a simple utility that helps you verify that your database connections are working correctly. It supports connections to PostgreSQL, MySQL, and MongoDB databases.

## Features
------------

* Parse database URIs and extract connection settings
* Connect to databases using the parsed credentials
* Handle errors and provide informative error messages
* Streamlit application for easy user interface

## Requirements
---------------

* Python 3.x
* psycopg2-binary (for PostgreSQL connections)
* pymongo (for MongoDB connections)
* mysql-connector (for MySQL connections)

## Usage
-----

1. Clone the repository: `git clone https://github.com/amoghsaxena/dburl-verify.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the Streamlit application: `streamlit run db-verify-main.py`
4. Select the database type and input the connection settings
5. Click "Verify" to test the connection

## Contributing
------------

Contributions are welcome! If you have any ideas for improving the project or would like to report a bug, please open an issue or submit a pull request.

## License
-------

This project is licensed under the MIT License. See the LICENSE file for details.