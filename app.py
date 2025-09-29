"""
Aplikasi GUI Clean untuk deteksi dan penghitungan mobil menggunakan YOLO
Versi Ultra Minimalist dan Clean Layout
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

import sys
import os
import cv2
import time
import requests
import threading
from urllib.parse import urlparse
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, 
                             QMessageBox, QFileDialog, QCheckBox, QProgressBar,
                             QFrame, QSlider, QSpinBox, QComboBox, QTabWidget,
                             QSplitter, QScrollArea, QMainWindow, QDialog)
from PyQt5.QtGui import QImage, QPixmap, QFont, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from detector import CarCounter
from data_input_dialog import DataInputDialog
from reports_widget import ReportsWidget
from yolo_asf_processor import YOLOASFProcessor
from detection_config import DetectionConfig, DEFAULT_CONFIG

class SimpleDropArea(QFrame):
    """Area sederhana untuk drag & drop video"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e5e5;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QFrame:hover {
                background-color: #f5f5f5;
                border-color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        self.label = QLabel("Drop video file here or click to select")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: none; font-size: 11px; color: #666;")
        layout.addWidget(self.label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if self._is_video_file(file_path):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if self._is_video_file(file_path):
                self.file_dropped.emit(file_path)
                self.label.setText(f"Selected: {os.path.basename(file_path)}")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                # Show loading state
                self.label.setText("Loading file dialog...")
                self.label.repaint()
                
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Select Video File", "", 
                    "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.asf);;ASF Files (*.asf);;All Files (*)"
                )
                
                if file_path:
                    self.file_dropped.emit(file_path)
                    self.label.setText(f"Selected: {os.path.basename(file_path)}")
                else:
                    # Reset to original text if no file selected
                    self.reset()
            except Exception as e:
                self.label.setText(f"Error: {str(e)}")
                # Reset after error
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(3000, self.reset)
    
    def _is_video_file(self, file_path):
        return file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.asf'))
    
    def reset(self):
        self.label.setText("Drop video file here or click to select")

class ASFProcessingThread(QThread):
    """Thread untuk memproses file ASF"""
    processing_completed = pyqtSignal()
    processing_error = pyqtSignal(str)
    
    def __init__(self, asf_processor, video_path):
        super().__init__()
        self.asf_processor = asf_processor
        self.video_path = video_path
    
    def run(self):
        try:
            self.asf_processor.process_video(
                video_path=self.video_path,
                show_video=False,
                save_output=False
            )
            self.processing_completed.emit()
        except Exception as e:
            self.processing_error.emit(str(e))

