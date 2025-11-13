#!/usr/bin/env python3
"""Focused extractor for onepage.pdf to validate parsing strategy."""

import csv
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pdfplumber

ARABIC_DIGIT_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

GLYPH_MAP: Dict[str, str] = {
    "د": "د",
    "و": "و",
    "ح": "ح",
    "ر": "ر",
    "س": "س",
    "ش": "ش",
    "ص": "ص",
    "ط": "ط",
    "ع": "ع",
    "غ": "غ",
    "ق": "ق",
    "ك": "ك",
    "ل": "ل",
    "م": "م",
    "ن": "ن",
    "ه": "ه",
    "ي": "ي",
    "ى": "ى",
    "ت": "ت",
    "ب": "ب",
    "ج": "ج",
    "ف": "ف",
    "ذ": "ذ",
    "ز": "ز",
    "ة": "ة",
    "ء": "ء",
    "|": "ا",
    "I": "ا",
    "1": "ا",
}

# Mapping extracted glyph sequences to readable Arabic letters
GLYPH_MAP: Dict[str, str] = {
    "د": "د",
    "و": "و",
    "ح": "ح",
    "ر": "ر",
    "س": "س",
    "ش": "ش",
    "ص": "ص",
    "ط": "ط",
    "ع": "ع",
    "غ": "غ",
    "ق": "ق",
    "ك": "ك",
    "ل": "ل",
    "م": "م",
    "ن": "ن",
    "ه": "ه",
    "ي": "ي",
    "ى": "ى",
    "ت": "ت",
    "ب": "ب",
    "ج": "ج",
    "ف": "ف",
    "ذ": "ذ",
    "ز": "ز",
    "ة": "ة",
    "ء": "ء",
    "|": "ا",
    "I": "ا",
    "1": "ا",
}


@dataclass
class VoterRow:
    voter_number: int
    full_name: str
    page_number: int
    location_number: int


def normalize_text(text: str) -> str:
    """Remove null chars and trim whitespace."""
    return text.replace("\u0000", "").strip()


def normalize_arabic_glyphs(text: str) -> str:
    cleaned = []
    for ch in text:
        if ch in GLYPH_MAP:
            cleaned.append(GLYPH_MAP[ch])
        elif "\u0600" <= ch <= "\u06FF":
            cleaned.append(ch)
        elif ch.strip():
            cleaned.append(ch)
    return "".join(cleaned)


def normalize_arabic_glyphs(text: str) -> str:
    """Convert custom glyph output into standard Arabic characters."""
    cleaned_chars: List[str] = []
    for ch in text:
        if ch in GLYPH_MAP:
            cleaned_chars.append(GLYPH_MAP[ch])
        elif "\u0600" <= ch <= "\u06FF":
            cleaned_chars.append(ch)
        elif ch.strip():
            cleaned_chars.append(ch)
    return "".join(cleaned_chars)


def arabic_to_int(value: str) -> int:
    """Convert a string containing Arabic digits to int."""
    value = normalize_text(value)
    if not value:
        raise ValueError("Empty numeric string")
    return int(value.translate(ARABIC_DIGIT_MAP))


