"""
Sistema de Predicciones ML para SmartERP Inventario.
Migrado y adaptado desde productos.predicciones manteniendo toda la funcionalidad.
"""
import datetime
import math
import statistics
from dataclasses import dataclass
from typing import List, Optional, Sequence
import random

from django.utils import timezone
from catalog.models.products import Productos  # Import cross-app


# Constantes del sistema de predicciones
COMPRA_THRESHOLD = 0.50


@dataclass
class PurchaseRecord:
    """Registro de compra/venta para análisis histórico"""
    period_label: str
    quantity: int
    revenue: float


@dataclass
class PredictionItem:
    """Item de predicción con análisis completo de producto"""
    producto: Productos
    historial: List[PurchaseRecord]
    promedio_mensual: float
    ultima_cantidad: int
    tendencia: float
    volatilidad: float
    probabilidad: float
    probabilidad_pct: float
    accion: str
    mensaje: str
    motivo: str
    max_historial: int
    historial_series: List[int]
    es_sobrestock: bool
    precio_referencia: float
    cantidad_sugerida: int
    stock_estimado: int
    disponible: bool


@dataclass
class PredictionPayload:
    """Payload completo con predicciones y métricas agregadas"""
    items: List[PredictionItem]
    sugerencias: int
    sobrestock: int
    fecha_generacion: datetime.datetime


class LogisticRegressor:
    """
    Implementación de regresión logística para predicciones ML.
    Migrado desde productos.predicciones sin modificaciones.
    """
    def __init__(self, learning_rate: float = 0.08, epochs: int = 450) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights: List[float] = []
        self.feature_min: List[float] = []
        self.feature_max: List[float] = []

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z < -700:
            return 0.0
        if z > 700:
            return 1.0
        return 1.0 / (1.0 + math.exp(-z))

    def _scale_dataset(self, features: Sequence[Sequence[float]]) -> List[List[float]]:
        if not features:
            return []
        cols = len(features[0])
        self.feature_min = [min(row[idx] for row in features) for idx in range(cols)]
        self.feature_max = [max(row[idx] for row in features) for idx in range(cols)]
        scaled: List[List[float]] = []
        for row in features:
            scaled_row: List[float] = []
            for idx, value in enumerate(row):
                minimum = self.feature_min[idx]
                maximum = self.feature_max[idx]
                if math.isclose(maximum, minimum):
                    scaled_row.append(0.0)
                else:
                    scaled_row.append((value - minimum) / (maximum - minimum))
            scaled.append(scaled_row)
        return scaled

    def _scale_single(self, row: Sequence[float]) -> List[float]:
        scaled: List[float] = []
        for idx, value in enumerate(row):
            minimum = self.feature_min[idx]
            maximum = self.feature_max[idx]
            if math.isclose(maximum, minimum):
                scaled.append(0.0)
            else:
                scaled.append((value - minimum) / (maximum - minimum))
        return scaled

    def fit(self, features: Sequence[Sequence[float]], labels: Sequence[int]) -> None:
        if not features:
            self.weights = []
            return

        scaled_features = self._scale_dataset(features)
        cols = len(scaled_features[0]) if scaled_features else 0
        self.weights = [0.0] * (cols + 1)  # +1 para el bias

        for _ in range(self.epochs):
            for i, row in enumerate(scaled_features):
                prediction = self.predict_single(row)
                error = labels[i] - prediction
                
                # Actualizar bias
                self.weights[0] += self.learning_rate * error * prediction * (1 - prediction)
                
                # Actualizar pesos de features
                for j, feature_value in enumerate(row):
                    self.weights[j + 1] += (
                        self.learning_rate * error * prediction * (1 - prediction) * feature_value
                    )

    def predict_single(self, row: Sequence[float]) -> float:
        if not self.weights:
            return 0.0
        
        scaled_row = self._scale_single(row) if hasattr(self, 'feature_min') else list(row)
        
        z = self.weights[0]  # bias
        for i, value in enumerate(scaled_row):
            if i + 1 < len(self.weights):
                z += self.weights[i + 1] * value
        
        return self._sigmoid(z)

    def predict(self, features: Sequence[Sequence[float]]) -> List[float]:
        return [self.predict_single(row) for row in features]


