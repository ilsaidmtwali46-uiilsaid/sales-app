import sqlite3

# 1. إنشاء قاعدة البيانات وجدول المبيعات
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 2. إضافة عملية بيع جديدة
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

# 3. عرض جميع المبيعات وحساب الإجمالي العام
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

# 4. قائمة التحكم بالبرنامج
if __name__ == "__main__":
    init_db()
    while True:
        print("\n--- نظام الكاشير والمبيعات ---")
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
