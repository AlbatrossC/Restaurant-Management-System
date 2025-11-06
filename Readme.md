# Restaurant Management System

A simple and intuitive restaurant management application built with Flask and MySQL. This system helps manage orders, customers, menu items, and table reservations with automatic database setup.

## Features

- 📋 Order Management (Dine-in, Takeaway, Delivery)
- 👥 Customer Database
- 🍽️ Menu Management
- 🪑 Table Status Tracking
- 💰 Sales Dashboard
- 🔄 Real-time Order Status Updates

## Quick Start (Recommended)

### Using Docker 🐳

The easiest way to get started! Docker handles everything for you.

1. **Clone the Repository**
```bash
git clone https://github.com/AlbatrossC/Restaurant-Management-System.git
cd Restaurant-Management-System
```

2. **Run with Docker**
```bash
docker-compose -f docker/docker-compose.yml up --build
```

3. **Access the Application**

Open your browser and go to:

👉 **http://localhost:6767**

**Note**: Port 6767 is used to avoid conflicts with other services.

That's it! Everything is set up automatically.

---

## Manual Setup

If you prefer not to use Docker, follow these steps:

### Prerequisites

- **MySQL Server**: Download from [mysql.com](https://www.mysql.com/downloads/)
  - Make sure MySQL is running before starting the application

### Steps

1. **Clone the Repository**
```bash
git clone https://github.com/AlbatrossC/Restaurant-Management-System.git
cd Restaurant-Management-System
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create a `.env` File**

Create a file named `.env` in the root of the project directory:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password

SECRET_KEY=your-random-secret-key-here
```

**Important**: Replace `your_mysql_password` with your actual MySQL root password.

4. **Run the Application**
```bash
python app.py
```

The application will automatically:
- Create the `restaurant_db` database if it doesn't exist
- Set up all required tables (Customers, Menu, Tables, Orders)
- Insert sample data to get you started

5. **Access the Application**

Open your browser and navigate to:
```
http://localhost:5000
```

You should now see the restaurant management dashboard!