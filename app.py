import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Sistem Rekrutmen Logistik",
    page_icon="📦",
    layout="centered"
)

# Password Rahasia untuk Akses Panel HRD
HRD_PASSWORD = "adminlogistik"  # Silakan ubah password sesuai kebutuhan Anda

# Data Bank Soal Lengkap
BANK_LOGIKA = [
    {"s": "1. Kecepatan rata-rata truk kontainer X adalah 50 km/jam, berangkat pukul 07.00. Truk Y memiliki kecepatan rata-rata 70 km/jam dan berangkat melewati rute yang persis sama pukul 08.30. Pukul berapa Truk Y tepat menyusul Truk X?", "o": ["Pukul 11.45", "Pukul 12.15", "Pukul 12.30"], "k": "B"},
    {"s": "2. Suatu area Cross-docking memiliki sirkulasi harian barang masuk 4.500 koli. Jika efisiensi pemrosesan drop 15% akibat kerusakan conveyor belt, dan tumpukan backlog tersisa 800 koli dari hari kemarin, berapakah total beban barang yang berhasil diproses secara sistem depo hari ini?", "o": ["4.625 koli", "3.825 koli", "4.425 koli"], "k": "A"},
    {"s": "3. Semua armada berpendingin (Cold Chain Fleet) wajib melakukan kalibrasi termostat tiap 3 bulan. Sebagian armada di Depo Surabaya bukan merupakan armada berpendingin. Kesimpulan:", "o": ["Sebagian armada di Depo Surabaya tidak wajib melakukan kalibrasi termostat tiap 3 bulan", "Semua armada di Depo Surabaya wajib kalibrasi termostat tiap 3 bulan", "Armada yang bukan berpendingin di Depo Surabaya wajib kalibrasi tiap 6 bulan"], "k": "A"},
    {"s": "4. Gudang penyimpanan material e-commerce memiliki dimensi efektif 40m x 20m x 5m. Ukuran standar satu palet beserta ruang amannya adalah 2m x 1m x 1.25m. Berapa kapasitas maksimum daya tampung palet (secara volume dan ruang spasial vertikal struktural jika ditumpuk penuh tanpa menyalahi clearance)?", "o": ["1.600 Palet", "1.333 Palet", "800 Palet"], "k": "A"},
    {"s": "5. Perusahaan mencatat rata-rata tingkat kegagalan pengiriman (failed delivery) kurir motor sebesar 4% dari total 25.000 resi bulanan. Tim HRD menuntut efisiensi perbaikan kerja agar maksimal paket gagal hanya boleh 650 resi. Berapa persen penurunan kegagalan yang wajib dicapai?", "o": ["Menurunkan angka kegagalan sebesar 35%", "Menurunkan angka kegagalan sebesar 40%", "Menurunkan angka kegagalan sebesar 25%"], "k": "A"},
    {"s": "6. Pola Deret Pengiriman Unit: 14, 19, 29, 44, 64, ... Berapakah kuantitas unit berikutnya yang mengisi pola deret reguler tersebut?", "o": ["84", "89", "94"], "k": "B"},
    {"s": "7. Jika 12 operator inbound pergudangan mampu melakukan unloading dan scanning data 3.600 item dalam waktu 3 jam, berapa lamakah waktu yang dibutuhkan oleh 9 operator untuk menyelesaikan item dengan volume yang sama?", "o": ["4 Jam", "4 Jam 30 Menit", "5 Jam"], "k": "A"},
    {"s": "8. Truk kontainer 40ft bermuatan penuh besi baja memiliki tonase muatan lebih berat dari Truk 20ft bermuatan tekstil. Truk C memiliki muatan lebih ringan dari Truk 20ft tekstil. Truk D lebih berat dari Truk 40ft besi baja. Mana urutan unit dari tonase paling BERAT ke paling RINGAN?", "o": ["D - Truk 40ft - Truk 20ft - Truk C", "Truk D - Truk C - Truk 40ft - Truk 20ft", "Truk 40ft - D - Truk 20ft - Truk C"], "k": "A"},
    {"s": "9. Sebuah Depo ban kendaraan logistik mendapati data internal: Ban merk P lebih awet dari ban merk Q. Ban merk R tidak lebih awet dari merk Q. Ban merk S jauh lebih awet dari merk P. Ban manakah yang memiliki ketahanan pemakaian paling rendah?", "o": ["Merk P", "Merk Q", "Merk R"], "k": "C"},
    {"s": "10. Pengiriman pasokan logistik bantuan harus melintasi kota K, L, M, N, O. Kota K harus dicapai sebelum L. Kota M dicapai tepat setelah K. Kota O adalah destinasi akhir. Jalur rute manakah yang memenuhi prasyarat operasional di atas?", "o": ["K - L - M - N - O", "K - M - L - N - O", "M - K - L - N - O"], "k": "B"},
    {"s": "11. Umur ekonomis Truk Tronton A adalah dua kali lipat umur Engkel B. Umur Engkel B ditambah 3 tahun sama dengan umur CDD C. Jika umur CDD C saat ini adalah 7 tahun, berapakah umur ekonomis armada Truk Tronton A?", "o": ["8 Tahun", "10 Tahun", "12 Tahun"], "k": "A"},
    {"s": "12. Lead time pengiriman vendor A adalah 5 days, Vendor B adalah 8 days, Vendor C adalah 12 days. Jika perusahaan menerapkan siklus penggabungan restock bersamaan di hari pertama, pada hari ke berapakah ketiga vendor tersebut akan berada di jadwal kedatangan yang sama?", "o": ["Hari ke-60", "Hari ke-120", "Hari ke-240"], "k": "B"},
    {"s": "13. Tingkat akurasi stock opname Gudang Sayur X adalah 98%. Jika total variasi item (SKU) aktif ada 4.000 jenis, berapa maksimal SKU yang diperbolehkan mengalami selisih pencatatan (discrepancy) tanpa merusak Key Performance Indicator (KPI) akurasi?", "o": ["80 SKU", "40 SKU", "120 SKU"], "k": "A"}
]

