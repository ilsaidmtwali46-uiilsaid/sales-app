import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- 1. إنشاء وتهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    # جدول المنتجات والمخزون
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    # جدول المبيعات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# --- 2. فحص حالة التفعيل ---
def is_activated():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'activated'")
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == "true"

def activate_system():
    key = entry_key.get().strip()
    if key == "SAID2026":
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('activated', 'true')")
        conn.commit()
        conn.close()
        messagebox.showinfo("نجاح", "تم تفعيل البرنامج بنجاح! يرجى إعادة إغلاقه وفتحه.")
        activation_win.destroy()
        open_main_app()
    else:
        messagebox.showerror("خطأ", "كود التفعيل غير صحيح!")

# --- 3. نافذة التطبيق الرئيسية ---
def open_main_app():
    root = tk.Tk()
    root.title("نظام الكاشير وإدارة المخزون")
    root.geometry("450x600")

    # --- وظائف المخزون والمبيعات ---
    def refresh_tables():
        # تحديث جدول المنتجات
        for item in tree_products.get_children():
            tree_products.delete(item)
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock FROM products")
        for row in cursor.fetchall():
            tree_products.insert("", "end", values=row)

        # تحديث جدول المبيعات
        for item in tree_sales.get_children():
            tree_sales.delete(item)
        cursor.execute("SELECT product_name, quantity, total_price, date FROM sales ORDER BY id DESC")
        for row in cursor.fetchall():
            tree_sales.insert("", "end", values=row)
        conn.close()

    def add_product():
        name = entry_prod_name.get().strip()
        price = entry_prod_price.get().strip()
        stock = entry_prod_stock.get().strip()

        if not name or not price or not stock:
            messagebox.showwarning("تنبيه", "يرجى ملء جميع بيانات المنتج")
            return
        try:
            conn = sqlite3.connect("sales.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, float(price), int(stock)))
            conn.commit()
            conn.close()
            messagebox.showinfo("نجاح", f"تم إضافة المنتج '{name}' للمخزون")
            entry_prod_name.delete(0, tk.END)
            entry_prod_price.delete(0, tk.END)
            entry_prod_stock.delete(0, tk.END)
            refresh_tables()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "هذا المنتج موجود بالفعل بالمخزون!")

    def make_sale():
        name = entry_sale_name.get().strip()
        qty_str = entry_sale_qty.get().strip()

        if not name or not qty_str:
            messagebox.showwarning("تنبيه", "يرجى كتابة اسم المنتج والكمية")
            return

        qty = int(qty_str)
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("SELECT price, stock FROM products WHERE name = ?", (name,))
        prod = cursor.fetchone()

        if not prod:
            messagebox.showerror("خطأ", "المنتج غير موجود في المخزن!")
            conn.close()
            return

        price, current_stock = prod
        if qty > current_stock:
            messagebox.showerror("خطأ", f"الكمية المتاحة في المخزن هي {current_stock} فقط!")
            conn.close()
            return

        # خصم الكمية وتسجيل البيع
        new_stock = current_stock - qty
        total_price = price * qty
        cursor.execute("UPDATE products SET stock = ? WHERE name = ?", (new_stock, name))
        cursor.execute("INSERT INTO sales (product_name, quantity, total_price) VALUES (?, ?, ?)", (name, qty, total_price))
        conn.commit()
        conn.close()

        messagebox.showinfo("تم البيع", f"تم عملية البيع بنجاح!\nالإجمالي: {total_price} ج.م")
        entry_sale_name.delete(0, tk.END)
        entry_sale_qty.delete(0, tk.END)
        refresh_tables()

    # --- الواجهة (Tabs) ---
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # تبويب المبيعات
    tab_sales = ttk.Frame(notebook)
    notebook.add(tab_sales, text="إجراء بيع")

    ttk.Label(tab_sales, text="اسم المنتج:").pack(pady=2)
    entry_sale_name = ttk.Entry(tab_sales)
    entry_sale_name.pack(pady=2)

    ttk.Label(tab_sales, text="الكمية المباعة:").pack(pady=2)
    entry_sale_qty = ttk.Entry(tab_sales)
    entry_sale_qty.pack(pady=2)

    ttk.Button(tab_sales, text="إتمام عملية البيع", command=make_sale).pack(pady=10)

    ttk.Label(tab_sales, text="سجل المبيعات الأخيرة:").pack(pady=5)
    tree_sales = ttk.Treeview(tab_sales, columns=("prod", "qty", "total", "date"), show="headings", height=8)
    tree_sales.heading("prod", text="المنتج")
    tree_sales.heading("qty", text="الكمية")
    tree_sales.heading("total", text="الإجمالي")
    tree_sales.heading("date", text="التاريخ")
    tree_sales.column("prod", width=90)
    tree_sales.column("qty", width=50)
    tree_sales.column("total", width=70)
    tree_sales.column("date", width=120)
    tree_sales.pack(fill="both", expand=True)

    # تبويب المخزون
    tab_stock = ttk.Frame(notebook)
    notebook.add(tab_stock, text="إدارة المخزون")

    ttk.Label(tab_stock, text="اسم المنتج الجديد:").pack(pady=2)
    entry_prod_name = ttk.Entry(tab_stock)
    entry_prod_name.pack(pady=2)

    ttk.Label(tab_stock, text="سعر القطعة:").pack(pady=2)
    entry_prod_price = ttk.Entry(tab_stock)
    entry_prod_price.pack(pady=2)

    ttk.Label(tab_stock, text="الكمية الأولية بالمخزن:").pack(pady=2)
    entry_prod_stock = ttk.Entry(tab_stock)
    entry_prod_stock.pack(pady=2)

    ttk.Button(tab_stock, text="إضافة للمخزن", command=add_product).pack(pady=10)

    ttk.Label(tab_stock, text="قائمة المنتجات والمخزون الحالي:").pack(pady=5)
    tree_products = ttk.Treeview(tab_stock, columns=("name", "price", "stock"), show="headings", height=8)
    tree_products.heading("name", text="اسم المنتج")
    tree_products.heading("price", text="السعر")
    tree_products.heading("stock", text="المخزون")
    tree_products.column("name", width=120)
    tree_products.column("price", width=80)
    tree_products.column("stock", width=80)
    tree_products.pack(fill="both", expand=True)

    refresh_tables()
    root.mainloop()

# --- 4. نقطة الانطلاق ---
if __name__ == "__main__":
    init_db()
    if is_activated():
        open_main_app()
    else:
        activation_win = tk.Tk()
        activation_win.title("تفعيل البرنامج")
        activation_win.geometry("300x180")

        tk.Label(activation_win, text="البرنامج غير مفعّل!\nأدخل كود التفعيل:").pack(pady=15)
        entry_key = tk.Entry(activation_win, show="*")
        entry_key.pack(pady=5)

        tk.Button(activation_win, text="تفعيل الآن", command=activate_system).pack(pady=10)
        activation_win.mainloop()
