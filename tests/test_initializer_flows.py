"""Cobertura adicional para el inicializador de credenciales."""

import builtins
import httpx

from kezan import initializer


def test_check_credentials_validity(monkeypatch):
    """Valida el flujo con variables presentes y ausentes."""
    monkeypatch.setenv("BLIZZ_CLIENT_ID", "id")
    monkeypatch.setenv("BLIZZ_CLIENT_SECRET", "sec")
    monkeypatch.setenv("REGION", "eu")

    monkeypatch.setattr(initializer, "_try_request_token", lambda *a: (True, ""))
    assert initializer.check_credentials_validity()

    monkeypatch.delenv("BLIZZ_CLIENT_ID", raising=False)
    monkeypatch.delenv("BLIZZ_CLIENT_SECRET", raising=False)
    assert not initializer.check_credentials_validity()


def test_try_request_token_variants(monkeypatch):
    """Cubre rutas de éxito y error de _try_request_token."""

    class Resp:
        def raise_for_status(self):
            pass

    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp())
    ok, err = initializer._try_request_token("id", "sec", "eu")
    assert ok and not err

    def boom(*a, **k):
        raise httpx.RequestError("fail", request=httpx.Request("POST", "u"))

    monkeypatch.setattr(httpx, "post", boom)
    ok, err = initializer._try_request_token("id", "sec", "eu")
    assert not ok and "Network error" in err


def test_prompt_for_credentials_console(monkeypatch, tmp_path):
    """Simula entrada por consola y guarda el archivo .env."""
    entradas = iter(["id", "sec", "eu", "1080"])
    monkeypatch.setattr(builtins, "input", lambda *_: next(entradas))
    monkeypatch.setattr(initializer, "_try_request_token", lambda *a: (True, ""))
    monkeypatch.setattr(initializer, "ENV_PATH", tmp_path / ".env")

    assert initializer.prompt_for_credentials_console()
    contenido = (tmp_path / ".env").read_text()
    assert "BLIZZ_CLIENT_ID=id" in contenido


def test_prompt_for_credentials_console_error(monkeypatch):
    """Regresa False cuando la verificación falla."""
    entradas = iter(["id", "sec", "eu", "1080"])
    monkeypatch.setattr(builtins, "input", lambda *_: next(entradas))
    monkeypatch.setattr(initializer, "_try_request_token", lambda *a: (False, "fallo"))
    assert not initializer.prompt_for_credentials_console()


def test_ensure_credentials(monkeypatch):
    """Cubre el flujo con y sin GUI."""
    monkeypatch.setattr(initializer, "check_credentials_validity", lambda: False)
    monkeypatch.setattr(initializer, "prompt_for_credentials_console", lambda: True)
    assert initializer.ensure_credentials(False)

    monkeypatch.setattr(initializer, "prompt_for_credentials_gui", lambda: True)
    assert initializer.ensure_credentials(True)


def test_prompt_for_credentials_gui(monkeypatch, tmp_path):
    """Simula el flujo GUI completo."""

    class DummyTk:
        class Tk:
            def withdraw(self):
                pass

    class DummyDialog:
        vals = iter(["id", "sec", "eu", "1080"])

        @staticmethod
        def askstring(*args, **kwargs):
            return next(DummyDialog.vals)

    monkeypatch.setattr(initializer, "tk", DummyTk)
    monkeypatch.setattr(initializer, "simpledialog", DummyDialog)
    monkeypatch.setattr(initializer, "_try_request_token", lambda *a: (True, ""))
    monkeypatch.setattr(initializer, "ENV_PATH", tmp_path / ".env")
    assert initializer.prompt_for_credentials_gui()


def test_prompt_for_credentials_gui_fallback(monkeypatch):
    """Cuando Tk no está disponible, usa consola."""
    monkeypatch.setattr(initializer, "tk", None)
    monkeypatch.setattr(initializer, "simpledialog", None)
    monkeypatch.setattr(initializer, "prompt_for_credentials_console", lambda: True)
    assert initializer.prompt_for_credentials_gui()


def test_prompt_gui_cancel_client_id(monkeypatch):
    """Retorna False si se cancela en el primer diálogo."""

    class DummyTk:
        class Tk:
            def withdraw(self):
                pass

    class DummyDialog:
        @staticmethod
        def askstring(*args, **kwargs):
            return None

    monkeypatch.setattr(initializer, "tk", DummyTk)
    monkeypatch.setattr(initializer, "simpledialog", DummyDialog)
    assert not initializer.prompt_for_credentials_gui()


def test_prompt_gui_cancel_client_secret(monkeypatch):
    """Retorna False si se cancela la contraseña."""

    class DummyTk:
        class Tk:
            def withdraw(self):
                pass

    respuestas = iter(["id", None])

    class DummyDialog:
        @staticmethod
        def askstring(*args, **kwargs):
            return next(respuestas)

    monkeypatch.setattr(initializer, "tk", DummyTk)
    monkeypatch.setattr(initializer, "simpledialog", DummyDialog)
    assert not initializer.prompt_for_credentials_gui()


def test_prompt_gui_network_error(monkeypatch):
    """Regresa False si falla la verificación de red."""

    class DummyTk:
        class Tk:
            def withdraw(self):
                pass

    respuestas = iter(["id", "sec", "eu", "1080"])

    class DummyDialog:
        @staticmethod
        def askstring(*args, **kwargs):
            return next(respuestas)

    monkeypatch.setattr(initializer, "tk", DummyTk)
    monkeypatch.setattr(initializer, "simpledialog", DummyDialog)
    monkeypatch.setattr(
        initializer, "_try_request_token", lambda *a: (False, "Network error")
    )
    assert not initializer.prompt_for_credentials_gui()


def test_ensure_credentials_valid(monkeypatch):
    """Si las credenciales son válidas no se solicita nada."""
    monkeypatch.setattr(initializer, "check_credentials_validity", lambda: True)
    assert initializer.ensure_credentials()