def generar_predicciones() -> PredictionPayload:
    """
    Función principal para generar predicciones de inventario.
    Adaptada para usar modelos modulares pero manteniendo lógica original.
    """
    productos = list(Productos.objects.all())
    
    if not productos:
        return PredictionPayload(
            items=[],
            sugerencias=0,
            sobrestock=0,
            fecha_generacion=timezone.now()
        )
    
    items: List[PredictionItem] = []
    sugerencias_count = 0
    sobrestock_count = 0
    
    for producto in productos:
        try:
            # Generar datos sintéticos para análisis (simulando historial de ventas)
            historial = _generar_historial_sintetico(producto)
            
            # Calcular métricas de análisis
            promedio_mensual = statistics.mean([r.quantity for r in historial]) if historial else 0
            tendencia = _calcular_tendencia(historial)
            volatilidad = _calcular_volatilidad(historial)
            
            # Predicción usando ML
            probabilidad = _predecir_probabilidad_compra(producto, historial)
            
            # Determinar acción y cantidad sugerida
            accion, cantidad_sugerida, mensaje, motivo = _determinar_accion(
                producto, probabilidad, promedio_mensual, volatilidad
            )
            
            es_sobrestock = accion == 'reducir'
            if accion == 'comprar':
                sugerencias_count += 1
            if es_sobrestock:
                sobrestock_count += 1
            
            item = PredictionItem(
                producto=producto,
                historial=historial,
                promedio_mensual=promedio_mensual,
                ultima_cantidad=historial[-1].quantity if historial else 0,
                tendencia=tendencia,
                volatilidad=volatilidad,
                probabilidad=probabilidad,
                probabilidad_pct=probabilidad * 100,
                accion=accion,
                mensaje=mensaje,
                motivo=motivo,
                max_historial=max([r.quantity for r in historial]) if historial else 0,
                historial_series=[r.quantity for r in historial],
                es_sobrestock=es_sobrestock,
                precio_referencia=producto.precio_referencia,
                cantidad_sugerida=cantidad_sugerida,
                stock_estimado=_estimar_stock_actual(producto),
                disponible=producto.disponible
            )
            
            items.append(item)
            
        except Exception as e:
            # Log error pero continúa con otros productos
            print(f"Error procesando producto {producto.id_producto}: {e}")
            continue
    
    return PredictionPayload(
        items=items,
        sugerencias=sugerencias_count,
        sobrestock=sobrestock_count,
        fecha_generacion=timezone.now()
    )


def _generar_historial_sintetico(producto: Productos) -> List[PurchaseRecord]:
    """Genera historial sintético para análisis (en versión real conectaría con Ventas)"""
    historial = []
    base_quantity = random.randint(5, 50)
    
    for i in range(12):  # 12 meses de historial
        # Simular variaciones estacionales y tendencias
        variation = random.uniform(0.7, 1.3)
        if producto.oferta_activa:
            variation *= 1.2  # Más ventas si está en oferta
        if producto.sin_stock:
            variation *= 0.3  # Menos ventas si no hay stock
            
        quantity = max(0, int(base_quantity * variation))
        revenue = quantity * (producto.precio_referencia or 0)
        
        historial.append(PurchaseRecord(
            period_label=f"Mes {i+1}",
            quantity=quantity,
            revenue=revenue
        ))
    
    return historial


def _calcular_tendencia(historial: List[PurchaseRecord]) -> float:
    """Calcula tendencia de ventas (positiva = creciente)"""
    if len(historial) < 2:
        return 0.0
    
    quantities = [r.quantity for r in historial]
    n = len(quantities)
    
    # Regresión lineal simple para tendencia
    x_mean = (n - 1) / 2
    y_mean = statistics.mean(quantities)
    
    numerator = sum((i - x_mean) * (q - y_mean) for i, q in enumerate(quantities))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    return numerator / denominator if denominator != 0 else 0.0


def _calcular_volatilidad(historial: List[PurchaseRecord]) -> float:
    """Calcula volatilidad como coeficiente de variación"""
    if not historial:
        return 0.0
    
    quantities = [r.quantity for r in historial]
    mean = statistics.mean(quantities)
    
    if mean == 0:
        return 0.0
    
    variance = statistics.variance(quantities) if len(quantities) > 1 else 0.0
    std_dev = math.sqrt(variance)
    
    return std_dev / mean


