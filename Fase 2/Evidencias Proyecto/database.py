import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import chardet
import os
import psycopg2

# Configuración de base de datos
DB_USER = "postgres"
DB_PASS = "Admin123*"
DB_HOST = "localhost"
DB_PORT = "5050"
DB_NAME = "postgres"

# Nombre de la tabla
TABLE_NAME = "productos_supermercado"

# SQL para crear la tabla si no existe
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS public.{TABLE_NAME} (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_brand TEXT,
    product_description TEXT,
    product_price NUMERIC(10,2),
    product_discount NUMERIC(5,2) DEFAULT 0,
    product_category1 TEXT,
    product_category2 TEXT,
    product_stock INTEGER,
    product_unit TEXT DEFAULT 'unidad',
    product_provider TEXT,
    product_status TEXT DEFAULT 'activo',
    product_creation_date TIMESTAMP DEFAULT NOW(),
    product_last_update TIMESTAMP DEFAULT NOW()
);
"""
# Detecta la codificación del archivo (UTF-8, ANSI, etc.).
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(50000))
    print(f"Codificación detectada: {result['encoding']}")
    return result['encoding']

# Normaliza nombres de columnas a formato compatible.
def normalize_columns(df):
    
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    return df

# Crea la tabla en PostgreSQL si no existe.
def create_table_if_not_exists():
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        print(f"Tabla '{TABLE_NAME}' creada o ya existía.")
    engine.dispose()

# Carga CSV a PostgreSQL usando pandas y SQLAlchemy.
def load_csv_to_postgres(file_path):
    # Detectar codificación
    encoding = detect_encoding(file_path)

    # Leer CSV
    df = pd.read_csv(file_path, sep=",", encoding=encoding, engine="python", on_bad_lines="skip", skip_blank_lines=True)
    df = normalize_columns(df)

    # Columnas esperadas según tabla
    expected_columns = [
        "product_name", "product_brand", "product_description", "product_price",
        "product_discount", "product_category1", "product_category2",
        "product_stock", "product_unit", "product_provider", "product_status",
        "product_creation_date", "product_last_update"
    ]

    # Agregar columnas faltantes
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]

    # Convertir columnas numéricas
    numeric_cols = ["product_price", "product_discount", "product_stock"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Guardar temporal en CSV limpio
    temp_csv = "temp_clean.csv"
    df.to_csv(temp_csv, index=False, header=False)

    # Conectar con psycopg2 y usar COPY FROM
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    with open(temp_csv, 'r', encoding=encoding) as f:
        cur.copy_from(f, TABLE_NAME, sep=',', null='', columns=expected_columns)

    conn.commit()
    cur.close()
    conn.close()
    os.remove(temp_csv)
    print(f"{len(df)} filas insertadas correctamente en '{TABLE_NAME}' usando COPY FROM.")

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    # Crear tabla si no existe
    create_table_if_not_exists()

    root = tk.Tk()
    root.withdraw()
    url = filedialog.askopenfilename(title="Selecciona el archivo CSV", filetypes=[("CSV files", "*.csv")])

    if url:
        load_csv_to_postgres(url)
    else:
        print("No se seleccionó ningún archivo.")
