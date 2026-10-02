import sqlite3

# 1. إنشاء قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    # جدول المبيعات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL
        )
    ''')
    # جدول التفعيل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. التحقق من التفعيل
def check_activation():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'activated'")
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "true":
        return True
    return False

# 3. تفعيل التطبيق
def activate_app():
    SECRET_KEY = "SAID2026"  # كود التفعيل الخاص بك كـ مبرمج
    print("\n=== تطبيق المبيعات غير مفعل ===")
    user_key = input("أدخل كود التفعيل لتشغيل البرنامج: ")
    
    if user_key == SECRET_KEY:
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('activated', 'true')")
        conn.commit()
        conn.close()
        print("تم تفعيل التطبيق بنجاح! مرحباً بك.")
        return True
    else:
        print("كود التفعيل غير صحيح! اتصل بالمبرمج للحصول على الكود.")
        return False

# 4. إضافة عملية بيع جديدة
def add_sale(product, quantity, price):
    total = quantity * price
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sales (product, quantity, price, total)
        VALUES (?, ?, ?, ?)
    ''', (product, quantity, price, total))
    conn.commit()
    conn.close()
    print(f"\n تم حفظ الفاتورة بنجاح! الإجمالي: {total}")

# 5. عرض سجل المبيعات
def show_sales():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    rows = cursor.fetchall()
    conn.close()

    print("\n=== سجل المبيعات ===")
    grand_total = 0
    for row in rows:
        print(f"مُعرف: {row[0]} | المنتج: {row[1]} | الكمية: {row[2]} | السعر: {row[3]} | الإجمالي: {row[4]}")
        grand_total += row[4]
    print(f"--------------------")
    print(f"إجمالي كل المبيعات: {grand_total} ج.م\n")

# 6. التشغيل الرئيسي
if __name__ == "__main__":
    init_db()
    
    # فحص التفعيل قبل الدخول للبرنامج
    if not check_activation():
        if not activate_app():
            exit()  # إغلاق البرنامج إذا لم يتم التفعيل

    while True:
        print("\n--- نظام الكاشير والمبيعات (مُفعل) ---")
        print("1. تسجيل عملية بيع جديدة")
        print("2. عرض سجل المبيعات والإجمالي")
        print("3. خروج")
        choice = input("اختر من القائمة (1-3): ")

        if choice == "1":
            p = input("اسم المنتج: ")
            q = int(input("الكمية: "))
            pr = float(input("السعر: "))
            add_sale(p, q, pr)
        elif choice == "2":
            show_sales()
        elif choice == "3":
            print("تم إغلاق البرنامج.")
            break
        else:
            print("خيار غير صحيح، حاول مرة أخرى.")
