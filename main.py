import sqlite3
import hashlib

# 1. معادلة التحقق من كود التفعيل
def verify_key(client_name, user_key, secret_salt="MY_PRIVATE_KEY_2026"):
    raw_string = f"{client_name.strip().lower()}_{secret_salt}"
    hash_obj = hashlib.md5(raw_string.encode('utf-8'))
    full_hash = hash_obj.hexdigest().upper()
    expected_key = f"{full_hash[:4]}-{full_hash[4:8]}-{full_hash[8:12]}-{full_hash[12:16]}"
    return user_key.strip().upper() == expected_key

# 2. تهيئة قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 3. فحص التفعيل
def check_activation():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'activated'")
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == "true"

def activate_app():
    print("\n" + "="*35)
    print("      تطبيق المبيعات غير مفعل")
    print("="*35)
    client_name = input("أدخل اسم المحل/العميل: ").strip()
    user_key = input("أدخل كود التفعيل الخاص بك: ").strip()
    
    if verify_key(client_name, user_key):
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('activated', 'true')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('client_name', ?)", (client_name,))
        conn.commit()
        conn.close()
        print(f"\n تم تفعيل التطبيق بنجاح لـ ({client_name})! مرحباً بك.")
        return True
    else:
        print("\n كود التفعيل أو اسم العميل غير صحيح! تواصل مع المبرمج للحصول على الكود.")
        return False

# 4. وظائف المخزون
def add_product():
    print("\n--- إضافة منتج جديد للمخزن ---")
    name = input("اسم المنتج: ").strip()
    try:
        price = float(input("سعر القطعة: "))
        stock = int(input("الكمية المتوفرة بالمخزن: "))
        
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()
        conn.close()
        print(f" تم إضافة المنتج '{name}' للمخزن بنجاح.")
    except sqlite3.IntegrityError:
        print(" هذا المنتج موجود بالفعل بالمخزن!")
    except ValueError:
        print(" خطأ في إدخال السعر أو الكمية! يرجى إدخال أرقام صحيحة.")

def show_stock():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*40)
    print("               حالة المخزون الحالي")
    print("="*40)
    if not rows:
        print("المخزن فارغ حالياً!")
    else:
        for row in rows:
            status = " (تنبيه: الكمية قريبة من النفاد!)" if row[3] <= 3 else ""
            print(f"ID: {row[0]} | المنتج: {row[1]} | السعر: {row[2]} ج.م | المخزون: {row[3]}{status}")
    print("="*40)

# 5. وظائف المبيعات
def make_sale():
    print("\n--- تسجيل عملية بيع ---")
    name = input("اسم المنتج المباع: ").strip()
    
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price, stock FROM products WHERE name = ?", (name,))
    prod = cursor.fetchone()
    
    if not prod:
        print(" خطأ: هذا المنتج غير موجود في المخزن!")
        conn.close()
        return

    try:
        qty = int(input("الكمية المباعة: "))
        price, current_stock = prod

        if qty <= 0:
            print(" الكمية يجب أن تكون أكبر من 0!")
            conn.close()
            return
            
        if qty > current_stock:
            print(f" خطأ: الكمية المتاحة في المخزن هي ({current_stock}) فقط!")
            conn.close()
            return

        new_stock = current_stock - qty
        total_price = price * qty
        cursor.execute("UPDATE products SET stock = ? WHERE name = ?", (new_stock, name))
        cursor.execute("INSERT INTO sales (product_name, quantity, total_price) VALUES (?, ?, ?)", (name, qty, total_price))
        conn.commit()
        conn.close()

        print(f"\n تم البيع بنجاح! الإجمالي: {total_price} ج.م")
        print(f"المتبقي بالمخزن من '{name}': {new_stock} قطعة.")
    except ValueError:
        print(" يرجى إدخال رقم صحيح للكمية!")

def show_sales_report():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, quantity, total_price, date FROM sales ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    print("\n" + "="*45)
    print("               سجل المبيعات والأرباح")
    print("="*45)
    grand_total = 0
    if not rows:
        print("لا توجد عمليات بيع مسجلة حتى الآن.")
    else:
        for row in rows:
            print(f"رقم: {row[0]} | المنتج: {row[1]} | الكمية: {row[2]} | الإجمالي: {row[3]} ج.م | التاريخ: {row[4]}")
            grand_total += row[3]
    print("-"*45)
    print(f"إجمالي المبيعات الكلية: {grand_total} ج.م")
    print("="*45)

# 6. التشغيل الرئيسي
if __name__ == "__main__":
    init_db()
    
    if not check_activation():
        if not activate_app():
            exit()

    while True:
        print("\n--- نظام الكاشير والمخزون (مُفعل) ---")
        print("1. تسجيل عملية بيع جديدة")
        print("2. عرض سجل المبيعات والأرباح")
        print("3. إضافة منتج جديد للمخزن")
        print("4. عرض حالة المخزون")
        print("5. خروج")
        choice = input("اختر خياراً (1-5): ").strip()

        if choice == "1":
            make_sale()
        elif choice == "2":
            show_sales_report()
        elif choice == "3":
            add_product()
        elif choice == "4":
            show_stock()
        elif choice == "5":
            print("\nتم إغلاق البرنامج بنجاح. شكراً لك!")
            break
        else:
            print("خيار غير صحيح، حاول مرة أخرى.")
