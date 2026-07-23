import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import urllib.parse
import requests

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Sistem Rekrutmen Logistik",
    page_icon="📦",
    layout="centered"
)

# Password Rahasia untuk Akses Panel HRD
HRD_PASSWORD = "adminlogistik"

# --- PASTE LINK GOOGLE SHEET (CSV Export Link) DI SINI ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQHrkTeAJyKiUY3G9VD10wgE2GnBR0mfu8qbaWo2iEFasprbTncr8jbA5UtpXAQo8_yd3Psr-oUnchC/pub?output=csv" 

# --- PASTE WEB APP URL GOOGLE APPS SCRIPT DI SINI ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIXtqqcw23Laxslcs2UoA7fJOT-0K4jgxbM5WGwKJA3FhddM5UqVdvXEWrmfmLKFgrXA/exec"

# ========================================================
# FUNGSI ANTI-KECURANGAN (TAB SWITCH & DISABLE COPY-PASTE)
# ========================================================
def inject_anti_cheat_script():
    anti_cheat_html = """
    <script>
      (function() {
        // Mengakses Window Utama (Top Frame) Streamlit
        const topWin = window.top || window.parent || window;
        const topDoc = topWin.document;

        // 1. INJECT STYLESHEET UNTUK DISABLE TEXT SELECTION
        if (!topDoc.getElementById('anti-select-style')) {
          const style = topDoc.createElement('style');
          style.id = 'anti-select-style';
          style.innerHTML = `
            * {
              -webkit-user-select: none !important;
              -moz-user-select: none !important;
              -ms-user-select: none !important;
              user-select: none !important;
            }
          `;
          topDoc.head.appendChild(style);
        }

        // 2. DISABLE RIGHT CLICK, COPY, PASTE, CUT
        const blockEvents = ['contextmenu', 'copy', 'cut', 'paste', 'dragstart'];
        blockEvents.forEach(evt => {
          topDoc.addEventListener(evt, e => e.preventDefault(), true);
        });

        // 3. DISABLE KEYBOARD SHORTCUTS (Ctrl+C, Ctrl+V, F12, dll)
        topDoc.addEventListener('keydown', e => {
          const isCtrl = e.ctrlKey || e.metaKey;
          const key = e.key.toLowerCase();
          if (
            (isCtrl && ['c', 'v', 'x', 'a', 'u', 's', 'p'].includes(key)) ||
            e.key === 'F12' ||
            (isCtrl && e.shiftKey && ['i', 'j', 'c'].includes(key))
          ) {
            e.preventDefault();
            e.stopPropagation();
          }
        }, true);

        // 4. TAB SWITCH DETECTOR
        if (typeof topWin.violationCount === 'undefined') {
          topWin.violationCount = 0;
        }

        const maxViolations = 3;

        function handleVisibilityChange() {
          if (topDoc.hidden) {
            topWin.violationCount++;
            if (topWin.violationCount >= maxViolations) {
              alert('PERINGATAN SELESAI!\nAnda telah keluar dari halaman tes sebanyak ' + topWin.violationCount + ' kali. Akses tes dihentikan.');
              topWin.location.reload();
            } else {
              const tersisa = maxViolations - topWin.violationCount;
              alert('PERINGATAN KECURANGAN!\nAnda terdeteksi meninggalkan halaman tes.\n\nPelanggaran: ' + topWin.violationCount + '/' + maxViolations + '.\nTersisa ' + tersisa + ' kali kesempatan lagi!');
            }
          }
        }

        // Hapus listener lama jika ada (mencegah pemicuan ganda)
        topDoc.removeEventListener('visibilitychange', handleVisibilityChange);
        topDoc.addEventListener('visibilitychange', handleVisibilityChange);

      })();
    </script>
    """
    components.html(anti_cheat_html, height=0, width=0)

