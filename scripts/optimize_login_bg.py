import argparse
import shutil
import sys
from pathlib import Path
from typing import List

try:
    from PIL import Image, ImageSequence
except Exception:
    print("Pillow is required. Install with: python -m pip install pillow", file=sys.stderr)
    sys.exit(2)


def human_size(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024.0:
            return f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}TB"


def optimize_webp(path: Path, max_width: int, quality: int, backup: bool) -> None:
    if not path.exists():
        raise FileNotFoundError(path)

    if backup:
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(path, bak)

    before_size = path.stat().st_size

    with Image.open(path) as im:
        im.load()

        # Detect animation
        n_frames = getattr(im, "n_frames", 1)
        is_animated = n_frames and n_frames > 1

        if not is_animated:
            # Single frame flow
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")
            w, h = im.size
            if w > max_width:
                ratio = max_width / float(w)
                new_size = (max_width, int(h * ratio))
                im = im.resize(new_size, Image.LANCZOS)

            im.save(
                path,
                format="WEBP",
                quality=quality,
                method=6,
                lossless=False,
                exact=False,
                subsampling="4:2:0",
            )
        else:
            # Animated flow: preserve frames, durations, loop
            frames: List[Image.Image] = []
            durations: List[int] = []

            for i, frame in enumerate(ImageSequence.Iterator(im)):
                fr = frame.convert("RGBA") if frame.mode not in ("RGB", "RGBA") else frame.copy()
                w, h = fr.size
                if w > max_width:
                    ratio = max_width / float(w)
                    new_size = (max_width, int(h * ratio))
                    fr = fr.resize(new_size, Image.LANCZOS)
                frames.append(fr)
                # duration per frame (ms); default to 100ms if missing
                durations.append(frame.info.get("duration", im.info.get("duration", 100)))

            loop = im.info.get("loop", 0)

            # Save animated webp; requires Pillow with animated WebP support
            frames[0].save(
                path,
                format="WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=loop,
                quality=quality,
                method=6,
                lossless=False,
                exact=False,
                subsampling="4:2:0",
            )

    after_size = path.stat().st_size
    print(f"Optimized {path.name}: {human_size(before_size)} -> {human_size(after_size)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Optimize a WebP image in-place for size.")
    ap.add_argument("--path", type=Path, default=Path("static/images/login-bg.webp"))
    ap.add_argument("--max-width", type=int, default=1920)
    ap.add_argument("--quality", type=int, default=70)
    ap.add_argument("--no-backup", action="store_true", help="Do not create .bak of original")
    args = ap.parse_args()

    try:
        optimize_webp(args.path, args.max_width, args.quality, backup=not args.no_backup)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
