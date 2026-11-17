
"""Tests unitaires du module aoc_core.

Exécution :
    python -m pytest tests/ -v

Les tests réseau utilisent des mocks et ne contactent aucun serveur.
"""

from __future__ import annotations

import io
import urllib.error
import urllib.request
from unittest.mock import MagicMock

import pytest

import aoc_core as core


# ============================================================================
# HTTP — Tests de la fonction http_get
# ============================================================================


def test_http_get_returns_decoded_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie le décodage UTF-8 de la réponse HTTP."""

    response = io.BytesIO("Advent of Code".encode("utf-8"))

    opener = MagicMock()
    opener.open.return_value.__enter__.return_value = response

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    result = core.http_get("https://adventofcode.com/2026")

    assert result == "Advent of Code"
    opener.open.assert_called_once()


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/file",
        "javascript:alert(1)",
        "custom://example.com/resource",
        "https:///missing-host",
    ],
)
def test_http_get_rejects_unsupported_urls(
    url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie le rejet des protocoles et URL non autorisés."""

    build_opener = MagicMock()

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        build_opener,
    )

    with pytest.raises(core.AocError):
        core.http_get(url)

    build_opener.assert_not_called()


def test_http_get_uses_http_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie que seuls les gestionnaires HTTP et HTTPS sont configurés."""

    opener = MagicMock()
    opener.open.return_value.__enter__.return_value = io.BytesIO(b"OK")

    http_handler = object()
    https_handler = object()
    handlers = []

    monkeypatch.setattr(
        urllib.request,
        "HTTPHandler",
        lambda: http_handler,
    )
    monkeypatch.setattr(
        urllib.request,
        "HTTPSHandler",
        lambda: https_handler,
    )

    def fake_build_opener(*args):
        handlers.extend(args)
        return opener

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        fake_build_opener,
    )

    result = core.http_get("https://adventofcode.com/2026")

    assert result == "OK"
    assert handlers == [http_handler, https_handler]
    opener.open.assert_called_once()


def test_http_get_uses_session_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie l'ajout du cookie de session Advent of Code."""

    opener = MagicMock()
    opener.open.return_value.__enter__.return_value = io.BytesIO(b"OK")

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    core.http_get(
        "https://adventofcode.com/2026",
        session="test-session",
    )

    request = opener.open.call_args.args[0]

    assert request.get_header("Cookie") == "session=test-session"


def test_http_get_without_session_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie qu'aucun cookie n'est ajouté sans session."""

    opener = MagicMock()
    opener.open.return_value.__enter__.return_value = io.BytesIO(b"OK")

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    core.http_get("https://adventofcode.com/2026")

    request = opener.open.call_args.args[0]

    assert request.get_header("Cookie") is None


def test_http_get_handles_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie la gestion des erreurs HTTP."""

    opener = MagicMock()
    opener.open.side_effect = urllib.error.HTTPError(
        url="https://adventofcode.com/2026",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=None,
    )

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    with pytest.raises(core.AocError, match="404"):
        core.http_get("https://adventofcode.com/2026")


def test_http_get_handles_network_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie la gestion des erreurs réseau."""

    opener = MagicMock()
    opener.open.side_effect = urllib.error.URLError("Connection refused")

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    with pytest.raises(core.AocError):
        core.http_get("https://adventofcode.com/2026")


def test_http_get_uses_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie que la requête utilise un délai maximal."""

    opener = MagicMock()
    opener.open.return_value.__enter__.return_value = io.BytesIO(b"OK")

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *args: opener,
    )

    core.http_get("https://adventofcode.com/2026")

    _, kwargs = opener.open.call_args

    assert kwargs["timeout"] == 15
