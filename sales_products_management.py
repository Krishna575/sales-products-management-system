import sqlite3
import datetime

# Database setup
def create_tables():
    """
    Creates the necessary tables in the SQLite database.
    - Products table: Stores product details with product_id as primary key.
    - Sales table: Stores sales records with sale_id as primary key and product_id as foreign key.
    """
    conn = sqlite3.connect('sales_products.db')
    cursor = conn.cursor()

    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Create Sales table with foreign key to Products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        )
    ''')

    conn.commit()
    conn.close()

# Function to add a new product
def add_product():
    """
    Adds a new product to the Products table.
    Prompts user for product name, price, and quantity.
    Validates inputs to ensure positive price and quantity.
    """
    try:
        name = input("Enter product name: ").strip()
        if not name:
            print("Product name cannot be empty.")
            return

        price = float(input("Enter product price: "))
        if price <= 0:
            print("Price must be positive.")
            return

        quantity = int(input("Enter initial quantity: "))
        if quantity < 0:
            print("Quantity cannot be negative.")
            return

        conn = sqlite3.connect('sales_products.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Products (product_name, price, quantity) VALUES (?, ?, ?)', (name, price, quantity))
        conn.commit()
        conn.close()
        print("Product added successfully.")
    except ValueError:
        print("Invalid input. Please enter numeric values for price and quantity.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Function to update product details
def update_product():
    """
    Updates an existing product's details.
    Prompts for product ID, then allows updating name, price, or quantity.
    Validates inputs.
    """
    try:
        product_id = int(input("Enter product ID to update: "))
        conn = sqlite3.connect('sales_products.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        if not product:
            print("Product not found.")
            conn.close()
            return

        print(f"Current details: Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}")
        name = input("Enter new name (leave blank to keep current): ").strip() or product[1]
        price_input = input("Enter new price (leave blank to keep current): ").strip()
        price = float(price_input) if price_input else product[2]
        if price <= 0:
            print("Price must be positive.")
            conn.close()
            return

        quantity_input = input("Enter new quantity (leave blank to keep current): ").strip()
        quantity = int(quantity_input) if quantity_input else product[3]
        if quantity < 0:
            print("Quantity cannot be negative.")
            conn.close()
            return

        cursor.execute('UPDATE Products SET product_name = ?, price = ?, quantity = ? WHERE product_id = ?',
                       (name, price, quantity, product_id))
        conn.commit()
        conn.close()
        print("Product updated successfully.")
    except ValueError:
        print("Invalid input. Please enter numeric values where required.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Function to delete a product
def delete_product():
    """
    Deletes a product from the Products table.
    Also deletes related sales records to maintain integrity.
    """
    try:
        product_id = int(input("Enter product ID to delete: "))
        conn = sqlite3.connect('sales_products.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Products WHERE product_id = ?', (product_id,))
        if not cursor.fetchone():
            print("Product not found.")
            conn.close()
            return

        # Delete related sales records first
        cursor.execute('DELETE FROM Sales WHERE product_id = ?', (product_id,))
        cursor.execute('DELETE FROM Products WHERE product_id = ?', (product_id,))
        conn.commit()
        conn.close()
        print("Product and related sales records deleted successfully.")
    except ValueError:
        print("Invalid product ID.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Function to view all products
def view_products():
    """
    Displays all products in the Products table.
    """
    conn = sqlite3.connect('sales_products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    conn.close()

    if not products:
        print("No products found.")
        return

    print("\nProducts:")
    print("ID | Name | Price | Quantity")
    print("-" * 30)
    for product in products:
        print(f"{product[0]} | {product[1]} | {product[2]} | {product[3]}")

# Function to record a sales transaction
def record_sale():
    """
    Records a sale, updates inventory, and calculates total amount.
    Checks if sufficient quantity is available.
    """
    try:
        product_id = int(input("Enter product ID: "))
        quantity_sold = int(input("Enter quantity sold: "))
        if quantity_sold <= 0:
            print("Quantity sold must be positive.")
            return

        conn = sqlite3.connect('sales_products.db')
        cursor = conn.cursor()
        cursor.execute('SELECT product_name, price, quantity FROM Products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        if not product:
            print("Product not found.")
            conn.close()
            return

        name, price, current_quantity = product
        if quantity_sold > current_quantity:
            print("Insufficient quantity in stock.")
            conn.close()
            return

        total_amount = price * quantity_sold
        sale_date = datetime.date.today().isoformat()

        # Insert sale record
        cursor.execute('INSERT INTO Sales (product_id, quantity_sold, sale_date, total_amount) VALUES (?, ?, ?, ?)',
                       (product_id, quantity_sold, sale_date, total_amount))

        # Update product quantity
        new_quantity = current_quantity - quantity_sold
        cursor.execute('UPDATE Products SET quantity = ? WHERE product_id = ?', (new_quantity, product_id))

        conn.commit()
        conn.close()
        print(f"Sale recorded successfully. Total amount: {total_amount}")
    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Function to view all sales records
def view_sales():
    """
    Displays all sales records from the Sales table.
    """
    conn = sqlite3.connect('sales_products.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.sale_id, p.product_name, s.quantity_sold, s.sale_date, s.total_amount
        FROM Sales s
        JOIN Products p ON s.product_id = p.product_id
    ''')
    sales = cursor.fetchall()
    conn.close()

    if not sales:
        print("No sales records found.")
        return

    print("\nSales Records:")
    print("Sale ID | Product Name | Quantity Sold | Date | Total Amount")
    print("-" * 60)
    for sale in sales:
        print(f"{sale[0]} | {sale[1]} | {sale[2]} | {sale[3]} | {sale[4]}")

# Main menu function
def main():
    """
    Main function with menu-driven interface.
    Allows user to choose operations.
    """
    create_tables()  # Ensure tables are created on startup
    while True:
        print("\nSales and Products Management System")
        print("1. Add Product")
        print("2. Update Product")
        print("3. Delete Product")
        print("4. View Products")
        print("5. Record Sale")
        print("6. View Sales")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()
        if choice == '1':
            add_product()
        elif choice == '2':
            update_product()
        elif choice == '3':
            delete_product()
        elif choice == '4':
            view_products()
        elif choice == '5':
            record_sale()
        elif choice == '6':
            view_sales()
        elif choice == '7':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# Instructions to run the project:
# 1. Ensure Python 3.x is installed on your system.
# 2. Save this file as 'sales_products_management.py'.
# 3. Open a command prompt or terminal and navigate to the directory where the file is saved.
# 4. Run the script using: python sales_products_management.py
# 5. Follow the on-screen menu to perform operations.
# 6. The database file 'sales_products.db' will be created automatically in the same directory.
