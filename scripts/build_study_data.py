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
    text = re.sub(r"\b(?:It'?s|I was|I have|This|That|There|Please|Can|The|A lot|If|At|She|He|My|Your|Let'?s)\b.*$", "", text)
    text = text.replace(" t?", "").replace(" G?", "").replace(" Gi?", "").replace(" Geu?", "")
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
    text = text.replace("Isomeone", "someone").replace("Isomeonel", "someone")
    text = text.replace("Itime", "time").replace("Itriste", "triste").replace("Igripado", "gripado")
    text = text.replace("It.]", "").replace("I]", "").replace("I ", "")
    return re.sub(r"\s+([.,!?;:])", r"\1", text).strip()


TERM_OVERRIDES = {
    "ちょうどいしい": "ちょうどいい",
    "たすねる": "たずねる",
    "迅える": "迎える",
    "すいぶん": "ずいぶん",
    "あいさつ(する": "あいさつ(する)",
    "(高校)": "高校",
    "決して(ーない": "決して(～ない)",
    "1市": None,
    "野の": "普通",
    "中変": None,
    "日本の生活": None,
    "せしかー": None,
    "世んせし": None,
    "様子や感想を聞くとき": None,
    "大事な指輪がなくなった": None,
}

READING_OVERRIDES = {
    "割引き": "わりびき",
    "特に": "とくに",
    "近所": "きんじょ",
    "迷惑": "めいわく",
    "娘(さん)": "むすめ(さん)",
    "駐車場": "ちゅうしゃじょう",
    "世話": "せわ",
    "特別な": "とくべつな",
    "行う": "おこなう",
    "探す": "さがす",
    "都合": "つごう",
    "汚れる": "よごれる",
    "続く": "つづく",
}

