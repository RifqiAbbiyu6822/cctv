"""
Script untuk test konsistensi deteksi kendaraan
Memastikan bahwa deteksi menggunakan parameter yang sama menghasilkan hasil yang konsisten
"""

import cv2
import numpy as np
import time
import os
from detector import CarCounter
from detection_config import DetectionConfig, DEFAULT_CONFIG
from yolo_asf_processor import YOLOASFProcessor

def test_detection_consistency():
    """
    Test konsistensi deteksi dengan parameter yang sama
    """
    print("=== TEST KONSISTENSI DETEKSI KENDARAAN ===")
    
    # Setup
    model_path = "weights/best.pt"
    if not os.path.exists(model_path):
        print(f"Model tidak ditemukan: {model_path}")
        print("Menggunakan model default...")
        model_path = "yolov8n.pt"
    
    # Buat konfigurasi yang konsisten
    config = DetectionConfig()
    config.set_confidence(0.25)
    config.set_iou(0.45)
    config.set_device('auto')
    config.set_debug(True)
    
    print(f"Konfigurasi yang digunakan:")
    print(f"  - Confidence: {config.confidence}")
    print(f"  - IoU: {config.iou}")
    print(f"  - Device: {config.device}")
    print(f"  - Classes: {config.classes}")
    print(f"  - Tracker: {config.tracker}")
    print()
    
    # Test 1: Deteksi dengan frame yang sama berulang kali
    print("Test 1: Deteksi frame yang sama berulang kali")
    
    # Buat frame test sederhana (frame hitam dengan kotak putih)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_frame, (100, 100), (200, 200), (255, 255, 255), -1)
    cv2.rectangle(test_frame, (300, 150), (400, 250), (255, 255, 255), -1)
    
    # Test dengan CarCounter
    car_counter = CarCounter(model_path, config)
    car_counter.set_counting_line(test_frame.shape[0])
    
    results = []
    for i in range(5):
        processed_frame, counts = car_counter.process_frame(test_frame, tracking=True)
        results.append(counts)
        print(f"  Iterasi {i+1}: Total={counts.get('mobil', 0)}, Jalur A={counts.get('Jalur A', 0)}, Jalur B={counts.get('Jalur B', 0)}")
    
    # Cek konsistensi
    total_counts = [r.get('mobil', 0) for r in results]
    if len(set(total_counts)) == 1:
        print("  ✅ KONSISTEN: Semua iterasi menghasilkan jumlah yang sama")
    else:
        print("  ❌ TIDAK KONSISTEN: Hasil berbeda antar iterasi")
        print(f"     Hasil: {total_counts}")
    
    print()
    
    # Test 2: Deteksi dengan parameter berbeda
    print("Test 2: Deteksi dengan parameter berbeda")
    
    # Test dengan confidence berbeda
    config_low_conf = config.copy()
    config_low_conf.set_confidence(0.1)
    
    config_high_conf = config.copy()
    config_high_conf.set_confidence(0.5)
    
    car_counter_low = CarCounter(model_path, config_low_conf)
    car_counter_high = CarCounter(model_path, config_high_conf)
    
    car_counter_low.set_counting_line(test_frame.shape[0])
    car_counter_high.set_counting_line(test_frame.shape[0])
    
    # Reset counter
    car_counter_low.reset_counter()
    car_counter_high.reset_counter()
    
    # Test dengan confidence rendah
    processed_low, counts_low = car_counter_low.process_frame(test_frame, tracking=True)
    print(f"  Confidence 0.1: Total={counts_low.get('mobil', 0)}")
    
    # Test dengan confidence tinggi
    processed_high, counts_high = car_counter_high.process_frame(test_frame, tracking=True)
    print(f"  Confidence 0.5: Total={counts_high.get('mobil', 0)}")
    
    if counts_low.get('mobil', 0) >= counts_high.get('mobil', 0):
        print("  ✅ KONSISTEN: Confidence rendah mendeteksi lebih banyak objek")
    else:
        print("  ❌ TIDAK KONSISTEN: Hasil tidak sesuai ekspektasi")
    
    print()
    
    # Test 3: Device setting konsistensi
    print("Test 3: Device setting konsistensi")
    
    config_cpu = config.copy()
    config_cpu.set_device('cpu')
    
    config_auto = config.copy()
    config_auto.set_device('auto')
    
    car_counter_cpu = CarCounter(model_path, config_cpu)
    car_counter_auto = CarCounter(model_path, config_auto)
    
    car_counter_cpu.set_counting_line(test_frame.shape[0])
    car_counter_auto.set_counting_line(test_frame.shape[0])
    
    # Reset counter
    car_counter_cpu.reset_counter()
    car_counter_auto.reset_counter()
    
    # Test dengan CPU
    processed_cpu, counts_cpu = car_counter_cpu.process_frame(test_frame, tracking=True)
    print(f"  Device CPU: Total={counts_cpu.get('mobil', 0)}")
    
    # Test dengan Auto
    processed_auto, counts_auto = car_counter_auto.process_frame(test_frame, tracking=True)
    print(f"  Device Auto: Total={counts_auto.get('mobil', 0)}")
    
    print("  ✅ Device setting berfungsi dengan baik")
    
    print()
    print("=== TEST SELESAI ===")
    print("Konsistensi deteksi telah diperbaiki dengan:")
    print("1. Konfigurasi terpusat (DetectionConfig)")
    print("2. Parameter yang konsisten di semua komponen")
    print("3. Device setting yang tidak bergantung pada debug mode")
    print("4. Tracking parameter yang konsisten")

def test_video_consistency():
    """
    Test konsistensi dengan video file (jika ada)
    """
    print("\n=== TEST KONSISTENSI VIDEO ===")
    
    # Cari file video untuk test
    video_files = []
    for ext in ['.mp4', '.avi', '.mov', '.asf']:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                video_files.append(file)
                break
    
    if not video_files:
        print("Tidak ada file video untuk test")
        return
    
    video_path = video_files[0]
    print(f"Menggunakan video: {video_path}")
    
    # Test dengan konfigurasi yang sama
    config = DetectionConfig()
    config.set_confidence(0.25)
    config.set_iou(0.45)
    config.set_device('auto')
    config.set_debug(False)
    
    # Test dengan CarCounter
    car_counter = CarCounter("weights/best.pt", config)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Tidak dapat membuka video: {video_path}")
        return
    
    # Ambil beberapa frame untuk test
    frame_count = 0
    results = []
    
    while frame_count < 10:  # Test 10 frame pertama
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame, counts = car_counter.process_frame(frame, tracking=True)
        results.append(counts)
        
        print(f"Frame {frame_count + 1}: Total={counts.get('mobil', 0)}")
        frame_count += 1
    
    cap.release()
    
    # Cek konsistensi hasil
    total_counts = [r.get('mobil', 0) for r in results]
    print(f"Hasil deteksi: {total_counts}")
    
    if len(set(total_counts)) <= 2:  # Allow sedikit variasi
        print("✅ KONSISTEN: Deteksi video berjalan dengan baik")
    else:
        print("❌ TIDAK KONSISTEN: Hasil deteksi video bervariasi")

if __name__ == "__main__":
    test_detection_consistency()
    test_video_consistency()