# Data Bank Soal Lengkap (13 Logika, 20 Sikap Kerja, 12 Excel)
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
    {"id": "PATUH", "s": "10. Saya bersedia melaporkan indikasi fraud, pungutan liar, atau kecurangan pencatatan BBM yang dilakukan oleh rekan kerja satu divisi demi integritas keamanan depo."},
    {"id": "TELITI", "s": "11. Saya selalu melakukan konfirmasi ulang secara fisik terhadap jumlah barang di atas palet sebelum menandatangani berita acara serah terima barang."},
    {"id": "STRES", "s": "12. Perubahan instruksi mendadak dari manajemen terkait prioritas pengiriman barang tidak mengganggu ketenangan dan fokus kerja saya."},
    {"id": "PATUH", "s": "13. Saya menolak untuk meloloskan truk yang over-dimension dan over-load (ODOL) meskipun mendapat desakan dari pihak vendor angkutan."},
    {"id": "TELITI", "s": "14. Bagi saya, kecocokan antara data fisik di gudang dengan catatan di sistem WMS (Warehouse Management System) adalah harga mati yang tidak boleh ada selisih."},
    {"id": "STRES", "s": "15. Saat terjadi perselisihan atau adu argumen dengan tim muat (co-loader) di lapangan, saya tetap dapat mengendalikan emosi dengan tenang."},
    {"id": "PATUH", "s": "16. Menggunakan Alat Pelindung Diri (APD) lengkap di area gudang/depo adalah kewajiban yang selalu saya patuhi tanpa perlu ditegur atasan."},
    {"id": "TELITI", "s": "17. Saya terbiasa memeriksa ulang detail kode barang (SKU) yang mirip sebelum proses paking dan penempelan label resi."},
    {"id": "STRES", "s": "18. Beban kerja yang menumpuk menjelang akhir jam operasional gudang tidak membuat saya tergesa-gesa hingga mengurangi kualitas kerja."},
    {"id": "PATUH", "s": "19. Apabila saya menemukan celah sistem yang bisa dimanfaatkan untuk mempercepat pekerjaan tetapi melanggar prosedur resmi, saya tetap memilih mengikuti aturan."},
    {"id": "TELITI", "s": "20. Saya mencatat setiap riwayat perawatan rutin armada logistik secara rapi dan terorganisasi agar tidak ada jadwal pemeriksaan yang terlewat."}
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

# Inisialisasi Database Lokal Backup
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

# Timer Widget
def render_timer():
    timer_html = """
    <div id="timer_box" style="
        position: fixed; top: 15px; right: 20px; 
        background: #dc3545; color: white; padding: 10px 20px; 
        font-size: 18px; font-weight: bold; border-radius: 8px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); z-index: 9999;">
        Sisa Waktu: <span id="time">30:00</span>
    </div>
    <script>
    if (!window.timerStarted) {
        window.timerStarted = true;
        var duration = 30 * 60;
        var display = document.querySelector('#time');
        var timer = duration, minutes, seconds;
        var interval = setInterval(function () {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
            display.textContent = minutes + ":" + seconds;
            if (--timer < 0) {
                clearInterval(interval);
                alert("Batas Waktu 30 Menit Habis! Silakan simpan jawaban Anda.");
            }
        }, 1000);
    }
    </script>
    """
    components.html(timer_html, height=60)

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
            
    st.markdown("<br><hr><p style='text-align: center; color: #adb5bd; font-size: 12px; font-style: italic;'>created by iqbalmantam</p>", unsafe_allow_html=True)

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
    - Total Komponen Soal: **45 Butir Instrumen Pemeringkat** (13 Logika Logistik, 20 Psikometrik Perilaku, 12 Formulasi Excel).
    - Batas Waktu Pengerjaan: **30 Menit** (Timer dimulai otomatis saat lembar soal dibuka).
    - **Sistem Keamanan:** Dilarang menyalin teks (Copy-Paste) dan dilarang meninggalkan / berpindah tab browser selama tes.
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
    inject_anti_cheat_script()  # 🔒 Pengunci Keamanan Tambahan
    render_timer()
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
    inject_anti_cheat_script()  # 🔒 Pengunci Keamanan Tambahan
    render_timer()
    st.subheader("Bagian 2: Profil Kecocokan Sikap & Karakter Kerja Psikometrik (20 Soal)")
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
    inject_anti_cheat_script()  # 🔒 Pengunci Keamanan Tambahan
    render_timer()
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

