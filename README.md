Flask API for Delivery and Product Management
This project is a Flask-based RESTful API for managing delivery orders, driver routes, customers, and product data. The API integrates with a SQL Server database and includes various endpoints to perform CRUD operations on delivery orders, driver information, and product catalog. Additionally, it incorporates asynchronous tasks using Azure Functions and automated scheduling with Azure Scheduler.

Features
Database Integration: Connects to SQL Server with PyODBC.
CRUD Operations:
Manage delivery orders.
Retrieve, update, and delete driver and product data.
Retrieve and manage customer data.
Distance Calculation and Optimization: Uses Google Maps API integration for route optimization and delivery scheduling.
Error Handling and Logging: Detailed logging and error handling for database and general errors.
Pagination and Filtering: Supports pagination and filtering for larger datasets.
Date Range Filtering: Allows filtering by start and end dates for retrieving orders within specific periods.
Custom Classes: Encapsulates data into custom classes for better data structure and management.
Project Structure
app.py: Main file containing all routes, functions, and connection settings.
Classes: Defines custom classes like DeliveryOrder, Kontak, Karyawan, and others to structure and manage data.
Distance Calculation: Functions for calculating delivery distance and optimal route.
Error Handling: Structured exception handling for database and general errors.
Installation
Prerequisites
Python 3.7+
SQL Server
Required Python packages:
Flask
Flask-CORS
pyodbc
traceback
Steps
Clone the repository:

git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
Install dependencies:

pip install -r requirements.txt
Set up your database connection in app.py:

server = 'database.windows.net'
database = 'database'
username = 'username'
password = 'password'
driver = 'ODBC Driver 17 for SQL Server'
Run the app:

python app.py
The app will be accessible at http://localhost:5100.

API Endpoints
Authentication
Not included in this version; you may consider adding JWT or other forms of authentication for security.
Delivery Orders
POST /add_delivery_order: Add new delivery orders.
GET /get_delivery_order: Retrieve all delivery orders with optional pagination and date range filtering.
GET /detail_delivery_order/<id>: Retrieve details of a specific delivery order by ID.
DELETE /delete_detail_delivery_order/<id>: Delete a delivery order by ID.
POST /edit_delivery_order/<id>: Edit an existing delivery order by ID.
Driver and Customer Management
GET /list_driver: Retrieve a list of drivers.
GET /get_driver/<name>: Retrieve a driver by name.
GET /list_pelanggan: Retrieve a list of customers with location data.
GET /get_pelanggan/<name>: Retrieve a customer by name.
Product Management
GET /list_produk: Retrieve a list of all products.
GET /get_produk/<name>: Retrieve products by name.
Route Optimization and Delivery History
POST /submit_perjalanan: Submit a new delivery route.
POST /history_pengantaran: Retrieve delivery history with filtering options.
POST /cek_google: Check optimal route with Google Maps data.
Database Setup
The API uses stored procedures for certain actions (e.g., updating delivery details). Ensure these procedures are created in your SQL Server database for the API to function as expected.

Custom Classes
DeliveryOrder: Manages delivery order data.
Kontak: Manages customer contact details.
Karyawan: Manages employee details, specifically drivers.
HistoryPengantaranFilter and ReturnCekGoogle: Filters and formats history data for delivery routes.
SubmitPengantaran: Manages submission data for new deliveries.
Error Handling
The API includes structured error handling for database connection errors, SQL exceptions, and general exceptions.
Log messages are generated for debugging, capturing full stack traces when errors occur.
Deployment
To deploy this API in production, consider hosting it on platforms like Azure, AWS, or Google Cloud. For local development, it uses Flask’s built-in server, but for production, it’s recommended to use Gunicorn or uWSGI with Nginx.

# Example using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5100 app:app
License
This project is licensed under the MIT License.
