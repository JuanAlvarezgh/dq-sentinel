import pytest

airflow = pytest.importorskip("airflow")
from airflow.models import DagBag  # noqa: E402


def test_dag_carga_sin_errores():
    bag = DagBag(dag_folder="dags", include_examples=False)
    assert bag.import_errors == {}
    assert "centinela_calidad" in bag.dags