class VideoProcessor(QThread):
    """Thread untuk memproses video"""
    frame_ready = pyqtSignal(QImage)
    count_updated = pyqtSignal(dict)
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    finished_processing = pyqtSignal()
    progress_completed = pyqtSignal(dict)
    
    def __init__(self, video_path, model_path, line_position=60, confidence=0.25, 
                 iou=0.45, detection_zone=50, frame_skip=1, device="auto", playback_speed=1.0):
        super().__init__()
        self.video_path = video_path
        self.model_path = model_path
        self.line_position = line_position
        self.confidence = confidence
        self.iou = iou
        self.detection_zone = detection_zone
        self.frame_skip = frame_skip
        self.device = device
        self.running = True
        self.paused = False
        self.car_counter = None
        self.playback_speed = max(0.1, float(playback_speed))  # guard minimal speed
        self._skip_residual = 0.0  # for fractional frame skipping on files
        
        # Buat konfigurasi konsisten
        self.detection_config = DEFAULT_CONFIG.copy()
        self.detection_config.set_confidence(confidence)
        self.detection_config.set_iou(iou)
        self.detection_config.set_device(device)
        self.detection_config.detection_zone = detection_zone
    
    def run(self):
        try:
            # Initialize detector dengan konfigurasi konsisten
            self.car_counter = CarCounter(self.model_path, self.detection_config)
            
            # Check if it's a live stream (RTSP/HTTP) or file
            is_live_stream = self._is_live_stream(self.video_path)
            
            # Open video with appropriate settings for live streams
            if is_live_stream:
                cap = cv2.VideoCapture(self.video_path, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
            else:
                # Special handling for ASF files
                if self._is_asf_file(self.video_path):
                    # Try multiple backends for ASF files
                    cap = None
                    backends = [cv2.CAP_FFMPEG, cv2.CAP_DSHOW, cv2.CAP_ANY]
                    
                    for backend in backends:
                        try:
                            cap = cv2.VideoCapture(self.video_path, backend)
                            if cap.isOpened():
                                # Test if we can read a frame
                                ret, test_frame = cap.read()
                                if ret and test_frame is not None:
                                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
                                    print(f"ASF file opened successfully with backend: {backend}")
                                    break
                                else:
                                    cap.release()
                                    cap = None
                        except Exception as e:
                            if cap:
                                cap.release()
                            cap = None
                            continue
                    
                    if cap and cap.isOpened():
                        # Optimized settings for ASF files
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 15000)  # Extended timeout
                        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 15000)
                        # Try to set optimal codec
                        try:
                            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                        except:
                            pass  # Ignore if codec setting fails
                    else:
                        # Fallback to default VideoCapture
                        cap = cv2.VideoCapture(self.video_path)
                else:
                    cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                self.error_occurred.emit(f"Cannot open video: {self.video_path}")
                return
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            
            # For live streams, total_frames might be 0 or -1
            if total_frames <= 0:
                total_frames = -1  # Indicate live stream
            
            # Read first frame to get dimensions
            ret, first_frame = cap.read()
            if not ret:
                self.error_occurred.emit("Cannot read first frame from video")
                return
            
            # Set counting line position based on frame dimensions
            self.car_counter.set_counting_line(first_frame.shape[0], self.line_position / 100.0)
            
            # Set detection zone
            self.car_counter.set_detection_zone(self.detection_zone)
            
            # Set debug mode - konsisten dengan config
            self.car_counter.set_debug(False)  # Disable debug for performance
            
            # Reset video to beginning only for files
            if not is_live_stream and total_frames > 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            frame_count = 0
            consecutive_failures = 0
            max_failures = 30  # Max consecutive failures before giving up
            
            while self.running:
                if not self.paused:
                    ret, frame = cap.read()
                    
                    if not ret:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            if is_live_stream:
                                self.error_occurred.emit("Lost connection to live stream")
                            else:
                                self.error_occurred.emit("End of video file reached")
                            break
                        self.msleep(100)  # Wait a bit before retrying
                        continue
                    
                    consecutive_failures = 0  # Reset failure counter on success
                    
                    # Process frame dengan parameter konsisten
                    processed_frame, counts = self.car_counter.process_frame(
                        frame, 
                        tracking=True,  # Always use tracking for now
                        confidence=self.confidence,
                        iou=self.iou
                    )
                    
                    # Convert to Qt format
                    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
                    
                    # Emit signals
                    self.frame_ready.emit(qt_image)
                    self.count_updated.emit(counts)
                    
                    # For file videos, perform frame skipping to speed up playback beyond inference speed
                    skipped_this_iter = 0
                    if not is_live_stream and self.playback_speed > 1.0:
                        self._skip_residual += (self.playback_speed - 1.0)
                        # Grab frames without decoding to skip efficiently
                        while self._skip_residual >= 1.0:
                            grabbed = cap.grab()
                            if not grabbed:
                                consecutive_failures += 1
                                break
                            skipped_this_iter += 1
                            self._skip_residual -= 1.0

                    # Update progress (only for files, not live streams)
                    frame_count += 1 + skipped_this_iter
                    if total_frames > 0:
                        progress = int((frame_count / total_frames) * 100)
                        self.progress_updated.emit(progress)
                        if progress >= 100:
                            self.progress_completed.emit(counts)
                    else:
                        self.progress_updated.emit(50)  # Keep at 50% for live streams
                    
                    # Control playback speed
                    if is_live_stream:
                        base_ms = 33  # ~30 FPS baseline for live streams
                        sleep_ms = max(1, int(base_ms / self.playback_speed))
                        self.msleep(sleep_ms)
                    else:
                        # For file playback, we already skip frames; keep minimal sleep for UI responsiveness
                        frame_ms = 1000 / fps if fps > 0 else 33
                        sleep_ms = max(1, int(frame_ms / self.playback_speed))
                        self.msleep(sleep_ms)
            
            cap.release()
            self.finished_processing.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Processing error: {str(e)}")
    
    def _is_live_stream(self, video_path):
        """Check if the video path is a live stream (RTSP/HTTP)"""
        if isinstance(video_path, str):
            return (video_path.startswith(('rtsp://', 'http://', 'https://', 'rtmp://')) or 
                    video_path.startswith('0') or video_path == 0)  # Webcam
        return False
    
    def _is_asf_file(self, video_path):
        """Check if the video file is ASF format"""
        if isinstance(video_path, str):
            return video_path.lower().endswith(('.asf', '.wmv'))
        return False
    
    def stop(self):
        self.running = False
        self.wait()
    
    def pause(self):
        self.paused = not self.paused
    
    def reset_counter(self):
        if self.car_counter:
            self.car_counter.reset_counter()

