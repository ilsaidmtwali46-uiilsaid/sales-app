def print_invoice(product, quantity, price):
    total = quantity * price
    print("\n--- فاتورة مبيعات ---")
    print(f"المنتج: {product}")
    print(f"الكمية: {quantity}")
    print(f"السعر: {price}")
    print(f"الإجمالي: {total}")
    print("--------------------")

if __name__ == "__main__":
    p = input("اسم المنتج: ")
    q = int(input("الكمية: "))
    pr = float(input("السعر: "))
    print_invoice(p, q, pr)
