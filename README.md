# Flask API for Delivery and Product Management

This project is a **Flask-based RESTful API** for managing delivery orders, driver routes, customers, and product data. The API integrates with a SQL Server database and includes various endpoints to perform CRUD operations on delivery orders, driver information, and product catalog. Additionally, it incorporates asynchronous tasks using **Azure Functions** and automated scheduling with **Azure Scheduler**.

---

## Features

- **Database Integration**: Connects to SQL Server with PyODBC.
- **CRUD Operations**:
  - Manage delivery orders.
  - Retrieve, update, and delete driver and product data.
  - Retrieve and manage customer data.
- **Distance Calculation and Optimization**: Uses Google Maps API integration for route optimization and delivery scheduling.
- **Error Handling and Logging**: Detailed logging and error handling for database and general errors.
- **Pagination and Filtering**: Supports pagination and filtering for larger datasets.
- **Date Range Filtering**: Allows filtering by start and end dates for retrieving orders within specific periods.
- **Custom Classes**: Encapsulates data into custom classes for better data structure and management.

---

## Installation

### Prerequisites

- Python 3.7+
- SQL Server
- Required Python packages:
  - Flask
  - Flask-CORS
  - pyodbc
  - traceback

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Set up your database connection in app.py**:
    ```bash
    server = 'database.windows.net'
    database = 'database'
    username = 'username'
    password = 'password'
    driver = 'ODBC Driver 17 for SQL Server'

4. **Run the app**:
    ```bash
    python app.py
    
The app will be accessible at http://localhost:5100.

# API Documentation

This project provides a Flask-based RESTful API for managing delivery orders, drivers, customers, and product data. Below are the key API endpoints, database requirements, custom classes, and deployment instructions.

---

## **API Endpoints**

### **Delivery Orders**
- **POST** `/add_delivery_order`: Add new delivery orders.
- **GET** `/get_delivery_order`: Retrieve all delivery orders with optional pagination and date range filtering.
- **GET** `/detail_delivery_order/<id>`: Retrieve details of a specific delivery order by ID.
- **DELETE** `/delete_detail_delivery_order/<id>`: Delete a delivery order by ID.
- **POST** `/edit_delivery_order/<id>`: Edit an existing delivery order by ID.

### **Driver and Customer Management**
- **GET** `/list_driver`: Retrieve a list of drivers.
- **GET** `/get_driver/<name>`: Retrieve a driver by name.
- **GET** `/list_pelanggan`: Retrieve a list of customers with location data.
- **GET** `/get_pelanggan/<name>`: Retrieve a customer by name.

### **Product Management**
- **GET** `/list_produk`: Retrieve a list of all products.
- **GET** `/get_produk/<name>`: Retrieve products by name.

### **Route Optimization and Delivery History**
- **POST** `/submit_perjalanan`: Submit a new delivery route.
- **POST** `/history_pengantaran`: Retrieve delivery history with filtering options.
- **POST** `/cek_google`: Check optimal route with Google Maps data.

---

## **Database Setup**

The API uses stored procedures for certain actions (e.g., updating delivery details). Ensure these procedures are created in your SQL Server database for the API to function as expected.

---

# Route Optimization with Google Maps API

This project is a Python script that calculates the most efficient route between multiple points using Google Maps API. It determines the shortest distance and estimated travel time for delivery or other routing purposes. The code includes caching for API responses to improve performance and reduce redundant API calls.

---

## **Features**

1. **Google Maps API Integration**:
   - Fetches distance and duration between two locations using the Google Maps Distance Matrix API.
   - Converts distance to kilometers and duration to minutes for easy interpretation.

2. **Route Optimization**:
   - Calculates the most efficient path starting from a specified point (e.g., "Toko Permata").
   - Implements a nearest neighbor algorithm to minimize travel distance and duration.

3. **Cache Implementation**:
   - Reduces redundant API calls by caching distances and durations between points.

4. **Customizable Points**:
   - Allows you to define multiple locations (latitude and longitude) for route planning.

5. **Google Maps URL Generation**:
   - Generates a sharable Google Maps URL for the optimized route.

---

## **Prerequisites**

- Python 3.7+
- A valid **Google Maps API Key** with access to the Distance Matrix API.

### **Required Python Libraries**
Install the required packages before running the script:
  ```bash
  pip install requests

---


## **Custom Classes**

- **DeliveryOrder**: Manages delivery order data.
- **Kontak**: Manages customer contact details.
- **Karyawan**: Manages employee details, specifically drivers.
- **HistoryPengantaranFilter** and **ReturnCekGoogle**: Filters and formats history data for delivery routes.
- **SubmitPengantaran**: Manages submission data for new deliveries.

---

## **Error Handling**

- The API includes structured error handling for database connection errors, SQL exceptions, and general exceptions.
- Log messages are generated for debugging, capturing full stack traces when errors occur.

---

## **Deployment**

To deploy this API in production, consider hosting it on platforms like **Azure**, **AWS**, or **Google Cloud**. For local development, it uses Flask’s built-in server, but for production, it’s recommended to use **Gunicorn** or **uWSGI** with **Nginx**.

### **Example Deployment with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5100 app:app
