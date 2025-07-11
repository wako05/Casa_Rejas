# ui.py
import streamlit as st
import pandas as pd
# Asegúrate de importar todas las funciones necesarias, incluyendo las nuevas de eliminación
from main import add_product, get_all_products, record_sale, get_all_sales, get_product_by_id, get_current_inventory, update_product_details, get_inventory_modifications, calculate_profit_per_type, delete_product, delete_sale
from io import BytesIO

# Función para convertir un DataFrame a formato Excel
def to_excel(df):
    output = BytesIO() # Crea un objeto BytesIO en memoria
    writer = pd.ExcelWriter(output, engine='xlsxwriter') # Crea un escritor de Excel
    df.to_excel(writer, index=False, sheet_name='Sheet1') # Escribe el DataFrame al Excel
    writer.close() # Cierra el escritor
    processed_data = output.getvalue() # Obtiene los datos del Excel
    return processed_data # Retorna los datos

# Título principal de la aplicación
st.set_page_config(layout="wide") # Configura el diseño de la página para que sea ancho
st.title("Sistema de Gestión de Inventario y Ventas") # Título de la aplicación

# Crea las pestañas para navegar entre las diferentes secciones de la aplicación
tab1, tab2, tab3, tab4 = st.tabs(["Inventario", "Ventas", "Reportes y Stock Actual", "Modificación Inventario"])

# --- Pestaña de Inventario ---
with tab1:
    st.header("Gestión de Inventario") # Encabezado de la sección de inventario

    with st.expander("Agregar Nuevo Producto"): # Un expansor para ocultar/mostrar el formulario de agregar producto
        st.subheader("Agregar Producto") # Subencabezado para agregar producto
        # Campos de entrada para los detalles del producto
        product_name = st.text_input("Nombre del Producto")
        col1, col2, col3 = st.columns(3) # Columnas para organizar los campos de precio
        with col1:
            price_caja_fria = st.number_input("Precio Caja Fria", min_value=0.0, format="%.2f", key="add_price_caja_fria")
            price_six_pack = st.number_input("Precio Six-Pack", min_value=0.0, format="%.2f", key="add_price_six_pack")
        with col2:
            price_caja_caliente = st.number_input("Precio Caja Caliente", min_value=0.0, format="%.2f", key="add_price_caja_caliente")
            price_unitario = st.number_input("Precio Unitario", min_value=0.0, format="%.2f", key="add_price_unitario")
        with col3:
            price_caja_particular = st.number_input("Precio Caja Particular", min_value=0.0, format="%.2f", key="add_price_caja_particular")

        # Nuevo campo: Valor Caja (Costo al Distribuidor)
        cost_price_box = st.number_input("Valor Caja (Costo al Distribuidor)", min_value=0.0, format="%.2f", key="add_cost_price_box")

        stock = st.number_input("Stock Actual", min_value=0, step=1, key="add_stock") # Campo para el stock actual
        min_stock = st.number_input("Stock Mínimo para Alerta", min_value=0, step=1, key="add_min_stock") # Campo para el stock mínimo

        # Selector para las unidades por caja
        units_per_box_options = {"30 unidades": 30, "24 unidades": 24, "13 unidades": 13, "6 unidades (Six-Pack)": 6, "1 unidad (Unitario)": 1}
        selected_units_per_box_label = st.selectbox("Unidades por CAJA (para precios de caja)", list(units_per_box_options.keys()), key="add_units_per_box_label")
        units_per_box = units_per_box_options[selected_units_per_box_label] # Obtiene el valor numérico

        # Botón para agregar el producto
        if st.button("Agregar Producto al Inventario", key="add_product_button"):
            if product_name and (price_caja_fria >= 0 and price_caja_caliente >= 0 and price_caja_particular >= 0 and price_six_pack >= 0 and price_unitario >= 0 and cost_price_box >= 0):
                success, message = add_product(product_name, price_caja_fria, price_caja_caliente, price_caja_particular, price_six_pack, price_unitario, stock, min_stock, units_per_box, cost_price_box)
                if success:
                    st.success(message) # Muestra mensaje de éxito
                else:
                    st.error(message) # Muestra mensaje de error
            else:
                st.warning("Por favor, complete todos los campos y asegúrese de que los precios y el costo no sean negativos.") # Advertencia si faltan campos

    st.subheader("Productos en Inventario") # Subencabezado para la lista de productos
    products = get_all_products() # Obtiene todos los productos de la base de datos
    if products:
        # Crea un DataFrame de pandas para mostrar los productos de manera tabular
        products_data = []
        for p in products:
            profits = calculate_profit_per_type(p) # Calcula las ganancias para cada producto
            products_data.append({
                "ID": p.id,
                "Nombre": p.name,
                "Caja Fria": f"${p.price_caja_fria:,.2f}",
                "Caja Caliente": f"${p.price_caja_caliente:,.2f}",
                "Caja Particular": f"${p.price_caja_particular:,.2f}",
                "Six-Pack": f"${p.price_six_pack:,.2f}",
                "Unitario": f"${p.price_unitario:,.2f}",
                "Valor Caja (Costo)": f"${p.cost_price_box:,.2f}", # Mostrar el nuevo campo
                "Stock Actual": p.stock,
                "Stock Mínimo": p.min_stock,
                "Unidades por Caja": p.units_per_box,
                "Ganancia CF": f"${profits['Caja Fria']:.2f}",
                "Ganancia CC": f"${profits['Caja Caliente']:.2f}",
                "Ganancia CP": f"${profits['Caja Particular']:.2f}",
                "Ganancia SP": f"${profits['Six-Pack']:.2f}",
                "Ganancia U": f"${profits['Unitario']:.2f}"
            })
        df_products = pd.DataFrame(products_data)
        st.dataframe(df_products, use_container_width=True) # Muestra el DataFrame en Streamlit

        # Botón para descargar datos de productos a Excel
        st.download_button(
            label="Descargar Inventario a Excel",
            data=to_excel(df_products),
            file_name="inventario_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay productos en el inventario.") # Mensaje si no hay productos

