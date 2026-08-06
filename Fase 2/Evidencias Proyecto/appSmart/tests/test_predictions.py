from inventory.services import predictions


def test_generar_predicciones_imports():
    # Basic import test to ensure module loads and function exists
    assert hasattr(predictions, "generar_predicciones")


def test_dummy_prediction_run(monkeypatch):
    # Avoid database access by monkeypatching Productos.objects.all
    class DummyQS:
        def all(self):
            return []

        def __iter__(self):
            return iter([])

    class DummyProductos:
        objects = DummyQS()

    monkeypatch.setattr(
        "inventory.services.predictions.Productos", DummyProductos, raising=False
    )

    payload = predictions.generar_predicciones()
    assert payload is not None
