from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
from typing import Any

import fitz
from paddleocr import PaddleOCR


def parse_pages(value: str, page_count: int) -> list[int]:
    pages: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(x.strip()) for x in part.split("-", 1)]
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return [page for page in sorted(pages) if 1 <= page <= page_count]


def render_page(doc: fitz.Document, page_number: int, scale: float, out_dir: pathlib.Path) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"page_{page_number:03}_{scale:g}x.png"
    if path.exists():
        return path
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(path)
    return path


def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def box_to_bounds(box: Any) -> dict[str, int]:
    points = [[int(point[0]), int(point[1])] for point in box]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {
        "x": min(xs),
        "y": min(ys),
        "w": max(xs) - min(xs),
        "h": max(ys) - min(ys),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR a scanned PDF into page-level JSON.")
    parser.add_argument("--pdf", default="Nihongo_Challenge_Kotoba_N4.pdf")
    parser.add_argument("--pages", default="16-120", help="1-based pages, e.g. 16-120 or 16,17,21")
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--out", default="data/ocr/raw")
    parser.add_argument("--images", default="data/ocr/images")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    pdf_path = pathlib.Path(args.pdf)
    out_dir = pathlib.Path(args.out)
    image_dir = pathlib.Path(args.images)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    page_numbers = parse_pages(args.pages, doc.page_count)
    if not page_numbers:
        raise SystemExit("No pages selected.")

    ocr = PaddleOCR(
        lang="japan",
        ocr_version="PP-OCRv3",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    for index, page_number in enumerate(page_numbers, start=1):
        out_path = out_dir / f"page_{page_number:03}.json"
        if out_path.exists() and not args.force:
            print(f"[{index}/{len(page_numbers)}] page {page_number}: cached")
            continue

        image_path = render_page(doc, page_number, args.scale, image_dir)
        started = time.time()
        result = ocr.predict(str(image_path))[0]
        lines = []
        for text, score, poly in zip(result["rec_texts"], result["rec_scores"], result["dt_polys"]):
            cleaned = clean_text(str(text))
            if not cleaned:
                continue
            bounds = box_to_bounds(poly)
            lines.append(
                {
                    "text": cleaned,
                    "score": round(float(score), 4),
                    **bounds,
                }
            )
        lines.sort(key=lambda item: (item["y"], item["x"]))
        payload = {
            "source": str(pdf_path),
            "page": page_number,
            "scale": args.scale,
            "image": str(image_path),
            "elapsedSeconds": round(time.time() - started, 2),
            "lines": lines,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"[{index}/{len(page_numbers)}] page {page_number}: "
            f"{len(lines)} lines in {payload['elapsedSeconds']}s"
        )


if __name__ == "__main__":
    main()