# --- Pestaña de Ventas ---
with tab2:
    st.header("Registro de Ventas") # Encabezado de la sección de ventas

    products = get_all_products() # Obtiene todos los productos para el selector de ventas
    if products:
        # Mapea nombres de productos a sus IDs
        product_names = {p.name: p.id for p in products}
        selected_product_name = st.selectbox("Seleccione un Producto", list(product_names.keys()), key="sale_product_select")

        selected_product_id = product_names[selected_product_name] if selected_product_name else None
        
        # Obtiene el objeto producto completo para acceder a sus precios y unidades por caja
        current_product = get_product_by_id(selected_product_id) if selected_product_id else None

        # Selector de tipo de precio
        price_types = ["Caja Fria", "Caja Caliente", "Caja Particular", "six-pack", "Unitario"]
        selected_price_type = st.selectbox("Tipo de Precio", price_types, key="sale_price_type_select")

        # Determine the label for the quantity input based on the selected price type
        quantity_label = "Cantidad de Unidades"
        if selected_price_type in ["Caja Fria", "Caja Caliente", "Caja Particular"]:
            quantity_label = "Cantidad de Cajas"
        elif selected_price_type == "six-pack":
            quantity_label = "Cantidad de Six-Packs"

        quantity_input = st.number_input(quantity_label, min_value=1, step=1, key="sale_quantity_input") # Campo para la cantidad
        discount = st.number_input("Descuento (valor entero)", min_value=0, step=1, key="sale_discount_input") # Campo para el descuento

        unit_price_display = 0.0 # Este será el precio por unidad (o por caja/six-pack para mostrar)
        total_price_display = 0.0
        cost_price_at_sale_calc = 0.0 # Costo unitario para almacenar en la venta
        
        # Variables para pasar a record_sale (unidades reales y precio unitario real para el registro)
        quantity_for_sale_record = 0 # Cantidad total de unidades individuales vendidas
        unit_price_for_sale_record = 0.0 # Precio por unidad individual para almacenar en el registro de venta

        if current_product:
            # Calcular el costo por unidad basado en el 'Valor Caja' del producto
            current_cost_per_unit = 0.0
            if current_product.units_per_box > 0:
                current_cost_per_unit = current_product.cost_price_box / current_product.units_per_box
            else:
                current_cost_per_unit = current_product.cost_price_box # Asumimos que para unitario, el costo de la "caja" es el costo unitario

            if selected_price_type == "Caja Fria":
                unit_price_display = current_product.price_caja_fria # Mostrar precio de caja
                quantity_for_sale_record = quantity_input * current_product.units_per_box # Total de unidades para stock
                unit_price_for_sale_record = current_product.price_caja_fria / current_product.units_per_box # Precio unitario real para registro
                cost_price_at_sale_calc = current_cost_per_unit # Costo unitario al momento de la venta
            elif selected_price_type == "Caja Caliente":
                unit_price_display = current_product.price_caja_caliente # Mostrar precio de caja
                quantity_for_sale_record = quantity_input * current_product.units_per_box
                unit_price_for_sale_record = current_product.price_caja_caliente / current_product.units_per_box
                cost_price_at_sale_calc = current_cost_per_unit
            elif selected_price_type == "Caja Particular":
                unit_price_display = current_product.price_caja_particular # Mostrar precio de caja
                quantity_for_sale_record = quantity_input * current_product.units_per_box
                unit_price_for_sale_record = current_product.price_caja_particular / current_product.units_per_box
                cost_price_at_sale_calc = current_cost_per_unit
            elif selected_price_type == "six-pack":
                unit_price_display = current_product.price_six_pack # Mostrar precio de six-pack
                quantity_for_sale_record = quantity_input * 6 # Total de unidades para stock
                unit_price_for_sale_record = current_product.price_six_pack / 6 # Precio unitario real para registro
                cost_price_at_sale_calc = current_cost_per_unit
            elif selected_price_type == "Unitario":
                unit_price_display = current_product.price_unitario # Mostrar precio unitario
                quantity_for_sale_record = quantity_input # Total de unidades para stock
                unit_price_for_sale_record = current_product.price_unitario # Precio unitario real para registro
                cost_price_at_sale_calc = current_cost_per_unit
            
            # Calcular el precio total basado en lo que se muestra (precio de caja/six-pack/unidad)
            total_price_display = (unit_price_display * quantity_input) - discount
            if total_price_display < 0:
                total_price_display = 0

        st.write(f"**Valor por Unidad ({selected_price_type}):** ${unit_price_display:,.2f}") # Muestra el valor por unidad (o caja/six-pack)
        st.write(f"**Valor Total de la Compra:** ${total_price_display:,.2f}") # Muestra el valor total

        # Botón para registrar la venta
        if st.button("Registrar Venta", key="record_sale_button"):
            if selected_product_id and quantity_input > 0:
                # Pasar la cantidad total de unidades calculada y el precio unitario real para el registro de venta
                success, message = record_sale(
                    product_id=selected_product_id,
                    quantity=quantity_for_sale_record,
                    unit_price_at_sale=unit_price_for_sale_record, # Pasar el precio unitario real para el registro
                    total_price=total_price_display, # Pasar el precio total calculado
                    discount=discount, # Pasar el descuento
                    cost_price_at_sale=cost_price_at_sale_calc # Pasar el costo unitario al momento de la venta
                )
                if success:
                    st.success(message) # Muestra mensaje de éxito
                else:
                    st.error(message) # Muestra mensaje de error
            else:
                st.warning("Por favor, seleccione un producto y una cantidad válida.") # Advertencia si faltan campos
    else:
        st.info("No hay productos disponibles para registrar ventas. Agregue productos en la pestaña 'Inventario'.")