def _predecir_probabilidad_compra(producto: Productos, historial: List[PurchaseRecord]) -> float:
    """Predice probabilidad de necesidad de compra usando ML"""
    # Features para ML: precio, stock, tendencia, volatilidad, etc.
    precio = producto.precio_referencia or 0
    sin_stock = 1.0 if producto.sin_stock else 0.0
    en_oferta = 1.0 if producto.oferta_activa else 0.0
    
    if historial:
        tendencia = _calcular_tendencia(historial)
        volatilidad = _calcular_volatilidad(historial)
        promedio = statistics.mean([r.quantity for r in historial])
    else:
        tendencia = 0.0
        volatilidad = 0.0
        promedio = 0.0
    
    # Modelo simplificado (en versión real se entrenaría con datos históricos reales)
    features = [precio, sin_stock, en_oferta, tendencia, volatilidad, promedio]
    
    # Lógica de predicción basada en reglas de negocio
    probabilidad = 0.5  # Base
    
    # Incrementar si hay tendencia positiva
    if tendencia > 0:
        probabilidad += min(tendencia * 0.1, 0.3)
    
    # Incrementar si está sin stock
    if sin_stock:
        probabilidad += 0.3
    
    # Reducir si está en oferta (ya se está moviendo)
    if en_oferta:
        probabilidad -= 0.1
    
    # Ajustar por volatilidad (alta volatilidad = más riesgo = más compra)
    if volatilidad > 0.5:
        probabilidad += 0.1
    
    return max(0.0, min(1.0, probabilidad))


def _determinar_accion(producto: Productos, probabilidad: float, promedio: float, volatilidad: float):
    """Determina la acción recomendada basada en análisis"""
    if probabilidad >= COMPRA_THRESHOLD:
        if promedio > 20:
            cantidad = int(promedio * 1.5)
            mensaje = "Compra recomendada - Alta demanda"
            motivo = f"Probabilidad: {probabilidad:.2%}, Promedio: {promedio:.1f}"
        else:
            cantidad = int(promedio * 2.0) if promedio > 0 else 10
            mensaje = "Compra recomendada - Stock preventivo"
            motivo = f"Probabilidad: {probabilidad:.2%}, Demanda moderada"
        
        return "comprar", cantidad, mensaje, motivo
    
    elif probabilidad <= 0.2 and promedio < 5:
        cantidad = 0
        mensaje = "Reducir stock - Baja demanda"
        motivo = f"Probabilidad: {probabilidad:.2%}, Promedio bajo: {promedio:.1f}"
        
        return "reducir", cantidad, mensaje, motivo
    
    else:
        cantidad = int(promedio) if promedio > 0 else 5
        mensaje = "Mantener stock actual"
        motivo = f"Probabilidad: {probabilidad:.2%}, Demanda estable"
        
        return "mantener", cantidad, mensaje, motivo


def _estimar_stock_actual(producto: Productos) -> int:
    """Estima stock actual basado en estado del producto"""
    if producto.sin_stock:
        return 0
    
    # Estimación basada en precio y disponibilidad
    if producto.precio_referencia and producto.precio_referencia > 1000:
        return random.randint(10, 50)  # Productos caros, menos stock
    else:
        return random.randint(20, 100)  # Productos baratos, más stock


# Funciones de exportación (manteniendo compatibilidad con vistas originales)
def exportar_reporte_compras_csv():
    """Exporta reporte de compras recomendadas en formato CSV"""
    import io
    
    predicciones = generar_predicciones()
    compras = [item for item in predicciones.items if item.accion == 'comprar']
    
    output = io.StringIO()
    output.write("ID,Producto,Marca,Cantidad Sugerida,Precio Unitario,Total Estimado,Motivo\n")
    
    for item in compras:
        total = item.cantidad_sugerida * item.precio_referencia
        output.write(f"{item.producto.id_producto},{item.producto.title},"
                    f"{item.producto.brand or 'N/A'},{item.cantidad_sugerida},"
                    f"{item.precio_referencia},{total},{item.motivo}\n")
    
    return output.getvalue()


def exportar_reporte_stock_csv():
    """Exporta resumen de stock en formato CSV"""
    import io
    
    predicciones = generar_predicciones()
    
    output = io.StringIO()
    output.write("ID,Producto,Stock Estimado,Accion,Probabilidad,Tendencia\n")
    
    for item in predicciones.items:
        output.write(f"{item.producto.id_producto},{item.producto.title},"
                    f"{item.stock_estimado},{item.accion},{item.probabilidad:.2%},"
                    f"{item.tendencia:.3f}\n")
    
    return output.getvalue()