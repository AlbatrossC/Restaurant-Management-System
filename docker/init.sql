-- Create database
CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT,
    joined_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu Table
CREATE TABLE IF NOT EXISTS Menu (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables Table
CREATE TABLE IF NOT EXISTS Tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_number VARCHAR(10) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    status ENUM('Available', 'Occupied', 'Reserved') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    items JSON NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    payment_method ENUM('Cash','Card','UPI','Other') NOT NULL,
    order_status ENUM('Pending','Preparing','Completed') DEFAULT 'Pending',
    order_type ENUM('Dine-in','Takeaway','Delivery') NOT NULL,
    table_number VARCHAR(10),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- Sample Menu
INSERT INTO Menu (item_name, category, price) VALUES
('Paneer Tikka', 'Appetizer', 180.00),
('Veg Spring Roll', 'Appetizer', 120.00),
('Chicken Wings', 'Appetizer', 220.00),
('French Fries', 'Appetizer', 100.00),
('Dal Tadka', 'Main Course', 150.00),
('Paneer Butter Masala', 'Main Course', 250.00),
('Chicken Curry', 'Main Course', 280.00),
('Butter Chicken', 'Main Course', 320.00),
('Fish Curry', 'Main Course', 350.00),
('Veg Biryani', 'Main Course', 200.00),
('Chicken Biryani', 'Main Course', 280.00),
('Naan', 'Bread', 40.00),
('Roti', 'Bread', 20.00),
('Garlic Naan', 'Bread', 50.00),
('Butter Roti', 'Bread', 25.00),
('Gulab Jamun', 'Dessert', 80.00),
('Ice Cream', 'Dessert', 100.00),
('Ras Malai', 'Dessert', 120.00),
('Cold Coffee', 'Beverage', 100.00),
('Masala Chai', 'Beverage', 40.00),
('Fresh Lime Soda', 'Beverage', 60.00),
('Mango Lassi', 'Beverage', 80.00);

-- Sample Tables
INSERT INTO Tables (table_number, capacity) VALUES
('T1', 2), ('T2', 2), ('T3', 4), ('T4', 4),
('T5', 4), ('T6', 6), ('T7', 6), ('T8', 8);