BANK_KEPRIBADIAN = [
    {"id": "STRES", "s": "1. Ketika terjadi lonjakan paket (peak season) mendadak yang mengakibatkan antrean truk mengular di luar depo gudang, saya mendapati diri saya mudah cemas dan emosional menghadapi desakan tim lapangan."},
    {"id": "TELITI", "s": "2. Menghabiskan waktu 5 menit ekstra untuk memastikan keakuratan data nomor resi kargo satu per satu jauh lebih penting bagi saya daripada sekadar mengejar kecepatan laporan cepat."},
    {"id": "PATUH", "s": "3. Menurut pandangan saya, mengabaikan prosedur operasional standar (SOP) keselamatan kerja dapat dimaklumi apabila target waktu pemuatan (loading window) kapal/pesawat sudah sangat kritis."},
    {"id": "STRES", "s": "4. Saya mampu mengisolasi tekanan psikologis dari komplain kemarahan pelanggan eksternal/sopir angkutan tanpa mengganggu fokus pengerjaan entri data administrasi berikutnya."},
    {"id": "TELITI", "s": "5. Saya cenderung mengabaikan kesalahan kecil pada digit angka di dokumen manifes perjalanan, selama total jumlah tonase akhir di jembatan timbang terlihat cocok."},
    {"id": "PATUH", "s": "6. Saya konsisten menjalankan inspeksi checklist kelayakan armada (ramp check) secara detail meskipun pengawasan dari Head of Fleet atau Supervisor sedang longgar."},
    {"id": "STRES", "s": "7. Rencana distribusi alokasi truk yang mendadak berubah di tengah malam akibat kecelakaan lalu lintas atau penutupan jalan tol membuat saya sulit berkonsentrasi menentukan keputusan darurat."},
    {"id": "TELITI", "s": "8. Rekan kerja atau atasan seringkali memuji hasil pelaporan kerja saya karena tingkat presisi penempatan koordinat lokasi rak gudang yang sangat akurat."},
    {"id": "PATUH", "s": "9. Memodifikasi data kerusakan aset logistik di sistem agar performa operasional divisi terlihat tetap aman di mata manajemen perusahaan bagi saya adalah hal yang wajar dilakukan."},
    {"id": "PATUH", "s": "10. Saya bersedia melaporkan indikasi fraud, pungutan liar, atau kecurangan pencatatan BBM yang dilakukan oleh rekan kerja satu divisi demi integritas keamanan depo."}
]

