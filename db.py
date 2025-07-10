# db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Define la base declarativa para los modelos de SQLAlchemy
Base = declarative_base()

# Define el modelo de la tabla de Productos
class Product(Base):
    __tablename__ = 'products' # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True) # Clave primaria autoincremental
    name = Column(String, unique=True, nullable=False) # Nombre del producto, debe ser único y no nulo
    price_caja_fria = Column(Float, nullable=False) # Precio para "Caja Fria"
    price_caja_caliente = Column(Float, nullable=False) # Precio para "Caja Caliente"
    price_caja_particular = Column(Float, nullable=False) # Precio para "Caja Particular"
    price_six_pack = Column(Float, nullable=False) # Precio para "six-pack"
    price_unitario = Column(Float, nullable=False) # Precio para "Unitario"
    stock = Column(Integer, default=0) # Cantidad actual en stock, por defecto 0
    min_stock = Column(Integer, default=0) # Stock mínimo para activar alarma, por defecto 0
    units_per_box = Column(Integer, default=1) # Unidades por caja (para tipos de caja), por defecto 1
    cost_price_box = Column(Float, nullable=False, default=0.0) # Valor de compra de la caja al distribuidor

    # Relación con la tabla de ventas, indica que un producto puede tener muchas ventas
    sales = relationship("Sale", back_populates="product")
    # Relación con la tabla de modificaciones de inventario
    modifications = relationship("InventoryModification", back_populates="product")


    def __repr__(self):
        # Representación en cadena del objeto Producto
        return f"<Product(id={self.id}, name='{self.name}', stock={self.stock})>"

# Define el modelo de la tabla de Ventas
class Sale(Base):
    __tablename__ = 'sales' # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True) # Clave primaria autoincremental
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False) # Clave foránea al ID del producto
    quantity = Column(Integer, nullable=False) # Cantidad de unidades vendidas
    discount = Column(Integer, default=0) # Descuento aplicado (entero, no porcentaje), por defecto 0
    unit_price_at_sale = Column(Float, nullable=False) # Precio unitario al momento de la venta
    total_price = Column(Float, nullable=False) # Precio total de la venta
    sale_date = Column(DateTime, default=datetime.now) # Fecha y hora de la venta, por defecto la actual
    cost_price_at_sale = Column(Float, nullable=False, default=0.0) # Nuevo campo: Costo unitario al momento de la venta

    # Relación con la tabla de productos, indica que una venta pertenece a un producto
    product = relationship("Product", back_populates="sales")

    def __repr__(self):
        # Representación en cadena del objeto Venta
        return f"<Sale(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, total={self.total_price})>"

# Define el modelo de la tabla de Historial de Modificaciones de Inventario
class InventoryModification(Base):
    __tablename__ = 'inventory_modifications' # Nombre de la tabla

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    field_modified = Column(String, nullable=False) # Campo que fue modificado (ej. 'stock', 'price_caja_fria')
    old_value = Column(String, nullable=False) # Valor anterior del campo (almacenado como string)
    new_value = Column(String, nullable=False) # Nuevo valor del campo (almacenado como string)
    modification_date = Column(DateTime, default=datetime.now) # Fecha y hora de la modificación

    # Relación con la tabla de productos
    product = relationship("Product", back_populates="modifications")

    def __repr__(self):
        return f"<InventoryModification(id={self.id}, product_id={self.product_id}, field='{self.field_modified}', date={self.modification_date})>"


# Configura la conexión a la base de datos SQLite
# 'sqlite:///inventory.db' crea un archivo de base de datos llamado 'inventory.db' en el mismo directorio
engine = create_engine('sqlite:///inventory.db')

# Crea todas las tablas definidas en los modelos en la base de datos
# Si ya existe una base de datos, esto no la sobrescribirá, solo agregará la nueva columna si es necesario.
# Sin embargo, para que los cambios en la estructura de la tabla (como añadir una nueva columna)
# se apliquen a una base de datos existente, a menudo se necesita una herramienta de migración (como Alembic).
# Para este ejemplo, si ya tienes datos, es posible que necesites borrar inventory.db y volver a ejecutar
# para que la nueva columna 'cost_price_at_sale' se cree con el default.
Base.metadata.create_all(engine)

# Crea una clase de sesión para interactuar con la base de datos
Session = sessionmaker(bind=engine)

# Función para obtener una nueva sesión de base de datos
def get_db_session():
    return Session()
