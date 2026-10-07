from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ttdltq.config import PROJECT_ROOT, RAW_DIR, ensure_runtime_directories, load_yaml


USER_AGENT = "TTDLTQ-Education-Research/1.0 (+academic reproducibility)"
MANIFEST_PATH = PROJECT_ROOT / "data" / "source_manifest.json"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(
    url: str,
    destination: Path,
    *,
    force: bool = False,
    retries: int = 4,
    timeout: int = 180,
) -> Path:
    """Download a file atomically with retries and a traceable user agent."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return destination

    partial = destination.with_suffix(destination.suffix + ".part")
    if partial.exists():
        partial.unlink()

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with partial.open("wb") as output:
                    shutil.copyfileobj(response, output, length=1024 * 1024)
            partial.replace(destination)
            return destination
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if partial.exists():
                partial.unlink()
            if attempt < retries:
                time.sleep(2**attempt)

    raise RuntimeError(f"Could not download {url}: {last_error}")


def _safe_member_path(root: Path, member_name: str) -> Path:
    target = (root / member_name).resolve()
    root_resolved = root.resolve()
    if root_resolved != target and root_resolved not in target.parents:
        raise ValueError(f"Unsafe path inside ZIP: {member_name}")
    return target


def extract_zip(
    archive: Path,
    destination: Path,
    *,
    selected_names: Iterable[str] | None = None,
) -> list[Path]:
    """Extract an archive safely; optionally keep only exact member basenames."""

    destination.mkdir(parents=True, exist_ok=True)
    wanted = {name.lower() for name in selected_names} if selected_names else None
    extracted: list[Path] = []
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():
                continue
            basename = Path(member.filename).name
            if wanted is not None and basename.lower() not in wanted:
                continue
            target = _safe_member_path(destination, basename)
            with bundle.open(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted.append(target)
    if not extracted:
        raise RuntimeError(f"No expected files extracted from {archive}")
    return extracted


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"schema_version": 1, "sources": {}, "protected_files": {}}
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    with MANIFEST_PATH.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _record_source(
    manifest: dict[str, Any],
    key: str,
    url: str,
    archive: Path,
    extracted: list[Path],
) -> None:
    manifest["sources"][key] = {
        "url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive": str(archive.relative_to(PROJECT_ROOT)),
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256_file(archive),
        "extracted": [
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in extracted
        ],
    }


def _record_protected_rubric(manifest: dict[str, Any]) -> None:
    candidates = list(PROJECT_ROOT.glob("RUBRIC*.pdf"))
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one protected RUBRIC PDF in project root")
    rubric = candidates[0]
    manifest["protected_files"][rubric.name] = {
        "sha256": sha256_file(rubric),
        "policy": "read_only_do_not_modify",
    }


def acquire_scorecard(
    config: dict[str, Any], *, include_history: bool, force: bool
) -> None:
    manifest = _load_manifest()
    scorecard_root = RAW_DIR / "scorecard"

    for key in ("institution", "field_of_study"):
        item = config["scorecard"][key]
        archive = scorecard_root / "downloads" / item["archive_name"]
        download_file(item["url"], archive, force=force)
        extracted = extract_zip(archive, scorecard_root / key)
        _record_source(manifest, f"scorecard_{key}", item["url"], archive, extracted)

    if include_history:
        item = config["scorecard"]["history"]
        archive = scorecard_root / "downloads" / item["archive_name"]
        download_file(item["url"], archive, force=force, timeout=600)
        selected = [
            f"MERGED{start}_{str(start + 1)[-2:]}_PP.csv"
            for start in range(2017, 2023)
        ]
        extracted = extract_zip(
            archive,
            scorecard_root / "history",
            selected_names=selected,
        )
        _record_source(manifest, "scorecard_history", item["url"], archive, extracted)

    _record_protected_rubric(manifest)
    _save_manifest(manifest)


def acquire_ipeds(config: dict[str, Any], *, force: bool) -> None:
    manifest = _load_manifest()
    base_url = config["ipeds"]["base_url"].rstrip("/")
    ipeds_root = RAW_DIR / "ipeds"

    for table in config["ipeds"]["tables"]:
        table_id = table["id"]
        url = f"{base_url}/{table_id}.zip"
        archive = ipeds_root / "downloads" / f"{table_id}.zip"
        download_file(url, archive, force=force, timeout=300)
        extracted = extract_zip(archive, ipeds_root / table_id)
        _record_source(manifest, f"ipeds_{table_id}", url, archive, extracted)

    _record_protected_rubric(manifest)
    _save_manifest(manifest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download official education data")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Download the large historical College Scorecard archive",
    )
    parser.add_argument("--force", action="store_true", help="Redownload existing files")
    parser.add_argument("--skip-scorecard", action="store_true")
    parser.add_argument("--skip-ipeds", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_runtime_directories()
    config = load_yaml("data_sources.yaml")
    if not args.skip_scorecard:
        acquire_scorecard(config, include_history=args.include_history, force=args.force)
    if not args.skip_ipeds:
        acquire_ipeds(config, force=args.force)
    print(f"Source manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

