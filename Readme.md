# Restaurant Management System

This is a simple restaurant management application built with Flask and MySQL.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **MySQL Server**: Make sure you have a MySQL server running. You can download it from [mysql.com](https://www.mysql.com/downloads/)


## How to Run the Code

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/AlbatrossC/Restaurant-Management-System.git
```

### 2. Move to the Repository Directory

```bash
cd Restaurant-Management-System
```

### 3. Create a `.env` File

Create a file named `.env` in the root of the project directory. This file will store your database credentials.

Add the following keys and your corresponding values:

```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=restaurant_db
SECRET_KEY=your_secret_key
```

Replace `your_mysql_user`, `your_mysql_password`, and `your_secret_key` with your actual credentials and a secret key of your choice.

### 4. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 5. Set Up the Database

You need to create the database and the necessary tables. You can do this by running the `restaurant_db.sql` file in the MySQL server shell.

Open your command prompt or terminal and run the following command. You will be prompted to enter your MySQL root password.

```bash
mysql -u root -p < "restaurant_db.sql"
```

### 6. Run the Application

Now, you can run the Flask application:

```bash
python app.py
```

### 7. Access the Application

Open your web browser and go to the following address:

```
http://localhost:5000
```

You should now see the restaurant management application running.