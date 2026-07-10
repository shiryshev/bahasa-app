#!/usr/bin/env python3
"""
Генератор данных приложения из базы-источника (страница Notion «Bahasa Dictionary»).
Вход:  notion_dump.txt — строки из раздела «## Записи».
Выход: base.js (данные приложения + полный бэкап), notion_normalized.txt (строки с #id).
Формат строки: - #id · **indonesian** · pronunciation · russian   (#id можно опустить у новых записей)
ID монотонны: скрипт помнит наибольший выданный номер (LALA_NEXT_ID в прошлом base.js);
после удаления номер НЕ переиспользуется.
"""
import re, json, sys, datetime
SRC = sys.argv[1] if len(sys.argv) > 1 else "notion_dump.txt"
OUT = "base.js"

def parse(md):
    recs = []
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("- "): continue
        parts = s[2:].split(" · ")
        rid = None
        if parts and parts[0].strip().startswith("#"):
            rid = int(parts[0].strip().lstrip("#")); parts = parts[1:]
        if len(parts) < 3: continue
        indo, pron, ru = parts[0], parts[1], " · ".join(parts[2:])
        recs.append({"id": rid, "id_text": indo.strip().strip("*"),
                     "pron": pron.strip(), "ru": ru.strip()})
    return recs

def prev_next(path):
    try:
        m = re.search(r"LALA_NEXT_ID\s*=\s*(\d+)", open(path, encoding="utf-8").read())
        return int(m.group(1)) if m else 0
    except FileNotFoundError:
        return 0

recs = parse(open(SRC, encoding="utf-8").read())
next_id = max(prev_next(OUT), (max([r["id"] for r in recs if r["id"] is not None] or [-1]) + 1))
assigned = 0
for r in recs:
    if r["id"] is None: r["id"] = next_id; next_id += 1; assigned += 1
recs.sort(key=lambda r: r["id"])
maxid = max(r["id"] for r in recs)
today = datetime.date.today().isoformat()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("// Lala Bahasa — данные приложения и полный бэкап словаря.\n")
    f.write("// ИСТОЧНИК ИСТИНЫ — страница Notion «Bahasa Dictionary». Файл ГЕНЕРИРУЕТСЯ, руками не править.\n")
    f.write("window.LALA_BASE = " + json.dumps(recs, ensure_ascii=False, indent=0) + ";\n")
    f.write("window.LALA_BASE_DATE = " + json.dumps(today) + ";\n")
    f.write("window.LALA_BASE_MAXID = " + str(maxid) + ";\n")
    f.write("window.LALA_NEXT_ID = " + str(next_id) + ";  // самый большой выданный + 1; только растёт\n")

with open("notion_normalized.txt", "w", encoding="utf-8") as f:
    for r in recs:
        f.write(f"- #{r['id']} · **{r['id_text']}** · {r['pron']} · {r['ru']}\n")
print(f"записей: {len(recs)} | max id: {maxid} | назначено: {assigned} | LALA_NEXT_ID: {next_id}")
