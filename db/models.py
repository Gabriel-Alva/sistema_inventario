import psycopg2
from .config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def insertar_producto(nombre, descripcion, precio_venta, precio_compra, stock, stock_minimo, id_categoria=None, id_proveedor=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO productos (nombre, descripcion, precio_venta, precio_compra, stock, stock_minimo, id_categoria, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_producto;
        ''', (nombre, descripcion, precio_venta, precio_compra, stock, stock_minimo, id_categoria, id_proveedor))
        id_producto = cur.fetchone()[0]
        conn.commit()
        return id_producto
    finally:
        cur.close()
        conn.close()

def insertar_entrada(id_producto, cantidad):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO entradas (id_producto, cantidad)
            VALUES (%s, %s)
            RETURNING id_entrada;
        ''', (id_producto, cantidad))
        id_entrada = cur.fetchone()[0]
        conn.commit()
        return id_entrada
    finally:
        cur.close()
        conn.close()

def insertar_venta(id_producto, cantidad, precio_total):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO ventas (id_producto, cantidad, precio_total)
            VALUES (%s, %s, %s)
            RETURNING id_venta;
        ''', (id_producto, cantidad, precio_total))
        id_venta = cur.fetchone()[0]
        conn.commit()
        return id_venta
    finally:
        cur.close()
        conn.close()

def consultar_productos_bajos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM productos_bajos();')
        resultados = cur.fetchall()
        return [
            {
                'id_producto': r[0],
                'nombre': r[1],
                'stock': r[2],
                'stock_minimo': r[3]
            } for r in resultados
        ]
    finally:
        cur.close()
        conn.close()

def calcular_total_ventas(producto_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT calcular_total_ventas(%s);', (producto_id,))
        total = cur.fetchone()[0]
        return total
    finally:
        cur.close()
        conn.close()

def obtener_stock_producto(producto_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT obtener_stock_producto(%s);', (producto_id,))
        stock = cur.fetchone()[0]
        return stock
    finally:
        cur.close()
        conn.close()

def total_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM usuarios;')
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def total_categorias():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM categorias;')
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def total_productos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM productos;')
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def total_ventas():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM ventas;')
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def productos_mas_vendidos(limit=3):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT p.nombre, SUM(v.cantidad) as total_vendido, COUNT(v.id_venta) as cantidad_total
            FROM ventas v
            JOIN productos p ON v.id_producto = p.id_producto
            GROUP BY p.nombre
            ORDER BY total_vendido DESC
            LIMIT %s;
        ''', (limit,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def ultimas_ventas(limit=5):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT v.id_venta, p.nombre, v.fecha_venta, v.precio_total
            FROM ventas v
            JOIN productos p ON v.id_producto = p.id_producto
            ORDER BY v.fecha_venta DESC
            LIMIT %s;
        ''', (limit,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def productos_recientes(limit=3):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT nombre, precio_venta, fecha_creacion
            FROM productos
            ORDER BY fecha_creacion DESC
            LIMIT %s;
        ''', (limit,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def listar_categorias():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT id_categoria, nombre, descripcion FROM categorias ORDER BY nombre;')
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def agregar_categoria(nombre, descripcion):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s) RETURNING id_categoria;', (nombre, descripcion))
        conn.commit()
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def editar_categoria(id_categoria, nombre, descripcion):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE categorias SET nombre=%s, descripcion=%s WHERE id_categoria=%s;', (nombre, descripcion, id_categoria))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def eliminar_categoria(id_categoria):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM categorias WHERE id_categoria=%s;', (id_categoria,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def listar_proveedores():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT id_proveedor, nombre, contacto, telefono, email FROM proveedores ORDER BY nombre;')
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def agregar_proveedor(nombre, contacto, telefono, email):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO proveedores (nombre, contacto, telefono, email) VALUES (%s, %s, %s, %s) RETURNING id_proveedor;', (nombre, contacto, telefono, email))
        conn.commit()
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def editar_proveedor(id_proveedor, nombre, contacto, telefono, email):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE proveedores SET nombre=%s, contacto=%s, telefono=%s, email=%s WHERE id_proveedor=%s;', (nombre, contacto, telefono, email, id_proveedor))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def eliminar_proveedor(id_proveedor):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM proveedores WHERE id_proveedor=%s;', (id_proveedor,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def registrar_usuario(username, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO usuarios (username, password) VALUES (%s, %s) RETURNING id;', (username, password))
        conn.commit()
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def total_proveedores():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM proveedores;')
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close() 