# ... (kode sebelumnya tetap sama)

class CarCounterApp(QMainWindow):
    """Main application - Ultra Clean Minimalist Design
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)"""
    
    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.current_video = None
        self.frame_count = 0
        self.start_time = None
        self.current_counts = {'total': 0, 'naik': 0, 'turun': 0}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup ultra clean minimalist UI"""
        self.setWindowTitle('Vehicle Counter - YOLO Detection')
        self.setGeometry(100, 100, 1300, 800)
        
        # Set window icon from assets
        try:
            from PyQt5.QtGui import QIcon
            icon_paths = [
                "assets/logo launcher.png",
                "assets/logo_jjcnormal.png",
                "assets/logo_notext.png"
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
                    break
        except:
            pass
        
        # Ultra minimal clean styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 12px;
            }
            
            QGroupBox {
                font-weight: 500;
                border: 1px solid #e5e5e5;
                background-color: #ffffff;
                border-radius: 4px;
                margin: 6px 0px;
                padding: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0px 4px;
                color: #333;
                font-size: 11px;
                font-weight: 500;
                background-color: white;
            }
            
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: 400;
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
                font-size: 11px;
                min-height: 16px;
            }
            
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #999;
            }
            
            QPushButton:pressed {
                background-color: #e9ecef;
            }
            
            QLineEdit, QComboBox {
                padding: 4px 6px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                min-height: 12px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #2196F3;
                outline: none;
            }
            
            QSlider::groove:horizontal {
                border: none;
                height: 2px;
                background-color: #d0d0d0;
                border-radius: 1px;
            }
            
            QSlider::handle:horizontal {
                background-color: #2196F3;
                border: none;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -5px 0;
            }
            
            QTabWidget::pane {
                border: 1px solid #e5e5e5;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 6px 12px;
                margin-right: 1px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                font-size: 11px;
                font-weight: 400;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            
            QProgressBar {
                border: 1px solid #d0d0d0;
                border-radius: 2px;
                background-color: #f0f0f0;
                height: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 1px;
            }
            
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #fafafa;
                font-size: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                padding: 4px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with minimal spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Minimal header - increased height
        header_widget = self.create_header()
        header_widget.setMinimumHeight(80)  # Increased from 60
        header_widget.setMaximumHeight(100)  # Added maximum height
        main_layout.addWidget(header_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Counting
        counting_tab = self.create_counting_tab()
        self.tab_widget.addTab(counting_tab, "Detection")
        
        # Tab 2: Reports
        self.reports_widget = ReportsWidget()
        self.tab_widget.addTab(self.reports_widget, "Reports")
        
        main_layout.addWidget(self.tab_widget, 1)
    
    def create_header(self):
        """Create header with logo from assets - Fixed to prevent text cropping"""
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e5e5e5;
                padding: 12px 0px;  /* Increased padding */
            }
        """)
        
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(16, 8, 16, 8)  # Increased margins
        header_layout.setSpacing(16)  # Increased spacing
        
        # Logo from assets - bigger size
        logo_label = QLabel()
        try:
            # Try different logo assets in order of preference
            logo_paths = [
                "assets/logo_jjcnormal.png",
                "assets/logo_notext.png", 
                "assets/logoJJCWhite.png",
                "assets/logo launcher.png"
            ]
            
            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    pixmap = QPixmap(logo_path)
                    # Scale logo to larger size
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    logo_loaded = True
                    break
            
            if not logo_loaded:
                # Fallback text logo - bigger size
                logo_label.setText("VC")
                logo_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        font-weight: 700;
                        color: #2196F3;
                        background-color: #f0f8ff;
                        border: 2px solid #2196F3;
                        border-radius: 25px;
                        padding: 12px;
                        min-width: 50px;
                        min-height: 50px;
                    }
                """)
        except Exception as e:
            # Fallback text logo - bigger size
            logo_label.setText("VC")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: 700;
                    color: #2196F3;
                    background-color: #f0f8ff;
                    border: 2px solid #2196F3;
                    border-radius: 25px;
                    padding: 12px;
                    min-width: 50px;
                    min-height: 50px;
                }
            """)
        
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)
        
        # Title section - with proper spacing
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)  # Increased spacing
        
        # Main title - bigger font
        title_label = QLabel("Vehicle Counter")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;  /* Increased from 18px */
                font-weight: 600;
                color: #333;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Subtitle - bigger font
        subtitle = QLabel("YOLO Detection System")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 13px;  /* Increased from 11px */
                color: #666;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle)
        header_layout.addWidget(title_container)
        
        header_layout.addStretch()
        
        # Status indicator - bigger
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;  /* Increased from 14px */
                border: none;
                margin: 0px 12px;  /* Increased margin */
            }
        """)
        header_layout.addWidget(self.status_indicator)
        
        # Simple status - bigger font
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 13px;  /* Increased from 11px */
                border: none;
                margin-right: 8px;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        return header_container

# ... (kode setelahnya tetap sama)
    
    def create_counting_tab(self):
        """Create minimal counting tab"""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Left panel - Controls (compact)
        control_panel = self.create_control_panel()
        control_panel.setMinimumWidth(280)
        control_panel.setMaximumWidth(300)
        layout.addWidget(control_panel)
        
        # Right panel - Video display
        video_panel = self.create_video_panel()
        layout.addWidget(video_panel, 1)
        
        return tab_widget
    
    def create_control_panel(self):
        """Create ultra minimal control panel"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Video Source Section
        source_group = QGroupBox("Source")
        source_layout = QVBoxLayout(source_group)
        source_layout.setSpacing(6)
        
        # Source type
        self.source_type = QComboBox()
        self.source_type.addItems(["Local File", "CCTV Stream", "Webcam", "ASF File"])
        self.source_type.currentTextChanged.connect(self.on_source_type_changed)
        source_layout.addWidget(self.source_type)
        
        # File drop area
        self.drop_area = SimpleDropArea()
        self.drop_area.file_dropped.connect(self.on_video_selected)
        source_layout.addWidget(self.drop_area)
        
        # CCTV input (hidden by default)
        self.cctv_input = QLineEdit()
        self.cctv_input.setPlaceholderText("rtsp://ip:port/stream")
        self.cctv_input.setVisible(False)
        source_layout.addWidget(self.cctv_input)
        
        # Model path
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QLineEdit("weights/best.pt")
        self.model_input.setPlaceholderText("Model path")
        model_layout.addWidget(self.model_input)
        source_layout.addLayout(model_layout)
        
        layout.addWidget(source_group)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(6)
        
        # Playback Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1x", "1.5x", "2x", "4x", "6x", "8x", "10x"])
        self.speed_combo.setCurrentText("1x")
        speed_layout.addWidget(self.speed_combo)
        settings_layout.addLayout(speed_layout)

        # Confidence
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(25)
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
        self.confidence_label = QLabel("0.25")
        self.confidence_label.setMinimumWidth(30)
        conf_layout.addWidget(self.confidence_slider)
        conf_layout.addWidget(self.confidence_label)
        settings_layout.addLayout(conf_layout)
        
        # Line position
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("Line Position:"))
        self.line_position_slider = QSlider(Qt.Horizontal)
        self.line_position_slider.setRange(10, 90)
        self.line_position_slider.setValue(60)
        self.line_position_slider.valueChanged.connect(self.on_line_position_changed)
        self.line_position_label = QLabel("60%")
        self.line_position_label.setMinimumWidth(30)
        line_layout.addWidget(self.line_position_slider)
        line_layout.addWidget(self.line_position_label)
        settings_layout.addLayout(line_layout)
        
        layout.addWidget(settings_group)
        
        # Controls
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(4)
        
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; }")
        self.start_btn.clicked.connect(self.start_processing)
        
        button_row = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_processing)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        
        button_row.addWidget(self.pause_btn)
        button_row.addWidget(self.stop_btn)
        
        self.save_data_btn = QPushButton("Save Data")
        self.save_data_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; }")
        self.save_data_btn.clicked.connect(self.manual_save_data)
        self.save_data_btn.setEnabled(False)
        
        self.reset_btn = QPushButton("Reset Counter")
        self.reset_btn.clicked.connect(self.reset_counter)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addLayout(button_row)
        control_layout.addWidget(self.save_data_btn)
        control_layout.addWidget(self.reset_btn)
        layout.addWidget(control_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Minimal log
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(50)
        self.log_area.setPlaceholderText("System log...")
        layout.addWidget(self.log_area)
        
        layout.addStretch()
        
        return container
    
    def create_video_panel(self):
        """Create minimal video display panel"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel { 
                border: 1px solid #d0d0d0; 
                border-radius: 3px;
                background-color: #fafafa;
            }
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Video preview will appear here")
        layout.addWidget(self.video_label)
        
        # Counter display
        counter_container = QFrame()
        counter_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 8px;
            }
        """)
        counter_layout = QHBoxLayout(counter_container)
        counter_layout.setSpacing(20)
        
        self.total_label = QLabel("Total: 0")
        self.total_label.setStyleSheet("QLabel { font-size: 16px; font-weight: 600; color: #333; border: none; }")
        
        self.up_label = QLabel("Jalur A: 0")
        self.up_label.setStyleSheet("QLabel { font-size: 12px; color: #4CAF50; border: none; }")
        
        self.down_label = QLabel("Jalur B: 0")
        self.down_label.setStyleSheet("QLabel { font-size: 12px; color: #f44336; border: none; }")
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("QLabel { font-size: 10px; color: #666; border: none; }")
        
        counter_layout.addWidget(self.total_label)
        counter_layout.addWidget(self.up_label)
        counter_layout.addWidget(self.down_label)
        counter_layout.addStretch()
        counter_layout.addWidget(self.fps_label)
        
        layout.addWidget(counter_container)
        
        return container
    
    def on_video_selected(self, file_path):
        """Handle video file selection"""
        try:
            if not file_path or not os.path.exists(file_path):
                QMessageBox.warning(self, "Warning", "Invalid file selected!")
                self.drop_area.reset()
                return
            
            if not self._is_video_file(file_path):
                QMessageBox.warning(self, "Warning", "Please select a valid video file!")
                self.drop_area.reset()
                return
            
            self.current_video = file_path
            self.log(f"Video selected: {os.path.basename(file_path)}")
            self.status_label.setText("Video Ready")
            self.update_status_indicator("ready")
            
            # Show file info
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            self.log(f"File size: {file_size_mb:.1f} MB")
            
            # Special info for ASF files
            if file_path.lower().endswith(('.asf', '.wmv')):
                self.log("ASF/WMV file detected - using optimized processing")
                self.log("Note: ASF/WMV files may require additional codec support")
                self.log("Using multiple backends for better ASF compatibility")
                self.log("Debug mode enabled for ASF troubleshooting")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error selecting video: {str(e)}")
            self.log(f"ERROR: {str(e)}")
            self.drop_area.reset()
            self.update_status_indicator("error")
    
    def _is_video_file(self, file_path):
        """Check if file is a valid video file"""
        if not file_path:
            return False
        return file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.asf'))
    
    def update_status_indicator(self, status):
        """Update status indicator color"""
        if hasattr(self, 'status_indicator'):
            if status == "ready":
                self.status_indicator.setStyleSheet("QLabel { color: #4CAF50; font-size: 14px; border: none; margin: 0px 8px; }")
            elif status == "processing":
                self.status_indicator.setStyleSheet("QLabel { color: #FF9800; font-size: 14px; border: none; margin: 0px 8px; }")
            elif status == "paused":
                self.status_indicator.setStyleSheet("QLabel { color: #9E9E9E; font-size: 14px; border: none; margin: 0px 8px; }")
            elif status == "error":
                self.status_indicator.setStyleSheet("QLabel { color: #F44336; font-size: 14px; border: none; margin: 0px 8px; }")
            else:
                self.status_indicator.setStyleSheet("QLabel { color: #4CAF50; font-size: 14px; border: none; margin: 0px 8px; }")
    
    def on_source_type_changed(self, source_type):
        """Handle source type change"""
        self.drop_area.setVisible(source_type in ["Local File", "ASF File"])
        self.cctv_input.setVisible(source_type == "CCTV Stream")
        
        if source_type == "CCTV Stream":
            self.cctv_input.clear()
            self.current_video = None
            self.status_label.setText("Enter CCTV URL")
            self.update_status_indicator("ready")
            self.drop_area.reset()
        elif source_type == "Webcam":
            self.current_video = 0
            self.status_label.setText("Webcam Ready")
            self.update_status_indicator("ready")
            self.drop_area.reset()
        elif source_type == "Local File":
            self.current_video = None
            self.status_label.setText("Select video file")
            self.update_status_indicator("ready")
            self.drop_area.reset()
        elif source_type == "ASF File":
            self.current_video = None
            self.status_label.setText("Select ASF video file")
            self.update_status_indicator("ready")
            # Update drop area label for ASF
            self.drop_area.label.setText("Drop ASF file here or click to select")
            # Reset drop area
            self.drop_area.reset()
            self.log("ASF file mode selected - optimized processing enabled")
    
    def on_confidence_changed(self, value):
        """Handle confidence threshold change"""
        self.confidence_label.setText(f"{value/100:.2f}")
    
    def on_line_position_changed(self, value):
        """Handle line position change"""
        self.line_position_label.setText(f"{value}%")
    
    def start_processing(self):
        """Start video processing"""
        # Handle different source types
        if self.source_type.currentText() == "CCTV Stream":
            cctv_url = self.cctv_input.text().strip()
            if not cctv_url:
                QMessageBox.warning(self, "Warning", "Please enter CCTV URL!")
                return
            self.current_video = cctv_url
            
        elif self.source_type.currentText() == "Webcam":
            self.current_video = 0
            
        elif self.source_type.currentText() == "Local File":
            if not self.current_video:
                QMessageBox.warning(self, "Warning", "Please select a video file!")
                return
        elif self.source_type.currentText() == "ASF File":
            if not self.current_video:
                QMessageBox.warning(self, "Warning", "Please select an ASF video file!")
                return
            # Validate ASF file
            if not self.current_video.lower().endswith(('.asf', '.wmv')):
                QMessageBox.warning(self, "Warning", "Please select a valid ASF/WMV file!")
                return
            
            # Log ASF file info
            self.log(f"ASF file selected: {os.path.basename(self.current_video)}")
            self.log("Using dedicated ASF processor with optimized settings")
            self.log("Debug mode enabled for ASF troubleshooting")
            self.log("Multiple backend support for better ASF compatibility")
        else:
            QMessageBox.warning(self, "Warning", "Please select video source!")
            return
        
        model_path = self.model_input.text().strip()
        if not os.path.exists(model_path):
            QMessageBox.warning(self, "Warning", f"Model file not found: {model_path}")
            return
        
        # Get settings
        line_position = self.line_position_slider.value()
        confidence = self.confidence_slider.value() / 100.0
        
        # Use ASF processor for ASF files, regular processor for others
        if self.source_type.currentText() == "ASF File":
            self.start_asf_processing()
            return  # Exit early for ASF processing
        
        # Create processing thread for non-ASF files
        # Parse playback speed from UI (e.g., "2x" -> 2.0)
        speed_text = getattr(self, 'speed_combo', None).currentText() if hasattr(self, 'speed_combo') else "1x"
        try:
            playback_speed = float(speed_text.replace("x", ""))
        except Exception:
            playback_speed = 1.0

        self.video_thread = VideoProcessor(
            self.current_video, model_path, line_position, confidence, playback_speed=playback_speed
        )
        self.video_thread.frame_ready.connect(self.update_video)
        self.video_thread.count_updated.connect(self.update_counters)
        self.video_thread.progress_updated.connect(self.update_progress)
        self.video_thread.error_occurred.connect(self.show_error)
        self.video_thread.finished_processing.connect(self.on_processing_finished)
        self.video_thread.progress_completed.connect(self.on_progress_completed)
        
        self.video_thread.start()
        
        # Reset counters
        self.frame_count = 0
        self.start_time = None
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.save_data_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Processing...")
        self.update_status_indicator("processing")
        
        self.log("Processing started")
    
    def start_asf_processing(self):
        """Start ASF file processing using dedicated ASF processor"""
        try:
            model_path = self.model_input.text().strip()
            if not os.path.exists(model_path):
                QMessageBox.warning(self, "Warning", f"Model file not found: {model_path}")
                return
            
            self.log("Starting ASF processing with dedicated processor...")
            self.log(f"ASF file: {os.path.basename(self.current_video)}")
            
            # Create ASF processor with debug enabled for troubleshooting
            config = DEFAULT_CONFIG.copy()
            config.set_debug(True)  # Enable debug for ASF troubleshooting
            self.asf_processor = YOLOASFProcessor(model_path, config)
            
            # Update UI for ASF processing
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)  # ASF processor handles pause differently
            self.stop_btn.setEnabled(True)
            self.save_data_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.status_label.setText("Processing ASF...")
            self.update_status_indicator("processing")
            
            # Reset counters
            self.frame_count = 0
            self.start_time = None
            self.current_counts = {'total': 0, 'naik': 0, 'turun': 0}
            
            # Process ASF file with error handling in a separate thread
            self.asf_thread = ASFProcessingThread(self.asf_processor, self.current_video)
            self.asf_thread.processing_completed.connect(self.on_asf_processing_completed)
            self.asf_thread.processing_error.connect(self.on_asf_processing_error)
            self.asf_thread.start()
            
        except Exception as e:
            self.log(f"ASF processing initialization error: {str(e)}")
            QMessageBox.critical(self, "Error", f"ASF processing initialization failed: {str(e)}")
            self.on_processing_finished()
    
    def on_asf_processing_error(self, error_msg):
        """Handle ASF processing error"""
        self.log(f"ASF processing error: {error_msg}")
        QMessageBox.critical(self, "ASF Processing Error", f"Failed to process ASF file: {error_msg}")
        self.on_processing_finished()
    
    def on_asf_processing_completed(self):
        """Handle ASF processing completion"""
        try:
            # Get counts from ASF processor
            if hasattr(self, 'asf_processor') and self.asf_processor.car_counter:
                counts = self.asf_processor.car_counter.counts
                self.current_counts = {
                    'total': counts['total'],
                    'naik': counts['up'],
                    'turun': counts['down']
                }
                
                # Update display
                self.update_counters({
                    'mobil': counts['total'],
                    'Jalur A': counts['up'],
                    'Jalur B': counts['down']
                })
                
                self.log(f"ASF processing completed - Total: {counts['total']}, Up: {counts['up']}, Down: {counts['down']}")
            else:
                self.log("ASF processing completed but no counts available")
                self.current_counts = {'total': 0, 'naik': 0, 'turun': 0}
            
            # Show completion dialog
            self.log("Opening input dialog for ASF data")
            
            dialog = DataInputDialog(self.current_counts, self)
            dialog.data_saved.connect(self.on_data_saved)
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                self.log("ASF data saved successfully")
                if hasattr(self, 'reports_widget'):
                    self.reports_widget.load_data()
            else:
                self.log("ASF dialog cancelled")
                
        except Exception as e:
            self.log(f"Error in ASF completion: {str(e)}")
            QMessageBox.warning(self, "Warning", f"Error in ASF completion: {str(e)}")
        finally:
            self.on_processing_finished()
    
    def pause_processing(self):
        """Pause/resume processing"""
        if self.video_thread:
            self.video_thread.pause()
            if self.video_thread.paused:
                self.pause_btn.setText("Resume")
                self.status_label.setText("Paused")
                self.update_status_indicator("paused")
            else:
                self.pause_btn.setText("Pause")
                self.status_label.setText("Processing...")
                self.update_status_indicator("processing")
    
    def stop_processing(self):
        """Stop processing"""
        if self.video_thread:
            self.video_thread.stop()
        if hasattr(self, 'asf_thread') and self.asf_thread:
            self.asf_thread.terminate()
            self.asf_thread.wait()
        self.on_processing_finished()
    
    def manual_save_data(self):
        """Manual save data"""
        if not hasattr(self, 'current_counts') or not self.current_counts:
            QMessageBox.warning(self, "Warning", "No counting data to save!")
            return
        
        self.save_data_btn.setEnabled(False)
        self.log("Manual save data - Opening input dialog")
        
        try:
            dialog = DataInputDialog(self.current_counts, self)
            dialog.data_saved.connect(self.on_data_saved)
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                self.log("Data saved successfully")
                if hasattr(self, 'reports_widget'):
                    self.reports_widget.load_data()
            else:
                self.log("Dialog cancelled")
                
        except Exception as e:
            self.log(f"Error in manual save: {str(e)}")
        finally:
            if hasattr(self, 'current_counts') and self.current_counts.get('total', 0) > 0:
                self.save_data_btn.setEnabled(True)
    
    def reset_counter(self):
        """Reset vehicle counter"""
        if self.video_thread:
            self.video_thread.reset_counter()
        
        self.update_counters({'mobil': 0, 'Jalur B': 0, 'Jalur A': 0})
        self.current_counts = {'total': 0, 'naik': 0, 'turun': 0}
        self.save_data_btn.setEnabled(False)
        self.log("Counter reset")
        
        self.frame_count = 0
        self.start_time = None
        self.fps_label.setText("FPS: 0")
    
    def update_video(self, qt_image):
        """Update video display"""
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
    
    def update_counters(self, counts):
        """Update counter displays"""
        total = counts.get('mobil', 0)
        up = counts.get('Jalur A', 0)
        down = counts.get('Jalur B', 0)
        
        self.total_label.setText(f"Total: {total}")
        self.up_label.setText(f"Jalur A: {up}")
        self.down_label.setText(f"Jalur B: {down}")
        
        self.current_counts = {
            'total': total,
            'naik': up,
            'turun': down
        }
        
        if total > 0:
            self.save_data_btn.setEnabled(True)
        else:
            self.save_data_btn.setEnabled(False)
        
        # Update FPS
        self.frame_count += 1
        
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed_time = time.time() - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_bar.setValue(progress)
    
    def on_progress_completed(self, counts):
        """Handle progress 100% completion"""
        self.log("Progress 100% - Opening input dialog")
        
        converted_counts = {
            'total': counts.get('mobil', 0),
            'naik': counts.get('Jalur A', 0), 
            'turun': counts.get('Jalur B', 0)
        }
        
        try:
            dialog = DataInputDialog(converted_counts, self)
            dialog.data_saved.connect(self.on_data_saved)
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                self.log("Data saved successfully")
                if hasattr(self, 'reports_widget'):
                    self.reports_widget.load_data()
            else:
                self.log("Progress dialog cancelled")
                
        except Exception as e:
            self.log(f"Error in progress completed: {str(e)}")
    
    def on_data_saved(self, data):
        """Handle data saved signal"""
        self.log(f"Data saved: {data['tanggal']} - Total: {data['total']}")
        
        if hasattr(self, 'current_counts') and self.current_counts.get('total', 0) > 0:
            self.save_data_btn.setEnabled(True)
    
    def on_processing_finished(self):
        """Handle processing finished"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(False)
        
        if hasattr(self, 'current_counts') and self.current_counts.get('total', 0) > 0:
            self.save_data_btn.setEnabled(True)
        else:
            self.save_data_btn.setEnabled(False)
            
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Finished")
        self.update_status_indicator("ready")
        
        self.log("Processing finished")
        self.video_thread = None
    
    def show_error(self, error_msg):
        """Show error message"""
        QMessageBox.critical(self, "Error", error_msg)
        self.log(f"ERROR: {error_msg}")
        self.update_status_indicator("error")
        self.on_processing_finished()
    
    def log(self, message):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.video_thread:
            self.video_thread.stop()
        if hasattr(self, 'asf_thread') and self.asf_thread:
            self.asf_thread.terminate()
            self.asf_thread.wait()
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Vehicle Counter")
    app.setApplicationVersion("2.1")
    
    app.setStyle('Fusion')
    
    window = CarCounterApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()