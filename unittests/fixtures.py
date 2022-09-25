import pytest


@pytest.fixture
def env(monkeypatch):
    variables = {"MQTT_HOST": "localhost"}
    for var_name, value in variables.items():
        monkeypatch.setenv(var_name, value)
