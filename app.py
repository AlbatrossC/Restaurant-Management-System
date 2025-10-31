from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'local-running-secret-key')

# Database configuration - Base config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'restaurant_db'),
    'autocommit': False
}

# Add SSL configuration only if running on Vercel (or if DB_HOST is not localhost)
# This detects Vercel deployment via VERCEL environment variable or non-localhost DB
if os.getenv('VERCEL') or (DB_CONFIG['host'] not in ['localhost', '127.0.0.1']):
    DB_CONFIG.update({
        'ssl_ca': os.getenv('SSL_CA'),  # Optional: path to CA certificate
        'ssl_verify_identity': True,     # Verify server identity
        'ssl_disabled': False
    })
    print("SSL enabled for database connection")
else:
    print("Running locally - SSL disabled")

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Helper: Format datetime to "31 Oct 8:27 pm"
def format_datetime(dt):
    """Convert datetime to '31 Oct 8:27 pm' format"""
    if not dt:
        return "-"
    return dt.strftime("%d %b %I:%M %p").lstrip("0").replace(" 0", " ").lower().replace(" pm", " pm").replace(" am", " am")

@app.route('/')
def index():
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect('/')

    cursor = connection.cursor()

    try:
        status_filter = request.args.get('status', 'All')
        order_type_filter = request.args.get('order_type', 'All')

        # Query orders with customer and items
        query = """
            SELECT o.order_id, c.name, o.order_date, o.total_amount, o.payment_method, 
                   o.order_status, o.order_type, o.table_number, o.items
            FROM Orders o
            JOIN Customers c ON o.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []
        if status_filter != 'All':
            query += " AND o.order_status = %s"
            params.append(status_filter)
        if order_type_filter != 'All':
            query += " AND o.order_type = %s"
            params.append(order_type_filter)

        query += " ORDER BY o.order_date DESC"
        cursor.execute(query, params)
        orders_raw = cursor.fetchall()

        # Format orders: date + items as string
        orders = []
        for o in orders_raw:
            items_json = o[8] or '[]'
            try:
                items = json.loads(items_json)
                items_str = ", ".join([f"{item['item']} (₹{item['price']})" for item in items])
            except:
                items_str = "Invalid items"
            orders.append((
                o[0], o[1], format_datetime(o[2]), o[3], o[4], o[5], o[6], o[7] or '-', items_str
            ))

        # Fetch menu, customers, tables
        cursor.execute("SELECT item_id, item_name, category, price FROM Menu WHERE is_available = TRUE ORDER BY category, item_name")
        menu = cursor.fetchall()

        cursor.execute("SELECT customer_id, name, phone, email, address, joined_on FROM Customers ORDER BY joined_on DESC")
        customers = cursor.fetchall()

        cursor.execute("SELECT table_id, table_number, capacity, status FROM Tables ORDER BY table_number")
        tables = cursor.fetchall()

        # Stats
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE order_status = 'Pending'")
        pending_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Tables WHERE status = 'Available'")
        available_tables = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Orders WHERE DATE(order_date) = CURDATE()")
        today_sales = cursor.fetchone()[0]

        return render_template('index.html',
                               orders=orders,
                               menu=menu,
                               customers=customers,
                               tables=tables,
                               pending_orders=pending_orders,
                               available_tables=available_tables,
                               today_sales=today_sales,
                               status_filter=status_filter,
                               order_type_filter=order_type_filter)

    except Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while loading data.', 'error')
        return redirect('/')
    finally:
        cursor.close()
        connection.close()


@app.route('/add', methods=['POST'])
def add_order():
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect('/')

    cursor = connection.cursor()

    try:
        customer_id = request.form.get('customer_id')
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        payment_method = request.form.get('payment_method')
        order_type = request.form.get('order_type')
        table_number = request.form.get('table_number')
        discount = float(request.form.get('discount', 0))
        selected_items = request.form.getlist('items')

        # Validate items
        if not selected_items:
            flash('Please select at least one item', 'warning')
            return redirect('/')

        # Handle customer
        if customer_id and customer_id != 'new' and customer_id.strip():
            customer_id = int(customer_id)
        else:
            if not phone or not name:
                flash('Phone number and name are required for new customers', 'warning')
                return redirect('/')

            cursor.execute("SELECT customer_id FROM Customers WHERE phone = %s", (phone,))
            existing = cursor.fetchone()
            if existing:
                customer_id = existing[0]
            else:
                cursor.execute(
                    "INSERT INTO Customers (name, phone, email, address) VALUES (%s, %s, %s, %s)",
                    (name, phone, email or None, address or None)
                )
                connection.commit()
                customer_id = cursor.lastrowid

        # Build items detail
        items_detail = []
        total = 0.0
        for item_id in selected_items:
            cursor.execute("SELECT item_name, price FROM Menu WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()
            if item:
                price = float(item[1])
                items_detail.append({"item": item[0], "price": price})
                total += price

        if total == 0:
            flash('Invalid items selected', 'error')
            return redirect('/')

        # Apply discount
        total_after_discount = total - (total * discount / 100)

        # Validate table for dine-in
        if order_type == 'Dine-in' and table_number:
            cursor.execute("SELECT status FROM Tables WHERE table_number = %s", (table_number,))
            table_status = cursor.fetchone()
            if table_status and table_status[0] == 'Occupied':
                flash('Selected table is already occupied.', 'warning')
                return redirect('/')

        # Insert order
        cursor.execute("""
            INSERT INTO Orders (customer_id, items, total_amount, payment_method, order_type, table_number, discount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (customer_id, json.dumps(items_detail), total_after_discount, payment_method, order_type,
              table_number if table_number else None, discount))
        connection.commit()

        # Update table status
        if order_type == 'Dine-in' and table_number:
            cursor.execute("UPDATE Tables SET status = 'Occupied' WHERE table_number = %s", (table_number,))
            connection.commit()

        flash('Order placed successfully', 'success')
        return redirect('/')

    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        flash(f'Failed to place order: {str(e)}', 'error')
        return redirect('/')
    except ValueError as e:
        connection.rollback()
        flash('Invalid input data', 'error')
        return redirect('/')
    finally:
        cursor.close()
        connection.close()


