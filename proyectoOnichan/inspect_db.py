import sqlite3
try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Try to find product table (assuming app name is appOnichan)
    product_table = None
    for t in tables:
        if 'product' in t[0].lower():
            product_table = t[0]
            break
            
    if product_table:
        cursor.execute(f"SELECT count(*) FROM {product_table}")
        print(f"Count in {product_table}:", cursor.fetchone()[0])
    else:
        print("No product table found")
        
    conn.close()
except Exception as e:
    print("Error:", e)
