# -*- coding: utf-8 -*-
"""Validate data/questions/*.json against the schema and data/curriculum.json.

Usage: python tools/check_questions.py
Exit code 0 = all good ("0 errors"); nonzero = fix before committing.

Rules enforced (see CLAUDE.md "Soru bankasi"):
- required fields: id, topic, difficulty, q, options, answer, explanation
- id format <PREFIX>-<NNNN>, unique, prefix matches the subject file
- exactly 4 options, answer in A-D, difficulty in 1-3
- topic id must exist in curriculum.json for that subject
- no duplicate question text (normalized exact match) within a subject
- optional fields allowed: passage, image
"""
import json
import os
import re
import sys
import unicodedata

# Windows konsolu cp1252 olabilir; Turkce mesajlar icin UTF-8'e zorla
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBJECT_PREFIX = {"matematik": "MAT", "fen": "FEN", "sosyal": "SOS", "turkce": "TUR"}
REQUIRED = ["id", "topic", "difficulty", "q", "options", "answer", "explanation"]
OPTIONAL = ["passage", "image"]


def norm_text(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"\s+", " ", s).strip()


def load_curriculum():
    path = os.path.join(ROOT, "data", "curriculum.json")
    with open(path, encoding="utf-8") as f:
        cur = json.load(f)
    topics = {}  # subject id -> {topic id: topic name}
    for subj in cur["subjects"]:
        t = {}
        for unit in subj["units"]:
            for topic in unit["topics"]:
                t[topic["id"]] = topic["name"]
        topics[subj["id"]] = t
    return topics


def check_subject(subject, topics, errors):
    path = os.path.join(ROOT, "data", "questions", subject + ".json")
    if not os.path.exists(path):
        errors.append(f"{subject}: dosya yok ({path})")
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("subject") != subject:
        errors.append(f"{subject}: 'subject' alani '{data.get('subject')}' olmamali")
    prefix = SUBJECT_PREFIX[subject]
    id_re = re.compile(r"^" + prefix + r"-(\d{4})$")
    seen_ids, seen_texts = set(), {}
    counts = {}  # topic -> count
    for i, q in enumerate(data.get("questions", [])):
        where = f"{subject}[{i}] {q.get('id', '?')}"
        for field in REQUIRED:
            if field not in q:
                errors.append(f"{where}: eksik alan '{field}'")
        unknown = set(q) - set(REQUIRED) - set(OPTIONAL)
        if unknown:
            errors.append(f"{where}: bilinmeyen alan(lar) {sorted(unknown)}")
        qid = q.get("id", "")
        m = id_re.match(qid)
        if not m:
            errors.append(f"{where}: id formati '{prefix}-NNNN' olmali")
        if qid in seen_ids:
            errors.append(f"{where}: id tekrarli")
        seen_ids.add(qid)
        topic = q.get("topic")
        if topic not in topics.get(subject, {}):
            errors.append(f"{where}: topic '{topic}' curriculum.json'da yok")
        else:
            counts[topic] = counts.get(topic, 0) + 1
        if q.get("difficulty") not in (1, 2, 3):
            errors.append(f"{where}: difficulty 1-3 olmali")
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4:
            errors.append(f"{where}: options tam 4 ogeli liste olmali")
        # NOT: buyuk/kucuk harf YAZIM sorulari ayni metnin farkli harfli
        # hallerini secenek yapar; bu yuzden karsilastirma case-sensitive.
        elif len({re.sub(r"\s+", " ", o).strip() for o in opts}) != 4:
            errors.append(f"{where}: secenekler birbirinden farkli olmali")
        if q.get("answer") not in ("A", "B", "C", "D"):
            errors.append(f"{where}: answer A-D olmali")
        text = norm_text(q.get("q", "")) + "||" + norm_text(q.get("passage", ""))
        if text in seen_texts:
            errors.append(f"{where}: soru metni {seen_texts[text]} ile ayni")
        else:
            seen_texts[text] = qid
        if not q.get("explanation", "").strip():
            errors.append(f"{where}: explanation bos olmamali")
    return counts


def main():
    topics = load_curriculum()
    errors = []
    print("Konu basina soru sayilari:")
    for subject in SUBJECT_PREFIX:
        counts = check_subject(subject, topics, errors)
        total = sum(counts.values())
        print(f"\n[{subject}] toplam {total} soru")
        for tid, tname in topics[subject].items():
            n = counts.get(tid, 0)
            flag = "" if n >= 10 else "  << 10'dan az"
            print(f"  {n:3d}  {tid}{flag}")
    print()
    for e in errors:
        print("HATA:", e)
    print(f"DONE, {len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
