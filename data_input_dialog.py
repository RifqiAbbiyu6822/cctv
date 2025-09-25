"""
Dialog untuk input data kilometer, tanggal, dan periode jam
Muncul ketika progress 100% atau stop counting
Enhanced version dengan UI yang lebih modern
"""

import sys
import os
from datetime import datetime, date
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QDateEdit, QTimeEdit,
                             QFormLayout, QGroupBox, QMessageBox, QComboBox,
                             QFrame, QTextEdit, QScrollArea, QWidget, 
                             QSizePolicy, QSpacerItem, QGridLayout)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

class ModernCard(QFrame):
    """Widget kartu modern dengan shadow effect"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Layout utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Title jika ada
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            layout.addWidget(title_label)
        
        # Container untuk konten
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)
        
        # Styling
        self.setStyleSheet("""
            ModernCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
            }
            
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 8px;
            }
        """)
    
    def addWidget(self, widget):
        self.content_layout.addWidget(widget)
    
    def addLayout(self, layout):
        self.content_layout.addLayout(layout)

class ModernInput(QWidget):
    """Input field modern dengan label"""
    
    def __init__(self, label_text, widget, helper_text="", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Label
        label = QLabel(label_text)
        label.setObjectName("inputLabel")
        layout.addWidget(label)
        
        # Widget input
        self.input_widget = widget
        layout.addWidget(widget)
        
        # Helper text
        if helper_text:
            helper = QLabel(helper_text)
            helper.setObjectName("helperText")
            layout.addWidget(helper)
        
        # Styling
        self.setStyleSheet("""
            QLabel#inputLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
                margin-bottom: 2px;
            }
            
            QLabel#helperText {
                font-size: 11px;
                color: #6b7280;
                margin-top: 2px;
            }
        """)
class SummaryCard(QWidget):
    """Kartu ringkasan dengan statistik"""
    
    def __init__(self, title, value, subtitle="", color="#4f46e5", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("summaryTitle")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setObjectName("summaryValue")
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("summarySubtitle")
            layout.addWidget(subtitle_label)
        
        # Styling
        self.setStyleSheet("""
            SummaryCard {
                background-color: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            
            QLabel#summaryTitle {
                font-size: 11px;
                font-weight: 500;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QLabel#summarySubtitle {
                font-size: 12px;
                color: #64748b;
            }
        """)

class DataInputDialog(QDialog):
    """Dialog untuk input data counting dengan UI modern"""
    
    data_saved = pyqtSignal(dict)  # Signal ketika data berhasil disimpan
    
    def __init__(self, counting_data, parent=None):
        """
        Inisialisasi dialog input data
        
        Args:
            counting_data: Dictionary berisi data counting (total, naik, turun)
            parent: Parent widget
        """
        super().__init__(parent)
        self.counting_data = counting_data
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup UI dialog dengan desain modern"""
        self.setWindowTitle("Simpan Data Counting")
        self.setFixedSize(520, 650)
        self.setModal(True)
        
        # Set icon
        try:
            icon_path = "assets/logo launcher.png"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        # Main styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f1f5f9;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
            }
            
            QLineEdit, QDateEdit, QTimeEdit, QComboBox {
                padding: 12px 16px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
                color: #1f2937;
            }
            
            QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
                border-color: #4f46e5;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
                outline: none;
            }
            
            QTextEdit {
                padding: 12px 16px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                color: #1f2937;
            }
            
            QTextEdit:focus {
                border-color: #4f46e5;
                outline: none;
            }
            
            QPushButton {
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                min-height: 20px;
                cursor: pointer;
            }
            
            QPushButton:hover {
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                transform: translateY(0px);
            }
            
            QPushButton:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
        """)
        
        # Scroll area untuk konten
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget
        container = QWidget()
        scroll.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Container layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header Section
        self.create_header_section(layout)
        
        # Summary Section
        self.create_summary_section(layout)
        
        # Input Section
        self.create_input_section(layout)
        
        # Notes Section
        self.create_notes_section(layout)
        
        # Button Section
        self.create_button_section(layout)
        
        # Add stretch
        layout.addStretch()
        
        # Initial validation
        self.validate_input()
    
    def create_header_section(self, parent_layout):
        """Buat section header"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # Title
        title_label = QLabel("Simpan Data Counting")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
        """)
        
        # Subtitle
        subtitle_label = QLabel("Lengkapi informasi berikut untuk menyimpan hasil counting")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 15px;
            color: #6b7280;
            margin: 0;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addWidget(header_widget)
    
    def create_summary_section(self, parent_layout):
        """Buat section ringkasan data"""
        summary_card = ModernCard("Ringkasan Counting")
        
        # Grid layout untuk summary cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        # Total card
        total_card = SummaryCard(
            "Total Kendaraan", 
            self.counting_data.get('total', 0),
            "Kendaraan tercatat",
            "#1f2937"
        )
        
        # Jalur A card (Naik)
        naik_card = SummaryCard(
            "Jalur A (Naik)", 
            self.counting_data.get('naik', 0),
            "Naik",
            "#10b981"
        )
        
        # Jalur B card (Turun)
        turun_card = SummaryCard(
            "Jalur B (Turun)", 
            self.counting_data.get('turun', 0),
            "Turun", 
            "#ef4444"
        )
        
        grid_layout.addWidget(total_card, 0, 0, 1, 2)
        grid_layout.addWidget(naik_card, 1, 0)
        grid_layout.addWidget(turun_card, 1, 1)
        
        summary_card.addLayout(grid_layout)
        parent_layout.addWidget(summary_card)
    
    def create_input_section(self, parent_layout):
        """Buat section input data"""
        input_card = ModernCard("Informasi Lokasi & Waktu")
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Kilometer input
        self.kilometer_input = QLineEdit()
        self.kilometer_input.setPlaceholderText("Contoh: 12+100")
        self.kilometer_input.setText("12+100")
        
        kilometer_widget = ModernInput(
            "Kilometer Jalan Tol", 
            self.kilometer_input,
            "Format: [KM]+[Meter] (contoh: 12+100)"
        )
        form_layout.addWidget(kilometer_widget)
        
        # Tanggal input
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dddd, dd MMMM yyyy")
        
        date_widget = ModernInput(
            "Tanggal Counting", 
            self.date_input,
            "Pilih tanggal pelaksanaan counting"
        )
        form_layout.addWidget(date_widget)
        
        # Periode jam
        time_container = QWidget()
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(12)
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(19, 0))
        self.start_time.setDisplayFormat("HH:mm")
        
        time_separator = QLabel("—")
        time_separator.setAlignment(Qt.AlignCenter)
        time_separator.setStyleSheet("font-size: 16px; color: #6b7280; font-weight: 600;")
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(12, 0))
        self.end_time.setDisplayFormat("HH:mm")
        
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(time_separator)
        time_layout.addWidget(self.end_time)
        
        time_widget = ModernInput(
            "Periode Counting", 
            time_container,
            "Waktu mulai dan selesai counting"
        )
        form_layout.addWidget(time_widget)
        
        input_card.addLayout(form_layout)
        parent_layout.addWidget(input_card)
    
    def create_notes_section(self, parent_layout):
        """Buat section catatan"""
        notes_card = ModernCard("Catatan Tambahan")
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Tambahkan catatan atau observasi khusus dari hasil counting ini...")
        
        notes_widget = ModernInput(
            "Catatan (Opsional)", 
            self.notes_input,
            "Informasi tambahan yang relevan dengan hasil counting"
        )
        
        notes_card.addWidget(notes_widget)
        parent_layout.addWidget(notes_card)
    
    def create_button_section(self, parent_layout):
        """Buat section tombol"""
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 12, 0, 0)
        button_layout.setSpacing(12)
        
        # Cancel button
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6b7280;
                border: 2px solid #d1d5db;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Save button
        self.save_btn = QPushButton("💾 Simpan ke Spreadsheet")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
            }
            QPushButton:hover:enabled {
                background-color: #4338ca;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.save_btn.clicked.connect(self.save_data)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addWidget(button_container)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.kilometer_input.textChanged.connect(self.validate_input)
        self.date_input.dateChanged.connect(self.validate_input)
    
    def validate_input(self):
        """Validasi input data dengan visual feedback"""
        # Validate kilometer format
        kilometer_text = self.kilometer_input.text().strip()
        is_kilometer_valid = self.validate_kilometer_format(kilometer_text)
        
        # Validate date
        is_date_valid = self.date_input.date().isValid()
        
        # Enable/disable save button
        self.save_btn.setEnabled(is_kilometer_valid and is_date_valid)
        
        # Update styling based on validation
        if is_kilometer_valid:
            self.kilometer_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #10b981;
                    background-color: #f0fdf4;
                }
            """)
        elif kilometer_text:  # Only show error if there's text
            self.kilometer_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #ef4444;
                    background-color: #fef2f2;
                }
            """)
        else:
            self.kilometer_input.setStyleSheet("")  # Reset to default
    
    def validate_kilometer_format(self, kilometer_text):
        """
        Validasi format kilometer (12+100)
        
        Args:
            kilometer_text: Text input kilometer
            
        Returns:
            bool: True jika format valid
        """
        if not kilometer_text:
            return False
        
        try:
            # Check if contains '+' and has valid numbers
            if '+' not in kilometer_text:
                return False
            
            parts = kilometer_text.split('+')
            if len(parts) != 2:
                return False
            
            # Try to convert to integers
            int(parts[0])
            int(parts[1])
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def save_data(self):
        """Simpan data ke spreadsheet"""
        try:
            # Validate input again
            if not self.validate_kilometer_format(self.kilometer_input.text().strip()):
                QMessageBox.warning(
                    self, 
                    "Format Tidak Valid", 
                    "Format kilometer tidak valid!\n\nGunakan format: [KM]+[Meter]\nContoh: 12+100"
                )
                return
            
            # Prepare data with proper conversion
            data = {
                'tanggal': self.date_input.date().toString("yyyy-MM-dd"),
                'kilometer': self.kilometer_input.text().strip(),
                'periode_jam': f"{self.start_time.time().toString('HH:mm')}-{self.end_time.time().toString('HH:mm')}",
                'total': int(self.counting_data.get('total', 0)),
                'naik': int(self.counting_data.get('naik', 0)),
                'turun': int(self.counting_data.get('turun', 0)),
                'deskripsi': self.notes_input.toPlainText().strip()
            }
            
            print(f"Data yang akan disimpan: {data}")  # Debug log
            print(f"Counting data original: {self.counting_data}")  # Debug log
            
            # Import and use Google Sheets manager
            from google_sheets_helper import GoogleSheetsManager
            
            # Initialize and authenticate
            sheets_manager = GoogleSheetsManager()
            if not sheets_manager.authenticate():
                QMessageBox.critical(
                    self, 
                    "Koneksi Gagal", 
                    "Tidak dapat mengakses Google Sheets!\n\n"
                    "Pastikan:\n"
                    "• File credentials.json sudah dikonfigurasi\n"
                    "• Koneksi internet tersedia\n"
                    "• Akun Google memiliki akses ke spreadsheet"
                )
                return
            
            # Cek duplikasi waktu + tanggal + kilometer
            if sheets_manager.check_duplicate_time(data['tanggal'], data['periode_jam'], data['kilometer']):
                QMessageBox.warning(
                    self,
                    "Duplikasi Waktu",
                    "Sudah ada data dengan tanggal, periode jam, dan kilometer yang sama.\n"
                    "Silakan ubah jam atau tanggal, lalu simpan kembali."
                )
                # Kembali ke dialog tanpa menutup
                self.save_btn.setText("💾 Simpan ke Spreadsheet")
                self.save_btn.setEnabled(True)
                return
            
            # Show loading state
            self.save_btn.setText("⏳ Menyimpan...")
            self.save_btn.setEnabled(False)
            
            # Save data
            if sheets_manager.save_counting_data(data):
                QMessageBox.information(
                    self, 
                    "✅ Berhasil Disimpan", 
                    "Data counting berhasil disimpan ke Google Spreadsheet!\n\n"
                    f"Total: {data['total']} kendaraan\n"
                    f"Tanggal: {data['tanggal']}\n"
                    f"Lokasi: KM {data['kilometer']}"
                )
                
                # Emit signal
                self.data_saved.emit(data)
                
                # Close dialog
                self.accept()
            else:
                QMessageBox.critical(
                    self, 
                    "❌ Gagal Menyimpan", 
                    "Tidak dapat menyimpan data ke spreadsheet!\n\n"
                    "Silakan coba lagi atau periksa koneksi internet."
                )
                
                # Reset button
                self.save_btn.setText("💾 Simpan ke Spreadsheet")
                self.save_btn.setEnabled(True)
                
        except Exception as e:
            # Reset button
            self.save_btn.setText("💾 Simpan ke Spreadsheet")
            self.save_btn.setEnabled(True)
            
            QMessageBox.critical(
                self, 
                "❌ Terjadi Kesalahan", 
                f"Terjadi kesalahan saat menyimpan data:\n\n{str(e)}\n\n"
                "Silakan coba lagi atau hubungi administrator."
            )
    
    def get_input_data(self):
        """Ambil data input untuk testing"""
        return {
            'tanggal': self.date_input.date().toString("yyyy-MM-dd"),
            'kilometer': self.kilometer_input.text().strip(),
            'periode_jam': f"{self.start_time.time().toString('HH:mm')}-{self.end_time.time().toString('HH:mm')}",
            'total': self.counting_data.get('total', 0),
            'naik': self.counting_data.get('naik', 0),
            'turun': self.counting_data.get('turun', 0),
            'notes': self.notes_input.toPlainText().strip()
        }

if __name__ == "__main__":
    # Test dialog
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test data
    test_counting_data = {
        'total': 1247,
        'naik': 623,
        'turun': 624
    }
    
    dialog = DataInputDialog(test_counting_data)
    dialog.show()
    
    sys.exit(app.exec_())