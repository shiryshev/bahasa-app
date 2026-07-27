#!/usr/bin/env python3
"""
Синхронизация рабочей копии словаря приложения с источником Obsidian.

Источник (ТОЛЬКО ЧТЕНИЕ): dictionary.md в Obsidian — его пополняет навык-переводчик.
Копия (правится мной): app-dictionary.md в репозитории — из неё генерируется base.js.

Логика: копия = все записи источника, КРОМЕ id из раздела «## Удалено» (надгробия).
Так новые слова подтягиваются автоматически, а удалённые из обучения НЕ возвращаются
при следующей синхронизации. Правки переводов в источнике тоже подхватываются.

Раздел «## Удалено» содержит строки вида «#id · indonesian» — они не начинаются с «- »,
поэтому build_base.py их игнорирует.
"""
import re, sys, datetime

SRC  = "/Users/shiryshev/Documents/Obsidian/Home/10-Wiki/Languages/Bahasa/dictionary.md"
COPY = "app-dictionary.md"

def record_lines(md):
    """Строки-записи «- #id · ...» из текста, в словарь id -> строка."""
    out = {}
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("- "): continue
        head = s[2:].split(" · ", 1)[0].strip()
        if not head.startswith("#"): continue
        try: rid = int(head.lstrip("#"))
        except ValueError: continue
        out[rid] = s
    return out

def read_tombstones(path):
    """id из раздела «## Удалено» (строки, начинающиеся с «#»)."""
    ids, texts = set(), {}
    try:
        txt = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return ids, texts
    m = re.search(r"##\s*Удалено.*?$(.*)$", txt, re.S | re.M)
    section = m.group(1) if m else ""
    for line in section.splitlines():
        s = line.strip()
        if not s.startswith("#"): continue
        head = s.split(" · ", 1)
        try: rid = int(head[0].lstrip("#").strip())
        except ValueError: continue
        ids.add(rid)
        texts[rid] = head[1].strip() if len(head) > 1 else ""
    return ids, texts

def main():
    src = record_lines(open(SRC, encoding="utf-8").read())
    tomb_ids, tomb_texts = read_tombstones(COPY)

    active_ids = sorted(i for i in src if i not in tomb_ids)
    added = [i for i in active_ids]  # для отчёта считаем позже относительно прошлой копии

    prev = record_lines(open(COPY, encoding="utf-8").read()) if _exists(COPY) else {}
    new_ids = [i for i in active_ids if i not in prev]

    today = datetime.date.today().isoformat()
    L = []
    L += ["# app-dictionary — рабочая копия словаря приложения", ""]
    L += ["> Генерируется скриптом `sync_dictionary.py` из источника Obsidian `dictionary.md` (только чтение).", ""]
    L += ["> `base.js` собирается из ЭТОГО файла. Удаления из обучения — через раздел «## Удалено» ниже.", ""]
    L += [f"Синхронизировано: {today} · активных записей: {len(active_ids)} · исключено: {len(tomb_ids)}", ""]
    L += ["## Записи", ""]
    L += [src[i] for i in active_ids]
    L += ["", "## Удалено", "",
          "<!-- id, исключённые из обучения; НЕ возвращаются при синхронизации. Формат: #id · indonesian -->"]
    for i in sorted(tomb_ids):
        L.append(f"#{i} · {tomb_texts.get(i,'')}".rstrip())
    open(COPY, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"источник: {len(src)} | активных: {len(active_ids)} | исключено: {len(tomb_ids)} | новых с прошлой синхр.: {len(new_ids)}")
    if new_ids:
        print("новые id:", ", ".join(map(str, new_ids)))

def _exists(p):
    import os; return os.path.exists(p)

if __name__ == "__main__":
    main()
