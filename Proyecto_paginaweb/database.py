import sqlite3

def conectar():
    conn = sqlite3.connect("nexoffice.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            precio REAL,
            stock INTEGER
        )
    """)
    
    # Insertar los 11 modelos base si la tabla está vacía
    cursor.execute("SELECT count(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        productos = [
            ('Canon Láser MF-445DW', 15990.0, 10),
            ('Multifuncional Canon Láser MF-236N', 28995.0, 8),
            ('Multifuncional Canon Láser a Color MF-731CDW', 40595.0, 5),
            ('Multifuncional Canon Láser IR-1643i II', 52995.0, 3),
            ('Multifuncional Canon Láser MF-264DW', 16000.0, 12),
            ('Multifuncional Canon Láser MF-414DW', 18990.0, 7),
            ('Multifuncional Canon Láser MF-455DW', 25000.0, 6),
            ('Multifuncional Canon Láser MF-453DW', 28995.0, 9),
            ('Multifuncional Laser Color Brother MFC-9570CDW', 60990.0, 4),
            ('Multifuncional Laser Monocromática Brother MFC-L5800DW', 30995.0, 10),
            ('Multifuncional Laser Monocromatica Brother MFC-L6750DW', 25990.0, 5)
        ]
        cursor.executemany("INSERT INTO inventario (nombre, precio, stock) VALUES (?, ?, ?)", productos)
    
    conn.commit()
    conn.close()

def obtener_inventario():
    conn = sqlite3.connect("nexoffice.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio, stock FROM inventario")
    data = cursor.fetchall()
    conn.close()
    return data

def actualizar_stock(nombre, cant):
    conn = sqlite3.connect("nexoffice.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE inventario SET stock = stock - ? WHERE nombre = ?", (cant, nombre))
    conn.commit()
    conn.close()

# ESTA ES LA FUNCIÓN NUEVA QUE NECESITA EL MANAGER
def guardar_o_actualizar_producto(nombre, precio, stock):
    conn = sqlite3.connect("nexoffice.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO inventario (nombre, precio, stock) 
        VALUES (?, ?, ?)
    """, (nombre, precio, stock))
    conn.commit()
    conn.close()