Explicación del Programa de Gestión de Inventario y Ventas

Este programa es una aplicación de escritorio sencilla diseñada para ayudar a pequeños negocios a gestionar su inventario y registrar ventas. Está construido utilizando Python y varias librerías clave que facilitan la interacción con bases de datos y la creación de interfaces gráficas web.
Componentes del Programa:

El programa está estructurado en varios archivos Python, cada uno con una responsabilidad específica:

    db.py:

        Propósito: Define la estructura de la base de datos y cómo interactuar con ella.

        Contenido: Contiene los modelos de datos para Product (Producto) y Sale (Venta) utilizando SQLAlchemy. Establece la conexión a una base de datos SQLite llamada inventory.db.

        Funcionalidad: Crea las tablas necesarias en la base de datos si no existen y proporciona una función para obtener sesiones de base de datos.

    main.py:

        Propósito: Contiene la lógica de negocio principal de la aplicación.

        Contenido: Define funciones para realizar operaciones clave como:

            add_product(): Agregar nuevos productos al inventario.

            get_all_products(): Obtener todos los productos registrados.

            get_product_by_id(): Buscar un producto específico por su ID.

            record_sale(): Registrar una nueva venta, actualizando el stock del producto.

            get_all_sales(): Obtener el historial completo de ventas.

            update_product_stock(): Actualizar manualmente el stock de un producto.

            get_current_inventory(): Obtener el estado actual del inventario.

        Funcionalidad: Estas funciones interactúan con la base de datos a través de db.py para asegurar la persistencia de los datos.

    ui.py:

        Propósito: Construye la interfaz gráfica de usuario (GUI) de la aplicación.

        Contenido: Utiliza el framework Streamlit para crear una aplicación web interactiva con tres pestañas principales:

            Inventario: Permite agregar nuevos productos con diferentes tipos de precios (Caja Fría, Caja Caliente, Caja Particular, Six-Pack, Unitario), stock actual, stock mínimo y unidades por caja. Muestra una tabla de todos los productos y permite descargarla en Excel.

            Ventas: Permite seleccionar un producto, el tipo de precio, la cantidad y un descuento. Calcula el precio unitario y el total de la compra, y registra la venta, actualizando el stock.

            Reportes y Stock Actual: Muestra el inventario actual con alertas visuales si el stock está por debajo del mínimo. También presenta el historial de todas las ventas. Ambas tablas se pueden descargar en formato Excel.

        Funcionalidad: Proporciona una experiencia de usuario intuitiva para interactuar con la lógica de negocio definida en main.py.

    run_app.py:

        Propósito: Es el script principal para iniciar la aplicación Streamlit.

        Contenido: Contiene una función run_streamlit_app() que utiliza subprocess para ejecutar el archivo ui.py con el comando streamlit run.

        Funcionalidad: Simplifica el proceso de lanzamiento de la aplicación, haciéndola compatible para ser ejecutada directamente o empaquetada.

Dependencias y Requerimientos:

Para que la aplicación funcione correctamente, necesitas tener instaladas las siguientes dependencias de Python:

    Python 3.x: El lenguaje de programación principal.

    SQLAlchemy: Un kit de herramientas SQL y mapeador objeto-relacional (ORM) que permite interactuar con bases de datos de manera orientada a objetos.

        Instalación: pip install sqlalchemy

    Streamlit: Un framework de código abierto para crear aplicaciones web interactivas de ciencia de datos y aprendizaje automático.

        Instalación: pip install streamlit

    Pandas: Una librería para manipulación y análisis de datos, utilizada para crear DataFrames y facilitar la exportación a Excel.

        Instalación: pip install pandas

    Openpyxl: Una librería necesaria para que Pandas pueda escribir y leer archivos .xlsx (Excel).

        Instalación: pip install openpyxl

Cómo Ejecutar la Aplicación:

    Instala Python: Si no lo tienes, descárgalo e instálalo desde python.org.

    Instala las dependencias: Abre tu terminal o línea de comandos y ejecuta el siguiente comando:

    pip install sqlalchemy streamlit pandas openpyxl

    Guarda los archivos: Asegúrate de que db.py, main.py, ui.py y run_app.py estén todos en el mismo directorio.

    Ejecuta la aplicación: Desde la terminal, navega al directorio donde guardaste los archivos y ejecuta:

    python run_app.py

    Esto iniciará la aplicación y la abrirá automáticamente en tu navegador web predeterminado.

Notas Adicionales:

    Base de Datos: La aplicación creará un archivo inventory.db en el mismo directorio donde se ejecute run_app.py. Este archivo contendrá toda la información de productos y ventas.

    PyInstaller (Opcional): Si deseas crear un ejecutable de Windows para la aplicación, puedes usar PyInstaller. Sin embargo, su configuración puede ser más compleja y no está incluida en este paquete inicial.

        Instalación (si la necesitas): pip install pyinstaller

        Uso (ejemplo básico): pyinstaller --onefile run_app.py (esto creará un solo ejecutable, pero puede requerir ajustes adicionales para Streamlit).