BANK_EXCEL = [
    {"s": "1. Anda ditugaskan menggabungkan data text Kode Kurir di kolom B3, Wilayah Kerja di kolom C3, dan ID Manifes di kolom D3 dengan delimeter garis miring (Contoh: K01/BARAT/M99). Formula mana yang paling bersih dan ringkas di Excel modern?", "o": ["=TEXTJOIN(\"/\"; TRUE; B3:D3)", "=B3 & \"/\" & C3 & \"/\" & D3", "=CONCATENATE(B3; \"/\"; C3; \"/\"; D3)"], "k": "A"},
    {"s": "2. Input rumus logika bersusun (Nested IF) untuk mengevaluasi efisiensi BBM di sel E2: Jika rasio > 1:8 ditulis 'Sangat Efisien', jika rentang 1:5 sampai 1:8 ditulis 'Normal', dan jika di bawah 1:5 ditulis 'Boros'. Sintaks formula yang paling valid:", "o": ["=IF(E2>8;\"Sangat Efisien\";IF(E2>=5;\"Normal\";\"Boros\"))", "=IF(E2>8;\"Sangat Efisien\";\"Normal\";\"Boros\")", "=IF(E2>8;\"Sangat Efisien\") & IF(E2>=5;\"Normal\")"], "k": "A"},
    {"s": "3. Menghitung akumulasi total kuantitas muatan barang (koli) yang berada di range F2:F200 namun HANYA untuk nama driver 'Budi' di range C2:C200 dan Status Unit 'Completed' di range D2:D200. Rumus yang tepat:", "o": ["=SUMIF(C2:C200;\"Budi\";F2:F200)", "=SUMIFS(F2:F200; C2:C200; \"Budi\"; D2:D200; \"Completed\")", "=COUNTIFS(C2:C200;\"Budi\";D2:D200;\"Completed\")"], "k": "B"},
    {"s": "4. Untuk menarik nama vendor logistik dari tabel master data referensi secara horizontal berdasarkan ID Vendor yang dicantumkan, fungsi default apa yang digunakan jika XLOOKUP tidak tersedia?", "o": ["=VLOOKUP()", "=INDEX(MATCH())", "=HLOOKUP()"], "k": "C"},
    {"s": "5. Muncul eror '#DIV/0!' pada laporan Excel Anda ketika menghitung utilitas tonase truk karena jumlah kapasitas terpakai dibagi dengan nol (armada maintenance). Fungsi proteksi untuk mengganti eror tersebut menjadi teks kosong (string kosong) adalah...", "o": ["=IFERROR(Formula_Anda; \"\")", "=IFNA(Formula_Anda; 0)", "=CLEAN(Formula_Anda)"], "k": "A"},
    {"s": "6. Sel A1 berisi teks string panjang data mentah: 'JKT-TRK0098-ENGKEL'. Anda hanya ingin mengekstrak 7 karakter di tengah yaitu ID Truk 'TRK0098'. Formula string manipulatife yang wajib dieksekusi:", "o": ["=LEFT(A1; 7)", "=MID(A1; 5; 7)", "=RIGHT(A1; 7)"], "k": "B"},
    {"s": "7. Rumus di sel G5 tertulis =XLOOKUP(A5; Master!$B$2:$B$500; Master!$E$2:$E$500; \"Not Found\"). Apa fungsi spesifik dari argumen terakhir 'Not Found' tersebut?", "o": ["Mengunci data agar tidak berubah saat sel disalin ke bawah", "Menggantikan eror standard #N/A secara otomatis jika data kode A5 tidak ditemukan", "Mencari kecocokan data string yang mirip saja"], "k": "B"},
    {"s": "8. Anda ingin mewarnai baris data resi secara otomatis menjadi MERAH jika kolom status keterlambatan (Delay) bernilai lebih dari 2 jam. Fitur Tracking Excel yang diimplementasikan adalah...", "o": ["Data Validation", "Conditional Formatting", "Flash Fill"], "k": "B"},
    {"s": "9. Rumus Excel manakah yang digunakan untuk mencari total jumlah baris/sel unik (unik secara numerik resi) yang memiliki isi angka di area kolom manifes?", "o": ["=COUNT()", "=COUNTA()", "=COUNTBLANK()"], "k": "A"},
    {"s": "10. Dalam pembuatan dasbor metrik logistik harian, pintasan keyboard (shortcut) tercepat di Excel untuk membuat grafik chart otomatis dari tabel yang terblok adalah...", "o": ["Alt + F1", "Ctrl + P", "Shift + F5"], "k": "A"},
    {"s": "11. Fungsi utama dari fitur 'Data Validation' dengan kriteria 'List' pada tabel input manifes pergudangan adalah...", "o": ["Menghitung total baris nama sopir secara otomatis", "Membatasi input sel hanya boleh diisi oleh opsi teks tertentu yang sudah ditentukan (mencegah salah ketik)", "Mengurutkan data abjad kota asal ke kota tujuan"], "k": "B"},
    {"s": "12. Formula di sel H10 adalah =COUNTA(D2:D50). Jika di dalam rentang tersebut terdapat 5 sel kosong, 5 sel berisi teks eror, dan 40 sel berisi teks normal. Berapakah angka hasil keluaran rumus tersebut?", "o": ["40", "45", "50"], "k": "B"}
]

