# Restaurant Management System

A simple and intuitive restaurant management application built with Flask and MySQL. This system helps manage orders, customers, menu items, and table reservations with automatic database setup.

## Features

- 📋 Order Management (Dine-in, Takeaway, Delivery)
- 👥 Customer Database
- 🍽️ Menu Management
- 🪑 Table Status Tracking
- 💰 Sales Dashboard
- 🔄 Real-time Order Status Updates

## Prerequisites

- **MySQL Server**: Download from [mysql.com](https://www.mysql.com/downloads/)
  - Make sure MySQL is running before starting the application

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/AlbatrossC/Restaurant-Management-System.git
cd Restaurant-Management-System
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a file named `.env` in the root of the project directory with the following configuration:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password

SECRET_KEY=your-random-secret-key-here
```

**Important**: Replace `your_mysql_password` with your actual MySQL root password.

The application will automatically create the database and all required tables!

### 4. Run the Application

Simply start the Flask application:

```bash
python app.py
```

**That's it!** The application will automatically:
- Create the `restaurant_db` database if it doesn't exist
- Set up all required tables (Customers, Menu, Tables, Orders)
- Insert sample data to get you started

### 5. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should now see the restaurant management dashboard!