# --- Pestaña de Reportes y Stock Actual ---
with tab3:
    st.header("Reportes y Stock Actual") # Encabezado de la sección de reportes

    st.subheader("Inventario Actual") # Subencabezado para el inventario actual
    current_inventory_products = get_current_inventory() # Obtiene el inventario actual
    if current_inventory_products:
        inventory_data = []
        for p in current_inventory_products:
            # Determina si el stock actual es menor que el stock mínimo para mostrar una alarma
            alarm_status = "🚨 ALARMA: Stock Bajo" if p.stock < p.min_stock else "✅ OK"
            inventory_data.append({
                "ID": p.id,
                "Nombre": p.name,
                "Stock Actual": p.stock,
                "Stock Mínimo": p.min_stock,
                "Estado": alarm_status
            })
        df_inventory = pd.DataFrame(inventory_data)
        st.dataframe(df_inventory, use_container_width=True) # Muestra el DataFrame del inventario

        # Botón para descargar el inventario actual a Excel
        st.download_button(
            label="Descargar Inventario Actual a Excel",
            data=to_excel(df_inventory),
            file_name="inventario_actual.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay datos de inventario para mostrar.")

    st.subheader("Historial de Ventas") # Subencabezado para el historial de ventas
    all_sales = get_all_sales() # Obtiene todas las ventas
    if all_sales:
        sales_data = []
        for s in all_sales:
            # Obtiene el nombre del producto asociado a la venta
            product = get_product_by_id(s.product_id)
            product_name = product.name if product else "Desconocido"
            
            # Calcular la ganancia por esta venta
            # Ganancia = (Precio Unitario de Venta - Costo Unitario al Momento de la Venta) * Cantidad Total de Unidades Vendidas
            profit_per_sale = (s.unit_price_at_sale - s.cost_price_at_sale) * s.quantity
            
            sales_data.append({
                "ID Venta": s.id,
                "Producto": product_name,
                "Cantidad": s.quantity,
                "Precio Unitario Venta": f"${s.unit_price_at_sale:,.2f}",
                "Costo Unitario Venta": f"${s.cost_price_at_sale:,.2f}", # Mostrar el costo unitario de la venta
                "Descuento": f"${s.discount:,.2f}",
                "Precio Total": f"${s.total_price:,.2f}",
                "Ganancia Venta": f"${profit_per_sale:,.2f}", # Nueva columna de ganancia por venta
                "Fecha Venta": s.sale_date.strftime("%Y-%m-%d %H:%M:%S") # Formatea la fecha
            })
        df_sales = pd.DataFrame(sales_data)
        st.dataframe(df_sales, use_container_width=True) # Muestra el DataFrame de ventas

        # Botón para descargar el historial de ventas a Excel
        st.download_button(
            label="Descargar Historial de Ventas a Excel",
            data=to_excel(df_sales),
            file_name="historial_ventas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.write("---")
        st.subheader("Eliminar Venta")
        # Selector para elegir la venta a eliminar
        sales_for_deletion = {f"ID: {s.id} - Producto: {get_product_by_id(s.product_id).name if get_product_by_id(s.product_id) else 'Desconocido'} - Fecha: {s.sale_date.strftime('%Y-%m-%d %H:%M')}" : s.id for s in all_sales}
        selected_sale_to_delete_label = st.selectbox("Seleccione una Venta a Eliminar", list(sales_for_deletion.keys()), key="delete_sale_select")
        selected_sale_to_delete_id = sales_for_deletion[selected_sale_to_delete_label] if selected_sale_to_delete_label else None

        # Confirmación y botón de eliminación de venta
        if selected_sale_to_delete_id:
            confirm_delete_sale = st.checkbox(f"Confirmar eliminación de Venta ID: {selected_sale_to_delete_id}", key="confirm_delete_sale")
            if st.button("Eliminar Venta Seleccionada", key="delete_sale_button"):
                if confirm_delete_sale:
                    success, message = delete_sale(selected_sale_to_delete_id)
                    if success:
                        st.success(message)
                        st.rerun() # Recargar para reflejar la eliminación
                    else:
                        st.error(message)
                else:
                    st.warning("Por favor, marque la casilla para confirmar la eliminación de la venta.")
    else:
        st.info("No hay ventas registradas.")

# --- Nueva Pestaña: Modificación Inventario ---
with tab4:
    st.header("Modificación de Inventario")
    
    products_to_modify = get_all_products()
    if products_to_modify:
        product_names_to_modify = {p.name: p.id for p in products_to_modify}
        selected_product_name_modify = st.selectbox("Seleccione un Producto para Modificar", list(product_names_to_modify.keys()), key="mod_product_select")

        selected_product_id_modify = product_names_to_modify[selected_product_name_modify] if selected_product_name_modify else None
        
        current_product_modify = get_product_by_id(selected_product_id_modify) if selected_product_id_modify else None

        if current_product_modify:
            st.subheader(f"Modificando: {current_product_modify.name}")

            # Mostrar nombre del producto y unidades por caja (inmutables)
            st.info(f"Nombre del Producto: **{current_product_modify.name}** (No modificable)")
            st.info(f"Unidades por Caja: **{current_product_modify.units_per_box}** (No modificable)")

            st.write("---")
            st.subheader("Modificar Precios")
            # Campos para modificar precios
            new_price_caja_fria = st.number_input("Nuevo Precio Caja Fria", value=current_product_modify.price_caja_fria, min_value=0.0, format="%.2f", key="mod_price_caja_fria")
            new_price_caja_caliente = st.number_input("Nuevo Precio Caja Caliente", value=current_product_modify.price_caja_caliente, min_value=0.0, format="%.2f", key="mod_price_caja_caliente")
            new_price_caja_particular = st.number_input("Nuevo Precio Caja Particular", value=current_product_modify.price_caja_particular, min_value=0.0, format="%.2f", key="mod_price_caja_particular")
            new_price_six_pack = st.number_input("Nuevo Precio Six-Pack", value=current_product_modify.price_six_pack, min_value=0.0, format="%.2f", key="mod_price_six_pack")
            new_price_unitario = st.number_input("Nuevo Precio Unitario", value=current_product_modify.price_unitario, min_value=0.0, format="%.2f", key="mod_price_unitario")
            
            # Nuevo campo para modificar: Valor Caja (Costo al Distribuidor)
            new_cost_price_box = st.number_input("Nuevo Valor Caja (Costo al Distribuidor)", value=current_product_modify.cost_price_box, min_value=0.0, format="%.2f", key="mod_cost_price_box")


            st.write("---")
            st.subheader("Modificar Stock")
            # Campos para modificar stock y stock mínimo
            new_stock = st.number_input("Nuevo Stock Actual", value=current_product_modify.stock, min_value=0, step=1, key="mod_stock")
            new_min_stock = st.number_input("Nuevo Stock Mínimo para Alerta", value=current_product_modify.min_stock, min_value=0, step=1, key="mod_min_stock")

            if st.button("Guardar Cambios en Inventario", key="save_mod_button"):
                new_prices = {
                    "price_caja_fria": new_price_caja_fria,
                    "price_caja_caliente": new_price_caja_caliente,
                    "price_caja_particular": new_price_caja_particular,
                    "price_six_pack": new_price_six_pack,
                    "price_unitario": new_price_unitario
                }
                success, message = update_product_details(
                    product_id=selected_product_id_modify,
                    new_prices=new_prices,
                    new_stock=new_stock,
                    new_min_stock=new_min_stock,
                    new_cost_price_box=new_cost_price_box # Pasar el nuevo valor de costo
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.info("Seleccione un producto para ver sus detalles y modificarlo.")
    else:
        st.info("No hay productos en el inventario para modificar. Agregue productos en la pestaña 'Inventario'.")

    st.write("---")
    st.subheader("Eliminar Producto")
    # Selector para elegir el producto a eliminar
    products_for_deletion = {f"ID: {p.id} - {p.name}" : p.id for p in get_all_products()}
    selected_product_to_delete_label = st.selectbox("Seleccione un Producto a Eliminar", list(products_for_deletion.keys()), key="delete_product_select")
    selected_product_to_delete_id = products_for_deletion[selected_product_to_delete_label] if selected_product_to_delete_label else None

    # Confirmación y botón de eliminación de producto
    if selected_product_to_delete_id:
        confirm_delete_product = st.checkbox(f"Confirmar eliminación de Producto: {selected_product_to_delete_label}", key="confirm_delete_product")
        if st.button("Eliminar Producto Seleccionado", key="delete_product_button"):
            if confirm_delete_product:
                success, message = delete_product(selected_product_to_delete_id)
                if success:
                    st.success(message)
                    st.rerun() # Recargar para reflejar la eliminación
                else:
                    st.error(message)
            else:
                st.warning("Por favor, marque la casilla para confirmar la eliminación del producto.")

    st.write("---")
    st.subheader("Historial de Modificaciones de Inventario")
    modifications = get_inventory_modifications()
    if modifications:
        mod_data = []
        for m in modifications:
            product = get_product_by_id(m.product_id)
            product_name = product.name if product else "Desconocido"
            mod_data.append({
                "ID Modificación": m.id,
                "Producto": product_name,
                "Campo Modificado": m.field_modified,
                "Valor Anterior": m.old_value,
                "Nuevo Valor": m.new_value,
                "Fecha Modificación": m.modification_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        df_modifications = pd.DataFrame(mod_data)
        st.dataframe(df_modifications, use_container_width=True)

        st.download_button(
            label="Descargar Historial de Modificaciones a Excel",
            data=to_excel(df_modifications),
            file_name="historial_modificaciones_inventario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay historial de modificaciones de inventario.")