# Inisialisasi Database Lokal / Session State
if 'database_hrd' not in st.session_state:
    st.session_state.database_hrd = []

if 'page' not in st.session_state:
    st.session_state.page = 'menu'
if 'identitas' not in st.session_state:
    st.session_state.identitas = {}
if 'jawaban_logika' not in st.session_state:
    st.session_state.jawaban_logika = {}
if 'jawaban_kepribadian' not in st.session_state:
    st.session_state.jawaban_kepribadian = {}
if 'jawaban_excel' not in st.session_state:
    st.session_state.jawaban_excel = {}

# Navigasi Halaman
def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 1. MENU UTAMA ---
if st.session_state.page == 'menu':
    st.markdown("<h2 style='text-align: center;'>SISTEM EVALUASI KOMPETENSI REKRUTMEN LOGISTIK</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Instrumen Penilaian Akurat: Logika Penalaran Analitis, Inventory & Fleet Control, Profil Sikap Kerja, dan Advanced Excel Data Processing.</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mulai Tes Seleksi (Kandidat)", type="primary", use_container_width=True):
            go_to('kandidat_reg')
    with col2:
        if st.button("Panel Manajemen HRD (Admin)", use_container_width=True):
            go_to('login_hrd')

# --- 2. LOGIN HRD ---
elif st.session_state.page == 'login_hrd':
    st.subheader("Autentikasi Panel Manajemen HRD")
    pwd_input = st.text_input("Masukkan Password Akses Admin HRD:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Masuk Panel", type="primary", use_container_width=True):
            if pwd_input == HRD_PASSWORD:
                go_to('hrd_panel')
            else:
                st.error("Password Salah! Akses ditolak.")
    with col2:
        if st.button("Kembali ke Menu", use_container_width=True):
            go_to('menu')

