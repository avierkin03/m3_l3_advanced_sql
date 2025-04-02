import sqlite3
from datetime import datetime

# Функція для створення з'єднання з базо даних
def create_connection():
    return sqlite3.connect('electronics_store.db')


# Функція для заповнення бази даних
def setup_database(conn):
    cursor = conn.cursor()
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        product_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL
                    )''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        customer_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE
                    )''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        order_date DATE NOT NULL,
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                    )''')
    conn.commit()


# Функція для заповнення бази даних
def fill_database(conn):
    cursor = conn.cursor()

    # Список продуктів для вставки
    products = [
        ("Lenovo Legion Y520", "Ноутбуки", 39999),
        ("MacBook Pro", "Ноутбуки", 44999),
        ("Samsung Galaxy M32", "Смартфони", 7999),
        ("Xiaomi Mi 9", "Смартфони", 10499),
        ("Samsung Galaxy Tab9", "Планшети", 14699),
        ("Lenovo Yoga Tab3", "Планшети", 15799)
    ]
    
    # Перевірка та вставка продуктів
    for name, category, price in products:
        cursor.execute("SELECT COUNT(*) FROM products WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:  # Якщо продукт не існує
            cursor.execute("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", 
                          (name, category, price))

    # Список клієнтів для вставки
    customers = [
        ("Олександр", "Аверкін", "avierkin03@gmail.com"),
        ("Владислав", "Казістов", "vlad02@gmail.com"),
        ("Олександр", "Кужель", "kuzhel@gmail.com"),
        ("Ангеліна", "Авраменко", "angela@gmail.com")
    ]
    
    # Перевірка та вставка клієнтів
    for first_name, last_name, email in customers:
        cursor.execute("SELECT COUNT(*) FROM customers WHERE email = ?", (email,))
        if cursor.fetchone()[0] == 0:  # Якщо клієнт не існує
            cursor.execute("INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)", 
                          (first_name, last_name, email))

    # Список замовлень для вставки
    orders = [
        (1, 1, 1, "2025-04-02"),
        (1, 3, 1, "2025-04-02"),
        (2, 2, 2, "2025-03-13"),
        (3, 4, 1, "2025-03-27"),
        (3, 5, 1, "2025-03-27"),
        (4, 6, 3, "2025-04-01")
    ]
    
    # Перевірка та вставка замовлень
    for customer_id, product_id, quantity, order_date in orders:
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ? AND product_id = ? AND order_date = ?", 
                      (customer_id, product_id, order_date))
        if cursor.fetchone()[0] == 0:  # Якщо замовлення не існує
            cursor.execute("INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)", 
                          (customer_id, product_id, quantity, order_date))

    conn.commit()

    
# Функція для виконання запитів до бази даних
def execute_query(conn, query, params=(), fetch=False):
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        return cursor.fetchall()
    return None


# Функція для підрахунку сумарного обсягу продажів (сума за всі замовлення)
def total_sales(conn):
    query = '''
    SELECT SUM(products.price * orders.quantity)
    FROM orders
    JOIN products ON orders.product_id = products.product_id
    '''
    result = execute_query(conn, query, fetch=True)
    return result[0][0] if result else 0


# Функція для підрахунку кількості замовлень на кожного клієнта
def orders_per_customer(conn):
    query = '''
    SELECT c.first_name, c.last_name, COUNT(o.order_id)
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
    '''
    return execute_query(conn, query, fetch=True)


# Функція для підрахунку середнього чеку замовлення (середня сума грошей в одному замовленні)
def average_order_value(conn):
    query = '''
    SELECT AVG(products.price * orders.quantity)
    FROM orders
    JOIN products ON orders.product_id = products.product_id
    '''
    result = execute_query(conn, query, fetch=True)
    return result[0][0] if result else 0


# Функція для пошуку категорії товарів, яка має найбільше замовлень
def most_popular_category(conn):
    query = '''
    SELECT p.category, COUNT(o.order_id) as order_count
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY order_count DESC
    LIMIT 1
    '''
    return execute_query(conn, query, fetch=True)


# Функція для обрахунку загальної кількості товарів кожної категорії
def products_per_category(conn):
    query = '''
    SELECT category, COUNT(product_id) as count
    FROM products
    GROUP BY category
    '''
    return execute_query(conn, query, fetch=True)


# Функція для оновлення ціни товарів в категорії "смартфони" на 10% збільшення
def update_smartphone_prices(conn):
    query = '''
    UPDATE products
    SET price = price * 1.10
    WHERE category = 'Смартфони'
    '''
    execute_query(conn, query)


# Основна фунуція
def main():
    conn = create_connection()
    setup_database(conn)
    fill_database(conn)

    while True:
        print("\nМеню:")
        print("1. Загальний обсяг продажів")
        print("2. Кількість замовлень на клієнта")
        print("3. Середній чек замовлення")
        print("4. Найпопулярніша категорія")
        print("5. Кількість товарів у категоріях")
        print("6. Оновити ціни смартфонів (+10%)")
        print("7. Вийти")
        
        choice = input("Виберіть опцію (1-7): ")
        
        if choice == '1':
            result = total_sales(conn)
            print(f"Загальний обсяг продажів: ${result:.2f}")
            
        elif choice == '2':
            results = orders_per_customer(conn)
            for first_name, last_name, count in results:
                print(f"{first_name} {last_name}: {count} замовлень")
                
        elif choice == '3':
            result = average_order_value(conn)
            print(f"Середній чек: ${result:.2f}")
            
        elif choice == '4':
            result = most_popular_category(conn)
            if result:
                category, count = result[0]
                print(f"Найпопулярніша категорія: {category} ({count} замовлень)")
                
        elif choice == '5':
            results = products_per_category(conn)
            for category, count in results:
                print(f"{category}: {count} товарів")
                
        elif choice == '6':
            update_smartphone_prices(conn)
            print("Ціни на смартфони оновлено")
            
        elif choice == '7':
            save = input("Зберегти зміни? (так/ні): ").lower()
            if save == 'так':
                conn.commit()
                print("Зміни збережено")
            else:
                conn.rollback()
                print("Зміни скасовано")
            break
            
        else:
            print("Невірний вибір")

    conn.close()

if __name__ == "__main__":
    main()
    