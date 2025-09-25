"""
Widget untuk tab laporan dan visualisasi data dari Google Spreadsheet
"""

import sys
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QGroupBox, QFormLayout, QFrame,
                             QScrollArea, QGridLayout, QProgressBar, QMessageBox,
                             QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from collections import defaultdict
import numpy as np

class DataVisualizationCanvas(FigureCanvas):
    """Canvas untuk visualisasi data dengan matplotlib"""
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 6), dpi=100)  # Ukuran optimal untuk A4
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Set style
        plt.style.use('default')
        
    def plot_daily_traffic(self, data):
        """Plot traffic harian dengan visualisasi modern"""
        self.figure.clear()
        
        if not data or len(data) == 0:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Tidak ada data untuk ditampilkan', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Data Traffic Harian', fontsize=12, fontweight='bold')
            self.draw()
            return
        
        # Prepare data - filter out invalid/empty records
        dates = []
        totals = []
        ups = []
        downs = []
        
        for record in data:
            try:
                # Skip records with empty or invalid dates
                date_str = record.get('Tanggal', '')
                if not date_str or date_str.strip() == '':
                    continue
                    
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Handle null/empty values for numeric fields
                total_val = record.get('Total', 0)
                # Baca kolom baru Jalur A/B atau fallback ke Naik/Turun jika lama
                up_val = record.get('Jalur A', record.get('Naik', 0))
                down_val = record.get('Jalur B', record.get('Turun', 0))
                
                # Convert to integers, default to 0 if invalid
                try:
                    total_int = int(total_val) if total_val not in [None, '', '0'] else 0
                    up_int = int(up_val) if up_val not in [None, '', '0'] else 0
                    down_int = int(down_val) if down_val not in [None, '', '0'] else 0
                except (ValueError, TypeError):
                    total_int, up_int, down_int = 0, 0, 0
                
                # Only add if we have valid data
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
        
        # Set modern style
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('seaborn')
        
        # Create subplots dengan layout grid 2x2 yang lebih compact untuk A4
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1], 
                                    hspace=0.25, wspace=0.15)
        ax1 = self.figure.add_subplot(gs[0, :])  # Line chart span 2 columns
        ax2 = self.figure.add_subplot(gs[1, 0])  # Pie chart
        ax3 = self.figure.add_subplot(gs[1, 1])  # Bar chart
        
        # Plot 1: Total traffic dengan area fill
        ax1.fill_between(dates, totals, alpha=0.3, color='#4CAF50')
        ax1.plot(dates, totals, marker='o', linewidth=2, markersize=4, color='#2E7D32', label='Total Kendaraan')
        ax1.set_title('Total Kendaraan Harian', fontsize=12, fontweight='bold', pad=15)
        ax1.set_ylabel('Jumlah Kendaraan', fontsize=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(fontsize=9)
        
        # Format x-axis untuk chart 1
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//8)))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
        
        # Plot 2: Pie chart untuk distribusi arah
        total_up = sum(ups)
        total_down = sum(downs)
        if total_up + total_down > 0:
            sizes = [total_up, total_down]
            labels = ['Jalur A (Naik)', 'Jalur B (Turun)']
            colors_pie = ['#2196F3', '#FF5722']
            
            wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie, 
                                             autopct='%1.1f%%', startangle=90,
                                             textprops={'fontsize': 8})
            ax2.set_title('Distribusi Arah', fontsize=10, fontweight='bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
        else:
            ax2.text(0.5, 0.5, 'Tidak ada\ndata', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=8, color='#9CA3AF')
            ax2.set_title('Distribusi Arah', fontsize=10, fontweight='bold')
        
        # Plot 3: Bar chart untuk perbandingan traffic
        width = 0.35
        x_pos = np.arange(len(dates))
        
        ax3.bar([d - width/2 for d in x_pos], ups, width, label='Jalur A (Naik)', color='#2196F3', alpha=0.8)
        ax3.bar([d + width/2 for d in x_pos], downs, width, label='Jalur B (Turun)', color='#FF5722', alpha=0.8)
        ax3.set_title('Perbandingan Traffic', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Jumlah Kendaraan', fontsize=8)
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.legend(fontsize=8)
        
        # Format x-axis untuk chart 3
        ax3.set_xticks(x_pos[::max(1, len(dates)//6)])
        ax3.set_xticklabels([dates[i].strftime('%d/%m') for i in range(0, len(dates), max(1, len(dates)//6))], rotation=45, fontsize=7)
        
        
        # Adjust layout dengan spacing yang lebih baik
        self.figure.tight_layout(pad=2.0)
        self.draw()
    
    def plot_summary_chart(self, stats):
        """Plot chart ringkasan statistik dengan visualisasi modern"""
        self.figure.clear()
        
        if not stats or not isinstance(stats, dict):
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Tidak ada data statistik', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Ringkasan Statistik', fontsize=12, fontweight='bold')
            self.draw()
            return
        
        # Set modern style
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('seaborn')
        
        # Create grid layout - chart lebih besar
        gs = self.figure.add_gridspec(1, 2, width_ratios=[1, 1])
        ax1 = self.figure.add_subplot(gs[0, 0])  # Pie chart
        ax2 = self.figure.add_subplot(gs[0, 1])  # Bar chart
        
        # Pie chart for directional traffic
        labels = ['Jalur A (Naik)', 'Jalur B (Turun)']
        sizes = [stats.get('total_up', 0) or 0, stats.get('total_down', 0) or 0]
        colors = ['#2196F3', '#FF5722']
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                             startangle=90, textprops={'fontsize': 9})
            ax1.set_title('Distribusi Arah Traffic', fontsize=11, fontweight='bold', pad=15)
            
            # Style pie chart
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        else:
            ax1.text(0.5, 0.5, 'Tidak ada data', ha='center', va='center', transform=ax1.transAxes, fontsize=10)
            ax1.set_title('Distribusi Arah Traffic', fontsize=11, fontweight='bold', pad=15)
        
        # Bar chart for summary stats dengan style modern
        categories = ['Total\nKendaraan', 'Total\nJalur A', 'Total\nJalur B', 'Rata-rata\nper Hari']
        values = [
            stats.get('total_vehicles', 0) or 0,
            stats.get('total_up', 0) or 0,
            stats.get('total_down', 0) or 0,
            stats.get('average_per_day', 0) or 0
        ]
        bar_colors = ['#4CAF50', '#2196F3', '#FF5722', '#FF9800']
        
        bars = ax2.bar(categories, values, color=bar_colors, alpha=0.8, edgecolor='white', linewidth=2)
        ax2.set_title('Ringkasan Statistik', fontsize=11, fontweight='bold', pad=15)
        ax2.set_ylabel('Jumlah', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars dengan style yang lebih baik
        max_val = max(values) if values else 1
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max_val*0.02,
                    f'{int(value):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        
        # Adjust layout
        self.figure.tight_layout(pad=2.0)
        self.draw()

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
            
            # Initialize manager
            manager = GoogleSheetsManager()
            if not manager.authenticate():
                self.error_occurred.emit("Gagal mengakses Google Sheets!")
                return
            
            # Load data
            if self.start_date and self.end_date:
                data = manager.get_data_by_date_range(self.start_date, self.end_date)
            else:
                data = manager.get_all_data()
            
            # Get stats based on filtered data
            stats = self.calculate_filtered_stats(data)
            
            # Emit signals
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
        
        # Filter data yang valid
        valid_data = []
        for record in data:
            if record and isinstance(record, dict):
                # Pastikan record memiliki data yang valid
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
        
        # Handle null values dengan aman
        total_vehicles = 0
        total_up = 0
        total_down = 0
        
        for record in valid_data:
            try:
                total_val = record.get('Total', 0)
                up_val = record.get('Naik', 0)
                down_val = record.get('Turun', 0)
                
                total_vehicles += int(total_val) if total_val not in [None, '', '0'] else 0
                total_up += int(up_val) if up_val not in [None, '', '0'] else 0
                total_down += int(down_val) if down_val not in [None, '', '0'] else 0
            except (ValueError, TypeError):
                # Skip record jika ada error konversi
                continue
        
        # Hitung rata-rata per hari
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
    """Widget utama untuk tab laporan"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_loader_thread = None
        self.current_data = []
        self.current_stats = {}
        self.setup_ui()
        self.setup_connections()
        
        # Auto-load data on startup
        QTimer.singleShot(1000, self.load_data)
    
    def setup_ui(self):
        """Setup UI untuk reports widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
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
        self.load_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.load_btn.clicked.connect(self.load_data)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
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
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Data table
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
        
        table_layout.addWidget(self.data_table)
        main_layout.addWidget(table_group)
    
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
        stats_layout.addRow("Total Naik:", self.total_up_label)
        stats_layout.addRow("Total Turun:", self.total_down_label)
        stats_layout.addRow("Rata-rata/hari:", self.average_label)
        stats_layout.addRow("Hari Unik:", self.unique_dates_label)
        
        layout.addWidget(stats_group)
        
        # Quick actions
        actions_group = QGroupBox("Aksi Cepat")
        actions_layout = QVBoxLayout(actions_group)
        
        self.export_btn = QPushButton("Export Data (Excel)")
        self.export_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; }")
        self.export_btn.clicked.connect(self.export_data)
        
        self.print_btn = QPushButton("Export PDF Report")
        self.print_btn.setStyleSheet("QPushButton { background-color: #607D8B; color: white; }")
        self.print_btn.clicked.connect(self.print_report)
        
        actions_layout.addWidget(self.export_btn)
        actions_layout.addWidget(self.print_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return panel
    
    def create_charts_panel(self):
        """Buat panel chart"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Chart tabs
        chart_group = QGroupBox("Visualisasi Data")
        chart_layout = QVBoxLayout(chart_group)
        
        # Chart canvas
        self.chart_canvas = DataVisualizationCanvas(self)
        chart_layout.addWidget(self.chart_canvas)
        
        layout.addWidget(chart_group)
        
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
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
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
        # Filter out invalid records
        valid_data = []
        for record in data:
            if record and isinstance(record, dict):
                # Pastikan record memiliki data yang valid
                if any(str(record.get(key, '')).strip() for key in ['Tanggal', 'Total', 'Naik', 'Turun']):
                    valid_data.append(record)
        
        self.current_data = valid_data
        self.update_data_table(valid_data)
        self.update_charts(valid_data)
    
    def on_stats_loaded(self, stats):
        """Handle stats loaded signal"""
        self.current_stats = stats
        self.update_stats_display(stats)
        self.chart_canvas.plot_summary_chart(stats)
    
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
            # Jika tidak ada data, tampilkan tabel kosong
            self.data_table.setRowCount(0)
            return
        self.data_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            if not record or not isinstance(record, dict):
                continue
            # Handle null/empty values dengan menampilkan 0 atau string kosong
            self.data_table.setItem(row, 0, QTableWidgetItem(str(record.get('ID', '') or '')))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(record.get('Tanggal', '') or '')))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(record.get('Kilometer', '') or '')))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(record.get('Periode Jam', '') or '')))
            # Pastikan nilai numerik ditampilkan sebagai 0 jika null/empty
            total = record.get('Total', 0)
            naik = record.get('Jalur A', record.get('Naik', 0))
            turun = record.get('Jalur B', record.get('Turun', 0))
            
            self.data_table.setItem(row, 4, QTableWidgetItem(str(total if total not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(naik if naik not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 6, QTableWidgetItem(str(turun if turun not in [None, '', '0'] else 0)))
            self.data_table.setItem(row, 7, QTableWidgetItem(str(record.get('Deskripsi', '') or '')))
            self.data_table.setItem(row, 8, QTableWidgetItem(str(record.get('Waktu Input', '') or '')))
    
    def update_stats_display(self, stats):
        """Update display statistik"""
        if not stats or not isinstance(stats, dict):
            # Jika stats null atau tidak valid, tampilkan 0
            self.total_records_label.setText("0")
            self.total_vehicles_label.setText("0")
            self.total_up_label.setText("0")
            self.total_down_label.setText("0")
            self.average_label.setText("0")
            self.unique_dates_label.setText("0")
            return
        
        # Pastikan semua nilai ditampilkan sebagai 0 jika null
        self.total_records_label.setText(str(stats.get('total_records', 0) or 0))
        self.total_vehicles_label.setText(str(stats.get('total_vehicles', 0) or 0))
        self.total_up_label.setText(str(stats.get('total_up', 0) or 0))
        self.total_down_label.setText(str(stats.get('total_down', 0) or 0))
        self.average_label.setText(str(stats.get('average_per_day', 0) or 0))
        self.unique_dates_label.setText(str(stats.get('unique_dates', 0) or 0))
    
    def update_charts(self, data):
        """Update charts dengan data baru"""
        self.chart_canvas.plot_daily_traffic(data)
    
    def export_data(self):
        """Export data ke Excel (.xlsx)"""
        if not self.current_data:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk diekspor!")
            return
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            import pandas as pd

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Data (Excel)", f"counting_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if filename:
                df = pd.DataFrame(self.current_data)
                columns_order = ["ID", "Tanggal", "Kilometer", "Periode Jam", "Total", "Naik", "Turun", "Deskripsi", "Waktu Input"]
                # Reindex only for columns that exist
                columns = [c for c in columns_order if c in df.columns]
                df = df.reindex(columns=columns)
                df.to_excel(filename, index=False)

                QMessageBox.information(self, "Berhasil", f"Data berhasil diekspor ke: {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
    
    def print_report(self):
        """Export PDF report dengan template profesional seperti Flutter"""
        if not self.current_data:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk dibuatkan laporan!")
            return
        try:
            from PyQt5.QtWidgets import QFileDialog
            from pdf_service import PDFService

            filename, _ = QFileDialog.getSaveFileName(
                self, "Simpan Laporan PDF", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf);;All Files (*)"
            )
            if not filename:
                return

            # Buat date range string
            date_range = f"{self.start_date.date().toString('yyyy-MM-dd')} s/d {self.end_date.date().toString('yyyy-MM-dd')}"
            
            # Initialize PDF service
            pdf_service = PDFService()
            
            # Generate PDF dengan template profesional
            success = pdf_service.generate_simple_pdf(
                data=self.current_data,
                stats=self.current_stats,
                filename=filename,
                date_range=date_range,
                filter_info="Data Traffic Jalan Layang MBZ"
            )
            
            if success:
                QMessageBox.information(self, "Berhasil", f"Laporan PDF berhasil dibuat: {filename}")
            else:
                QMessageBox.critical(self, "Error", "Gagal membuat PDF dengan template baru. Mencoba metode lama...")
                self.print_report_legacy(filename)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat PDF: {str(e)}")
    
    def print_report_legacy(self, filename):
        """Fallback method untuk PDF generation"""
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            import pandas as pd

            df = pd.DataFrame(self.current_data)

            with PdfPages(filename) as pdf:
                # Halaman 1: Ringkasan
                fig1 = Figure(figsize=(11.69, 8.27))
                ax = fig1.add_subplot(111)
                stats = self.current_stats or {}
                summary_text = (
                    f"Tanggal: {self.start_date.date().toString('yyyy-MM-dd')} s/d {self.end_date.date().toString('yyyy-MM-dd')}\n"
                    f"Total Record: {stats.get('total_records', 0)}\n"
                    f"Total Kendaraan: {stats.get('total_vehicles', 0)}\n"
                    f"Total Naik: {stats.get('total_up', 0)}\n"
                    f"Total Turun: {stats.get('total_down', 0)}\n"
                    f"Rata-rata/hari: {stats.get('average_per_day', 0)}\n"
                )
                ax.axis('off')
                ax.text(0.05, 0.95, "Ringkasan Laporan", fontsize=16, fontweight='bold', va='top')
                ax.text(0.05, 0.85, summary_text, fontsize=12, va='top')
                pdf.savefig(fig1)

                # Halaman 2: Grafik harian
                fig2 = Figure(figsize=(11.69, 8.27))
                canvas2 = FigureCanvas(fig2)
                self.chart_canvas.figure = fig2
                self.chart_canvas.plot_daily_traffic(self.current_data)
                pdf.savefig(self.chart_canvas.figure)

                # Halaman 3: Tabel data
                fig3 = Figure(figsize=(11.69, 8.27))
                ax3 = fig3.add_subplot(111)
                ax3.axis('off')
                table_cols = ["Tanggal", "Kilometer", "Periode Jam", "Total", "Jalur A", "Jalur B", "Deskripsi"]
                table_cols = [c for c in table_cols if c in df.columns]
                df_table = df[table_cols]
                table = ax3.table(cellText=df_table.values, colLabels=df_table.columns, loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1.2)
                pdf.savefig(fig3)

            QMessageBox.information(self, "Berhasil", f"Laporan PDF berhasil dibuat: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat PDF legacy: {str(e)}")

if __name__ == "__main__":
    # Test reports widget
    from PyQt5.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Reports Widget Test")
    window.setGeometry(100, 100, 1200, 800)
    
    reports_widget = ReportsWidget()
    window.setCentralWidget(reports_widget)
    
    window.show()
    
    sys.exit(app.exec_())