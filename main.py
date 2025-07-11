# main.py
from db import Product, Sale, InventoryModification, get_db_session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Función para agregar un nuevo producto a la base de datos
def add_product(name, price_caja_fria, price_caja_caliente, price_caja_particular, price_six_pack, price_unitario, stock, min_stock, units_per_box, cost_price_box):
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
            units_per_box=units_per_box,
            cost_price_box=cost_price_box # Nuevo campo
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
# Ahora también recibe cost_price_at_sale para almacenarlo en el registro de venta
def record_sale(product_id, quantity, unit_price_at_sale, total_price, discount, cost_price_at_sale):
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
            sale_date=datetime.now(), # Registra la fecha y hora actual de la venta
            cost_price_at_sale=cost_price_at_sale # Nuevo campo: Costo unitario al momento de la venta
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
def update_product_details(product_id, new_prices, new_stock, new_min_stock, new_cost_price_box):
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
        
        # Verificar y actualizar el valor de compra de la caja
        if product.cost_price_box != new_cost_price_box:
            old_cost_price_box = product.cost_price_box
            product.cost_price_box = new_cost_price_box
            changes_made = True
            change_records.append({
                "field": "cost_price_box",
                "old_value": old_cost_price_box,
                "new_value": new_cost_price_box
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

# Función para calcular la ganancia por tipo de precio (potencial, no por venta real)
def calculate_profit_per_type(product):
    profits = {}
    cost_per_unit = 0.0

    # Calcular el costo por unidad basado en el 'Valor Caja' y 'Unidades por Caja'
    if product.units_per_box > 0:
        cost_per_unit = product.cost_price_box / product.units_per_box
    else:
        # Si units_per_box es 0 (lo cual no debería pasar con las opciones dadas)
        # o para el caso Unitario, el costo por unidad es el mismo que el costo de la caja si es 1 unidad
        # Asumimos que para unitario, el cost_price_box es el costo de una unidad.
        cost_per_unit = product.cost_price_box 

    # Ganancia para Caja Fria
    if product.units_per_box > 0:
        profit_caja_fria = (product.price_caja_fria / product.units_per_box) - cost_per_unit
    else: # Fallback para evitar división por cero si units_per_box no está configurado correctamente
        profit_caja_fria = product.price_caja_fria - cost_per_unit
    profits["Caja Fria"] = profit_caja_fria

    # Ganancia para Caja Caliente
    if product.units_per_box > 0:
        profit_caja_caliente = (product.price_caja_caliente / product.units_per_box) - cost_per_unit
    else:
        profit_caja_caliente = product.price_caja_caliente - cost_per_unit
    profits["Caja Caliente"] = profit_caja_caliente

    # Ganancia para Caja Particular
    if product.units_per_box > 0:
        profit_caja_particular = (product.price_caja_particular / product.units_per_box) - cost_per_unit
    else:
        profit_caja_particular = product.price_caja_particular - cost_per_unit
    profits["Caja Particular"] = profit_caja_particular

    # Ganancia para Six-Pack (siempre 6 unidades)
    # El costo por unidad para six-pack es el mismo costo_per_unit general
    profit_six_pack = (product.price_six_pack / 6) - cost_per_unit # Usar cost_per_unit general
    profits["Six-Pack"] = profit_six_pack

    # Ganancia para Unitario
    profit_unitario = product.price_unitario - cost_per_unit
    profits["Unitario"] = profit_unitario

    return profits

# Nueva función para eliminar un producto
def delete_product(product_id):
    session = get_db_session()
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return False, "Error: Producto no encontrado."

        # Registrar la eliminación en el historial de modificaciones
        new_modification = InventoryModification(
            product_id=product.id,
            field_modified="product_deletion",
            old_value=f"Producto: {product.name}, ID: {product.id}",
            new_value="ELIMINADO",
            modification_date=datetime.now()
        )
        session.add(new_modification)

        # Eliminar el producto
        session.delete(product)
        session.commit()
        return True, f"Producto '{product.name}' eliminado exitosamente."
    except Exception as e:
        session.rollback()
        return False, f"Error al eliminar producto: {e}"
    finally:
        session.close()

# Nueva función para eliminar una venta
def delete_sale(sale_id):
    session = get_db_session()
    try:
        sale = session.query(Sale).filter_by(id=sale_id).first()
        if not sale:
            return False, "Error: Venta no encontrada."

        # Obtener el producto asociado para el registro de historial
        product = get_product_by_id(sale.product_id)
        product_name = product.name if product else "Desconocido"

        # Registrar la eliminación en el historial de modificaciones
        new_modification = InventoryModification(
            product_id=sale.product_id, # Usar el ID del producto asociado a la venta
            field_modified="sale_deletion",
            old_value=f"Venta ID: {sale.id}, Producto: {product_name}, Cantidad: {sale.quantity}, Total: {sale.total_price}",
            new_value="ELIMINADA",
            modification_date=datetime.now()
        )
        session.add(new_modification)

        # Eliminar la venta
        session.delete(sale)
        session.commit()
        return True, f"Venta ID {sale.id} eliminada exitosamente."
    except Exception as e:
        session.rollback()
        return False, f"Error al eliminar venta: {e}"
    finally:
        session.close()