MEANING_OVERRIDES = {
    ("半額", "pt"): "metade do preço",
    ("冷凍(する)", "en"): "freezing; to freeze",
    ("冷凍(する)", "pt"): "congelado; congelar",
    ("今夜", "pt"): "esta noite",
    ("用意(する)", "en"): "preparation; to prepare",
    ("用意(する)", "pt"): "preparo; preparar",
    ("先輩", "pt"): "colega veterano",
    ("決める", "pt"): "decidir",
    ("迷惑", "pt"): "incômodo",
    ("近所", "pt"): "vizinhança",
    ("娘(さん)", "pt"): "filha",
    ("あいさつ(する)", "en"): "greeting; to greet",
    ("あいさつ(する)", "pt"): "cumprimento; cumprimentar",
    ("かまいません", "en"): "not to mind",
    ("かまいません", "pt"): "não se importar",
    ("特別な", "en"): "special",
    ("行う", "pt"): "realizar; fazer",
    ("なるべく", "pt"): "na medida do possível",
    ("出席(する)", "en"): "attendance; to attend",
    ("出席(する)", "pt"): "participação; participar",
    ("遠慮(する)", "en"): "hesitation; to hesitate",
    ("遠慮(する)", "pt"): "hesitação; hesitar",
    ("相談(する)", "pt"): "consulta; consultar",
    ("準備(する)", "en"): "preparation; to prepare",
    ("準備(する)", "pt"): "preparo; preparar",
    ("できる", "en"): "to be built; to be completed",
    ("できる", "pt"): "ficar pronto; ser construído",
    ("ずいぶん", "en"): "a great deal",
    ("工場", "pt"): "fábrica",
    ("生産(する)", "en"): "production; to produce",
    ("生産(する)", "pt"): "produção; produzir",
    ("輸入(する)", "en"): "importation; to import",
    ("輸入(する)", "pt"): "importação; importar",
    ("計画(する)", "en"): "plan; to plan",
    ("計画(する)", "pt"): "plano; planejar",
    ("運転(する)", "en"): "driving; to drive",
    ("運転(する)", "pt"): "direção; dirigir",
    ("通り", "pt"): "rua; avenida",
    ("心配(する)", "en"): "worry; to worry",
    ("心配(する)", "pt"): "preocupação; preocupar-se",
    ("クラシック(な)", "en"): "classical",
    ("開く", "pt"): "abrir; realizar",
    ("すばらしい", "en"): "wonderful",
    ("すばらしい", "pt"): "maravilhoso",
    ("招待(する)", "en"): "invitation; to invite",
    ("招待(する)", "pt"): "convite; convidar",
    ("よろこぶ", "en"): "to be delighted",
    ("よろこぶ", "pt"): "ficar contente",
    ("予約(する)", "en"): "reservation; to reserve",
    ("予約(する)", "pt"): "reserva; reservar",
    ("動物", "en"): "animal",
    ("美しい", "en"): "beautiful",
    ("体験(する)", "en"): "experience; to experience",
    ("体験(する)", "pt"): "experiência; vivenciar",
    ("希望(する)", "en"): "wish; to wish for",
    ("希望(する)", "pt"): "desejo; desejar",
    ("失礼(する)", "pt"): "desculpar-se; retirar-se",
    ("競争(する)", "en"): "competition; to compete",
    ("競争(する)", "pt"): "competição; competir",
    ("入院(する)", "en"): "hospitalization; to be hospitalized",
    ("入院(する)", "pt"): "internação; internar",
    ("退院(する)", "pt"): "alta; receber alta",
    ("気をつける", "en"): "to be careful",
    ("説明(する)", "en"): "explanation; to explain",
    ("説明(する)", "pt"): "explicação; explicar",
    ("国際", "en"): "international",
    ("国際", "pt"): "internacional",
    ("入学(する)", "en"): "entrance; to enter a school",
    ("入学(する)", "pt"): "ingresso; ingressar",
    ("大学院", "en"): "graduate school",
    ("大学院", "pt"): "pós-graduação",
    ("高校", "en"): "senior high school",
    ("高校", "pt"): "ensino médio",
    ("高校生", "en"): "high school student",
    ("高校生", "pt"): "estudante do ensino médio",
    ("運動(する)", "en"): "exercise; to exercise",
    ("運動(する)", "pt"): "exercício; praticar esporte",
    ("無理な", "pt"): "impossível; excessivo",
    ("家内", "pt"): "minha esposa",
    ("妻ノ家内", "pt"): "esposa / minha esposa",
    ("久しぶり", "pt"): "muito tempo; há quanto tempo",
    ("風邪をひく", "pt"): "ficar gripado",
    ("なくす", "pt"): "perder",
    ("最後", "en"): "the last",
    ("最後", "pt"): "último",
    ("わかす", "pt"): "esquentar; ferver",
    ("手伝う", "pt"): "ajudar",
    ("かぎをかける", "pt"): "trancar com chave",
    ("おなかがすく", "pt"): "ficar com fome",
    ("続ける", "pt"): "continuar",
    ("確認(する)", "en"): "confirmation; to check",
    ("確認(する)", "pt"): "confirmação; verificar",
    ("連絡(する)", "en"): "contact; to contact",
    ("連絡(する)", "pt"): "contato; comunicar",
    ("失敗(する)", "en"): "mistake; failure; to fail",
    ("失敗(する)", "pt"): "fracasso; falhar",
    ("注意(する)", "en"): "care; to be careful",
    ("注意(する)", "pt"): "atenção; prestar atenção",
    ("気分", "pt"): "disposição; humor",
    ("安心(する)", "en"): "relief; to be relieved",
    ("安心(する)", "pt"): "alívio; sentir-se seguro",
    ("見える", "pt"): "parecer; ser visto",
}

DEFAULT_MEANINGS = {
    "Tシャツ": {"en": "T-shirt", "pt": "camiseta"},
    "スカート": {"en": "skirt", "pt": "saia"},
    "サンダル": {"en": "sandals", "pt": "sandália"},
    "側に": {"en": "beside; on the side", "pt": "ao lado"},
    "ばかり": {"en": "nothing but; only", "pt": "só; apenas"},
    "～まま": {"en": "as is", "pt": "do jeito que está"},
}

DROP_EXAMPLE_TERMS = {"Tシャツ", "スカート", "サンダル"}


def has_page_reference(text: str) -> bool:
    return bool(re.search(r"(?:p|ｐ)\s*\d+", text, re.IGNORECASE))


def clean_term(term: str) -> str | None:
    term = clean_text(term).replace("一", "ー")
    term = TERM_OVERRIDES.get(term, term)
    if term is None:
        return None
    term = re.sub(r"[＊*]+$", "", term)
    term = re.sub(r"\((?:\d|〜|~|-)+\)$", "", term)
    term = re.sub(r"（(?:\d|〜|~|-)+）$", "", term)
    term = term.strip()
    if not term or term.startswith("*"):
        return None
    if re.search(r"[0-9]", term) and not re.fullmatch(r"\d+日(?:\(間\))?|\d+時", term):
        return None
    if any(marker in term for marker in ["亭", "市正", "言しい方"]):
        return None
    return term if has_japanese(term) else None


