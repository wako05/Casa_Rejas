# main.py
from db import Product, Sale, InventoryModification, get_db_session # Importa InventoryModification
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Función para agregar un nuevo producto a la base de datos
def add_product(name, price_caja_fria, price_caja_caliente, price_caja_particular, price_six_pack, price_unitario, stock, min_stock, units_per_box):
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        # Crea una nueva instancia de Producto
        new_product = Product(
            name=name,
            price_caja_fria=price_caja_fria,
            price_caja_caliente=price_caja_caliente,
            price_caja_particular=price_caja_particular,
            price_six_pack=price_six_pack,
            price_unitario=price_unitario,
            stock=stock,
            min_stock=min_stock,
            units_per_box=units_per_box
        )
        session.add(new_product) # Agrega el nuevo producto a la sesión
        session.commit() # Confirma los cambios en la base de datos
        return True, "Producto agregado exitosamente." # Retorna éxito
    except IntegrityError:
        session.rollback() # Si hay un error de integridad (ej. nombre duplicado), revierte la transacción
        return False, "Error: Ya existe un producto con este nombre." # Retorna error
    except Exception as e:
        session.rollback() # Si hay cualquier otro error, revierte la transacción
        return False, f"Error al agregar producto: {e}" # Retorna error con el mensaje de la excepción
    finally:
        session.close() # Cierra la sesión de la base de datos

# Función para obtener todos los productos de la base de datos
def get_all_products():
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        products = session.query(Product).all() # Consulta todos los productos
        return products # Retorna la lista de productos
    finally:
        session.close() # Cierra la sesión de la base de datos

# Función para obtener un producto por su ID
def get_product_by_id(product_id):
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        product = session.query(Product).filter_by(id=product_id).first() # Busca un producto por su ID
        return product # Retorna el producto encontrado o None si no existe
    finally:
        session.close() # Cierra la sesión de la base de datos

# Función para registrar una venta
# Modificada para recibir unit_price_at_sale y total_price ya calculados desde la UI
def record_sale(product_id, quantity, unit_price_at_sale, total_price, discount):
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        product = session.query(Product).filter_by(id=product_id).first() # Busca el producto por su ID
        if not product:
            return False, "Error: Producto no encontrado." # Retorna error si el producto no existe

        if product.stock < quantity:
            return False, "Error: No hay suficiente stock disponible." # Retorna error si no hay stock suficiente

        # Crea una nueva instancia de Venta
        new_sale = Sale(
            product_id=product.id,
            quantity=quantity, # Esta es la cantidad total de unidades vendidas
            discount=discount,
            unit_price_at_sale=unit_price_at_sale, # Precio unitario real de la venta
            total_price=total_price, # Precio total de la venta
            sale_date=datetime.now() # Registra la fecha y hora actual de la venta
        )
        session.add(new_sale) # Agrega la nueva venta a la sesión

        product.stock -= quantity # Reduce el stock del producto por la cantidad total de unidades
        session.commit() # Confirma los cambios en la base de datos

        return True, "Venta registrada exitosamente." # Retorna éxito
    except Exception as e:
        session.rollback() # Si hay un error, revierte la transacción
        return False, f"Error al registrar venta: {e}" # Retorna error con el mensaje de la excepción
    finally:
        session.close() # Cierra la sesión de la base de datos

# Función para obtener todas las ventas de la base de datos
def get_all_sales():
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        # Consulta todas las ventas, ordenadas por fecha de venta descendente
        sales = session.query(Sale).order_by(Sale.sale_date.desc()).all()
        return sales # Retorna la lista de ventas
    finally:
        session.close() # Cierra la sesión de la base de datos

# Función para actualizar los detalles de un producto y registrar el historial de cambios
def update_product_details(product_id, new_prices, new_stock, new_min_stock):
    session = get_db_session()
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return False, "Error: Producto no encontrado."

        changes_made = False
        # Lista para almacenar los detalles de los cambios realizados
        change_records = []

        # Verificar y actualizar precios
        for price_type, new_value in new_prices.items():
            current_value = getattr(product, price_type)
            if current_value != new_value:
                setattr(product, price_type, new_value)
                changes_made = True
                change_records.append({
                    "field": price_type,
                    "old_value": current_value,
                    "new_value": new_value
                })

        # Verificar y actualizar stock
        if product.stock != new_stock:
            old_stock = product.stock
            product.stock = new_stock
            changes_made = True
            change_records.append({
                "field": "stock",
                "old_value": old_stock,
                "new_value": new_stock
            })

        # Verificar y actualizar stock mínimo
        if product.min_stock != new_min_stock:
            old_min_stock = product.min_stock
            product.min_stock = new_min_stock
            changes_made = True
            change_records.append({
                "field": "min_stock",
                "old_value": old_min_stock,
                "new_value": new_min_stock
            })

        if changes_made:
            # Registrar cada cambio individualmente en el historial
            for record in change_records:
                new_modification = InventoryModification(
                    product_id=product.id,
                    field_modified=record["field"],
                    old_value=str(record["old_value"]), # Convertir a string para almacenar
                    new_value=str(record["new_value"]), # Convertir a string para almacenar
                    modification_date=datetime.now()
                )
                session.add(new_modification)
            
            session.commit()
            return True, "Detalles del producto actualizados exitosamente."
        else:
            return False, "No se detectaron cambios para actualizar."
    except Exception as e:
        session.rollback()
        return False, f"Error al actualizar detalles del producto: {e}"
    finally:
        session.close()

# Función para obtener el historial de modificaciones de inventario
def get_inventory_modifications():
    session = get_db_session()
    try:
        modifications = session.query(InventoryModification).order_by(InventoryModification.modification_date.desc()).all()
        return modifications
    finally:
        session.close()

# Función para obtener el inventario actual (productos con stock actualizado)
def get_current_inventory():
    session = get_db_session() # Obtiene una nueva sesión de base de datos
    try:
        # Consulta todos los productos
        products = session.query(Product).all()
        return products # Retorna la lista de productos
    finally:
        session.close() # Cierra la sesión de la base de datos