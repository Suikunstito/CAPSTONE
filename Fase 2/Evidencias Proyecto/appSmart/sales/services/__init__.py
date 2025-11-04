"""
Módulo de exportación para servicios del dominio Sales
"""
from .orders import register_sale, get_sales_summary, get_top_selling_products

__all__ = ['register_sale', 'get_sales_summary', 'get_top_selling_products']