@app.route('/update_status/<int:order_id>/<status>')
def update_status(order_id, status):
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect('/')

    cursor = connection.cursor()

    try:
        valid_statuses = ['Pending', 'Preparing', 'Completed']
        if status not in valid_statuses:
            flash('Invalid status', 'error')
            return redirect('/')

        cursor.execute("SELECT table_number, order_type, order_status FROM Orders WHERE order_id = %s", (order_id,))
        order_info = cursor.fetchone()

        if not order_info:
            flash('Order not found', 'error')
            return redirect('/')

        table_number, order_type, current_status = order_info

        # Update status
        cursor.execute("UPDATE Orders SET order_status = %s WHERE order_id = %s", (status, order_id))
        connection.commit()

        # Handle table status
        if order_type == 'Dine-in' and table_number:
            if status == 'Completed':
                cursor.execute("UPDATE Tables SET status = 'Available' WHERE table_number = %s", (table_number,))
                connection.commit()
            elif current_status == 'Completed' and status in ['Pending', 'Preparing']:
                cursor.execute("UPDATE Tables SET status = 'Occupied' WHERE table_number = %s", (table_number,))
                connection.commit()

        flash(f'Order status updated to {status}', 'success')
        return redirect('/')

    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        flash('Failed to update status', 'error')
        return redirect('/')
    finally:
        cursor.close()
        connection.close()


@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect('/')

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT table_number, order_type FROM Orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            flash('Order not found', 'error')
            return redirect('/')

        table_number, order_type = result

        # Delete order
        cursor.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))
        connection.commit()

        # Free table if no active orders
        if order_type == 'Dine-in' and table_number:
            cursor.execute("""
                SELECT COUNT(*) FROM Orders 
                WHERE table_number = %s AND order_type = 'Dine-in' 
                AND order_status IN ('Pending', 'Preparing')
            """, (table_number,))
            active_count = cursor.fetchone()[0]
            if active_count == 0:
                cursor.execute("UPDATE Tables SET status = 'Available' WHERE table_number = %s", (table_number,))
                connection.commit()

        flash('Order deleted successfully', 'success')
        return redirect('/')

    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        flash('Failed to delete order', 'error')
        return redirect('/')
    finally:
        cursor.close()
        connection.close()


@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect('/')

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE customer_id = %s", (customer_id,))
        order_count = cursor.fetchone()[0]

        if order_count > 0:
            flash('Cannot delete customer with existing orders', 'warning')
            return redirect('/')

        cursor.execute("DELETE FROM Customers WHERE customer_id = %s", (customer_id,))
        connection.commit()

        flash('Customer deleted successfully', 'success')
        return redirect('/')

    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        flash('Failed to delete customer', 'error')
        return redirect('/')
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)