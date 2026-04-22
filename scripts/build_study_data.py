from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Iterable


JP_RE = re.compile(r"[ぁ-んァ-ン一-龯々ー]")
KANJI_RE = re.compile(r"[一-龯々]")
ASCII_RE = re.compile(r"[A-Za-z]")
UNIT_ID_RE = re.compile(r"^unit-(\d{2})$")

UNIT_TITLE_OVERRIDES = {
    "unit-01": "1・スーパーで買い物",
    "unit-02": "2・ショッピング",
    "unit-03": "3・近所迷惑",
    "unit-04": "4・子どもの学校からの手紙",
    "unit-05": "5・引っ越し",
    "unit-06": "6・町",
    "unit-07": "7・交通",
    "unit-08": "8・道をたずねる",
    "unit-09": "9・母の誕生日",
    "unit-10": "10・パーティー",
    "unit-11": "11・ホテルの予約",
    "unit-12": "12・旅行に行こう",
    "unit-13": "13・アルバイト",
    "unit-14": "14・会社",
    "unit-15": "15・ランチタイム",
    "unit-16": "16・仕事",
    "unit-17": "17・日本語勉強中",
    "unit-18": "18・大学生活",
    "unit-19": "19・将来の夢",
    "unit-20": "20・子ども時代",
    "unit-21": "21・風邪",
    "unit-22": "22・落し物",
    "unit-23": "23・忘れ物",
    "unit-24": "24・失敗",
    "unit-25": "25・季節",
    "unit-26": "26・天気予報",
    "unit-27": "27・事故",
    "unit-28": "28・火事",
    "unit-29": "29・手紙",
    "unit-30": "30・健康",
    "unit-31": "31・趣味",
    "unit-32": "32・会話はむずかしい",
}


@dataclass
class Line:
    text: str
    score: float
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h


def has_japanese(text: str) -> bool:
    return bool(JP_RE.search(text))


def has_kanji(text: str) -> bool:
    return bool(KANJI_RE.search(text))


def clean_text(text: str) -> str:
    fullwidth_digits = str.maketrans("０１２３４５６７８９", "0123456789")
    text = text.translate(fullwidth_digits)
    text = text.replace("ａ", "a").replace("ｂ", "b").replace("Ｃ", "c")
    text = text.replace("ą", "a").replace("ā", "a").replace("Ｂ", "b")
    text = text.replace("（", "(").replace("）", ")")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ・·")


PT_REPLACEMENTS = [
    (r"\bpromocao\b", "promoção"),
    (r"\bPromocao\b", "Promoção"),
    (r"\bpreco\b", "preço"),
    (r"\bPreco\b", "Preço"),
    (r"\bja\b", "já"),
    (r"\bJa\b", "Já"),
    (r"\bvoce\b", "você"),
    (r"\bVoce\b", "Você"),
    (r"\bvoces\b", "vocês"),
    (r"\bVocês\b", "Vocês"),
    (r"\bnao\b", "não"),
    (r"\bNao\b", "Não"),
    (r"\besta\b", "está"),
    (r"\bEsta\b", "Está"),
    (r"\bestao\b", "estão"),
    (r"\bEstao\b", "Estão"),
    (r"\be\b", "é"),
    (r"\bE\b", "É"),
    (r"\bate\b", "até"),
    (r"\bAte\b", "Até"),
    (r"\bmes\b", "mês"),
    (r"\bMes\b", "Mês"),
    (r"\btaxi\b", "táxi"),
    (r"\bTaxi\b", "Táxi"),
    (r"\bonibus\b", "ônibus"),
    (r"\bOnibus\b", "Ônibus"),
    (r"\bproximo\b", "próximo"),
    (r"\bProximo\b", "Próximo"),
    (r"\bultimo\b", "último"),
    (r"\bUltimo\b", "Último"),
    (r"\bsaude\b", "saúde"),
    (r"\bSaude\b", "Saúde"),
    (r"\bdificil\b", "difícil"),
    (r"\bDificil\b", "Difícil"),
    (r"\bfacil\b", "fácil"),
    (r"\bFacil\b", "Fácil"),
    (r"\bnecessario\b", "necessário"),
    (r"\bNecessario\b", "Necessário"),
    (r"\bpossivel\b", "possível"),
    (r"\bPossivel\b", "Possível"),
    (r"\bnumero\b", "número"),
    (r"\bNumero\b", "Número"),
    (r"\bJapones\b", "Japonês"),
    (r"\bjapones\b", "japonês"),
    (r"\bcerimonia\b", "cerimônia"),
    (r"\bCerimonia\b", "Cerimônia"),
    (r"\bconveniencia\b", "conveniência"),
    (r"\bConveniência\b", "Conveniência"),
    (r"\btransito\b", "trânsito"),
    (r"\bTransito\b", "Trânsito"),
    (r"\bpredio\b", "prédio"),
    (r"\bPredio\b", "Prédio"),
    (r"\bquimica\b", "química"),
    (r"\bQuimica\b", "Química"),
    (r"\bpolitica\b", "política"),
    (r"\bPolitica\b", "Política"),
]


