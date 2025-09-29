"""
Script untuk melatih model YOLOv8 untuk deteksi mobil.
Disesuaikan dengan praktik terbaik untuk mencegah overfitting dan
memastikan pelatihan yang efisien.
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk).
"""

from ultralytics import YOLO
import os
import shutil

def train_yolo_model():
    """
    Melatih model YOLOv8 dengan dataset mobil.
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk).
    """
    print("Memulai pelatihan model YOLOv8...")

    # --- PENTING: Konfigurasi Dataset ---
    # Pastikan file 'data.yaml' Anda sudah benar dan memiliki pembagian data
    # validasi yang cukup (rekomendasi: 20%). Contoh:
    # train: ../train/images
    # val: ../valid/images
    #
    # Jumlah data validasi yang terlalu sedikit akan membuat metrik tidak stabil
    # dan hasil model tidak dapat diandalkan.
    # 
    # PENTING: Dataset harus berisi hanya gambar mobil (tidak termasuk bus dan truk)
    # untuk konsistensi dengan konfigurasi aplikasi.
    # ------------------------------------
    
    # Load pretrained model YOLOv8n (nano version - ringan dan cepat)
    model = YOLO('yolov8n.pt')
    
    # Mulai pelatihan dengan parameter yang dioptimalkan
    try:
        results = model.train(
            data='data.yaml',         # File konfigurasi dataset Anda.
            imgsz=640,                # Ukuran gambar input (resolusi).
            batch=20,                 # Jumlah gambar per batch. Sesuaikan jika VRAM GPU terbatas.
            epochs=150,               # Jumlah epoch MAKSIMUM. Pelatihan kemungkinan akan berhenti lebih awal.
            patience=25,              # Early stopping: berhenti jika metrik validasi tidak membaik setelah 25 epoch.
                                      # Ini adalah cara terbaik untuk menemukan jumlah epoch yang optimal secara otomatis.
            name='car_detection_v1',  # Nama eksperimen agar mudah diidentifikasi (hanya mobil).
            save=True,                # Pastikan model disimpan.
            save_period=10,           # Simpan checkpoint setiap 10 epoch untuk backup.
            device='cuda',            # Gunakan GPU ('cuda'). Ubah ke 'cpu' jika tidak ada GPU yang kompatibel.
            workers=2                # Jumlah worker untuk memuat data. Sesuaikan dengan kemampuan CPU Anda.
        )
        
        print("\nPelatihan selesai!")
        
        # --- Menyimpan Model Terbaik ---
        # Lokasi model terbaik akan ada di dalam direktori 'results.save_dir'
        best_model_path = os.path.join(results.save_dir, 'weights/best.pt')
        
        # Buat folder 'weights' jika belum ada
        output_folder = 'weights'
        os.makedirs(output_folder, exist_ok=True)
        
        # Tentukan path tujuan
        destination_path = os.path.join(output_folder, 'car_detector_best.pt')  # Hanya untuk mobil
        
        # Salin dan ganti nama model terbaik untuk akses yang lebih mudah
        shutil.copy(best_model_path, destination_path)
        
        print(f"Model terbaik berhasil disimpan di: {destination_path}")
        print("Model ini hanya akan mendeteksi mobil (tidak termasuk bus dan truk)")

    except Exception as e:
        print(f"Terjadi error saat pelatihan: {e}")
        print("Pastikan dataset hanya berisi gambar mobil (tidak termasuk bus dan truk)")

if __name__ == "__main__":
    train_yolo_model()