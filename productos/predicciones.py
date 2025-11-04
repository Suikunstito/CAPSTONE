import datetime
import math
import statistics
from dataclasses import dataclass
from typing import List, Optional, Sequence
import random

from django.utils import timezone

from .models import Productos

COMPRA_THRESHOLD = 0.50

@dataclass
class PurchaseRecord:
    period_label: str
    quantity: int
    revenue: float


@dataclass
class PredictionItem:
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
    items: List[PredictionItem]
    sugerencias: int
    sobrestock: int
    fecha_generacion: datetime.datetime


class LogisticRegressor:
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
        scaled = self._scale_dataset(features)
        n_features = len(scaled[0])
        self.weights = [0.0] * (n_features + 1)
        samples = len(scaled)

        for _ in range(self.epochs):
            gradients = [0.0] * (n_features + 1)
            for row, label in zip(scaled, labels):
                z = self.weights[0]
                for weight, value in zip(self.weights[1:], row):
                    z += weight * value
                prediction = self._sigmoid(z)
                error = prediction - label
                gradients[0] += error
                for idx, value in enumerate(row, start=1):
                    gradients[idx] += error * value
            for idx in range(len(self.weights)):
                self.weights[idx] -= (self.learning_rate / samples) * gradients[idx]

    def predict_proba(self, row: Sequence[float]) -> float:
        if not self.weights:
            return 0.0
        scaled = self._scale_single(row)
        z = self.weights[0]
        for weight, value in zip(self.weights[1:], scaled):
            z += weight * value
        return self._sigmoid(z)


def _month_label_for(offset: int, base_date: datetime.date) -> str:
    target = base_date - datetime.timedelta(days=30 * offset)
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    return f"{months[target.month - 1]} {str(target.year)[-2:]}"


def _generate_purchase_history(producto: Productos, months: int = 6) -> List[PurchaseRecord]:
    rng = random.Random(producto.id_producto * 97 + 13)
    base_price = float(producto.normal_price) if producto.normal_price else 0.0
    base_demand = max(8.0, 240.0 - base_price * 0.8)
    if producto.oferta:
        base_demand *= 1.2
    if producto.sin_stock:
        base_demand *= 0.65
    if producto.brand:
        base_demand *= 1.05

    today = timezone.now().date().replace(day=1)
    history: List[PurchaseRecord] = []
    drift = rng.uniform(-0.12, 0.18)

    for idx in range(months - 1, -1, -1):
        seasonality = 1.0 + math.sin((months - idx) / 6.0 * math.pi) * 0.15
        noise = rng.uniform(0.85, 1.15)
        trend_multiplier = 1.0 + drift * ((months - idx) / months)
        quantity = max(0, int(base_demand * seasonality * noise * trend_multiplier))
        revenue = quantity * base_price if base_price else quantity * rng.uniform(4.0, 9.5)
        history.append(
            PurchaseRecord(
                period_label=_month_label_for(idx, today),
                quantity=quantity,
                revenue=float(f"{revenue:.2f}"),
            )
        )
    return history


def _derive_label(history: Sequence[PurchaseRecord], producto: Productos) -> int:
    quantities = [record.quantity for record in history]
    if not quantities:
        return 0
    avg = statistics.fmean(quantities)
    last = quantities[-1]
    first = quantities[0]
    max_value = max(quantities)
    in_shortage = producto.sin_stock or last == 0
    strong_trend = last > first * 1.25
    recovering = last > avg * 1.15
    low_rotation = avg < (max_value * 0.4 if max_value else 1)

    if in_shortage or strong_trend or recovering:
        return 1
    if low_rotation and not producto.oferta:
        return 0
    return 1 if last >= avg else 0


def _build_features(history: Sequence[PurchaseRecord], producto: Productos) -> List[float]:
    quantities = [record.quantity for record in history]
    if not quantities:
        quantities = [0]

    avg = statistics.fmean(quantities)
    std = statistics.pstdev(quantities) if len(quantities) > 1 else 0.0
    last = quantities[-1]
    first = quantities[0]
    trend = last - first
    recent_avg = statistics.fmean(quantities[-3:]) if len(quantities) >= 3 else avg
    momentum = last - recent_avg
    price = float(producto.normal_price) if producto.normal_price else 0.0
    ahorro = float(producto.ahorro) if producto.ahorro else 0.0
    ahorro_percent = float(producto.ahorro_percent) if producto.ahorro_percent else 0.0

    return [
        avg,
        std,
        last,
        trend,
        momentum,
        price,
        ahorro,
        ahorro_percent,
        1.0 if producto.oferta else 0.0,
        1.0 if producto.sin_stock else 0.0,
    ]


def _motivo_para_item(
    item: PredictionItem,
) -> str:
    if item.accion == "no_comprar" and item.es_sobrestock:
        return "Inventario por encima de la demanda reciente; conviene esperar antes de reponer."
    if item.ultima_cantidad == 0 and item.promedio_mensual > 0:
        return "Sin ventas el ultimo mes, se proyecta oportunidad de reposicion."
    if item.tendencia > 0 and item.probabilidad >= 0.55:
        return "Venta en aumento durante los ultimos meses."
    if item.volatilidad > (item.promedio_mensual * 0.5):
        return "Demanda volatil, se recomienda reposicion controlada."
    if item.accion == "no_comprar":
        return "Rotacion baja y niveles estables, se aconseja pausar compras."
    return "Demanda saludable mantenida los ultimos periodos."


