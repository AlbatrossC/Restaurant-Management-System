from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error
import json
import os
from dotenv import load_dotenv
from datetime import datetime

try:
    from db_initializer import initialize_database
    DB_INITIALIZER_AVAILABLE = True
except ImportError:
    DB_INITIALIZER_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'default-secret-key-change-in-production'

# Check if .env file exists
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_file_path):
    ENV_ERROR = ".env file not found. Please create a .env file with database configuration."
    ENV_MISSING = True
else:
    load_dotenv()
    ENV_MISSING = False
    ENV_ERROR = None

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'autocommit': False
}

DB_NAME = os.getenv('DB_NAME', 'restaurant_db')

if not ENV_MISSING and os.getenv('SECRET_KEY'):
    app.secret_key = os.getenv('SECRET_KEY')

DB_CONNECTION_ERROR = None


def render_error(error_msg):
    """Render error page with diagnostic information"""
    return render_template('error.html', 
                         error=error_msg,
                         db_host=DB_CONFIG.get('host'),
                         db_port=DB_CONFIG.get('port'),
                         db_user=DB_CONFIG.get('user'),
                         db_name=DB_NAME)


def check_and_initialize_database():
    """Check if database exists, initialize if needed"""
    if ENV_MISSING or not DB_INITIALIZER_AVAILABLE:
        return False
    
    try:
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        connection = mysql.connector.connect(**config)
        
        cursor = connection.cursor()
        required_tables = ['Customers', 'Menu', 'Tables', 'Orders']
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        connection.close()
        
        if all(table in existing_tables for table in required_tables):
            print("✓ Database ready")
            return True
        else:
            return initialize_database()
            
    except Error as e:
        if "Unknown database" in str(e):
            return initialize_database()
        else:
            print(f"Database error: {e}")
            return False


def get_db_connection():
    """Create and return a database connection"""
    global DB_CONNECTION_ERROR
    
    try:
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        connection = mysql.connector.connect(**config)
        DB_CONNECTION_ERROR = None
        return connection
    except Error as e:
        error_msg = str(e)
        
        if "Unknown database" in error_msg:
            DB_CONNECTION_ERROR = f"Database '{DB_NAME}' does not exist. Run 'python db_initializer.py' to create it."
        elif "Access denied" in error_msg:
            DB_CONNECTION_ERROR = f"Access denied for user '{DB_CONFIG['user']}'@'{DB_CONFIG['host']}'. Check your DB_USER and DB_PASSWORD in .env file."
        elif "Can't connect to MySQL server" in error_msg:
            DB_CONNECTION_ERROR = f"Can't connect to MySQL server at {DB_CONFIG['host']}:{DB_CONFIG['port']}. Make sure MySQL is running."
        elif "Connection refused" in error_msg:
            DB_CONNECTION_ERROR = f"Connection refused to {DB_CONFIG['host']}:{DB_CONFIG['port']}. MySQL server is not accepting connections."
        else:
            DB_CONNECTION_ERROR = f"Database connection error: {error_msg}"
        
        return None


def format_datetime(dt):
    """Convert datetime to '31 Oct 8:27 pm' format"""
    if not dt:
        return "-"
    return dt.strftime("%d %b %I:%M %p").lstrip("0").replace(" 0", " ").lower()


@app.route('/')
def index():
    if ENV_MISSING:
        return render_error(ENV_ERROR)
    
    connection = get_db_connection()
    if not connection:
        return render_error(DB_CONNECTION_ERROR)

    cursor = connection.cursor()

    try:
        status_filter = request.args.get('status', 'All')
        order_type_filter = request.args.get('order_type', 'All')

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

        cursor.execute("SELECT item_id, item_name, category, price FROM Menu WHERE is_available = TRUE ORDER BY category, item_name")
        menu = cursor.fetchall()

        cursor.execute("SELECT customer_id, name, phone, email, address, joined_on FROM Customers ORDER BY joined_on DESC")
        customers = cursor.fetchall()

        cursor.execute("SELECT table_id, table_number, capacity, status FROM Tables ORDER BY table_number")
        tables = cursor.fetchall()

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
        error_msg = f"Database query error: {str(e)}"
        if "doesn't exist" in str(e).lower():
            error_msg = f"Database table is missing: {str(e)}. Run 'python db_initializer.py' to create all tables."
        return render_error(error_msg)
    finally:
        cursor.close()
        connection.close()


@app.route('/add', methods=['POST'])
def add_order():
    if ENV_MISSING:
        return render_error(ENV_ERROR)
    
    connection = get_db_connection()
    if not connection:
        return render_error(DB_CONNECTION_ERROR)

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

        total_after_discount = total - (total * discount / 100)

        # Validate table
        if order_type == 'Dine-in' and table_number:
            cursor.execute("SELECT status FROM Tables WHERE table_number = %s", (table_number,))
            table_status = cursor.fetchone()
            if table_status and table_status[0] == 'Occupied':
                flash('Selected table is already occupied', 'warning')
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
        error_msg = f"Failed to place order: {str(e)}"
        if "foreign key constraint" in str(e).lower():
            error_msg = f"Failed to place order: Referenced customer or menu item doesn't exist. {str(e)}"
        elif "duplicate entry" in str(e).lower():
            error_msg = f"Failed to place order: Duplicate entry detected. {str(e)}"
        elif "doesn't exist" in str(e).lower():
            error_msg = f"Failed to place order: Required table is missing. Run 'python db_initializer.py'. {str(e)}"
        return render_error(error_msg)
    finally:
        cursor.close()
        connection.close()


@app.route('/update_status/<int:order_id>/<status>')
def update_status(order_id, status):
    if ENV_MISSING:
        return render_error(ENV_ERROR)
    
    connection = get_db_connection()
    if not connection:
        return render_error(DB_CONNECTION_ERROR)

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
        error_msg = f"Failed to update status: {str(e)}"
        if "doesn't exist" in str(e).lower():
            error_msg = f"Failed to update status: Orders or Tables table is missing. Run 'python db_initializer.py'. {str(e)}"
        return render_error(error_msg)
    finally:
        cursor.close()
        connection.close()


@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    if ENV_MISSING:
        return render_error(ENV_ERROR)
    
    connection = get_db_connection()
    if not connection:
        return render_error(DB_CONNECTION_ERROR)

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT table_number, order_type FROM Orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            flash('Order not found', 'error')
            return redirect('/')

        table_number, order_type = result

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
        error_msg = f"Failed to delete order: {str(e)}"
        if "foreign key constraint" in str(e).lower():
            error_msg = f"Failed to delete order: This order is referenced by other records. {str(e)}"
        return render_error(error_msg)
    finally:
        cursor.close()
        connection.close()


@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    if ENV_MISSING:
        return render_error(ENV_ERROR)
    
    connection = get_db_connection()
    if not connection:
        return render_error(DB_CONNECTION_ERROR)

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
        error_msg = f"Failed to delete customer: {str(e)}"
        if "foreign key constraint" in str(e).lower():
            error_msg = f"Failed to delete customer: Customer has existing orders. {str(e)}"
        elif "doesn't exist" in str(e).lower():
            error_msg = f"Failed to delete customer: Customers table is missing. Run 'python db_initializer.py'. {str(e)}"
        return render_error(error_msg)
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    if not ENV_MISSING:
        check_and_initialize_database()
    
    app.run(debug=True)