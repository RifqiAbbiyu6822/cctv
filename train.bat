@echo off
echo Menjalankan script pelatihan YOLOv8...

REM Ganti "nama_lingkungan_anda" dengan nama lingkungan virtual yang Anda gunakan
REM Jika tidak menggunakan lingkungan virtual, hapus baris berikut atau ganti dengan jalur Python yang benar
REM C:\path\to\your\venv\Scripts\activate.bat

pip train_model.py

echo Pelatihan selesai. Tekan sembarang tombol untuk keluar.
pause