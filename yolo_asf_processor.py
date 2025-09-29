"""
Implementasi Alur Kerja YOLO untuk Video ASF
Mengikuti ringkasan alur kerja:
1. Baca File: Gunakan cv2.VideoCapture untuk membuka video ASF
2. Loop Bingkai: Ambil setiap bingkai video satu per satu dengan cap.read()
3. Deteksi: Berikan bingkai yang sudah diekstrak ke model YOLO
4. Visualisasi: Tampilkan hasil deteksi dengan cv2.imshow
5. Akhiri: Lepaskan objek VideoCapture dan tutup jendela tampilan

Terintegrasi dengan aplikasi CarCounter yang sudah ada
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
import sys
from detector import CarCounter
from detection_config import DetectionConfig, DEFAULT_CONFIG

class YOLOASFProcessor:
    """
    Kelas untuk memproses video ASF dengan YOLO detection
    Mengikuti alur kerja yang telah dirangkum
    Terintegrasi dengan CarCounter yang sudah ada
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
    """
    
    def __init__(self, model_path="weights/best.pt", config=None):
        """
        Inisialisasi processor dengan konfigurasi konsisten
        
        Args:
            model_path (str): Path ke model YOLO
            config (DetectionConfig): Konfigurasi deteksi (optional)
        """
        self.model_path = model_path
        self.car_counter = None
        self.cap = None
        self.frame_count = 0
        self.start_time = None
        
        # Gunakan konfigurasi yang disediakan atau default
        self.config = config if config is not None else DEFAULT_CONFIG.copy()
        
        # Load CarCounter yang sudah ada dengan konfigurasi konsisten
        self.load_car_counter()
    
    def load_car_counter(self):
        """Load CarCounter yang sudah ada dengan konfigurasi konsisten"""
        try:
            if not os.path.exists(self.model_path):
                print(f"Model file not found: {self.model_path}")
                print("Using default YOLOv8n model...")
                self.car_counter = CarCounter('yolov8n.pt', self.config)
            else:
                self.car_counter = CarCounter(self.model_path, self.config)
            print(f"CarCounter loaded successfully: {self.model_path}")
        except Exception as e:
            print(f"Error loading CarCounter: {e}")
            sys.exit(1)
    
    def open_video(self, video_path):
        """
        Langkah 1: Baca File - Gunakan cv2.VideoCapture untuk membuka video ASF
        Menggunakan konfigurasi yang sama dengan aplikasi utama untuk konsistensi
        
        Args:
            video_path (str): Path ke video ASF
            
        Returns:
            bool: True jika berhasil membuka video
        """
        try:
            # Cek apakah file ASF
            is_asf = video_path.lower().endswith(('.asf', '.wmv'))
            
            if is_asf:
                # Try multiple backends for ASF files (same as app.py)
                self.cap = None
                backends = [cv2.CAP_FFMPEG, cv2.CAP_DSHOW, cv2.CAP_ANY]
                
                for backend in backends:
                    try:
                        self.cap = cv2.VideoCapture(video_path, backend)
                        if self.cap.isOpened():
                            # Test if we can read a frame
                            ret, test_frame = self.cap.read()
                            if ret and test_frame is not None:
                                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
                                print(f"ASF file opened successfully with backend: {backend}")
                                break
                            else:
                                self.cap.release()
                                self.cap = None
                    except Exception as e:
                        if self.cap:
                            self.cap.release()
                        self.cap = None
                        continue
                
                if self.cap and self.cap.isOpened():
                    # Optimized settings for ASF files (same as app.py)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                    self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 15000)  # Extended timeout
                    self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 15000)
                    # Try to set optimal codec
                    try:
                        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    except:
                        pass  # Ignore if codec setting fails
                else:
                    # Fallback to default VideoCapture
                    self.cap = cv2.VideoCapture(video_path)
            else:
                # Standard VideoCapture for non-ASF files
                self.cap = cv2.VideoCapture(video_path)
            
            if not self.cap.isOpened():
                print(f"Error: Cannot open video file {video_path}")
                return False
            
            # Dapatkan informasi video
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video opened successfully:")
            print(f"  - FPS: {fps}")
            print(f"  - Frame count: {frame_count}")
            print(f"  - Resolution: {width}x{height}")
            if is_asf:
                print(f"  - ASF file detected and optimized")
            
            return True
            
        except Exception as e:
            print(f"Error opening video: {e}")
            return False
    
    def process_video(self, video_path, show_video=True, save_output=False, output_path="output.avi"):
        """
        Proses video ASF dengan YOLO detection
        
        Args:
            video_path (str): Path ke video ASF
            show_video (bool): Apakah menampilkan video real-time
            save_output (bool): Apakah menyimpan hasil ke file
            output_path (str): Path untuk menyimpan output
        """
        # Langkah 1: Baca File
        if not self.open_video(video_path):
            return
        
        # Setup untuk menyimpan output jika diperlukan
        out_writer = None
        if save_output:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Inisialisasi tracking
        self.start_time = time.time()
        self.frame_count = 0
        
        print("Starting video processing...")
        print("Press 'q' to quit, 'p' to pause/resume")
        
        paused = False
        
        try:
            # Langkah 2: Loop Bingkai - Ambil setiap bingkai video satu per satu dengan cap.read()
            consecutive_failures = 0
            max_failures = 30  # Max consecutive failures before giving up
            
            while True:
                if not paused:
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            print("End of video reached or too many consecutive failures")
                            break
                        print(f"Failed to read frame (attempt {consecutive_failures}/{max_failures})")
                        time.sleep(0.1)  # Wait a bit before retrying
                        continue
                    
                    consecutive_failures = 0  # Reset failure counter on success
                    self.frame_count += 1
                    
                    # Validasi frame
                    if frame is None or frame.size == 0:
                        print(f"Warning: Empty frame at {self.frame_count}")
                        continue
                    
                    # Langkah 3: Deteksi - Berikan bingkai yang sudah diekstrak ke model YOLO
                    processed_frame = self.detect_objects(frame)
                    
                    # Langkah 4: Visualisasi - Tampilkan hasil deteksi dengan cv2.imshow
                    if show_video:
                        self.show_frame(processed_frame)
                    
                    # Simpan frame jika diperlukan
                    if save_output and out_writer:
                        out_writer.write(processed_frame)
                    
                    # Tampilkan progress
                    if self.frame_count % 30 == 0:  # Setiap 30 frame
                        elapsed = time.time() - self.start_time
                        fps = self.frame_count / elapsed if elapsed > 0 else 0
                        print(f"Processed {self.frame_count} frames, FPS: {fps:.1f}")
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    paused = not paused
                    print("Paused" if paused else "Resumed")
        
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user")
        
        finally:
            # Langkah 5: Akhiri - Lepaskan objek VideoCapture dan tutup jendela tampilan
            self.cleanup(out_writer)
    
    def detect_objects(self, frame):
        """
        Langkah 3: Deteksi - Berikan bingkai yang sudah diekstrak ke model YOLO
        
        Args:
            frame: Frame video dari OpenCV
            
        Returns:
            numpy.ndarray: Frame dengan hasil deteksi
        """
        try:
            # Validasi frame
            if frame is None or frame.size == 0:
                print("Warning: Empty frame received")
                return frame
            
            # Gunakan CarCounter untuk deteksi yang konsisten dengan aplikasi utama
            if self.car_counter:
                # Gunakan parameter dari config untuk konsistensi
                processed_frame, counts = self.car_counter.process_frame(
                    frame, 
                    tracking=True,
                    confidence=self.config.confidence,
                    iou=self.config.iou
                )
                
                # Tambahkan informasi tambahan
                self.add_info_overlay(processed_frame)
                
                # Debug info untuk ASF files
                if self.config.debug and self.frame_count % 30 == 0:
                    print(f"ASF Detection - Frame {self.frame_count}: {counts}")
                
                return processed_frame
            else:
                # Fallback ke model langsung jika CarCounter tidak tersedia
                # Gunakan parameter dari config untuk konsistensi
                detection_params = self.config.get_detection_params()
                results = self.car_counter.model(frame, **detection_params)
                
                # Proses hasil deteksi
                if results and len(results) > 0:
                    # Gambar bounding box dan label pada frame
                    annotated_frame = results[0].plot()
                    
                    # Tambahkan informasi tambahan
                    self.add_info_overlay(annotated_frame)
                    
                    return annotated_frame
                else:
                    # Jika tidak ada deteksi, tambahkan info overlay saja
                    self.add_info_overlay(frame)
                    return frame
                
        except Exception as e:
            print(f"Error in detection: {e}")
            # Return original frame with error info
            error_frame = frame.copy()
            cv2.putText(error_frame, f"Detection Error: {str(e)[:50]}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return error_frame
    
    def add_info_overlay(self, frame):
        """Tambahkan informasi overlay pada frame"""
        # Tambahkan informasi frame
        cv2.putText(frame, f"Frame: {self.frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Tambahkan FPS
        if self.start_time:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.1f}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Tambahkan instruksi
        cv2.putText(frame, "Press 'q' to quit, 'p' to pause", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def show_frame(self, frame):
        """
        Langkah 4: Visualisasi - Tampilkan hasil deteksi dengan cv2.imshow
        
        Args:
            frame: Frame yang sudah diproses
        """
        # Resize frame jika terlalu besar
        height, width = frame.shape[:2]
        if width > 1280:
            scale = 1280 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Tampilkan frame
        cv2.imshow('YOLO ASF Detection', frame)
    
    def cleanup(self, out_writer=None):
        """
        Langkah 5: Akhiri - Lepaskan objek VideoCapture dan tutup jendela tampilan
        """
        print("Cleaning up...")
        
        # Lepaskan VideoCapture
        if self.cap:
            self.cap.release()
            print("VideoCapture released")
        
        # Tutup VideoWriter jika ada
        if out_writer:
            out_writer.release()
            print("VideoWriter released")
        
        # Tutup semua jendela OpenCV
        cv2.destroyAllWindows()
        print("All windows closed")
        
        # Tampilkan statistik
        if self.start_time:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            print(f"Processing completed:")
            print(f"  - Total frames: {self.frame_count}")
            print(f"  - Total time: {elapsed:.2f} seconds")
            print(f"  - Average FPS: {fps:.2f}")

def main():
    """Fungsi utama untuk menjalankan processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLO ASF Video Processor')
    parser.add_argument('video_path', help='Path to ASF video file')
    parser.add_argument('--model', default='weights/best.pt', help='Path to YOLO model')
    parser.add_argument('--no-display', action='store_true', help='Do not display video')
    parser.add_argument('--save', action='store_true', help='Save output video')
    parser.add_argument('--output', default='output.avi', help='Output video path')
    
    args = parser.parse_args()
    
    # Validasi file video
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}")
        return
    
    # Cek ekstensi file
    if not args.video_path.lower().endswith(('.asf', '.wmv')):
        print("Warning: File doesn't have ASF/WMV extension")
    
    # Buat processor
    processor = YOLOASFProcessor(args.model)
    
    # Proses video
    processor.process_video(
        video_path=args.video_path,
        show_video=not args.no_display,
        save_output=args.save,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
