"""A cron agent's prompt names the language its brief must be written in.

A scheduled run has no user turn to mirror, and every built-in automation blueprint ships an
English prompt (``cron/blueprint_catalog.py``), so a non-English profile got briefs in
whatever language the model happened to infer. The cron platform hint now carries one
advisory line naming the profile's ``display.language``; English profiles are untouched.
"""

from __future__ import annotations

import types

import pytest

from agent import i18n
from agent.prompt_builder import PLATFORM_HINTS
from agent.system_prompt import platform_hint
from gateway.session_context import _VAR_MAP


def _agent(platform, overrides=None):
    return types.SimpleNamespace(platform=platform, _platform_hint_overrides=overrides or {})


@pytest.fixture(autouse=True)
def _isolated_language(monkeypatch):
    """No ambient language, no delivery target: each test states its own."""
    monkeypatch.delenv("HERMES_LANGUAGE", raising=False)
    var = _VAR_MAP["HERMES_CRON_AUTO_DELIVER_PLATFORM"]
    token = var.set("")
    i18n.reset_language_cache()
    yield
    var.reset(token)
    i18n.reset_language_cache()


def _use(monkeypatch, lang: str) -> None:
    monkeypatch.setenv("HERMES_LANGUAGE", lang)
    i18n.reset_language_cache()


def test_english_profile_prompt_is_byte_identical(monkeypatch):
    _use(monkeypatch, "en")
    assert platform_hint(_agent("cron")) == PLATFORM_HINTS["cron"]


def test_cron_hint_names_the_profile_language(monkeypatch):
    _use(monkeypatch, "zh")
    hint = platform_hint(_agent("cron"))
    assert hint.startswith(PLATFORM_HINTS["cron"])
    assert "简体中文" in hint
    assert "(zh)" in hint
    # Advisory, not an override: a job prompt that names its own language still wins.
    assert "unless this job's own instructions name a different one" in hint


def test_language_line_survives_a_replaced_cron_hint(monkeypatch):
    _use(monkeypatch, "zh")
    hint = platform_hint(_agent("cron", {"cron": {"replace": "X"}}))
    assert hint.startswith("X\n\n")
    assert "简体中文" in hint


def test_language_line_is_cron_only(monkeypatch):
    _use(monkeypatch, "zh")
    assert "简体中文" not in platform_hint(_agent("desktop"))
