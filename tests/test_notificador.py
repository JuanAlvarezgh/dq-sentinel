import json

import httpx
import respx

from centinela import notificador
from centinela.modelos import FALLIDA, ResultadoValidacion

FALLIDO = ResultadoValidacion(
    "hechos_valor_indicador", "no_nulo", "valor", FALLIDA, 10, 2, "2 nulos"
)


@respx.mock
def test_envia_a_slack():
    ruta = respx.post("https://hooks.slack.test/abc").mock(return_value=httpx.Response(200))
    enviado = notificador.enviar_alerta([FALLIDO], webhook_url="https://hooks.slack.test/abc")
    assert enviado is True
    assert ruta.called


@respx.mock
def test_payload_contiene_mensaje():
    ruta = respx.post("https://hooks.slack.test/abc").mock(return_value=httpx.Response(200))
    notificador.enviar_alerta([FALLIDO], webhook_url="https://hooks.slack.test/abc")
    cuerpo = json.loads(ruta.calls.last.request.content)
    assert "hechos_valor_indicador" in cuerpo["text"]
    assert "2 nulos" in cuerpo["text"]
    assert "no_nulo" in cuerpo["text"]


def test_sin_webhook_va_a_consola(monkeypatch, capsys):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    enviado = notificador.enviar_alerta([FALLIDO], webhook_url=None)
    assert enviado is False
    assert "no_nulo" in capsys.readouterr().out