def generar_predicciones(productos_queryset: Optional[Sequence[Productos]] = None) -> PredictionPayload:
    productos = list(productos_queryset) if productos_queryset is not None else list(Productos.objects.all())

    if not productos:
        return PredictionPayload(items=[], sugerencias=0, sobrestock=0, fecha_generacion=timezone.now())

    histories = {producto.id_producto: _generate_purchase_history(producto) for producto in productos}
    features = [_build_features(histories[producto.id_producto], producto) for producto in productos]
    labels = [_derive_label(histories[producto.id_producto], producto) for producto in productos]

    model = LogisticRegressor()
    model.fit(features, labels)

    items: List[PredictionItem] = []
    comprar_count = 0
    no_comprar_count = 0

    for producto in productos:
        history = histories[producto.id_producto]
        feature_row = _build_features(history, producto)
        prob = model.predict_proba(feature_row)

        quantities = [record.quantity for record in history]
        avg = statistics.fmean(quantities) if quantities else 0.0
        last = quantities[-1] if quantities else 0
        trend = last - (quantities[0] if quantities else 0)
        std = statistics.pstdev(quantities) if len(quantities) > 1 else 0.0
        overstock_flag = last < avg * 0.6 if avg else False
        max_historial = max(quantities) if quantities else 0

        precio_candidatos = [
            producto.normal_price,
            producto.low_price,
            producto.high_price,
        ]
        precio_referencia = 0.0
        for candidato in precio_candidatos:
            try:
                if candidato is not None and float(candidato) > 0:
                    precio_referencia = float(candidato)
                    break
            except (TypeError, ValueError):
                continue

        accion = "comprar" if prob >= COMPRA_THRESHOLD else "no_comprar"
        if accion == "comprar":
            comprar_count += 1
            mensaje = "SUGERENCIA DE COMPRAS DE PRODUCTOS"
        else:
            mensaje = "NO COMPRAR POR SOBRESTOCK"
            no_comprar_count += 1

        disponible = not bool(producto.sin_stock)
        stock_estimado = 0
        if disponible:
            stock_estimado = max(int(round(avg)) if avg > 0 else last, 0)

        proyeccion_demanda = max(avg * 1.1, avg + std, last)
        cantidad_sugerida = int(round(max(proyeccion_demanda - last, 0)))
        if accion == "comprar" and cantidad_sugerida <= 0:
            cantidad_sugerida = max(int(round(avg)) or 1, 1)

        item = PredictionItem(
            producto=producto,
            historial=history,
            promedio_mensual=float(f"{avg:.2f}"),
            ultima_cantidad=last,
            tendencia=float(f"{trend:.2f}"),
            volatilidad=float(f"{std:.2f}"),
            probabilidad=float(f"{prob:.4f}"),
            probabilidad_pct=float(f"{(prob * 100):.2f}"),
            accion=accion,
            mensaje=mensaje,
            motivo="",
            max_historial=max_historial,
            historial_series=quantities,
            es_sobrestock=overstock_flag,
            precio_referencia=float(f"{precio_referencia:.2f}") if precio_referencia else 0.0,
            cantidad_sugerida=cantidad_sugerida,
            stock_estimado=stock_estimado,
            disponible=disponible,
        )
        item.motivo = _motivo_para_item(item)
        items.append(item)

    items.sort(key=lambda entry: entry.probabilidad, reverse=True)

    return PredictionPayload(
        items=items,
        sugerencias=comprar_count,
        sobrestock=no_comprar_count,
        fecha_generacion=timezone.now(),
    )


def exportar_reporte_compras_csv(predicciones: PredictionPayload) -> List[List[str]]:
    header = [
        "id_producto",
        "titulo",
        "marca",
        "estado_stock",
        "promedio_mensual",
        "venta_ultimo_mes",
        "cantidad_sugerida",
        "probabilidad_compra_pct",
        "precio_referencia",
        "motivo",
    ]
    filas = [header]
    for item in predicciones.items:
        if item.accion != "comprar":
            continue
        filas.append(
            [
                str(item.producto.id_producto),
                item.producto.title,
                item.producto.brand or "-",
                "Disponible" if item.disponible else "Sin stock",
                f"{item.promedio_mensual:.2f}",
                str(item.ultima_cantidad),
                str(item.cantidad_sugerida),
                f"{item.probabilidad_pct:.2f}",
                f"{item.precio_referencia:.2f}" if item.precio_referencia else "-",
                item.motivo,
            ]
        )
    if len(filas) == 1:
        filas.append(["-", "Sin sugerencias de compra registradas en esta corrida.", "", "", "", "", "", "", "", ""])
    return filas


def exportar_reporte_stock_csv(predicciones: PredictionPayload) -> List[List[str]]:
    header = [
        "id_producto",
        "titulo",
        "marca",
        "estado_stock",
        "stock_estimado",
        "promedio_mensual",
        "venta_ultimo_mes",
        "probabilidad_no_comprar_pct",
        "precio_referencia",
    ]
    filas = [header]
    for item in predicciones.items:
        filas.append(
            [
                str(item.producto.id_producto),
                item.producto.title,
                item.producto.brand or "-",
                "Disponible" if item.disponible else "Sin stock",
                str(item.stock_estimado),
                f"{item.promedio_mensual:.2f}",
                str(item.ultima_cantidad),
                f"{100 - item.probabilidad_pct:.2f}",
                f"{item.precio_referencia:.2f}" if item.precio_referencia else "-",
            ]
        )
    return filas
