from __future__ import annotations

import shutil
from pathlib import Path


def install_export(
    export_dir: Path,
    target_dir: Path,
    package_name: str,
    force: bool = True,
) -> Path:
    """Copy export_dir into target_dir/package_name.

    Raises FileNotFoundError if export_dir does not exist.
    Raises FileExistsError if the target path already exists and force is False.
    """
    if not export_dir.exists():
        raise FileNotFoundError(f"Export directory not found: {export_dir}")

    target = target_dir / package_name

    if target.exists():
        if not force:
            raise FileExistsError(f"Target already exists: {target}")
        shutil.rmtree(target)

    shutil.copytree(export_dir, target)
    return target
