# app/parser.py
import re

class BusinessCardParser:
    def parse(self, text):
        # Split teks menjadi baris-baris bersih
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 1]
        if len(lines) <= 1:
            lines = [line.strip() for line in re.split(r'\s{2,}', text) if len(line.strip()) > 1]

        email = "Unknown"
        phone = "Unknown"
        company = "Unknown"
        name = "Unknown"
        domain_keyword = ""

        # 1. EKSTRAKSI EMAIL & PHONE (Murni Regex Generik)
        for line in lines:
            line_clean = line.replace(" ", "")
            
            # Cari Email & Ekstrak Keyword Domain Perusahaan secara Otomatis
            if '@' in line:
                email_match = re.search(r'([\w\.-]+)@([\w\.-]+)\.([a-zA-Z]{2,})', line)
                if email_match:
                    email = email_match.group(0).strip()
                    domain_keyword = email_match.group(2).split('.')[0].lower() # Ambil nama perusahaan dari domain email
            elif '.com' in line_clean.lower() and email == "Unknown":
                alt_email = re.search(r'([a-zA-Z0-9_\.-]+)\s*[.\s@]\s*([a-zA-Z0-9_\.-]+\.(?:com|net|org|id))', line, re.IGNORECASE)
                if alt_email:
                    email = f"{alt_email.group(1)}@{alt_email.group(2)}".replace(" ", "")
                    domain_keyword = alt_email.group(2).split('.')[0].lower()

            # Cari Nomor Telepon (Asal ada pola angka berderet panjang)
            if any(c.isdigit() for c in line) and phone == "Unknown":
                phone_match = re.search(r'\+?\d[\d\s-]{7,15}\d', line)
                if phone_match:
                    phone = phone_match.group(0).strip()

        # Ekstraksi alternatif domain jika ada baris website www.
        if not domain_keyword:
            web_match = re.search(r'www\.([a-zA-Z0-9_-]+)\.', text, re.IGNORECASE)
            if web_match:
                domain_keyword = web_match.group(1).lower()

        # 2. FILTERING & SCORING DINAMIS (TANPA KATA KUNCI TERTULIS)
        name_candidates = []
        company_candidates = []

        for line in lines:
            line_lower = line.lower()
            
            # Lewati baris kontak murni
            if line == phone or line == email or '@' in line or 'www.' in line_lower:
                continue
                
            # Lewati baris sampah sisa monitor
            if any(w in line_lower for w in ['pm', 'am', '13/', '2026', 'start', 'search']):
                continue

            # DETEKSI DINAMIS BARIS ALAMAT: Mengandung kode pos (5 angka) atau nomor bangunan/RT/RW
            is_address = bool(re.search(r'\b\d{5}\b', line) or re.search(r'(?:no|blok|rt|rw|kav|floor|lt)\.?\s*\d+', line, re.IGNORECASE))

            # --- SKORING NAMA MANUSIA ---
            name_score = 100
            if is_address: name_score -= 90
            if domain_keyword and domain_keyword in line_lower: name_score -= 40 # Nama orang jarang sama persis dengan domain PT
            if line.isupper(): name_score += 30 # Nama orang hampir selalu UPPERCASE di kartu nama
            
            # Nama orang biasanya terdiri dari 2-3 kata, jarang sekali hanya 1 kata atau lebih dari 4 kata
            words = line.split()
            if 2 <= len(words) <= 3:
                name_score += 20
            else:
                name_score -= 30

            # Jika baris tersebut berada di bawah persis baris bertipe UPPERCASE, kemungkinan itu Jabatan (bukan nama)
            name_candidates.append((line, name_score))

            # --- SKORING PERUSAHAAN (COMPANY) ---
            company_score = 50
            if domain_keyword and domain_keyword in line_lower: 
                company_score += 100 # KUNCI UTAMA: Jika teks mengandung nama domain email/web, itu pasti Perusahaan!
            if is_address: 
                company_score -= 50
            if line.isupper(): 
                company_score += 15

            company_candidates.append((line, company_score))

        # 3. EVALUASI PEMENANG SKOR TERTINGGI
        if name_candidates:
            name_candidates.sort(key=lambda x: x[1], reverse=True)
            # Jika skor tertinggi diduduki oleh baris yang bukan UPPERCASE padahal ada pilihan UPPERCASE, prioritaskan UPPERCASE
            name = name_candidates[0][0]

        if company_candidates:
            company_candidates.sort(key=lambda x: x[1], reverse=True)
            # Pastikan nama perusahaan tidak tumpang tindih mengambil nama orang
            if company_candidates[0][0] == name and len(company_candidates) > 1:
                company = company_candidates[1][0]
            else:
                company = company_candidates[0][0]

        # Skenario darurat jika nama perusahaan masih Unknown, gunakan domain_keyword sebagai dasar penamaan
        if company == "Unknown" and domain_keyword:
            company = domain_keyword.upper()

        return {
            "name": name,
            "company": company,
            "email": email,
            "phone": phone
        }