def fix_pt(text: str | None) -> str | None:
    if not text:
        return text
    text = clean_text(text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    english_marker = r"\b(?:I|You|We|They|This|That|There|Please|Can|The|A lot|If|At|She|He|My|Your|Let's|To)\b"
    portuguese_starter = re.search(
        r"\b(?:Vou|Você|Tem|Meu|Minha|Não|Nao|Dá|Da para|Este|Esta|Realmente|Se é|Palavra|Uma|Sumir|envergonhar)\b",
        text,
    )
    if re.match(english_marker, text) and portuguese_starter:
        text = text[portuguese_starter.start() :]
    text = re.sub(rf"\s*{english_marker}[^.?!]*(?:[.?!]|$)", " ", text)
    text = re.sub(r"\bVazio\s+(Este|Esta)\b", r"\1", text)
    for pattern, replacement in PT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    return re.sub(r"\s+", " ", text).strip()


def fix_latin(text: str | None) -> str | None:
    if not text:
        return text
    text = clean_text(text)
    return re.sub(r"\s+([.,!?;:])", r"\1", text).strip()


def load_pages(raw_dir: pathlib.Path) -> list[dict]:
    pages = []
    for path in sorted(raw_dir.glob("page_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        lines = [
            Line(
                text=clean_text(item["text"]),
                score=float(item.get("score", 0)),
                x=int(item["x"]),
                y=int(item["y"]),
                w=int(item["w"]),
                h=int(item["h"]),
            )
            for item in data["lines"]
            if clean_text(item["text"])
        ]
        pages.append({**data, "lines": sorted(lines, key=lambda line: (line.y, line.x))})
    return pages


def is_page_number(text: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}", text))


def is_noise(line: Line) -> bool:
    text = line.text
    if line.score < 0.18:
        return True
    if len(text) <= 1 and not text.isdigit():
        return True
    if re.fullmatch(r"[-_.,'`~]+", text):
        return True
    return False


def is_sentence_like(text: str) -> bool:
    if len(text) > 22:
        return True
    return any(mark in text for mark in ["。", "、", "？", "?", "：", ":"])


def is_reading_line(line: Line, previous: Line | None = None) -> bool:
    if not has_japanese(line.text):
        return False
    if line.h > 24:
        return False
    if previous and line.y - previous.y > 52:
        return False
    return True


def compact_join(lines: Iterable[str]) -> str:
    parts = [clean_text(line) for line in lines if clean_text(line)]
    return " ".join(parts).strip()


def merge_lines(lines: list[Line], y_tolerance: int = 18) -> list[str]:
    groups: list[list[Line]] = []
    for line in sorted(lines, key=lambda item: (item.y, item.x)):
        if not groups or abs(groups[-1][0].y - line.y) > y_tolerance:
            groups.append([line])
        else:
            groups[-1].append(line)

    merged = []
    for group in groups:
        text = compact_join(line.text for line in sorted(group, key=lambda item: item.x))
        if text and not is_page_number(text):
            merged.append(text)
    return merged


def detect_unit_header(lines: list[Line]) -> tuple[int, str, str | None] | None:
    top = [line for line in lines if line.y < 190 and not is_noise(line)]
    numbers = [line for line in top if re.fullmatch(r"\d{1,2}", line.text)]
    titles = [
        line
        for line in top
        if has_japanese(line.text)
        and not is_page_number(line.text)
        and "ふく" not in line.text
        and "問題" not in line.text
        and len(line.text) >= 3
    ]
    if not numbers or not titles:
        return None

    number = int(numbers[0].text)
    title_line = max(titles, key=lambda line: (line.w, -line.y))
    subtitles = [
        line.text
        for line in top
        if not has_japanese(line.text) and not is_page_number(line.text) and len(line.text) > 4
    ]
    subtitle = " / ".join(subtitles[:2]) if subtitles else None
    return number, f"{number}・{title_line.text}", subtitle


def detect_review_header(lines: list[Line], footer: str | None) -> str | None:
    top_text = " ".join(line.text for line in lines if line.y < 220)
    footer = footer or ""
    if not any(marker in top_text + footer for marker in ["ふくし", "ふくしゆう", "問題"]):
        return None
    if "ふく" not in top_text + footer and "問題" not in top_text + footer:
        return None
    range_match = re.search(r"(\d{1,2})\s*[〜~\-－]\s*(\d{1,2})", top_text)
    if range_match:
        return f"{range_match.group(1)}〜{range_match.group(2)}・ふくしゅう問題"
    return "ふくしゅう問題"


def detect_footer(lines: list[Line]) -> str | None:
    if not lines:
        return None
    max_y = max(line.y for line in lines)
    bottom = [
        line
        for line in lines
        if line.y >= max_y - 95 and has_japanese(line.text) and not is_page_number(line.text)
    ]
    if not bottom:
        return None
    preferred = [line for line in bottom if "・" in line.text or "問題" in line.text or "付録" in line.text]
    line = max(preferred or bottom, key=lambda item: (item.w, item.x))
    return line.text


def parse_unit_title(text: str | None) -> tuple[int, str] | None:
    if not text:
        return None
    match = re.match(r"^\s*(\d{1,2})([・･]?)(.+?)\s*$", text)
    if not match:
        return None
    number = int(match.group(1))
    separator = match.group(2)
    title = clean_text(match.group(3))
    if separator == "" and (not title or not has_japanese(title[0])):
        return None
    if not title or "問題" in title or "付表" in title or "Appendix" in title or not has_japanese(title):
        return None
    return number, f"{number}・{title}"


def detect_appendix_title(lines: list[Line], footer: str | None, page: int) -> str:
    top = [
        line
        for line in lines
        if line.y < 180
        and has_japanese(line.text)
        and not is_page_number(line.text)
        and "付表" not in line.text
        and len(line.text) >= 2
    ]
    if top:
        title = max(top, key=lambda line: (line.h * line.w, line.w)).text
        return f"付録・{title}"
    if footer and has_japanese(footer) and "付表" not in footer:
        return f"付録・{footer}"
    return f"付録・Página {page}"


def chapter_id(title: str, number: int | None, fallback_page: int) -> str:
    if number is not None:
        return f"unit-{number:02}"
    key = re.sub(r"[^0-9A-Za-zぁ-んァ-ン一-龯]+", "-", title).strip("-")
    key = key[:40] or f"page-{fallback_page}"
    return f"section-{key}"


def exercise_start(lines: list[Line], is_review: bool) -> int | None:
    if is_review:
        return min((line.y for line in lines if line.y > 80), default=None)
    starts = [
        line.y
        for line in lines
        if line.y > 450 and any(marker in line.text for marker in ["れんし", "練習"])
    ]
    return min(starts) if starts else None


def page_content_bottom(lines: list[Line]) -> int:
    if not lines:
        return 99999
    return max(line.y for line in lines) - 90


def vocabulary_bounds(lines: list[Line], is_review: bool) -> tuple[int, int] | None:
    if is_review:
        return None
    start_candidates = [line.y for line in lines if "新しいことば" in line.text]
    start = min(start_candidates) + 40 if start_candidates else 260
    end = exercise_start(lines, False) or page_content_bottom(lines)
    if end - start < 80:
        return None
    return start, end


def is_term_candidate(line: Line) -> bool:
    if is_noise(line) or not has_japanese(line.text):
        return False
    if is_page_number(line.text) or "新しいことば" in line.text or "もうちょっと" in line.text:
        return False
    if is_sentence_like(line.text):
        return False
    if line.x > 285:
        return False
    if line.h < 24 and not has_kanji(line.text):
        return False
    return True


def split_translation(lines: list[Line]) -> tuple[str | None, str | None]:
    texts = [line.text for line in sorted(lines, key=lambda item: (item.y, item.x)) if not has_japanese(line.text)]
    if not texts:
        return None, None
    if len(texts) == 1:
        return None, texts[0]
    return texts[0], compact_join(texts[1:])


def split_example(lines: list[Line]) -> dict:
    sorted_lines = sorted(lines, key=lambda item: (item.y, item.x))
    jp = compact_join(line.text for line in sorted_lines if has_japanese(line.text))
    latin = [line.text for line in sorted_lines if not has_japanese(line.text)]
    example: dict[str, str] = {}
    if jp:
        example["ja"] = jp
    if latin:
        example["en"] = latin[0]
    if len(latin) > 1:
        example["pt"] = compact_join(latin[1:])
    return example


def extract_regular_cards(page: int, chapter: str, lines: list[Line], start: int, end: int) -> list[dict]:
    region = [line for line in lines if start <= line.y <= end and not is_noise(line)]
    candidates = [line for line in region if is_term_candidate(line)]
    terms: list[Line] = []
    for line in candidates:
        previous = terms[-1] if terms else None
        if previous and line.x < 150 and is_reading_line(line, previous):
            continue
        terms.append(line)

    cards = []
    seen: set[str] = set()
    for index, term in enumerate(terms):
        row_end = terms[index + 1].y - 4 if index + 1 < len(terms) else end
        row = [line for line in region if term.y - 8 <= line.y <= row_end]
        reading_lines = [
            line
            for line in row
            if line is not term and line.x < 285 and is_reading_line(line, term)
        ]
        reading = reading_lines[0].text if reading_lines else None
        translation_lines = [
            line
            for line in row
            if 300 <= line.x < 570 and not is_reading_line(line, term) and line is not term
        ]
        example_lines = [line for line in row if line.x >= 570 and line is not term]
        en, pt = split_translation(translation_lines)
        example = split_example(example_lines)
        if term.text in seen or not (en or pt or example):
            continue
        seen.add(term.text)
        cards.append(
            {
                "id": f"{chapter}-p{page}-{len(cards) + 1:02}",
                "chapterId": chapter,
                "page": page,
                "term": term.text,
                "reading": reading,
                "meanings": {"en": en, "pt": pt},
                "example": example or None,
            }
        )
    return cards


def extract_loose_cards(page: int, chapter: str, lines: list[Line], end: int, existing: set[str]) -> list[dict]:
    cards = []
    candidates = [
        line
        for line in lines
        if 150 <= line.y <= end
        and has_japanese(line.text)
        and not is_noise(line)
        and not is_sentence_like(line.text)
        and not is_page_number(line.text)
        and line.text not in existing
        and line.w <= 330
        and line.h >= 24
    ]
    for term in candidates:
        below = [
            line
            for line in lines
            if not has_japanese(line.text)
            and abs(line.x - term.x) <= 90
            and term.y + 20 <= line.y <= term.y + 120
            and line.score >= 0.45
        ]
        if not below:
            continue
        below.sort(key=lambda line: line.y)
        en = below[0].text
        pt = below[1].text if len(below) > 1 else None
        existing.add(term.text)
        cards.append(
            {
                "id": f"{chapter}-p{page}-loose-{len(cards) + 1:02}",
                "chapterId": chapter,
                "page": page,
                "term": term.text,
                "reading": None,
                "meanings": {"en": en, "pt": pt},
                "example": None,
            }
        )
    return cards


def extract_cards(page: int, chapter: str, lines: list[Line], is_review: bool) -> list[dict]:
    bounds = vocabulary_bounds(lines, is_review)
    if not bounds:
        return []
    start, end = bounds
    regular = extract_regular_cards(page, chapter, lines, start, end)
    if len(regular) >= 4:
        return regular
    existing = {card["term"] for card in regular}
    return regular + extract_loose_cards(page, chapter, lines, end, existing)


def extract_exercise(page: int, chapter: str, title: str, lines: list[Line], is_review: bool) -> dict | None:
    start = exercise_start(lines, is_review)
    if start is None:
        return None
    bottom = page_content_bottom(lines)
    exercise_lines = [
        line for line in lines if start <= line.y <= bottom and not is_noise(line) and line.score >= 0.25
    ]
    merged = merge_lines(exercise_lines)
    if len(merged) < 2:
        return None
    return {
        "id": f"{chapter}-exercise-p{page}",
        "chapterId": chapter,
        "title": title,
        "page": page,
        "lines": merged,
    }


def ensure_chapter(
    chapters: list[dict],
    by_id: dict[str, dict],
    title: str,
    page: int,
    number: int | None,
    subtitle: str | None,
    kind: str,
) -> dict:
    cid = chapter_id(title, number, page)
    if cid in by_id:
        return by_id[cid]
    chapter = {
        "id": cid,
        "kind": kind,
        "number": number,
        "title": title,
        "subtitle": subtitle,
        "pages": [],
        "cards": [],
        "exercises": [],
    }
    chapters.append(chapter)
    by_id[cid] = chapter
    return chapter


def review_for_units(title: str) -> list[str]:
    match = re.search(r"(\d{1,2})\s*[〜~\-－]\s*(\d{1,2})", title)
    if not match:
        return []
    start, end = int(match.group(1)), int(match.group(2))
    return [f"unit-{number:02}" for number in range(start, end + 1)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build flashcard study data from OCR JSON.")
    parser.add_argument("--raw", default="data/ocr/raw")
    parser.add_argument("--out", default="public/study-data.json")
    args = parser.parse_args()

    pages = load_pages(pathlib.Path(args.raw))
    if not pages:
        raise SystemExit("No OCR pages found. Run scripts/ocr_pdf.py first.")

    page_infos = []
    page_meta: dict[int, dict] = {}
    chapter_meta: dict[str, dict] = {}

    for page_data in pages:
        page = int(page_data["page"])
        lines: list[Line] = page_data["lines"]
        footer = detect_footer(lines)
        unit = detect_unit_header(lines)
        footer_unit = parse_unit_title(footer)
        review_title = detect_review_header(lines, footer)
        info = {
            "page": page,
            "lines": lines,
            "footer": footer,
            "unit": unit,
            "footer_unit": footer_unit,
            "review_title": review_title,
        }
        page_infos.append(info)

        if page < 104 and unit and not review_title:
            number, title, subtitle = unit
            cid = chapter_id(title, number, page)
            chapter_meta[cid] = {"title": title, "number": number, "subtitle": subtitle}
            page_meta[page] = {"id": cid, "title": title, "number": number, "subtitle": subtitle}

        if page < 104 and footer_unit and not review_title:
            number, title = footer_unit
            cid = chapter_id(title, number, page)
            chapter_meta.setdefault(cid, {"title": title, "number": number, "subtitle": None})
            page_meta[page] = {"id": cid, "title": title, "number": number, "subtitle": None}

            previous_page = page - 1
            previous_info = next((item for item in page_infos if item["page"] == previous_page), None)
            if previous_info and not previous_info["review_title"]:
                page_meta[previous_page] = {
                    "id": cid,
                    "title": title,
                    "number": number,
                    "subtitle": None,
                }

    chapters: list[dict] = []
    by_id: dict[str, dict] = {}
    current: dict | None = None

    for info in page_infos:
        page = int(info["page"])
        lines: list[Line] = info["lines"]
        footer = info["footer"]
        review_title = info["review_title"]
        meta = page_meta.get(page)

        if meta:
            current = ensure_chapter(
                chapters,
                by_id,
                meta["title"],
                page,
                meta["number"],
                meta.get("subtitle"),
                "unit",
            )
        elif review_title:
            if current and ("ふく" in current["title"] or "問題" in current["title"]) and review_title == "ふくしゅう問題":
                pass
            else:
                current = ensure_chapter(chapters, by_id, review_title, page, None, None, "review")
        elif page >= 104:
            title = detect_appendix_title(lines, footer, page)
            current = ensure_chapter(chapters, by_id, title, page, None, None, "appendix")
        elif current is None:
            fallback = footer or f"Página {page}"
            current = ensure_chapter(chapters, by_id, fallback, page, None, None, "review")

        assert current is not None
        if page not in current["pages"]:
            current["pages"].append(page)

        is_review = current["kind"] == "review"
        if "ふくし" in current["title"] or "問題" in current["title"]:
            is_review = True

        cards = extract_cards(page, current["id"], lines, is_review)
        current["cards"].extend(cards)

        exercise = extract_exercise(page, current["id"], current["title"], lines, is_review)
        if exercise:
            exercise["kind"] = "review" if is_review else current["kind"]
            exercise["reviewFor"] = review_for_units(current["title"]) if is_review else []
            current["exercises"].append(exercise)

    for chapter in chapters:
        if chapter["id"] in UNIT_TITLE_OVERRIDES:
            chapter["title"] = UNIT_TITLE_OVERRIDES[chapter["id"]]
        chapter["pages"].sort()
        chapter["cards"] = [
            card
            for card in chapter["cards"]
            if clean_text(card["term"]) and (card["meanings"].get("pt") or card["meanings"].get("en") or card.get("example"))
        ]
        for card in chapter["cards"]:
            if not card.get("reading") or not has_japanese(card["reading"]):
                card.pop("reading", None)
            if not card.get("example"):
                card.pop("example", None)
            else:
                example = card["example"]
                if example.get("en"):
                    example["en"] = fix_latin(example["en"])
                if example.get("pt"):
                    example["pt"] = fix_pt(example["pt"])
            card["meanings"] = {key: value for key, value in card["meanings"].items() if value}
            if card["meanings"].get("en"):
                card["meanings"]["en"] = fix_latin(card["meanings"]["en"])
            if card["meanings"].get("pt"):
                card["meanings"]["pt"] = fix_pt(card["meanings"]["pt"])

    payload = {
        "appName": "Dango N4 - 段語 N4",
        "source": "Nihongo Challenge Kotoba N4",
        "createdBy": "Daniel Prado de Campos",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "chapters": chapters,
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    total_cards = sum(len(chapter["cards"]) for chapter in chapters)
    total_exercises = sum(len(chapter["exercises"]) for chapter in chapters)
    print(f"Wrote {out_path}")
    print(f"Chapters: {len(chapters)}")
    print(f"Cards: {total_cards}")
    print(f"Exercise sets: {total_exercises}")


if __name__ == "__main__":
    main()
