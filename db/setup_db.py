import psycopg2
from .config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

# Script SQL para crear tablas, triggers y funciones
SQL_SCRIPT = '''
-- Tabla para almacenar las categorías de los productos
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar la información de los proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla principal para los productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio_venta NUMERIC(10, 2) NOT NULL CHECK (precio_venta > 0),
    precio_compra NUMERIC(10, 2) CHECK (precio_compra > 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INT NOT NULL DEFAULT 5 CHECK (stock_minimo >= 0),
    id_categoria INT,
    id_proveedor INT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
);

-- Tabla para registrar las entradas de stock
CREATE TABLE IF NOT EXISTS entradas (
    id_entrada SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    fecha_entrada TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla para registrar las ventas de productos
CREATE TABLE IF NOT EXISTS ventas (
    id_venta SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_total NUMERIC(10, 2) NOT NULL,
    fecha_venta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Función para obtener productos con stock bajo
CREATE OR REPLACE FUNCTION productos_bajos() RETURNS TABLE(
    id_producto INT,
    nombre VARCHAR,
    stock INT,
    stock_minimo INT
) AS $$
BEGIN
    RETURN QUERY SELECT id_producto, nombre, stock, stock_minimo FROM productos WHERE stock < stock_minimo;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar stock después de una venta
CREATE OR REPLACE FUNCTION actualizar_stock_venta() RETURNS TRIGGER AS $$
BEGIN
    UPDATE productos SET stock = stock - NEW.cantidad, ultima_actualizacion = CURRENT_TIMESTAMP WHERE id_producto = NEW.id_producto;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_stock_venta ON ventas;
CREATE TRIGGER trigger_actualizar_stock_venta
AFTER INSERT ON ventas
FOR EACH ROW EXECUTE FUNCTION actualizar_stock_venta();

-- Trigger para incrementar stock después de una entrada
CREATE OR REPLACE FUNCTION incrementar_stock_entrada() RETURNS TRIGGER AS $$
BEGIN
    UPDATE productos SET stock = stock + NEW.cantidad, ultima_actualizacion = CURRENT_TIMESTAMP WHERE id_producto = NEW.id_producto;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_incrementar_stock_entrada ON entradas;
CREATE TRIGGER trigger_incrementar_stock_entrada
AFTER INSERT ON entradas
FOR EACH ROW EXECUTE FUNCTION incrementar_stock_entrada();

-- Función para calcular el total de ventas de un producto
CREATE OR REPLACE FUNCTION calcular_total_ventas(producto_id INT) RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(precio_total), 0) FROM ventas WHERE id_producto = producto_id;
$$ LANGUAGE sql;

-- Función para obtener el stock actual de un producto
CREATE OR REPLACE FUNCTION obtener_stock_producto(producto_id INT) RETURNS INT AS $$
    SELECT stock FROM productos WHERE id_producto = producto_id;
$$ LANGUAGE sql;
'''

def setup_database():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(SQL_SCRIPT)
        print('Base de datos inicializada correctamente.')
    except Exception as e:
        print('Error al inicializar la base de datos:', e)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    setup_database() 