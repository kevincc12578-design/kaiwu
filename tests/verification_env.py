"""Run a verification suite against an expendable copy and a dedicated server."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class VerificationRun:
    root: Path
    base_url: str
    artifacts_dir: Path

    def get_json(self, path: str, timeout: float = 15.0) -> dict[str, Any]:
        return self._request(urllib.request.Request(self.base_url + path), timeout)

    def post_json(self, path: str, payload: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
        req = urllib.request.Request(
            self.base_url + path, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        return self._request(req, timeout)

    @staticmethod
    def _request(req: urllib.request.Request, timeout: float) -> dict[str, Any]:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=timeout) as response:
            return json.load(response)


def _ignore_copied_entries(directory: str, names: list[str]) -> list[str]:
    ignored = []
    for name in names:
        path = Path(directory) / name
        if name == "__pycache__" or path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            ignored.append(name)
    return ignored


def _wait_for_port(process: subprocess.Popen, log_path: Path) -> int:
    deadline = time.monotonic() + 60
    while process.poll() is None and time.monotonic() < deadline:
        log = log_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"Server listening at http://127\.0\.0\.1:(\d+)/", log)
        if match and 0 < int(match[1]) <= 65535:
            return int(match[1])
        time.sleep(0.1)
    raise RuntimeError(f"Verification server did not report a listening port. See {log_path}")


@contextmanager
def isolated_workbench(repo_root: Path, artifacts_dir: Path | None = None) -> Iterator[VerificationRun]:
    """Keep the server process and all mutable project inputs in a fresh copy."""
    if artifacts_dir is not None:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir = artifacts_dir.resolve()
    output = Path(tempfile.mkdtemp(prefix="kaiwu-verify-", dir=artifacts_dir)).resolve()
    print(f"Verification artifacts: {output}", flush=True)

    with tempfile.TemporaryDirectory(prefix="workbench-", dir=output) as temp:
        root = Path(temp)
        for folder in ("backend", "cases", "categories", "docs", "frontend", "rules", "templates"):
            source = repo_root / folder
            if source.is_symlink() or getattr(source, "is_junction", lambda: False)():
                raise ValueError(f"Verification requires a local project directory: {source}")
            shutil.copytree(source, root / folder, ignore=_ignore_copied_entries)
        for filename in ("VERSION", "README.md", "CHANGELOG.md", "UI与交互EU错误排查台账.md"):
            shutil.copy2(repo_root / filename, root / filename)

        log_path = output / "server.log"
        with log_path.open("wb") as log:
            process = subprocess.Popen(
                [sys.executable, "-B", "-X", "utf8", str(root / "backend" / "server.py"),
                 "--host", "127.0.0.1", "--port", "0"],
                cwd=root, stdout=log, stderr=subprocess.STDOUT,
            )
            try:
                port = _wait_for_port(process, log_path)
                run = VerificationRun(root, f"http://127.0.0.1:{port}", output)
                health = run.get_json("/api/health")
                if health.get("status") != "OK" or health.get("port") != port:
                    raise RuntimeError(f"Unexpected verification server health. See {log_path}")
                yield run
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
