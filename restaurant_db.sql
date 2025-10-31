drop database restaurant_db;
create database restaurant_db;
use restaurant_db;

-- Create Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(50),
    address TEXT,
    joined_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Menu Table
CREATE TABLE IF NOT EXISTS Menu (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(50) NOT NULL,
    category VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- Create Tables Table
CREATE TABLE IF NOT EXISTS Tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT UNIQUE NOT NULL,
    capacity INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Available'
);

-- Create Orders Table
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    items JSON NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'Pending',
    order_type VARCHAR(20) DEFAULT 'Dine-in',
    table_number INT,
    discount DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO Menu (item_name, category, price, is_available) VALUES
-- Starters
('Paneer Tikka', 'Starters', 180.00, TRUE),
('Veg Spring Roll', 'Starters', 120.00, TRUE),
('Chicken Wings', 'Starters', 220.00, TRUE),
('Fish Fingers', 'Starters', 240.00, TRUE),
('Mushroom Soup', 'Starters', 150.00, TRUE),

-- Main Course
('Butter Chicken', 'Main Course', 320.00, TRUE),
('Paneer Butter Masala', 'Main Course', 280.00, TRUE),
('Dal Makhani', 'Main Course', 200.00, TRUE),
('Veg Biryani', 'Main Course', 250.00, TRUE),
('Chicken Biryani', 'Main Course', 300.00, TRUE),
('Mutton Rogan Josh', 'Main Course', 380.00, TRUE),
('Fish Curry', 'Main Course', 350.00, TRUE),

-- Breads
('Butter Naan', 'Breads', 50.00, TRUE),
('Garlic Naan', 'Breads', 60.00, TRUE),
('Tandoori Roti', 'Breads', 30.00, TRUE),
('Kulcha', 'Breads', 55.00, TRUE),

-- Rice
('Jeera Rice', 'Rice', 120.00, TRUE),
('Steam Rice', 'Rice', 100.00, TRUE),
('Veg Fried Rice', 'Rice', 180.00, TRUE),

-- Desserts
('Gulab Jamun', 'Desserts', 80.00, TRUE),
('Ice Cream', 'Desserts', 100.00, TRUE),
('Ras Malai', 'Desserts', 120.00, TRUE),
('Kulfi', 'Desserts', 90.00, TRUE),

-- Beverages
('Lassi', 'Beverages', 70.00, TRUE),
('Cold Coffee', 'Beverages', 100.00, TRUE),
('Fresh Lime Soda', 'Beverages', 60.00, TRUE),
('Masala Chai', 'Beverages', 40.00, TRUE),
('Mango Juice', 'Beverages', 80.00, TRUE);


INSERT INTO Tables (table_number, capacity, status) VALUES
(1, 2, 'Available'),
(2, 2, 'Available'),
(3, 4, 'Available'),
(4, 4, 'Available'),
(5, 6, 'Available'),
(6, 6, 'Available'),
(7, 8, 'Available'),
(8, 4, 'Available'),
(9, 2, 'Available'),
(10, 4, 'Available');