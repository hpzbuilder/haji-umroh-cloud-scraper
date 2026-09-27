# 🕋 Haji & Umrah Cloud Legal & News Scraper

Sistem pemanen data independen khusus domain **Haji dan Umrah** yang berjalan otomatis dan 100% gratis di GitHub Actions.

## Cakupan Data
1. **Regulasi Kemenag RI:** PMA, KMA, SE terkait haji, umrah, kuota, perizinan PPIU/PIHK, dan BPIH dari JDIH Kemenag.
2. **Karya Ilmiah & Fiqih:** Tesis, disertasi, dan riset fiqih haji dari OAI-PMH UIN Sunan Kalijaga.
3. **Arsip Berita & Informasi Resmi (5 Tahun: 2021–2026):** LKBN ANTARA News (Kantor Berita Negara) mencakup kebijakan Arab Saudi, visa Nusuk, pelunasan BPIH, BPKH, evaluasi penyelenggaraan, dan investigasi.

## Struktur Hasil
- Format: Dokumen Markdown ringan (`.md`) dengan frontmatter metadata lengkap.
- Database: SQLite `knowledge_base/haji_umroh.db`.
- Indeks: Full-Text Search FTS5 `knowledge_base/haji_umroh_indeks.db`.
- Ekspor: Rilis `.zip` otomatis siap unduh di tab GitHub Releases.
