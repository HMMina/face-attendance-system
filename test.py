import psycopg2
try:
    conn = psycopg2.connect(
        dbname="attendance",
        user="postgres",
        password="Minh452004a5",
        host="localhost",
        port=5432
    )
    print("Kết nối database thành công!")
    conn.close()
except Exception as e:
    print("Lỗi kết nối:", e)