# --- 7. FINALISASI & KIRIM OTOMATIS ---
elif st.session_state.page == 'selesai_kandidat':
    st.subheader("Seluruh Tahapan Ujian Selesai")
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if not st.session_state.submitted:
        nama = st.session_state.identitas.get('nama', 'Tanpa Nama')
        posisi = st.session_state.identitas.get('posisi', 'Tanpa Posisi')
        
        jwb_logika = st.session_state.jawaban_logika
        benar_logika = sum(1 for i, item in enumerate(BANK_LOGIKA) if jwb_logika.get(i) == item['k'])
        skor_logika = round((benar_logika / len(BANK_LOGIKA)) * 100, 1)
        
        jwb_excel = st.session_state.jawaban_excel
        benar_excel = sum(1 for i, item in enumerate(BANK_EXCEL) if jwb_excel.get(i) == item['k'])
        skor_excel = round((benar_excel / len(BANK_EXCEL)) * 100, 1)
        
        p = [st.session_state.jawaban_kepribadian[i]['skor'] for i in range(len(BANK_KEPRIBADIAN))]
        stres_scores = [p[i] for i in range(len(p)) if BANK_KEPRIBADIAN[i]['id'] == 'STRES']
        teliti_scores = [p[i] for i in range(len(p)) if BANK_KEPRIBADIAN[i]['id'] == 'TELITI']
        patuh_scores = [p[i] for i in range(len(p)) if BANK_KEPRIBADIAN[i]['id'] == 'PATUH']
        
        total_stres = round(sum(stres_scores) / len(stres_scores), 1) if stres_scores else 3.0
        total_teliti = round(sum(teliti_scores) / len(teliti_scores), 1) if teliti_scores else 3.0
        total_patuh = round(sum(patuh_scores) / len(patuh_scores), 1) if patuh_scores else 3.0
        
        if skor_logika >= 80 and skor_excel >= 75:
            tag_status = "REKOMENDASI KHUSUS"
            desc_status = "Memiliki ketajaman berhitung kognitif tinggi serta pemahaman mendalam pada manipulasi database logistik. Sangat direkomendasikan untuk pos perencana strategis, rute armada optimal, atau kendali inventory depo utama."
        elif skor_logika >= 50 and skor_excel >= 50:
            tag_status = "DAPAT DIPERTIMBANGKAN"
            desc_status = "Berada pada level kompetensi rata-rata pasar kerja. Mampu mengeksekusi tugas administratif terstruktur dengan supervisi normal."
        else:
            tag_status = "TIDAK DIREKOMENDASIKAN"
            desc_status = "Kinerja pemecahan masalah kuantitatif dan penguasaan Excel berada di bawah batas efisiensi standar operasional harian perusahaan. Berisiko tinggi melakukan human error."

        record_hasil = {
            "Waktu Selesai": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nama Pelamar": nama,
            "Posisi Target": posisi,
            "Skor Logika": skor_logika,
            "Benar Logika": benar_logika,
            "Skor Excel": skor_excel,
            "Benar Excel": benar_excel,
            "Indeks Ketelitian": total_teliti,
            "Indeks Stres": total_stres,
            "Indeks Integritas": total_patuh,
            "Tag Status": tag_status,
            "Desc Status": desc_status
        }
        
        # 1. Kirim ke Google Sheets Apps Script
        if GOOGLE_SCRIPT_URL and "script.google.com" in GOOGLE_SCRIPT_URL:
            try:
                requests.post(GOOGLE_SCRIPT_URL, json=record_hasil, timeout=5)
            except:
                pass
        
        # 2. Simpan backup ke memori lokal
        st.session_state.database_hrd.append(record_hasil)
        st.session_state.submitted = True

    st.success("Jawaban Anda telah berhasil terkirim dan tersimpan secara aman ke sistem HRD.")
    st.info("Terima kasih telah mengikuti tes seleksi. Hasil evaluasi akan diproses secara internal oleh Tim HRD.")
    
    if st.button("Keluar & Selesai Ujian", use_container_width=True):
        st.session_state.identitas = {}
        st.session_state.jawaban_logika = {}
        st.session_state.jawaban_kepribadian = {}
        st.session_state.jawaban_excel = {}
        st.session_state.submitted = False
        go_to('menu')

