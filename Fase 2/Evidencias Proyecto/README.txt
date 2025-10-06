
-- Crear Base de Datos PostgreSQL
CREATE TABLE IF NOT EXISTS public.productos_supermercado
(
    product_id integer NOT NULL DEFAULT nextval('productos_supermercado_product_id_seq'::regclass),
    product_name text COLLATE pg_catalog."default" NOT NULL,
    product_brand text COLLATE pg_catalog."default",
    product_description text COLLATE pg_catalog."default",
    product_price numeric(10,2),
    product_discount numeric(5,2) DEFAULT 0,
    product_category1 text COLLATE pg_catalog."default",
    product_category2 text COLLATE pg_catalog."default",
    product_stock integer,
    product_unit text COLLATE pg_catalog."default" DEFAULT 'unidad'::text,
    product_provider text COLLATE pg_catalog."default",
    product_status text COLLATE pg_catalog."default" DEFAULT 'activo'::text,
    product_creation_date timestamp with time zone DEFAULT now(),
    product_last_update timestamp with time zone DEFAULT now(),
    CONSTRAINT productos_supermercado_pkey PRIMARY KEY (product_id)
)