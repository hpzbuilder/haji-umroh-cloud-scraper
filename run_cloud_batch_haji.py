#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_cloud_batch_haji.py — Orkestrator Cloud Khusus Haji & Umrah (GitHub Actions)
Menjalankan:
1. Regulasi Kemenag & Fiqih/Tesis UIN (scraper_haji_umroh.py)
2. Berita & Info Kredibel 5 Tahun LKBN ANTARA (scraper_berita_haji.py)
3. Pembangunan Indeks FTS5 Mandiri (kb_index_haji.py --build)
4. Pengarsipan ke Paket Zip Mandiri (haji_umroh_data_{ts}.zip)
"""

import sys
import os
import time
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

def run_step(cmd_args, label):
    print(f"\n{'='*65}")
    print(f"▶ MEMULAI: {label}")
    print(f"{'='*65}")
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable] + cmd_args, cwd=str(BASE_DIR), check=False)
        print(f"✔ SELESAI ({time.time()-t0:.1f}s) — Exit Code: {proc.returncode}")
        return proc.returncode == 0
    except Exception as e:
        print(f"✘ GAGAL: {e}")
        return False

def main():
    print("============================================================")
    print("   PORTAL HAJI & UMRAH — CLOUD AUTO-HARVEST RUNNER")
    print(f"   Waktu Mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("============================================================")

    # 1. Regulasi Resmi Kemenag & Karya Ilmiah UIN
    run_step(["scraper_haji_umroh.py"], 
             "Worker 1 — Regulasi Kemenag & Fiqih/Tesis Haji UIN")

    # 2. Berita & Informasi Kredibel LKBN ANTARA (2021-2026)
    run_step(["scraper_berita_haji.py", "--limit", "50"], 
             "Worker 2 — Berita & Info Kredibel Haji/Umrah (LKBN ANTARA)")

    # 3. Bangun Indeks FTS5 Mandiri
    run_step(["kb_index_haji.py", "--build"], 
             "Worker 3 — Rebuild FTS5 Index Khusus Haji & Umrah")

    # 4. Buat Paket Data Mandiri (.zip)
    print(f"\n{'='*65}")
    print("📦 MEMBUAT ARSIP PAKET DATA KHUSUS HAJI & UMRAH (.ZIP)")
    print(f"{'='*65}")
    
    kb_dir = BASE_DIR / "knowledge_base"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"haji_umroh_data_{ts}.zip"
    zip_path = BASE_DIR / zip_name

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        if kb_dir.exists():
            for root, _, files in os.walk(kb_dir):
                for file in files:
                    fp = Path(root) / file
                    if file.endswith(".part"):
                        continue
                    rel_path = fp.relative_to(BASE_DIR)
                    zf.write(fp, arcname=str(rel_path))
                    file_count += 1
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024) if zip_path.exists() else 0
    print(f"Arsip Berhasil Dibuat: {zip_path.name}")
    print(f"Total File Didalamnya : {file_count} berkas")
    print(f"Ukuran File Zip       : {zip_size_mb:.2f} MB")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"zip_name={zip_name}\n")
            f.write(f"zip_path={zip_path}\n")
            f.write(f"zip_size_mb={zip_size_mb:.2f}\n")
            f.write(f"file_count={file_count}\n")
            f.write(f"timestamp={ts}\n")

if __name__ == "__main__":
    main()
