"""
Updated Reports Widget with Compact Professional PDF
Using the new CompactPDFService for better layout
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

import sys
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QGroupBox, QFormLayout, QFrame,
                             QScrollArea, QGridLayout, QProgressBar, QMessageBox,
                             QHeaderView, QSplitter, QFileDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

# Import the new compact PDF service
from pdf_service import CompactPDFService

class DataVisualizationCanvas(FigureCanvas):
    """Canvas untuk visualisasi data dengan matplotlib - Layout yang tidak gepeng"""
    
    def __init__(self, parent=None):
        # Perbesar figsize dan tingkatkan DPI untuk kualitas yang lebih baik
        self.figure = Figure(figsize=(12, 8), dpi=120)
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Set basic style
        plt.style.use('default')
        
        # Set minimum size untuk canvas
        self.setMinimumSize(800, 600)
        
        # Connect resize event untuk responsive sizing
        self.resizeEvent = self.on_resize
        
    def plot_daily_traffic(self, data):
        """Plot traffic harian dengan visualisasi standar"""
        self.figure.clear()
        
        if not data or len(data) == 0:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Tidak ada data untuk ditampilkan', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Data Traffic Harian', fontsize=12, fontweight='bold')
            self.draw()
            return
        
        # Prepare data
        dates = []
        totals = []
        ups = []
        downs = []
        
        for record in data:
            try:
                date_str = record.get('Tanggal', '')
                if not date_str or date_str.strip() == '':
                    continue
                    
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                total_val = record.get('Total', 0)
                up_val = record.get('Jalur A', record.get('Naik', 0))
                down_val = record.get('Jalur B', record.get('Turun', 0))
                
                try:
                    total_int = int(total_val) if total_val not in [None, '', '0'] else 0
                    up_int = int(up_val) if up_val not in [None, '', '0'] else 0
                    down_int = int(down_val) if down_val not in [None, '', '0'] else 0
                except (ValueError, TypeError):
                    total_int, up_int, down_int = 0, 0, 0
                
                dates.append(date_obj)
                totals.append(total_int)
                ups.append(up_int)
                downs.append(down_int)
            except Exception as e:
                print(f"Error processing record: {e}")
                continue
        
        if not dates:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Data tidak valid untuk ditampilkan', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Data Traffic Harian', fontsize=12, fontweight='bold')
            self.draw()
            return
        
        # Create responsive grid layout dengan aspect ratio yang tepat
        fig = self.figure
        fig.clear()
        
        # Buat grid layout yang lebih responsif - 2x2 dengan spacing yang tepat
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3, 
                             left=0.08, right=0.95, top=0.93, bottom=0.08)
        
        # Main traffic line chart - Top row, span 2 columns
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(dates, totals, marker='o', linewidth=3, markersize=6, color='#2E7D32', label='Total Kendaraan')
        ax1.fill_between(dates, totals, alpha=0.2, color='#4CAF50')
        ax1.set_title('Total Kendaraan Harian', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('Jumlah Kendaraan', fontsize=12)
        ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax1.legend(fontsize=11, loc='upper left')
        
        # Format x-axis dengan spacing yang lebih baik
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        if len(dates) > 10:
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//8)))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, fontsize=10)
        
        # Pie chart - Bottom left dengan aspect ratio yang tepat
        ax2 = fig.add_subplot(gs[1, 0])
        total_up = sum(ups)
        total_down = sum(downs)
        if total_up + total_down > 0:
            sizes = [total_up, total_down]
            labels = ['Jalur A', 'Jalur B']
            colors = ['#2196F3', '#FF5722']
            
            wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90,
                                             textprops={'fontsize': 10})
            ax2.set_title('Distribusi Arah', fontsize=12, fontweight='bold', pad=15)
            
            # Styling untuk pie chart
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('500')
        else:
            ax2.text(0.5, 0.5, 'Tidak ada\ndata', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12, color='#666')
            ax2.set_title('Distribusi Arah', fontsize=12, fontweight='bold', pad=15)
        
        # Bar chart - Bottom right dengan spacing yang lebih baik
        ax3 = fig.add_subplot(gs[1, 1])
        width = 0.35
        x_pos = np.arange(len(dates))
        
        bars1 = ax3.bar([d - width/2 for d in x_pos], ups, width, label='Jalur A', 
                       color='#2196F3', alpha=0.8, edgecolor='white', linewidth=0.5)
        bars2 = ax3.bar([d + width/2 for d in x_pos], downs, width, label='Jalur B', 
                       color='#FF5722', alpha=0.8, edgecolor='white', linewidth=0.5)
        
        ax3.set_title('Perbandingan Traffic', fontsize=12, fontweight='bold', pad=15)
        ax3.set_ylabel('Jumlah', fontsize=11)
        ax3.set_xlabel('Tanggal', fontsize=11)
        ax3.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
        ax3.legend(fontsize=10, loc='upper right')
        
        # Format x-axis untuk bar chart dengan spacing yang lebih baik
        step = max(1, len(dates)//6)
        ax3.set_xticks(x_pos[::step])
        ax3.set_xticklabels([dates[i].strftime('%d/%m') for i in range(0, len(dates), step)], 
                           rotation=45, fontsize=9)
        
        # Tambahkan value labels pada bar chart jika tidak terlalu banyak data
        if len(dates) <= 10:
            for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                height1 = bar1.get_height()
                height2 = bar2.get_height()
                if height1 > 0:
                    ax3.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.1,
                            f'{int(height1)}', ha='center', va='bottom', fontsize=8)
                if height2 > 0:
                    ax3.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.1,
                            f'{int(height2)}', ha='center', va='bottom', fontsize=8)
        
        # Apply tight layout dengan padding yang tepat
        plt.tight_layout(pad=2.0)
        self.draw()
    
    def on_resize(self, event):
        """Handle resize event untuk responsive canvas"""
        if hasattr(self, 'figure') and self.figure:
            # Adjust DPI based on size untuk menjaga kualitas
            size = self.size()
            width = size.width()
            height = size.height()
            
            # Calculate appropriate DPI
            base_dpi = 100
            scale_factor = min(width / 800, height / 600, 2.0)  # Max 2x scaling
            new_dpi = int(base_dpi * scale_factor)
            
            # Update figure DPI if significantly different
            if abs(new_dpi - self.figure.dpi) > 10:
                self.figure.dpi = new_dpi
                self.draw()
        
        # Call parent resize event
        super().resizeEvent(event)

class DataLoaderThread(QThread):
    """Thread untuk loading data dari Google Sheets"""
    data_loaded = pyqtSignal(list)
    stats_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, start_date=None, end_date=None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self):
        try:
            from google_sheets_helper import GoogleSheetsManager
            
            manager = GoogleSheetsManager()
            if not manager.authenticate():
                self.error_occurred.emit("Gagal mengakses Google Sheets!")
                return
            
            if self.start_date and self.end_date:
                data = manager.get_data_by_date_range(self.start_date, self.end_date)
            else:
                data = manager.get_all_data()
            
            stats = self.calculate_filtered_stats(data)
            
            self.data_loaded.emit(data)
            self.stats_loaded.emit(stats)
            
        except Exception as e:
            self.error_occurred.emit(f"Error loading data: {str(e)}")
    
    def calculate_filtered_stats(self, data):
        """Hitung statistik berdasarkan data yang sudah difilter"""
        if not data:
            return {
                'total_records': 0,
                'total_vehicles': 0,
                'total_up': 0,
                'total_down': 0,
                'average_per_day': 0,
                'unique_dates': 0
            }
        
        valid_data = []
        for record in data:
            if record and isinstance(record, dict):
                if any(str(record.get(key, '')).strip() for key in ['Tanggal', 'Total', 'Jalur A', 'Jalur B']):
                    valid_data.append(record)
        
        if not valid_data:
            return {
                'total_records': 0,
                'total_vehicles': 0,
                'total_up': 0,
                'total_down': 0,
                'average_per_day': 0,
                'unique_dates': 0
            }
        
        total_records = len(valid_data)
        total_vehicles = 0
        total_up = 0
        total_down = 0
        
        for record in valid_data:
            try:
                total_val = record.get('Total', 0)
                up_val = record.get('Jalur A', record.get('Naik', 0))
                down_val = record.get('Jalur B', record.get('Turun', 0))
                
                total_vehicles += int(total_val) if total_val not in [None, '', '0'] else 0
                total_up += int(up_val) if up_val not in [None, '', '0'] else 0
                total_down += int(down_val) if down_val not in [None, '', '0'] else 0
            except (ValueError, TypeError):
                continue
        
        dates = set()
        for record in valid_data:
            date_str = record.get('Tanggal', '')
            if date_str and date_str.strip():
                dates.add(date_str)
        
        unique_dates = len(dates) if dates else 1
        average_per_day = total_vehicles / unique_dates if unique_dates > 0 else 0
        
        return {
            'total_records': total_records,
            'total_vehicles': total_vehicles,
            'total_up': total_up,
            'total_down': total_down,
            'average_per_day': round(average_per_day, 2),
            'unique_dates': unique_dates
        }

class ReportsWidget(QWidget):
    """Widget utama untuk tab laporan dengan compact PDF
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_loader_thread = None
        self.current_data = []
        self.current_stats = {}
        self.pdf_service = CompactPDFService()  # Initialize compact PDF service
        self.setup_ui()
        self.setup_connections()
        
        # Auto-load data on startup
        QTimer.singleShot(1000, self.load_data)
    
    def setup_ui(self):
        """Setup UI untuk reports widget dengan layout yang tidak gepeng"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Header
        header_label = QLabel("Laporan & Visualisasi Data")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Controls
        controls_group = QGroupBox("Filter & Kontrol")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(10)
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Dari:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Sampai:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.end_date)
        
        controls_layout.addLayout(date_layout)
        
        # Buttons
        self.load_btn = QPushButton("Muat Data")
        self.load_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; }")
        self.load_btn.clicked.connect(self.load_data)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px 16px; }")
        self.refresh_btn.clicked.connect(self.load_data)
        
        controls_layout.addWidget(self.load_btn)
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addStretch()
        
        main_layout.addWidget(controls_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Statistics
        left_panel = self.create_stats_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Charts
        right_panel = self.create_charts_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions - berikan lebih banyak ruang untuk visualisasi
        splitter.setSizes([250, 950])  # Stats panel lebih kecil, charts panel lebih besar
        splitter.setStretchFactor(0, 0)  # Stats panel tidak stretch
        splitter.setStretchFactor(1, 1)  # Charts panel dapat stretch
        main_layout.addWidget(splitter, 1)  # Stretch factor untuk responsiveness
        
        # Data table dengan height yang terbatas
        table_group = QGroupBox("Data Detail")
        table_layout = QVBoxLayout(table_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(9)
        self.data_table.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Kilometer", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi", "Waktu Input"
        ])
        
        # Set table properties
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Batasi tinggi tabel agar tidak mengambil terlalu banyak ruang
        self.data_table.setMaximumHeight(200)
        self.data_table.setMinimumHeight(150)
        
        table_layout.addWidget(self.data_table)
        main_layout.addWidget(table_group, 0)  # No stretch untuk table
    
    def create_stats_panel(self):
        """Buat panel statistik"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Summary stats
        stats_group = QGroupBox("Ringkasan Statistik")
        stats_layout = QFormLayout(stats_group)
        
        self.total_records_label = QLabel("0")
        self.total_records_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #333;")
        
        self.total_vehicles_label = QLabel("0")
        self.total_vehicles_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #4CAF50;")
        
        self.total_up_label = QLabel("0")
        self.total_up_label.setStyleSheet("font-size: 14px; color: #2196F3;")
        
        self.total_down_label = QLabel("0")
        self.total_down_label.setStyleSheet("font-size: 14px; color: #FF5722;")
        
        self.average_label = QLabel("0")
        self.average_label.setStyleSheet("font-size: 14px; color: #FF9800;")
        
        self.unique_dates_label = QLabel("0")
        self.unique_dates_label.setStyleSheet("font-size: 12px; color: #666;")
        
        stats_layout.addRow("Total Record:", self.total_records_label)
        stats_layout.addRow("Total Kendaraan:", self.total_vehicles_label)
        stats_layout.addRow("Total Jalur A:", self.total_up_label)
        stats_layout.addRow("Total Jalur B:", self.total_down_label)
        stats_layout.addRow("Rata-rata/hari:", self.average_label)
        stats_layout.addRow("Hari Unik:", self.unique_dates_label)
        
        layout.addWidget(stats_group)
        
        # Quick actions with updated PDF options
        actions_group = QGroupBox("Aksi Cepat")
        actions_layout = QVBoxLayout(actions_group)
        
        self.export_btn = QPushButton("Export Data (Excel)")
        self.export_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; padding: 8px; }")
        self.export_btn.clicked.connect(self.export_data)
        
        self.export_pdf_btn = QPushButton("Export PDF (Lengkap)")
        self.export_pdf_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-weight: bold; }")
        self.export_pdf_btn.clicked.connect(self.export_complete_pdf)
        
        actions_layout.addWidget(self.export_btn)
        actions_layout.addWidget(self.export_pdf_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return panel
    
    def create_charts_panel(self):
        """Buat panel chart dengan layout responsif yang tidak gepeng"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Chart tabs dengan styling yang lebih baik
        chart_group = QGroupBox("Visualisasi Data")
        chart_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 8px;
                color: #333;
                font-size: 14px;
                font-weight: 600;
                background-color: #fafafa;
            }
        """)
        
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.setContentsMargins(10, 15, 10, 10)
        chart_layout.setSpacing(10)
        
        # Chart canvas dengan sizing yang tepat
        self.chart_canvas = DataVisualizationCanvas(self)
        self.chart_canvas.setStyleSheet("""
            DataVisualizationCanvas {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
            }
        """)
        
        # Set minimum dan maximum size untuk canvas
        self.chart_canvas.setMinimumSize(800, 600)
        self.chart_canvas.setMaximumSize(1600, 1200)
        
        chart_layout.addWidget(self.chart_canvas, 1)  # Stretch factor 1 untuk responsiveness
        
        layout.addWidget(chart_group, 1)  # Stretch factor 1
        
        return panel
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def load_data(self):
        """Load data dari Google Sheets"""
        if self.data_loader_thread and self.data_loader_thread.isRunning():
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Disable buttons
        self.load_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        
        # Get date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Create and start thread
        self.data_loader_thread = DataLoaderThread(start_date, end_date)
        self.data_loader_thread.data_loaded.connect(self.on_data_loaded)
        self.data_loader_thread.stats_loaded.connect(self.on_stats_loaded)
        self.data_loader_thread.error_occurred.connect(self.on_error)
        self.data_loader_thread.finished.connect(self.on_loading_finished)
        self.data_loader_thread.start()
    
    def on_data_loaded(self, data):
        """Handle data loaded signal"""
        valid_data = []
        for record in data:
            if record and isinstance(record, dict):
                if any(str(record.get(key, '')).strip() for key in ['Tanggal', 'Total', 'Jalur A', 'Jalur B']):
                    valid_data.append(record)
        
        self.current_data = valid_data
        self.update_data_table(valid_data)
        self.update_charts(valid_data)
    
    def on_stats_loaded(self, stats):
        """Handle stats loaded signal"""
        self.current_stats = stats
        self.update_stats_display(stats)
    
    def on_error(self, error_msg):
        """Handle error signal"""
        QMessageBox.critical(self, "Error", error_msg)
    
    def on_loading_finished(self):
        """Handle loading finished"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
    
    def update_data_table(self, data):
        """Update data table dengan data baru"""
        if not data:
            self.data_table.setRowCount(0)
            return
            
        self.data_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            if not record or not isinstance(record, dict):
                continue
                
            self.data_table.setItem(row, 0, QTableWidgetItem(str(record.get('ID', '') or '')))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(record.get('Tanggal', '') or '')))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(record.get('Kilometer', '') or '')))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(record.get('Periode Jam', '') or '')))
            
            total = record.get('Total', 0)
            jalur_a = record.get('Jalur A', record.get('Naik', 0))
            jalur_b = record.get('Jalur B', record.get('Turun', 0))
            
            self.data_table.setItem(row, 4, QTableWidgetItem(str(total if total not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(jalur_a if jalur_a not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 6, QTableWidgetItem(str(jalur_b if jalur_b not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 7, QTableWidgetItem(str(record.get('Deskripsi', '') or '')))
            self.data_table.setItem(row, 8, QTableWidgetItem(str(record.get('Waktu Input', '') or '')))
    
    def update_stats_display(self, stats):
        """Update display statistik"""
        if not stats or not isinstance(stats, dict):
            self.total_records_label.setText("0")
            self.total_vehicles_label.setText("0")
            self.total_up_label.setText("0")
            self.total_down_label.setText("0")
            self.average_label.setText("0")
            self.unique_dates_label.setText("0")
            return
        
        self.total_records_label.setText(f"{stats.get('total_records', 0) or 0:,}")
        self.total_vehicles_label.setText(f"{stats.get('total_vehicles', 0) or 0:,}")
        self.total_up_label.setText(f"{stats.get('total_up', 0) or 0:,}")
        self.total_down_label.setText(f"{stats.get('total_down', 0) or 0:,}")
        self.average_label.setText(f"{stats.get('average_per_day', 0) or 0:,.1f}")
        self.unique_dates_label.setText(f"{stats.get('unique_dates', 0) or 0:,}")
    
    def update_charts(self, data):
        """Update charts dengan data baru"""
        self.chart_canvas.plot_daily_traffic(data)
    
    def export_data(self):
        """Export data ke Excel (.xlsx)"""
        if not self.current_data:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk diekspor!")
            return
        
        try:
            import pandas as pd

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Data (Excel)", f"counting_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if filename:
                df = pd.DataFrame(self.current_data)
                columns_order = ["ID", "Tanggal", "Kilometer", "Periode Jam", "Total", "Jalur A", "Jalur B", "Deskripsi", "Waktu Input"]
                columns = [c for c in columns_order if c in df.columns]
                df = df.reindex(columns=columns)
                df.to_excel(filename, index=False)

                QMessageBox.information(self, "Berhasil", f"Data berhasil diekspor ke: {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
    
    def export_complete_pdf(self):
        """Export PDF lengkap dengan semua fitur dalam satu dokumen"""
        if not self.current_data:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk dibuatkan laporan!")
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Simpan Laporan PDF Lengkap", f"complete_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf);;All Files (*)"
            )
            if not filename:
                return

            # Get date range
            date_range = f"{self.start_date.date().toString('yyyy-MM-dd')} s/d {self.end_date.date().toString('yyyy-MM-dd')}"
            
            # Generate complete PDF
            success = self.pdf_service.generate_complete_pdf(
                self.current_data, 
                self.current_stats, 
                filename, 
                date_range
            )
            
            if success:
                QMessageBox.information(self, "Berhasil", f"Laporan PDF lengkap berhasil dibuat: {filename}")
            else:
                QMessageBox.warning(self, "Peringatan", "Gagal membuat PDF lengkap. Periksa data dan coba lagi.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat PDF lengkap: {str(e)}")

if __name__ == "__main__":
    # Test reports widget
    from PyQt5.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Reports Widget - Compact PDF Version")
    window.setGeometry(100, 100, 1200, 800)
    
    reports_widget = ReportsWidget()
    window.setCentralWidget(reports_widget)
    
    window.show()
    
    sys.exit(app.exec_())