# --- 3. REGISTRASI KANDIDAT ---
elif st.session_state.page == 'kandidat_reg':
    st.subheader("Registrasi Profil Pelamar")
    st.info("""
    **Ketentuan Mutlak Pelaksanaan Ujian:**
    - Total Komponen Soal: **35 Butir Instrumen Pemeringkat** (13 Logika Logistik, 10 Psikometrik Perilaku, 12 Formulasi Excel).
    - Kerjakan dengan teliti dan utamakan efisiensi waktu Anda.
    """)
    
    nama = st.text_input("Nama Lengkap Pelamar:", placeholder="Masukkan nama lengkap sesuai dokumen resmi...")
    posisi = st.text_input("Formasi Jabatan yang Dituju:", placeholder="Contoh: Supervisor Gudang, Data Analyst Supply Chain, Fleet Planner...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Validasi & Buka Lembar Soal", type="primary", use_container_width=True):
            if not nama.strip() or not posisi.strip():
                st.error("Mohon lengkapi Data Diri Registrasi Anda.")
            else:
                st.session_state.identitas = {"nama": nama, "posisi": posisi}
                go_to('soal_logika')
    with col2:
        if st.button("Kembali", use_container_width=True):
            go_to('menu')

# --- 4. SOAL LOGIKA ---
elif st.session_state.page == 'soal_logika':
    st.subheader("Bagian 1: Logika Kognitif & Analitis Operasional (13 Soal)")
    
    with st.form("form_logika"):
        temp_answers = {}
        for idx, item in enumerate(BANK_LOGIKA):
            st.markdown(f"**{item['s']}**")
            options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(item['o'])]
            choice = st.radio(f"Pilih jawaban Soal {idx+1}:", options, key=f"logika_{idx}", index=None)
            if choice:
                temp_answers[idx] = choice[0]
            st.write("---")
            
        submitted = st.form_submit_button("Simpan & Melanjutkan Bagian 2")
        if submitted:
            if len(temp_answers) < len(BANK_LOGIKA):
                st.error("Peringatan: Ada soal Logika yang belum terisi. Lengkapi seluruh butir soal.")
            else:
                st.session_state.jawaban_logika = temp_answers
                go_to('soal_kepribadian')

# --- 5. SOAL KEPRIBADIAN ---
elif st.session_state.page == 'soal_kepribadian':
    st.subheader("Bagian 2: Profil Kecocokan Sikap & Karakter Kerja Psikometrik (10 Soal)")
    st.caption("Tentukan sikap Anda: 1 = Sangat Tidak Setuju | 2 = Tidak Setuju | 3 = Setuju | 4 = Sangat Setuju")
    
    with st.form("form_kepribadian"):
        temp_answers = {}
        for idx, item in enumerate(BANK_KEPRIBADIAN):
            st.markdown(f"**{item['s']}**")
            choice = st.select_slider(
                f"Sikap untuk Soal {idx+1}:",
                options=[1, 2, 3, 4],
                format_func=lambda x: {1: "1 - Sangat Tidak Setuju", 2: "2 - Tidak Setuju", 3: "3 - Setuju", 4: "4 - Sangat Setuju"}[x],
                key=f"kep_{idx}"
            )
            temp_answers[idx] = {"id": item['id'], "skor": choice}
            st.write("---")
            
        submitted = st.form_submit_button("Simpan & Melanjutkan Bagian 3")
        if submitted:
            st.session_state.jawaban_kepribadian = temp_answers
            go_to('soal_excel')

# --- 6. SOAL EXCEL ---
elif st.session_state.page == 'soal_excel':
    st.subheader("Bagian 3: Advanced Formula & Pengolahan Data Manifes Excel (12 Soal)")
    
    with st.form("form_excel"):
        temp_answers = {}
        for idx, item in enumerate(BANK_EXCEL):
            st.markdown(f"**{item['s']}**")
            options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(item['o'])]
            choice = st.radio(f"Pilih jawaban Soal {idx+1}:", options, key=f"excel_{idx}", index=None)
            if choice:
                temp_answers[idx] = choice[0]
            st.write("---")
            
        submitted = st.form_submit_button("Kunci Seluruh Jawaban & Selesai")
        if submitted:
            if len(temp_answers) < len(BANK_EXCEL):
                st.error("Peringatan: Jangan biarkan kompetensi Excel kosong. Silakan periksa kembali.")
            else:
                st.session_state.jawaban_excel = temp_answers
                go_to('selesai_kandidat')

