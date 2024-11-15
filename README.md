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
