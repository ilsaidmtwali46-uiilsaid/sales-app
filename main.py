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

# 3. تشغيل البرنامج
if __name__ == "__main__":
    init_db()
    p = input("اسم المنتج: ")
    q = int(input("الكمية: "))
    pr = float(input("السعر: "))
    add_sale(p, q, pr)
