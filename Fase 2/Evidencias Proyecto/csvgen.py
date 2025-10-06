# generar_csv_productos.py
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Cantidad de productos de prueba
N_PRODUCTOS = 4423

# Posibles valores para categorías, unidades y estados
categorias1 = ["Electrónica", "Alimentos", "Bebidas", "Ropa", "Hogar"]
categorias2 = ["Gadgets", "Snacks", "Lácteos", "Calzado", "Decoración"]
unidades = ["unidad", "kg", "litro", "caja"]
estados = ["activo", "inactivo", "descontinuado"]

productos = []

for i in range(N_PRODUCTOS):
    creation_date = fake.date_time_between(start_date='-1y', end_date='now')
    last_update = creation_date + timedelta(days=random.randint(0, 365))
    
    producto = {
        "product_id": i + 1,
        "product_name": fake.word().capitalize(),
        "product_brand": fake.company(),
        "product_description": fake.sentence(nb_words=10),
        "product_price": round(random.uniform(5, 500), 2),
        "product_discount": round(random.uniform(0, 50), 2),
        "product_category1": random.choice(categorias1),
        "product_category2": random.choice(categorias2),
        "product_stock": random.randint(0, 200),
        "product_unit": random.choice(unidades),
        "product_provider": fake.company(),
        "product_status": random.choice(estados),
        "product_creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "product_last_update": last_update.strftime("%Y-%m-%d %H:%M:%S")
    }
    productos.append(producto)

# Crear DataFrame y exportar a CSV
df = pd.DataFrame(productos)
df.to_csv("productos_prueba.csv", index=False)

print("CSV de prueba 'productos_prueba.csv' generado correctamente.")