def clean_reading(term: str, reading: str | None) -> str | None:
    override = READING_OVERRIDES.get(term)
    if override:
        return override
    if not reading:
        return None
    reading = clean_text(reading)
    if not re.fullmatch(r"[ぁ-んァ-ンー()（）]+", reading):
        return None
    return reading


def clean_japanese_example(text: str | None) -> str | None:
    if not text:
        return None
    text = clean_text(text)
    text = text.replace("ごの", "この").replace("おいしくなし", "おいしくない")
    text = text.replace("すわつても", "すわっても")
    text = re.sub(r"\s+", " ", text).strip()
    if "。" in text:
        first_sentence = text.split("。", 1)[0].strip() + "。"
        if has_japanese(first_sentence) and not has_page_reference(first_sentence):
            text = first_sentence
    elif text.count(" ") >= 2:
        return None
    if has_page_reference(text) or any(marker in text for marker in ["糸", "氷", "*", "×", "`"]):
        return None
    if re.search(r"[A-Za-z]{2,}", text):
        return None
    if any(marker in text for marker in ["古", "忙", "札", "正丁", "市正", "し中", "よ1", "オビ", "多(", "お口"]):
        return None
    return text if has_japanese(text) else None


def clean_card(card: dict) -> dict | None:
    term = clean_term(card["term"])
    if not term:
        return None
    card["term"] = term
    reading = clean_reading(term, card.get("reading"))
    if reading:
        card["reading"] = reading
    else:
        card.pop("reading", None)

    meanings = {}
    for key, value in card.get("meanings", {}).items():
        override = MEANING_OVERRIDES.get((term, key))
        cleaned = override if override else (fix_pt(value) if key == "pt" else fix_latin(value))
        if cleaned and not has_page_reference(cleaned):
            meanings[key] = cleaned
    if not meanings and term in DEFAULT_MEANINGS:
        meanings = DEFAULT_MEANINGS[term]
    card["meanings"] = meanings

    example = None if term in DROP_EXAMPLE_TERMS else card.get("example") or None
    if example:
        ja = clean_japanese_example(example.get("ja"))
        if ja:
            cleaned_example = {"ja": ja}
            if example.get("en"):
                en = fix_latin(example["en"])
                if en and not has_page_reference(en):
                    cleaned_example["en"] = en
            if example.get("pt"):
                pt = fix_pt(example["pt"])
                if pt and not has_page_reference(pt):
                    cleaned_example["pt"] = pt
            card["example"] = cleaned_example
        else:
            card.pop("example", None)

    if not card["meanings"] and not card.get("example"):
        return None
    return card


