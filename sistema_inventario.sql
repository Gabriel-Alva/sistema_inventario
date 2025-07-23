-- Base de datos: sistema_inventario
-- Estructura y datos de ejemplo realistas

-- Elimina tablas si existen (orden correcto por FK)
DROP TABLE IF EXISTS ventas CASCADE;
DROP TABLE IF EXISTS entradas CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;
DROP TABLE IF EXISTS proveedores CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL
);

-- Tabla de categorías
CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE
);

-- Tabla de productos
CREATE TABLE productos (
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

-- Tabla de entradas
CREATE TABLE entradas (
    id_entrada SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    fecha_entrada TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla de ventas
CREATE TABLE ventas (
    id_venta SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_total NUMERIC(10, 2) NOT NULL,
    fecha_venta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Función productos_bajos
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

-- Función calcular_total_ventas
CREATE OR REPLACE FUNCTION calcular_total_ventas(producto_id INT) RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(precio_total), 0) FROM ventas WHERE id_producto = producto_id;
$$ LANGUAGE sql;

-- Función obtener_stock_producto
CREATE OR REPLACE FUNCTION obtener_stock_producto(producto_id INT) RETURNS INT AS $$
    SELECT stock FROM productos WHERE id_producto = producto_id;
$$ LANGUAGE sql;

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

-- Usuarios ficticios
INSERT INTO usuarios (username, password) VALUES
('admin', 'admin123'),
('jose', 'josepass'),
('maria', 'maria2024');

-- Categorías ficticias
INSERT INTO categorias (nombre, descripcion) VALUES
('Bebidas', 'Bebidas frías y calientes'),
('Snacks', 'Botanas y snacks variados'),
('Limpieza', 'Productos de limpieza para el hogar'),
('Lácteos', 'Leche, quesos y derivados');

-- Proveedores ficticios
INSERT INTO proveedores (nombre, contacto, telefono, email) VALUES
('Distribuidora Central', 'Carlos Pérez', '987654321', 'contacto@distribcentral.com'),
('Alimentos del Norte', 'Ana Torres', '912345678', 'ventas@alimentosnorte.com'),
('LimpiaMax', 'Luis Gómez', '934567890', 'info@limpiamax.com');

-- Productos ficticios
INSERT INTO productos (nombre, descripcion, precio_venta, precio_compra, stock, stock_minimo, id_categoria, id_proveedor) VALUES
('Coca-Cola 600ml', 'Refresco embotellado', 1.20, 0.80, 30, 10, 1, 1),
('Papas Fritas', 'Bolsa de papas fritas 50g', 0.90, 0.50, 15, 5, 2, 2),
('Detergente Líquido', 'Detergente para ropa 1L', 3.50, 2.20, 8, 4, 3, 3),
('Queso Manchego', 'Queso manchego 200g', 2.80, 1.90, 12, 6, 4, 2),
('Agua Mineral', 'Botella 500ml', 0.70, 0.40, 25, 8, 1, 1);

-- Entradas ficticias
INSERT INTO entradas (id_producto, cantidad, fecha_entrada) VALUES
(1, 20, '2024-07-01 09:00:00'),
(2, 10, '2024-07-02 10:30:00'),
(3, 5, '2024-07-03 11:15:00'),
(4, 8, '2024-07-04 12:00:00'),
(5, 15, '2024-07-05 13:45:00');

-- Ventas ficticias
INSERT INTO ventas (id_producto, cantidad, precio_total, fecha_venta) VALUES
(1, 5, 6.00, '2024-07-06 14:00:00'),
(2, 3, 2.70, '2024-07-06 15:00:00'),
(3, 2, 7.00, '2024-07-07 16:00:00'),
(4, 4, 11.20, '2024-07-07 17:00:00'),
(5, 6, 4.20, '2024-07-08 18:00:00'); 