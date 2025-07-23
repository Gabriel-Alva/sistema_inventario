# Punto de entrada principal para probar el sistema de inventario 
from db.models import (
    insertar_producto, insertar_entrada, insertar_venta,
    consultar_productos_bajos, calcular_total_ventas, obtener_stock_producto
)

if __name__ == '__main__':
    # Ejemplo: Insertar un producto
    id_prod = insertar_producto(
        nombre='Paracetamol',
        descripcion='Caja de 20 tabletas',
        precio_venta=10.0,
        precio_compra=5.0,
        stock=10,
        stock_minimo=5
    )
    print(f'Producto insertado con ID: {id_prod}')

    # Ejemplo: Insertar una entrada (aumenta stock)
    id_entrada = insertar_entrada(id_producto=id_prod, cantidad=5)
    print(f'Entrada insertada con ID: {id_entrada}')

    # Ejemplo: Insertar una venta (disminuye stock)
    id_venta = insertar_venta(id_producto=id_prod, cantidad=3, precio_total=30.0)
    print(f'Venta insertada con ID: {id_venta}')

    # Consultar productos con stock bajo
    bajos = consultar_productos_bajos()
    print('Productos con stock bajo:', bajos)

    # Consultar total de ventas de un producto
    total_ventas = calcular_total_ventas(id_prod)
    print(f'Total vendido del producto {id_prod}: {total_ventas}')

    # Consultar stock actual de un producto
    stock_actual = obtener_stock_producto(id_prod)
    print(f'Stock actual del producto {id_prod}: {stock_actual}') 