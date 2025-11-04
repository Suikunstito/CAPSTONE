"""
Módulo de exportación para servicios del dominio Inventory
"""
from .stock import get_stock_stats, get_low_stock_products, calculate_inventory_value

__all__ = ['get_stock_stats', 'get_low_stock_products', 'calculate_inventory_value']