def extract_footer_numbers(page: pdfplumber.page.Page) -> Tuple[int, int]:
    """Return (page_number, location_number) from footer region."""
    height = page.height
    footer = page.within_bbox((0, height - 120, page.width, height))
    footer_text = footer.extract_text() or ""
    footer_text = normalize_text(footer_text.replace("\n", " "))
    # Capture all digit clusters (Arabic or Western)
    numbers = [n.translate(ARABIC_DIGIT_MAP) for n in re.findall(r"[0-9٠-٩]{1,4}", footer_text)]
    # Expect something like [..., '1021', '25', '76'] or similar order.
    # Identify page number as longest <=3 digits closest to top-right (use heuristics)
    # We'll inspect the footer words with coordinates for precise mapping.
    footer_words = footer.extract_words(use_text_flow=True, horizontal_ltr=False) or []
    extracted = []
    for word in footer_words:
        text = normalize_text(word.get("text", ""))
        if not text:
            continue
        candidate = text.translate(ARABIC_DIGIT_MAP)
        if candidate.isdigit():
            extracted.append((candidate, word["x0"], word["top"]))
    # Sort by top descending (footer lines from bottom up) and x0 descending (RTL)
    extracted.sort(key=lambda item: (item[2], item[1]))
    page_number = None
    location_number = None
    for idx, (candidate, x0, top) in enumerate(extracted):
        if len(candidate) <= 3 and page_number is None:
            page_number = int(candidate)
            continue
        if len(candidate) <= 3 and location_number is None:
            location_number = int(candidate)
            continue
    if page_number is None or location_number is None:
        # Fallback: use text regex order
        digits = [int(n) for n in numbers if n]
        if len(digits) >= 2:
            page_number = digits[-2] if page_number is None else page_number
            location_number = digits[-1] if location_number is None else location_number
    if page_number is None or location_number is None:
        raise ValueError(f"Unable to determine footer numbers. Text: {footer_text}")
    return page_number, location_number


def group_words_by_row(words: List[Dict], tolerance: float = 2.5) -> List[List[Dict]]:
    buckets: Dict[float, List[Dict]] = defaultdict(list)
    for word in words:
        text = normalize_text(word.get("text", ""))
        if not text:
            continue
        top = word.get("top")
        if top is None:
            continue
        key = round(top / tolerance) * tolerance
        buckets[key].append(word)
    # Sort rows by top coordinate ascending (top of page first)
    sorted_rows = sorted(buckets.items(), key=lambda item: item[0])
    return [sorted(row_words, key=lambda w: w["x0"], reverse=True) for _, row_words in sorted_rows]


def parse_rows(words: List[Dict], page_number: int, location_number: int) -> List[VoterRow]:
    rows: List[VoterRow] = []
    for row_words in group_words_by_row(words):
        ordered = sorted(row_words, key=lambda w: w["x0"], reverse=True)
        name_tokens: List[str] = []

        for word in ordered:
            raw_text = word.get("text", "")
            text = normalize_text(raw_text)
            if not text:
                continue

            translated = text.translate(ARABIC_DIGIT_MAP)
            is_number = translated.isdigit() and 1 <= len(translated) <= 4

            if is_number:
                if not name_tokens:
                    continue
                full_name = normalize_arabic_glyphs(" ".join(name_tokens)).strip()
                if not full_name:
                    name_tokens.clear()
                    continue
                rows.append(
                    VoterRow(
                        voter_number=int(translated),
                        full_name=full_name,
                        page_number=page_number,
                        location_number=location_number,
                    )
                )
                name_tokens.clear()
            else:
                name_tokens.append(normalize_arabic_glyphs(text))

    return rows


def extract_onepage(pdf_path: str = "onepage.pdf", output_csv: str = "output/onepage_voters.csv", output_json: str = "output/onepage_voters.json") -> Dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        footer_page_number, footer_location_number = extract_footer_numbers(page)
        words = page.extract_words(
            x_tolerance=1.5,
            y_tolerance=2.0,
            use_text_flow=True,
            keep_blank_chars=False,
            horizontal_ltr=False
        )
        voters = parse_rows(words, footer_page_number, footer_location_number)
    # Write CSV
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["voter_number", "full_name", "page_number", "location_number"])
        for voter in voters:
            writer.writerow([voter.voter_number, voter.full_name, voter.page_number, voter.location_number])
    # Write JSON for debugging
    with open(output_json, "w", encoding="utf-8") as jsonfile:
        json.dump([voter.__dict__ for voter in voters], jsonfile, ensure_ascii=False, indent=2)
    return {
        "status": "success",
        "records": len(voters),
        "csv": output_csv,
        "json": output_json,
        "page_number": footer_page_number,
        "location_number": footer_location_number
    }


def main() -> None:
    result = extract_onepage()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