# --- 7. FINALISASI & PENYIMPANAN OTOMATIS RAHASIA ---
elif st.session_state.page == 'selesai_kandidat':
    st.subheader("Seluruh Tahapan Ujian Selesai")
    
    # Hitung Skor Otomatis di Backend
    nama = st.session_state.identitas['nama']
    posisi = st.session_state.identitas['posisi']
    
    jwb_logika = st.session_state.jawaban_logika
    benar_logika = sum(1 for i, item in enumerate(BANK_LOGIKA) if jwb_logika.get(i) == item['k'])
    skor_logika = round((benar_logika / len(BANK_LOGIKA)) * 100, 1)
    
    jwb_excel = st.session_state.jawaban_excel
    benar_excel = sum(1 for i, item in enumerate(BANK_EXCEL) if jwb_excel.get(i) == item['k'])
    skor_excel = round((benar_excel / len(BANK_EXCEL)) * 100, 1)
    
    p = [st.session_state.jawaban_kepribadian[i]['skor'] for i in range(len(BANK_KEPRIBADIAN))]
    total_stres = round(((5 - p[0]) + p[3] + (5 - p[6])) / 3, 1)
    total_teliti = round((p[1] + (5 - p[4]) + p[7]) / 3, 1)
    total_patuh = round(((5 - p[2]) + p[5] + (5 - p[8]) + p[9]) / 4, 1)
    
    # Kategori Rekomendasi Fitment
    if skor_logika >= 80 and skor_excel >= 75:
        rekomendasi = "Top Talent (Sangat Direkomendasikan)"
    elif skor_logika >= 50 and skor_excel >= 50:
        rekomendasi = "Dapat Dipertimbangkan"
    else:
        rekomendasi = "Tidak Direkomendasikan"

    # Simpan Hasil ke Database Internal HRD
    record_hasil = {
        "Waktu Selesai": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nama Pelamar": nama,
        "Posisi Target": posisi,
        "Skor Logika": skor_logika,
        "Skor Excel": skor_excel,
        "Indeks Ketelitian": total_teliti,
        "Indeks Stres": total_stres,
        "Indeks Integritas": total_patuh,
        "Rekomendasi": rekomendasi
    }
    
    # Mencegah Duplikasi Entri saat Rerender
    if not any(d['Nama Pelamar'] == nama and d['Waktu Selesai'] == record_hasil['Waktu Selesai'] for d in st.session_state.database_hrd):
        st.session_state.database_hrd.append(record_hasil)
    
    st.success("Jawaban Anda telah berhasil terkirim dan tersimpan secara aman ke sistem HRD.")
    st.info("Terima kasih telah mengikuti tes seleksi. Hasil evaluasi akan diproses secara internal oleh Tim HRD.")
    
    if st.button("Keluar & Selesai Ujian", use_container_width=True):
        st.session_state.identitas = {}
        st.session_state.jawaban_logika = {}
        st.session_state.jawaban_kepribadian = {}
        st.session_state.jawaban_excel = {}
        go_to('menu')

# --- 8. PANEL RAHASIA HRD ---
elif st.session_state.page == 'hrd_panel':
    st.subheader("Panel Rahasia HRD - Database Hasil Ujian Kandidat")
    
    if len(st.session_state.database_hrd) == 0:
        st.warning("Belum ada data kandidat yang menyelesaikan ujian.")
    else:
        df = pd.DataFrame(st.session_state.database_hrd)
        st.dataframe(df, use_container_width=True)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Rekap Hasil Ujian (CSV/Excel)",
            data=csv_data,
            file_name=f"Rekap_Hasil_Ujian_Logistik_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary"
        )

    if st.button("Keluar dari Panel HRD", use_container_width=True):
        go_to('menu')