def clean_exercise_line(text: str) -> str:
    text = clean_text(text)
    replacements = {
        "どどちら": "どちら",
        "しどちら": "どちら",
        "いし": "いい",
        "メず": "必ず",
        "Ｂ": "b",
        "Ｄ": "b",
        "り、": " b.",
        "正めて": "止めて",
        "及って": "吸って",
        "ポヶット": "ポケット",
        "ノーティー": "パーティー",
        "遠恵": "遠慮",
        "迅え": "迎え",
        "ほなる": "になる",
        "スーパ一": "スーパー",
        "スー一": "スーパー",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"1・2・8・4", "1・2・3・4", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_probable_furigana_line(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    if len(compact) <= 10 and re.fullmatch(r"[ぁ-んァ-ンー]+", compact):
        return True
    return False


def looks_like_ocr_ruby_noise(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    if len(compact) <= 14 and re.fullmatch(r"[ぁ-んァ-ンー1-9」しエ土古]+", compact):
        return True
    return False


def is_exercise_instruction(text: str) -> bool:
    return any(
        marker in text
        for marker in [
            "れんしゅう",
            "ふくしゅう問題",
            "問題",
            "もんだい",
            "えらんでください",
            "ひとつえらんでください",
            "いちばんいいもの",
            "だいたいおなじ",
            "つかいかた",
        ]
    )


def parse_numbered_options(line: str) -> list[dict] | None:
    normalized = clean_exercise_line(line)
    normalized = re.sub(r"([1-4])([ぁ-んァ-ン一-龯々ーA-Za-z])", r"\1 \2", normalized)
    normalized = re.sub(r"([1-4])(?=\S)", r"\1 ", normalized)
    if " 2 " in normalized and not normalized.lstrip().startswith("1 "):
        normalized = "1 " + normalized
    matches = list(re.finditer(r"(?:^|\s)([1-4])\s+(.+?)(?=\s+[1-4]\s+|$)", normalized))
    options = []
    for match in matches:
        label = match.group(1)
        text = clean_exercise_line(match.group(2))
        if text:
            options.append({"id": label, "text": text})
    if len(options) == 3 and [option["id"] for option in options] == ["1", "2", "3"]:
        last_words = options[-1]["text"].split()
        if len(last_words) == 2 and all(has_japanese(word) for word in last_words):
            options[-1]["text"] = last_words[0]
            options.append({"id": "4", "text": last_words[1]})
    if len(options) >= 2:
        return options
    return None


def parse_inline_ab_options(line: str) -> tuple[str, list[dict]] | None:
    normalized = clean_exercise_line(line)
    if normalized.startswith(("A:", "A：", "B:", "B：", "B(")):
        return None
    if normalized.count("(a") + normalized.count("（a") > 1:
        return None
    match = re.search(r"[（(]\s*a[.。]?\s*(.+?)\s+b[.。]?\s*(.+?)\s*[）)]", normalized)
    if match:
        option_a = clean_exercise_line(match.group(1))
        option_b = clean_exercise_line(match.group(2))
        prompt = clean_exercise_line(normalized[: match.start()] + "(　)" + normalized[match.end() :])
    else:
        loose = re.search(r"[（(]\s*a[.。]?\s*(.+?)\s+b[.。]?\s*(.+)$", normalized)
        if not loose:
            return None
        option_a = clean_exercise_line(loose.group(1))
        b_and_tail = clean_exercise_line(loose.group(2))
        tail_match = re.match(r"([ぁ-んァ-ン一-龯々ー]+?)([。をにがはでと、へでください].*)?$", b_and_tail)
        option_b = clean_exercise_line(tail_match.group(1) if tail_match else b_and_tail)
        tail = clean_exercise_line(tail_match.group(2) if tail_match and tail_match.group(2) else "")
        prompt = clean_exercise_line(normalized[: loose.start()] + "(　)" + tail)
    if (
        not option_a
        or not option_b
        or len(option_a) > 18
        or len(option_b) > 18
        or re.search(r"[1-4]\s", option_a + option_b)
    ):
        return None
    return prompt, [{"id": "a", "text": option_a}, {"id": "b", "text": option_b}]


def clean_prompt_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        line = clean_exercise_line(line)
        if not line or is_exercise_instruction(line) or is_probable_furigana_line(line) or looks_like_ocr_ruby_noise(line):
            continue
        # Drop lonely OCR numbers that are not meaningful prompts.
        if re.fullmatch(r"[1-4]", line):
            continue
        segments = [line]
        if "/" in line:
            segments = [clean_exercise_line(segment) for segment in line.split("/") if clean_exercise_line(segment)]
        for segment in segments:
            segment = re.sub(r"\s*[※氷糸X][^。]*p/?\d+.*$", "", segment).strip()
            segment = re.sub(r"^[A-Z]:\s*", "", segment).strip()
            if not segment or is_probable_furigana_line(segment) or looks_like_ocr_ruby_noise(segment):
                continue
            if segment.startswith(("X", "※", "氷", "糸")):
                continue
            if (
                not has_kanji(segment)
                and segment.count(" ") >= 2
                and not any(mark in segment for mark in ["(", ")", "。", "、", "て", "に", "を", "が", "は"])
            ):
                continue
            if len(segment) <= 18 and not any(mark in segment for mark in ["(", ")", "。", "、", "て", "に", "を", "が", "は"]):
                continue
            cleaned.append(segment)
    return cleaned[-3:] or ["Escolha a melhor alternativa."]


CURATED_QUESTION_OVERRIDES = {
    "unit-02-exercise-p19-q2": {
        "prompt": ["今日の映画は(　)おもしろくなかった。"],
        "options": [
            {"id": "1", "text": "全然"},
            {"id": "2", "text": "とても"},
            {"id": "3", "text": "たくさん"},
            {"id": "4", "text": "必ず"},
        ],
        "answerId": "1",
    },
    "unit-02-exercise-p19-q4": {
        "prompt": ["わたしは女性だけど、(　)をつけるのがあまり好きじゃない。"],
        "options": [
            {"id": "1", "text": "コート"},
            {"id": "2", "text": "ぼうし"},
            {"id": "3", "text": "スカート"},
            {"id": "4", "text": "アクセサリー"},
        ],
        "answerId": "4",
    },
    "unit-03-exercise-p21-q1": {
        "prompt": ["ここでたばこを吸っても(　)。"],
        "options": [
            {"id": "a", "text": "かまいますか"},
            {"id": "b", "text": "かまいませんか"},
        ],
        "answerId": "b",
    },
    "unit-04-exercise-p23-q1": {
        "prompt": ["(　)、スーパーで買い物をしました。"],
        "options": [
            {"id": "1", "text": "さっき"},
            {"id": "2", "text": "すぐに"},
            {"id": "3", "text": "いつ"},
            {"id": "4", "text": "まだ"},
        ],
        "answerId": "1",
    },
    "unit-04-exercise-p23-q3": {
        "prompt": ["(　)早く来てください。"],
        "options": [
            {"id": "1", "text": "たぶん"},
            {"id": "2", "text": "なるべく"},
            {"id": "3", "text": "とても"},
            {"id": "4", "text": "あまり"},
        ],
        "answerId": "2",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q1": {
        "prompt": ["すぐに出かけるから、(　)しなさい。"],
        "answerId": "3",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q3": {
        "prompt": ["今日は子どもの(　)をしなければなりません。"],
        "answerId": "2",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q5": {
        "prompt": ["のこったりょうりは(　)しましょう。"],
        "answerId": "3",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q6": {
        "prompt": ["みじかい(　)でしたが、ありがとうございました。"],
        "answerId": "3",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q7": {
        "prompt": ["けっこんしきは、(　)イベントです。"],
        "answerId": "2",
    },
    "section-1-4-ふくしゅう問題-exercise-p24-q10": {
        "prompt": ["車にのっていたら、(　)おとがしてきました。"],
        "answerId": "4",
    },
    "unit-06-exercise-p29-q3": {
        "prompt": ["船で外国と貿易するとき、(　)を使う。"],
        "options": [
            {"id": "1", "text": "郵便局"},
            {"id": "2", "text": "建物"},
            {"id": "3", "text": "港"},
            {"id": "4", "text": "駅"},
        ],
        "answerId": "3",
    },
    "unit-06-exercise-p29-q4": {
        "prompt": ["来年、新しい駅が(　)らしい。"],
        "answerId": "4",
    },
    "unit-07-exercise-p31-q1": {
        "prompt": ["次の駅で(　)。"],
        "options": [
            {"id": "1", "text": "変わろう"},
            {"id": "2", "text": "進もう"},
            {"id": "3", "text": "乗り換えよう"},
            {"id": "4", "text": "変えよう"},
        ],
        "answerId": "3",
    },
    "unit-08-exercise-p33-q4": {
        "prompt": ["彼と結婚したいと言ったら、両親は(　)。"],
        "answerId": "2",
    },
    "unit-11-exercise-p41-q4": {
        "prompt": ["美術館は人で(　)だった。"],
        "answerId": "2",
    },
    "unit-13-exercise-p47-q2": {
        "prompt": ["あのレストランの(　)は親切だ。"],
        "answerId": "1",
    },
    "unit-18-exercise-p59-q2": {
        "prompt": ["「今日勉強したことを(　)しなさい」と先生に言われた。"],
        "answerId": "4",
    },
    "unit-18-exercise-p59-q3": {
        "prompt": ["日本の大学に(　)したい。"],
        "options": [
            {"id": "1", "text": "入学"},
            {"id": "2", "text": "卒業"},
            {"id": "3", "text": "計画"},
            {"id": "4", "text": "予約"},
        ],
        "answerId": "1",
    },
    "unit-21-exercise-p67-q4": {
        "prompt": ["歯が痛くて食べ物がよく(　)。"],
        "answerId": "4",
    },
    "unit-23-exercise-p71-q2": {
        "prompt": ["郵便局の人は毎日手紙などを(　)くれる。"],
        "answerId": "1",
    },
    "unit-23-exercise-p71-q4": {
        "prompt": ["家族に(　)方法を決めておきましょう。"],
        "answerId": "3",
    },
    "unit-27-exercise-p81-q1": {
        "prompt": ["(　)をした人が病院へ運ばれた。"],
        "answerId": "3",
    },
    "unit-29-exercise-p87-q1": {
        "prompt": ["この坂を(　)ところに郵便局があります。"],
        "options": [
            {"id": "1", "text": "急いだ"},
            {"id": "2", "text": "下りた"},
            {"id": "3", "text": "走った"},
            {"id": "4", "text": "止まった"},
        ],
        "answerId": "2",
    },
    "unit-30-exercise-p89-q3": {
        "prompt": ["自転車の二人乗りは危険だから(　)だよ。"],
        "answerId": "2",
    },
    "unit-31-exercise-p91-q4": {
        "prompt": ["今、映画館で子どもの好きなアニメをやっているので、娘を(　)。"],
        "answerId": "2",
    },
    "section-29-32-ふくしゅう問題-exercise-p102-q5": {
        "prompt": ["入学しきに(　)新しいふくを買ってあげた。"],
        "answerId": "1",
    },
}


def normalize_question(question: dict) -> dict:
    override = CURATED_QUESTION_OVERRIDES.get(question["id"])
    if override:
        question = {**question, **override}
    question["prompt"] = clean_prompt_lines(question["prompt"])
    question["options"] = [
        {"id": str(option["id"]), "text": clean_exercise_line(option["text"])}
        for option in question["options"]
        if clean_exercise_line(option["text"])
    ]
    return question


def is_usable_question(question: dict) -> bool:
    prompt = question.get("prompt") or []
    options = question.get("options") or []
    option_ids = [option["id"] for option in options]
    if not prompt or prompt == ["Escolha a melhor alternativa."]:
        return False
    if option_ids not in (["1", "2", "3", "4"], ["a", "b"]):
        return False
    if question.get("answerId") not in option_ids:
        return False
    prompt_text = " ".join(prompt)
    if any(marker in prompt_text for marker in ["Escolha", "Xルール", "Answer respostas", "event evento"]):
        return False
    if re.search(r"[（(]\s*a[.。]?", prompt_text) or re.search(r"\s+b[.。]", prompt_text):
        return False
    for option in options:
        text = option["text"]
        if not has_japanese(text):
            return False
        if re.search(r"(?:^|\s)[1-4]\s", text):
            return False
        if len(text) > 28:
            return False
    return True


def infer_answer_id(prompt: list[str], options: list[dict]) -> str:
    joined = " ".join(prompt)
    joined_compact = re.sub(r"\s+", "", joined)
    option_texts = {option["id"]: option["text"] for option in options}

    # Collocations and common N4 vocabulary clues recovered from the OCR text.
    clues = [
        ("全部好き", ["特に"]),
        ("サッカー", ["特に"]),
        ("100点", ["うれしい"]),
        ("品物がたくさん", ["品物"]),
        ("黒い", ["スーツ", "ぼうし"]),
        ("映画", ["全然"]),
        ("1年上", ["先輩"]),
        ("アクセサリー", ["アクセサリー"]),
        ("たばこを吸", ["かまいませんか"]),
        ("家と家", ["間"]),
        ("自転車", ["止めて"]),
        ("車を", ["とめる", "止める"]),
        ("子どもたち", ["さわいで"]),
        ("車を止める", ["駐車場"]),
        ("警官", ["交番"]),
        ("電車が止まる", ["駅"]),
        ("遊ぶところ", ["公園"]),
        ("パーティー", ["出席"]),
        ("早く来て", ["なるべく"]),
        ("仕事のこと", ["相談"]),
        ("荷物", ["片づける", "用意"]),
        ("10時間", ["すごく"]),
        ("来週の次", ["再来週"]),
        ("駅に着いた", ["やっと"]),
        ("広い", ["道路"]),
        ("工場", ["生産"]),
        ("貿易", ["港"]),
        ("新しい駅", ["できる"]),
        ("次の駅", ["乗り換えよう"]),
        ("迎え", ["空港"]),
        ("帰る", ["途中"]),
        ("交差点", ["信号"]),
        ("会わない間", ["しばらく"]),
        ("町の中", ["案内した"]),
        ("両親", ["反対した"]),
        ("せまい道", ["とおる"]),
        ("今日まで", ["かたづけ"]),
        ("こうばん", ["たずねた"]),
        ("外国", ["ゆしゅつ", "輸出"]),
        ("明日の", ["じゅんび", "準備"]),
        ("すぐに出かける", ["ようい"]),
        ("のこったりょうり", ["れいとう"]),
        ("みじかい", ["あいだ"]),
        ("けっこんしき", ["とくべつ"]),
        ("へんなおと", ["へんな"]),
        ("通勤", ["こむ"]),
        ("つうきん", ["こむ"]),
        ("へやがせまい", ["だんち"]),
        ("新幹線", ["のりかえる"]),
        ("しんかんせん", ["のりかえる"]),
        ("スポーツを", ["せんもん"]),
        ("寝て", ["ばかり"]),
        ("コンサート", ["チケット"]),
        ("興味", ["興味"]),
        ("上手に", ["なかなか"]),
        ("旅行の", ["お土産"]),
        ("妹の夫", ["招待"]),
        ("手紙を書いた", ["よろこん"]),
        ("日本の", ["季節"]),
        ("友だちの家", ["泊まる"]),
        ("富士山", ["景色"]),
        ("美術館", ["いっぱい"]),
        ("また日本", ["ぜひ"]),
        ("動物園", ["珍しい"]),
        ("行けなくて", ["残念"]),
        ("一番高い建物", ["世界"]),
        ("子どものこと", ["しんぱい"]),
        ("りょかん", ["よやく"]),
        ("ホテルの", ["あいて"]),
        ("りょうしんがうち", ["とまる"]),
        ("おみまい", ["おみまい"]),
        ("この うみ", ["うつくしい"]),
        ("おべんとう", ["けしき"]),
        ("かぞくにあげる", ["おみやげ"]),
        ("アルバイトをして", ["アルバイト"]),
        ("レストランの", ["店員"]),
        ("表と", ["裏"]),
        ("面接", ["面接"]),
        ("役に", ["立つ"]),
        ("ポスター", ["パソコン"]),
        ("給料", ["給料"]),
        ("考えられない", ["アイディア"]),
        ("別々", ["別々"]),
        ("毎日 食べ", ["サラダ"]),
        ("おっしゃいます", ["伺います"]),
        ("父が", ["倒れた"]),
        ("必ず1時", ["戻る"]),
        ("風邪", ["治らない"]),
        ("新しい・駅", ["できる"]),
        ("会わない", ["しばらく"]),
        ("今日までにこのしごと", ["かたづ"]),
        ("人たちは、みんなでルール", ["ちいき"]),
        ("コンサートは", ["チケット", "チヶット"]),
        ("のないこと", ["興味"]),
        ("よるよりひる", ["季節", "キせつ"]),
        ("結婚して", ["別々"]),
        ("仕事の 話", ["伺"]),
        ("勝", ["競争"]),
        ("今までやってきた", ["アルバイト"]),
        ("男の子はじぶん", ["ぼく", "ほく"]),
        ("花びん", ["かざって", "わって"]),
        ("母が したので", ["たいいん"]),
        ("まだ一かいも", ["かいがい"]),
        ("ゲームに", ["かったら"]),
        ("手で", ["さわって"]),
        ("インターネット", ["調べる"]),
        ("答え", ["正しい"]),
        ("日本の学校", ["中学校"]),
        ("自分で持って", ["大事"]),
        ("料理が", ["得意"]),
        ("育て", ["ほめて"]),
        ("けっこんしきに", ["あっまった", "あつまった"]),
        ("じゅぎょう", ["ふくしゅう", "おくしゅう"]),
        ("休みの間", ["ふくしゅう", "おくしゅう"]),
        ("今年高校に", ["にゅうがく", "入学"]),
        ("行かないほう", ["きけん"]),
        ("じしょ", ["ひいて"]),
        ("せいせき", ["せいせき"]),
        ("スポーツ大会", ["せいせき"]),
        ("上手ですね", ["ほめた"]),
        ("きようと", ["たとえば"]),
        ("ふた", ["かたくて"]),
        ("パスポート", ["落として"]),
        ("落し物を", ["拾ったら"]),
        ("携帯電話", ["見つかった"]),
        ("駅で一番多い", ["忘れ物"]),
        ("仕事で", ["失敗"]),
        ("がいたい", ["のど"]),
        ("せいかつに", ["ひつよう"]),
        ("へやの中があつい", ["れいぼう"]),
        ("人の もの", ["ぬすんで"]),
        ("プレゼント", ["つつんで"]),
        ("木にのぼったら", ["おれて"]),
        ("声が", ["聞こえる"]),
        ("シャワー", ["気持ちいい"]),
        ("運動したあと", ["気持ち"]),
        ("北と東", ["北東"]),
        ("夢を", ["こわい"]),
        ("雨に", ["ぬれて"]),
        ("コップが落ちて", ["割れて"]),
        ("まど", ["ガラス"]),
        ("梅雨", ["つゆ"]),
        ("雨の 日", ["つゆ"]),
        ("ドアのカギ", ["かけなさい"]),
        ("ねこがにわ", ["きもちよく"]),
        ("北東にむかう", ["南西"]),
        ("きゅうきゅうしゃ", ["聞こえました"]),
        ("道が", ["すべり"]),
        ("今から行けば", ["十分"]),
        ("散歩を", ["続けている"]),
        ("運転するのが", ["趣味"]),
        ("深い", ["深い"]),
        ("泳ぐ", ["深い"]),
        ("弱い人", ["いじめる"]),
        ("自分の意見", ["伝えない"]),
        ("やくそく", ["すっかり"]),
        ("ころんで", ["はずかし"]),
        ("しごとがおわります", ["たいてい"]),
        ("思い出せない", ["おもいだせない"]),
        ("買わなくてはいけない", ["おもいだせない"]),
        ("れんらくをくれるように", ["つたえて"]),
        ("おなか", ["すきました"]),
        ("父は", ["たまに"]),
        ("しごとがまだ", ["のこって"]),
        ("てんらん会", ["あんない"]),
        ("パソコン", ["きょうみ"]),
        ("せんもんの学校", ["きょう"]),
        ("テレビ", ["こわれて"]),
        ("見られません", ["こわれて"]),
        ("えいがを見て", ["すごく"]),
        ("しけんを", ["うけよう"]),
        ("うんどう会", ["おこないます"]),
        ("娘を", ["連れて"]),
        ("あかちゃん", ["きまりました", "決まりました"]),
        ("けっこんしきに する", ["しゅっせき"]),
        ("子どもを に行き", ["むかえ"]),
        ("ス一パーで", ["さっき"]),
        ("もっを", ["はこ"]),
        ("ちがうばしょ", ["ひっこ"]),
        ("ちがうばしょ", ["うつる"]),
        ("新しいいえ", ["たてて"]),
        ("まわりの人", ["めいわく"]),
        ("じこに気を", ["運転"]),
        ("じこに気", ["うんてん"]),
        ("げんきがない", ["とくに"]),
        ("やさしくなった", ["ずいぶん"]),
        ("やさしくなった", ["だいぶ"]),
        ("電話ばんごうを", ["しらべた"]),
        ("食べものはよく", ["かんで"]),
        ("コーヒーを", ["しゅうかん"]),
        ("コーヒーを", ["しゆうかん"]),
    ]
    for clue, answers in clues:
        if clue in joined or clue in joined_compact:
            for answer in answers:
                for option_id, text in option_texts.items():
                    if answer in text:
                        return option_id

    # If the prompt itself contains a term repeated in an option, that option is usually the target.
    for option in options:
        if option["text"] and option["text"] in joined:
            return option["id"]
    return options[0]["id"]


def parse_exercise_questions(lines: list[str], exercise_id: str) -> list[dict]:
    questions = []
    pending_prompt: list[str] = []

    for raw_line in lines:
        line = clean_exercise_line(raw_line)
        if not line:
            continue

        inline = parse_inline_ab_options(line)
        if inline:
            prompt_text, options = inline
            prompt = clean_prompt_lines([*pending_prompt, prompt_text])
            answer_id = infer_answer_id(prompt, options)
            questions.append(
                {
                    "id": f"{exercise_id}-q{len(questions) + 1}",
                    "prompt": prompt,
                    "options": options,
                    "answerId": answer_id,
                    "answerSource": "suggested",
                }
            )
            pending_prompt = []
            continue

        options = parse_numbered_options(line)
        if options:
            prompt = clean_prompt_lines(pending_prompt)
            answer_id = infer_answer_id(prompt, options)
            questions.append(
                {
                    "id": f"{exercise_id}-q{len(questions) + 1}",
                    "prompt": prompt,
                    "options": options,
                    "answerId": answer_id,
                    "answerSource": "suggested",
                }
            )
            pending_prompt = []
            continue

        if not is_probable_furigana_line(line) and not looks_like_ocr_ruby_noise(line):
            pending_prompt.append(line)

    # Remove accidental instruction-only questions.
    filtered = []
    for question in questions:
        question = normalize_question(question)
        if len(question["options"]) < 2:
            continue
        question["answerId"] = infer_answer_id(question["prompt"], question["options"])
        override = CURATED_QUESTION_OVERRIDES.get(question["id"])
        if override and "answerId" in override:
            question["answerId"] = override["answerId"]
        if all(is_exercise_instruction(line) for line in question["prompt"]):
            continue
        if not is_usable_question(question):
            continue
        filtered.append(question)
    return filtered


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
    exercise_id = f"{chapter}-exercise-p{page}"
    return {
        "id": exercise_id,
        "chapterId": chapter,
        "title": title,
        "page": page,
        "lines": [clean_exercise_line(line) for line in merged],
        "questions": parse_exercise_questions(merged, exercise_id),
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
        cleaned_cards = []
        seen_terms = set()
        for card in chapter["cards"]:
            cleaned = clean_card(card)
            if not cleaned or cleaned["term"] in seen_terms:
                continue
            seen_terms.add(cleaned["term"])
            cleaned_cards.append(cleaned)
        chapter["cards"] = cleaned_cards

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
