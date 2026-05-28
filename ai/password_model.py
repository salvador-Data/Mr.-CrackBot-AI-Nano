"""
Password guess generation for Mr. CrackBot AI Nano.

Uses lightweight heuristics by default. Set MR_CRACKBOT_USE_AI=1 and install
requirements-jetson.txt to enable GPT-2 via transformers (Jetson / GPU hosts).
"""

from __future__ import annotations

import logging
import os
import re
from logging.handlers import RotatingFileHandler
from typing import Any

logger = logging.getLogger("password_generator")
if not logger.handlers:
    handler = RotatingFileHandler(
        "mr_crackbot_ai.log",
        maxBytes=1024 * 1024,
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

_model = None
_tokenizer = None


def _ai_enabled() -> bool:
    return os.environ.get("MR_CRACKBOT_USE_AI", "").strip() in ("1", "true", "yes")


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "", text or "")
    return cleaned[:24] if cleaned else "network"


def validate_metadata(metadata: dict[str, Any]) -> bool:
    if "ssid" not in metadata:
        raise ValueError("Missing required metadata field: ssid")
    return True


def validate_password_complexity(password: str) -> bool:
    return len(password) >= 8 and any(c.isdigit() for c in password)


def generate_verizon_router_passwords() -> list[str]:
    words = ["trial", "admin", "default", "hello", "network"]
    patterns: list[str] = []
    for word1 in words:
        for number in range(1, 10):
            for word2 in words:
                pattern = f"{word1}-{word2}{number}-{word2}"
                if validate_password_complexity(pattern):
                    patterns.append(pattern)
    return patterns


def generate_heuristic_passwords(metadata: dict[str, Any]) -> list[str]:
    """SSID/BSSID-aware guesses without ML dependencies."""
    validate_metadata(metadata)
    ssid = metadata["ssid"]
    slug = _slug(ssid)
    bssid = metadata.get("bssid", "00:11:22:33:44:55")
    prefix = bssid.replace(":", "")[:6]

    guesses = {
        f"{slug}1234",
        f"{slug}2024!",
        f"{slug}-admin1",
        f"Welcome{slug}1",
        f"{prefix}{slug}1",
        f"{slug}@home123",
    }
    guesses.update(generate_verizon_router_passwords())
    return [g for g in guesses if validate_password_complexity(g)]


def _load_transformers():
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer
    from transformers import GPT2LMHeadModel, GPT2Tokenizer

    _model = GPT2LMHeadModel.from_pretrained("gpt2")
    _tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return _model, _tokenizer


def generate_ai_passwords(metadata: dict[str, Any]) -> list[str]:
    if not _ai_enabled():
        return []

    try:
        model, tokenizer = _load_transformers()
        input_text = (
            f"SSID: {metadata['ssid']} "
            f"Location: {metadata.get('location', 'unknown')}"
        )
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=100)
        outputs = model.generate(inputs["input_ids"], max_length=32, num_return_sequences=5)
        guesses = [tokenizer.decode(o, skip_special_tokens=True) for o in outputs]
        return [g for g in guesses if validate_password_complexity(g)]
    except Exception as exc:
        logger.warning("AI wordlist generation unavailable: %s", exc)
        return []


def generate_password_guesses(metadata: dict[str, Any]) -> list[str]:
    validate_metadata(metadata)
    combined = generate_heuristic_passwords(metadata) + generate_ai_passwords(metadata)
    # Preserve order, drop duplicates
    seen: set[str] = set()
    unique: list[str] = []
    for guess in combined:
        if guess not in seen:
            seen.add(guess)
            unique.append(guess)
    logger.info("Generated %d password guesses for SSID %s", len(unique), metadata["ssid"])
    return unique


class PasswordGenerator:
    """Small adapter used by WordlistManager and tests."""

    def generate(self, prompt: str) -> list[str]:
        ssid = "network"
        if "SSID:" in prompt:
            ssid = prompt.split("SSID:", 1)[1].split(",", 1)[0].strip()
        return generate_password_guesses({"ssid": ssid, "bssid": "00:11:22:33:44:55"})