# --- 8. PANEL RAHASIA HRD ---
elif st.session_state.page == 'hrd_panel':
    st.subheader("Panel Skoring HRD - Supply Chain Fitment Index")
    
    data_terpusat = []
    if SHEET_CSV_URL != "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ.../pub?output=csv":
        try:
            df_gsheet = pd.read_csv(SHEET_CSV_URL)
            data_terpusat = df_gsheet.to_dict('records')
        except:
            data_terpusat = st.session_state.database_hrd
    else:
        data_terpusat = st.session_state.database_hrd
    
    if len(data_terpusat) == 0:
        st.warning("Belum ada data kandidat yang menyelesaikan ujian dari PC mana pun.")
    else:
        df_summary = pd.DataFrame([{
            "Waktu": d.get("Waktu Selesai", "-"),
            "Nama Pelamar": d.get("Nama Pelamar", "-"),
            "Posisi Target": d.get("Posisi Target", "-"),
            "Skor Logika": f"{d.get('Skor Logika', 0)} / 100",
            "Skor Excel": f"{d.get('Skor Excel', 0)} / 100",
            "Status Fitment": d.get("Tag Status", "-")
        } for d in data_terpusat])
        
        st.write("### Rekapitulasi Data Seluruh Kandidat (Real-time)")
        st.dataframe(df_summary, use_container_width=True)
        
        st.write("---")
        st.write("### COMPREHENSIVE ASSESSMENT REPORT")
        st.caption("Pilih nama kandidat untuk bedah laporan detail komprehensif:")
        
        list_nama = [d.get("Nama Pelamar", "Kandidat") for d in data_terpusat]
        kandidat_terpilih = st.selectbox("Pilih Nama Kandidat:", list_nama)
        
        data_k = next(item for item in data_terpusat if item.get("Nama Pelamar") == kandidat_terpilih)
        
        detail_df = pd.DataFrame([
            {"Metrik Evaluasi": "Nama Lengkap Pelamar", "Nilai/Indeks": data_k.get('Nama Pelamar')},
            {"Metrik Evaluasi": "Target Posisi Formasi", "Nilai/Indeks": data_k.get('Posisi Target')},
            {"Metrik Evaluasi": "Skor Logika & Penalaran Distribusi", "Nilai/Indeks": f"{data_k.get('Skor Logika')} / 100 ({data_k.get('Benar Logika')} Benar)"},
            {"Metrik Evaluasi": "Skor Advanced Formula & Olah Data Excel", "Nilai/Indeks": f"{data_k.get('Skor Excel')} / 100 ({data_k.get('Benar Excel')} Benar)"},
            {"Metrik Evaluasi": "Indeks Ketelitian & Validasi Data (Skala 4)", "Nilai/Indeks": f"{data_k.get('Indeks Ketelitian')}"},
            {"Metrik Evaluasi": "Indeks Ketahanan Tekanan Kerja (Skala 4)", "Nilai/Indeks": f"{data_k.get('Indeks Stres')}"},
            {"Metrik Evaluasi": "Indeks Integritas & Kepatuhan Prosedur (Skala 4)", "Nilai/Indeks": f"{data_k.get('Indeks Integritas')}"},
        ])
        st.table(detail_df)
        
        st.markdown("#### Matriks Doktrin HRD & Rekomendasi Fitment:")
        
        st.markdown(f"""
        1. <span style='border: 1px solid #333; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{data_k.get('Tag Status')}</span> {data_k.get('Desc Status')}
        2. **Metrik Ketelitian:** {'Unggul. Menunjukkan tingkat presisi tinggi dalam memvalidasi data resi, manifes kargo, dan meminimalkan discrepancy stock opname.' if float(data_k.get('Indeks Ketelitian', 0)) >= 3.0 else 'Kurang Aman. Cenderung ceroboh dan melompati detail angka krusial saat dihadapkan pada volume pekerjaan yang padat.'}
        3. **Resiliensi Operasional:** {'Sangat Stabil. Mampu mengontrol emosi dengan baik serta tetap dapat mengambil keputusan logis walau dalam kondisi krisis depo/peak season.' if float(data_k.get('Indeks Stres', 0)) >= 3.0 else 'Rentan Burnout. Berpotensi mengalami penurunan performa signifikan atau salah keputusan jika ditempatkan di lini depan operasional yang fluktuatif.'}
        4. **Integritas & Kepatuhan Prosedur:** {'Tinggi. Memiliki komitmen absolut terhadap penegakan SOP keselamatan, pelaporan kecurangan, dan mitigasi fraud/kehilangan barang gudang.' if float(data_k.get('Indeks Integritas', 0)) >= 3.0 else 'Berisiko Tinggi. Terindikasi memiliki tendensi memotong prosedur regulasi resmi demi kenyamanan pribadi atau efisiensi semu.'}
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        csv_data = pd.DataFrame(data_terpusat).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Seluruh Data Rekap (CSV/Excel)",
            data=csv_data,
            file_name=f"Rekap_Hasil_Ujian_Logistik_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary"
        )

    if st.button("Keluar dari Panel HRD", use_container_width=True):
        go_to('menu')
