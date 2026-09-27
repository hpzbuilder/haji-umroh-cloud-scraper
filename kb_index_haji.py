#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb_index_haji.py — Indeks Pencarian FTS5 Mandiri Domain Haji & Umrah
Mengindeks regulasi Kemenag, fiqih/tesis UIN, dan berita LKBN Antara 5 tahun.
Database: knowledge_base/haji_umroh_indeks.db
"""

import os
import sys
import re
import sqlite3
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "knowledge_base"
HAJI_DIR = KB_DIR / "Haji_Umroh"
INDEX_DB = KB_DIR / "haji_umroh_indeks.db"

def init_index_db():
    KB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(INDEX_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS haji_fts USING fts5(
            id,
            judul,
            kategori,
            sumber,
            tahun,
            isi,
            path UNINDEXED,
            tokenize = 'unicode61 remove_diacritics 2'
        );
    """)
    conn.commit()
    conn.close()

def parse_frontmatter(content: str):
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body

def build_index():
    print(f"\n{'='*65}")
    print("▶ MEMBANGUN INDEKS FTS5 MANDIRI — HAJI & UMRAH")
    print(f"  Target Direktori : {HAJI_DIR}")
    print(f"  Database Indeks  : {INDEX_DB.name}")
    print(f"{'='*65}")

    if not HAJI_DIR.exists():
        print(f"✘ Direktori {HAJI_DIR} belum ada.")
        return 0

    init_index_db()
    conn = sqlite3.connect(INDEX_DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM haji_fts;")

    total = 0
    for root, _, files in os.walk(HAJI_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            fp = Path(root) / f
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
                meta, body = parse_frontmatter(text)

                doc_id = meta.get("id") or fp.stem
                judul = meta.get("judul") or fp.stem.replace("_", " ")
                kategori = meta.get("kategori") or fp.parent.name
                sumber = meta.get("sumber") or "Arsip Haji"
                tahun = meta.get("tahun") or ""
                rel_path = str(fp.relative_to(BASE_DIR)).replace("\\", "/")

                cur.execute("""
                    INSERT INTO haji_fts (id, judul, kategori, sumber, tahun, isi, path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (doc_id, judul, kategori, sumber, str(tahun), body, rel_path))
                total += 1
            except Exception as e:
                print(f"  ⚠ Gagal mengindeks {f}: {e}")

    conn.commit()
    conn.close()

    print(f"✔ Selesai! Sebanyak {total} berkas Haji & Umrah berhasil diindeks.")
    return total

def cari_dokumen(query: str, limit: int = 10):
    if not INDEX_DB.exists():
        print("✘ Indeks belum dibangun. Jalankan dengan opsi --build terlebih dahulu.")
        return

    conn = sqlite3.connect(INDEX_DB)
    cur = conn.cursor()

    safe_query = re.sub(r'[^\w\s]', ' ', query).strip()
    words = [w for w in safe_query.split() if len(w) > 1]
    if not words:
        print("Query kosong atau tidak valid.")
        return

    fts_query = " AND ".join(f'"{w}"' for w in words)

    try:
        cur.execute("""
            SELECT id, judul, kategori, sumber, tahun, snippet(haji_fts, 5, '<b>', '</b>', '...', 25), path, rank
            FROM haji_fts
            WHERE haji_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit))
        rows = cur.fetchall()

        print(f"\n{'='*65}")
        print(f"🔍 HASIL PENCARIAN HAJI & UMRAH: '{query}' ({len(rows)} ditemukan)")
        print(f"{'='*65}")
        for i, (doc_id, judul, kat, sumber, th, snip, path, rank) in enumerate(rows, 1):
            snip_clean = snip.replace("\n", " ").strip()
            print(f"{i}. [{kat} | {th}] {judul}")
            print(f"   Sumber: {sumber} | Path: {path}")
            print(f"   Kutipan: {snip_clean}\n")
    except Exception as e:
        print(f"✘ Kesalahan pencarian: {e}")
    finally:
        conn.close()

def stats():
    if not INDEX_DB.exists():
        print("Database indeks belum ada.")
        return
    conn = sqlite3.connect(INDEX_DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM haji_fts")
    total = cur.fetchone()[0]
    cur.execute("SELECT kategori, COUNT(*) FROM haji_fts GROUP BY kategori ORDER BY COUNT(*) DESC")
    by_kat = cur.fetchall()
    conn.close()

    print(f"\n{'='*65}")
    print("📊 STATISTIK INDEKS PENCARIAN HAJI & UMRAH")
    print(f"{'='*65}")
    print(f"Total Dokumen Terindeks: {total}")
    for kat, cnt in by_kat:
        print(f"  - {kat}: {cnt} dokumen")
    print(f"{'='*65}")

def main():
    parser = argparse.ArgumentParser(description="Indeks Pencarian FTS5 Domain Haji & Umrah")
    parser.add_argument("--build", action="store_true", help="Bangun ulang seluruh indeks FTS5")
    parser.add_argument("--cari", type=str, help="Kata kunci pencarian")
    parser.add_argument("--stats", action="store_true", help="Lihat statistik indeks")
    parser.add_argument("--limit", type=int, default=10, help="Batas hasil pencarian")
    args = parser.parse_args()

    if args.build:
        build_index()
    elif args.cari:
        cari_dokumen(args.cari, limit=args.limit)
    elif args.stats:
        stats()
    else:
        stats()

if __name__ == "__main__":
    main()
