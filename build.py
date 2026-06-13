from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def build(spec_file: Path | None, app_name: str, onefile: bool, windowed: bool) -> int:
    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        print("PyInstaller가 설치되어 있지 않습니다. `pip install pyinstaller` 후 다시 실행하세요.")
        return 1

    if spec_file is not None:
        cmd = [pyinstaller, "--clean", "--noconfirm", str(spec_file)]
        return subprocess.call(cmd)

    cmd = [pyinstaller, "--name", app_name, "--clean", "--noconfirm"]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if windowed:
        cmd.append("--windowed")

    cmd.append(str(ROOT / "main.py"))

    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Icon Bundler with PyInstaller")
    parser.add_argument("--spec", type=Path, default=ROOT / "icon_bundler.spec", help="Use a spec file")
    parser.add_argument("--name", default="IconBundler", help="Output app name")
    parser.add_argument("--onefile", action="store_true", help="Build a single-file bundle")
    parser.add_argument("--windowed", action="store_true", help="Build without console window")
    args = parser.parse_args()

    spec_file = args.spec if args.spec and args.spec.exists() else None
    return build(spec_file, args.name, args.onefile, args.windowed)


if __name__ == "__main__":
    raise SystemExit(main())
