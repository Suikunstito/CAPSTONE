"""
Script de inicialización - Crear tablas y datos de prueba en SQLite
Para uso en desarrollo local cuando no hay SQL Server disponible
"""
import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventario_web.settings")
django.setup()

from django.db import connection

from catalog.models.products import Productos
from sales.models.sales import Ventas


def crear_tablas_sqlite():
    """Crear tablas manualmente en SQLite para desarrollo"""
    print("📦 Creando tablas en SQLite local...")

    with connection.cursor() as cursor:
        # Tabla Productos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                brand TEXT,
                normal_price REAL,
                low_price REAL,
                high_price REAL,
                oferta BOOLEAN DEFAULT 0,
                categoria1 TEXT,
                categoria2 TEXT,
                sin_stock BOOLEAN DEFAULT 0,
                ahorro REAL,
                ahorro_percent INTEGER,
                kilo REAL,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page TEXT,
                total_venta REAL,
                Atributos TEXT
            )
        """
        )
        print("  ✅ Tabla Productos creada")

        # Tabla Ventas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER,
                cantidad_vendida INTEGER,
                precio_unitario REAL,
                total_venta REAL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
            )
        """
        )
        print("  ✅ Tabla Ventas creada")

        # Tabla StgProductosRaw (staging)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS StgProductosRaw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                brand TEXT,
                normal_price REAL,
                categoria1 TEXT,
                sin_stock BOOLEAN DEFAULT 0,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        print("  ✅ Tabla StgProductosRaw creada")


def insertar_datos_prueba():
    """Insertar productos de ejemplo para pruebas"""
    print("\n🎲 Insertando datos de prueba...")

    productos_ejemplo = [
        {
            "title": 'Laptop HP Pavilion 15.6"',
            "brand": "HP",
            "normal_price": 599990,
            "low_price": 499990,
            "high_price": 699990,
            "oferta": True,
            "categoria1": "Computación",
            "categoria2": "Notebooks",
            "sin_stock": False,
            "ahorro": 100000,
            "ahorro_percent": 17,
            "kilo": 2.1,
        },
        {
            "title": "Mouse Logitech MX Master 3",
            "brand": "Logitech",
            "normal_price": 89990,
            "low_price": None,
            "high_price": 99990,
            "oferta": False,
            "categoria1": "Computación",
            "categoria2": "Accesorios",
            "sin_stock": False,
            "kilo": 0.14,
        },
        {
            "title": "Teclado Mecánico Razer BlackWidow",
            "brand": "Razer",
            "normal_price": 129990,
            "low_price": 99990,
            "high_price": 149990,
            "oferta": True,
            "categoria1": "Computación",
            "categoria2": "Gaming",
            "sin_stock": False,
            "ahorro": 30000,
            "ahorro_percent": 23,
            "kilo": 1.3,
        },
        {
            "title": 'Monitor LG UltraWide 29"',
            "brand": "LG",
            "normal_price": 299990,
            "low_price": None,
            "high_price": 349990,
            "oferta": False,
            "categoria1": "Computación",
            "categoria2": "Monitores",
            "sin_stock": True,
            "kilo": 5.8,
        },
        {
            "title": "Audífonos Sony WH-1000XM5",
            "brand": "Sony",
            "normal_price": 349990,
            "low_price": 299990,
            "high_price": 399990,
            "oferta": True,
            "categoria1": "Audio",
            "categoria2": "Audífonos",
            "sin_stock": False,
            "ahorro": 50000,
            "ahorro_percent": 14,
            "kilo": 0.25,
        },
        {
            "title": "Webcam Logitech C920",
            "brand": "Logitech",
            "normal_price": 79990,
            "low_price": None,
            "high_price": 89990,
            "oferta": False,
            "categoria1": "Computación",
            "categoria2": "Accesorios",
            "sin_stock": False,
            "kilo": 0.16,
        },
        {
            "title": "SSD Samsung 970 EVO 1TB",
            "brand": "Samsung",
            "normal_price": 149990,
            "low_price": 119990,
            "high_price": 179990,
            "oferta": True,
            "categoria1": "Computación",
            "categoria2": "Almacenamiento",
            "sin_stock": False,
            "ahorro": 30000,
            "ahorro_percent": 20,
            "kilo": 0.05,
        },
        {
            "title": "Router ASUS RT-AX88U",
            "brand": "ASUS",
            "normal_price": 249990,
            "low_price": None,
            "high_price": 279990,
            "oferta": False,
            "categoria1": "Redes",
            "categoria2": "Routers",
            "sin_stock": True,
            "kilo": 1.0,
        },
        {
            "title": "Tablet Samsung Galaxy Tab S9",
            "brand": "Samsung",
            "normal_price": 799990,
            "low_price": 699990,
            "high_price": 899990,
            "oferta": True,
            "categoria1": "Tablets",
            "categoria2": "Android",
            "sin_stock": False,
            "ahorro": 100000,
            "ahorro_percent": 13,
            "kilo": 0.57,
        },
        {
            "title": "Impresora HP LaserJet Pro",
            "brand": "HP",
            "normal_price": 199990,
            "low_price": None,
            "high_price": 229990,
            "oferta": False,
            "categoria1": "Oficina",
            "categoria2": "Impresoras",
            "sin_stock": False,
            "kilo": 7.5,
        },
    ]

    for producto in productos_ejemplo:
        Productos.objects.create(**producto)
        print(f"  ✅ Producto creado: {producto['title']}")

    print(f"\n✅ {len(productos_ejemplo)} productos insertados correctamente")


def main():
    print("=" * 60)
    print("SmartERP - Inicialización Base de Datos SQLite")
    print("=" * 60)
    print()

    try:
        # Verificar si ya existen datos
        count = Productos.objects.count()
        if count > 0:
            respuesta = input(
                f"⚠️  Ya existen {count} productos. ¿Eliminar y recrear? (s/N): "
            )
            if respuesta.lower() == "s":
                print("\n🗑️  Eliminando datos existentes...")
                Productos.objects.all().delete()
                print("  ✅ Datos eliminados")
            else:
                print("\n❌ Operación cancelada")
                return
    except:
        # Primera vez, las tablas no existen
        pass

    # Crear tablas
    crear_tablas_sqlite()

    # Insertar datos de prueba
    insertar_datos_prueba()

    print("\n" + "=" * 60)
    print("✅ Inicialización completada exitosamente")
    print("=" * 60)
    print("\n💡 Ahora puedes:")
    print("  1. Iniciar el servidor: python manage.py runserver")
    print("  2. Acceder a: http://localhost:8000")
    print("  3. Login con el superusuario creado")
    print()


if __name__ == "__main__":
    main()
