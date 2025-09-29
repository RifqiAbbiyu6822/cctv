"""
Compact Professional PDF Service
Clean, minimalist design with optimized A4 layout and enhanced visualizations
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, white, grey, Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from io import BytesIO

class CompactPDFService:
    """Compact professional PDF service with clean A4 layout and enhanced visualizations
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_compact_styles()
        
    def setup_compact_styles(self):
        """Setup enhanced, professional typography styles with better visibility"""
        
        # Register fonts with consistent naming
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
        except:
            # Fallback to built-in fonts if Arial not available
            pass
        
        # Enhanced Document title with better visibility
        self.styles.add(ParagraphStyle(
            name='CompactTitle',
            parent=self.styles['Heading1'],
            fontSize=18,  # Increased from 16
            spaceAfter=15,  # Increased spacing
            spaceBefore=5,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor='#4a6fa5',
            borderPadding=8,
            backColor='#f8f9fa'  # Light background for better visibility
        ))
        
        # Enhanced Section headers with better contrast
        self.styles.add(ParagraphStyle(
            name='CompactSection',
            parent=self.styles['Heading2'],
            fontSize=14,  # Increased from 12
            spaceAfter=10,  # Increased spacing
            spaceBefore=15,  # Increased spacing
            alignment=TA_LEFT,
            textColor='#2c3e50',  # Darker color for better visibility
            fontName='Helvetica-Bold',
            borderWidth=0.5,
            borderColor='#4a6fa5',
            borderPadding=5,
            backColor='#e8f4f8'  # Light blue background
        ))
        
        # Enhanced Body text with better readability
        self.styles.add(ParagraphStyle(
            name='CompactBody',
            parent=self.styles['Normal'],
            fontSize=10,  # Increased from 9
            spaceAfter=6,  # Increased spacing
            alignment=TA_LEFT,
            textColor='#2c3e50',  # Darker color
            fontName='Helvetica',
            leading=12  # Line spacing for better readability
        ))
        
        # Enhanced Meta info with better visibility
        self.styles.add(ParagraphStyle(
            name='CompactMeta',
            parent=self.styles['Normal'],
            fontSize=9,  # Increased from 8
            spaceAfter=4,
            alignment=TA_CENTER,
            textColor='#34495e',  # Darker grey
            fontName='Helvetica',
            backColor='#ecf0f1',  # Light background
            borderPadding=3
        ))
        
        # New style for highlighted numbers
        self.styles.add(ParagraphStyle(
            name='HighlightNumber',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            alignment=TA_CENTER,
            textColor='#e74c3c',  # Red color for emphasis
            fontName='Helvetica-Bold',
            backColor='#fdf2f2',
            borderWidth=1,
            borderColor='#e74c3c',
            borderPadding=4
        ))
        
        # New style for summary boxes
        self.styles.add(ParagraphStyle(
            name='SummaryBox',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor='#2c3e50',
            fontName='Helvetica',
            backColor='#f8f9fa',
            borderWidth=1,
            borderColor='#dee2e6',
            borderPadding=8
        ))
    
    def create_matplotlib_charts(self, data, stats):
        """Buat chart menggunakan matplotlib untuk visualisasi yang lebih baik"""
        charts = {}
        
        if not data or len(data) == 0:
            return charts
        
        try:
            # Prepare data untuk chart
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
                return charts
            
            # Set matplotlib style untuk PDF
            plt.style.use('default')
            plt.rcParams['font.size'] = 10
            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['axes.facecolor'] = 'white'
            
            # 1. Line Chart - Total Kendaraan Harian
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            ax1.plot(dates, totals, marker='o', linewidth=2, markersize=4, color='#2E7D32', label='Total Kendaraan')
            ax1.fill_between(dates, totals, alpha=0.2, color='#4CAF50')
            ax1.set_title('Total Kendaraan Harian', fontsize=12, fontweight='bold', pad=10)
            ax1.set_ylabel('Jumlah Kendaraan', fontsize=10)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=9)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            if len(dates) > 10:
                ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//8)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
            
            plt.tight_layout()
            
            # Save sebagai BytesIO
            buffer1 = BytesIO()
            plt.savefig(buffer1, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer1.seek(0)
            charts['line_chart'] = buffer1
            plt.close(fig1)
            
            # 2. Pie Chart - Distribusi Arah
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            total_up = sum(ups)
            total_down = sum(downs)
            
            if total_up + total_down > 0:
                sizes = [total_up, total_down]
                labels = ['Jalur A', 'Jalur B']
                colors = ['#2196F3', '#FF5722']
                
                wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90,
                                                 textprops={'fontsize': 9})
                ax2.set_title('Distribusi Arah Kendaraan', fontsize=12, fontweight='bold', pad=10)
                
                # Styling untuk pie chart
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(8)
                
                for text in texts:
                    text.set_fontsize(9)
                    text.set_fontweight('500')
            else:
                ax2.text(0.5, 0.5, 'Tidak ada\ndata', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=12, color='#666')
                ax2.set_title('Distribusi Arah Kendaraan', fontsize=12, fontweight='bold', pad=10)
            
            plt.tight_layout()
            
            # Save sebagai BytesIO
            buffer2 = BytesIO()
            plt.savefig(buffer2, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer2.seek(0)
            charts['pie_chart'] = buffer2
            plt.close(fig2)
            
            # 3. Bar Chart - Perbandingan Traffic
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            width = 0.35
            x_pos = np.arange(len(dates))
            
            bars1 = ax3.bar([d - width/2 for d in x_pos], ups, width, label='Jalur A', 
                           color='#2196F3', alpha=0.8, edgecolor='white', linewidth=0.5)
            bars2 = ax3.bar([d + width/2 for d in x_pos], downs, width, label='Jalur B', 
                           color='#FF5722', alpha=0.8, edgecolor='white', linewidth=0.5)
            
            ax3.set_title('Perbandingan Traffic Harian', fontsize=12, fontweight='bold', pad=10)
            ax3.set_ylabel('Jumlah Kendaraan', fontsize=10)
            ax3.set_xlabel('Tanggal', fontsize=10)
            ax3.grid(True, alpha=0.3, axis='y')
            ax3.legend(fontsize=9)
            
            # Format x-axis untuk bar chart
            step = max(1, len(dates)//6)
            ax3.set_xticks(x_pos[::step])
            ax3.set_xticklabels([dates[i].strftime('%d/%m') for i in range(0, len(dates), step)], 
                               rotation=45, fontsize=8)
            
            plt.tight_layout()
            
            # Save sebagai BytesIO
            buffer3 = BytesIO()
            plt.savefig(buffer3, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer3.seek(0)
            charts['bar_chart'] = buffer3
            plt.close(fig3)
            
            # 4. Summary Statistics Chart
            fig4, ax4 = plt.subplots(figsize=(6, 4))
            
            categories = ['Total\nKendaraan', 'Jalur A\n(Naik)', 'Jalur B\n(Turun)']
            values = [stats.get('total_vehicles', 0), stats.get('total_up', 0), stats.get('total_down', 0)]
            colors = ['#4CAF50', '#2196F3', '#FF5722']
            
            bars = ax4.bar(categories, values, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
            ax4.set_title('Ringkasan Statistik', fontsize=12, fontweight='bold', pad=10)
            ax4.set_ylabel('Jumlah Kendaraan', fontsize=10)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                        f'{int(value):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            # Save sebagai BytesIO
            buffer4 = BytesIO()
            plt.savefig(buffer4, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer4.seek(0)
            charts['summary_chart'] = buffer4
            plt.close(fig4)
            
        except Exception as e:
            print(f"Error creating matplotlib charts: {e}")
            return {}
        
        return charts


    
    
    

    
    def generate_visual_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate PDF dengan visualisasi yang sesuai dengan data yang disimpan dengan grid yang baik pada halaman berbeda"""
        print(f"[DEBUG] Starting visual PDF generation for {filename}")
        print(f"[DEBUG] Data length: {len(data) if data else 0}")
        print(f"[DEBUG] Stats: {stats}")
        print(f"[DEBUG] Date range: {date_range}")
        
        try:
            # Setup document dengan minimal margins
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.6*inch, leftMargin=0.6*inch, 
                                 topMargin=0.6*inch, bottomMargin=0.6*inch)
            
            elements = []
            print(f"[DEBUG] Document template created")
            
            # Create header dengan logo
            logo_path = os.path.join('assets', 'logo_jjcnormal.png')
            print(f"[DEBUG] Checking logo at: {logo_path}")
            
            # Prepare filter information
            filter_text = ""
            if date_range:
                filter_text = f"Tanggal: {date_range}"
            elif data and len(data) > 0:
                dates = [record.get('Tanggal', '') for record in data if record.get('Tanggal')]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    filter_text = f"Filter: {min_date} - {max_date}"
            
            if os.path.exists(logo_path):
                print("[DEBUG] Logo found, adding to PDF with filter info")
                header_table_data = [
                    [Image(logo_path, width=2*inch, height=0.5*inch), 
                     '', 
                     Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])]
                ]
                
                header_table = Table(header_table_data, colWidths=[2*inch, 3*inch, 2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (2,0), (2,0), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5)
                ]))
                elements.append(header_table)
            else:
                print("[DEBUG] Logo not found at expected path")
                if filter_text:
                    filter_para = Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])
                    elements.append(Paragraph("", self.styles['Normal']))
                    elements.append(filter_para)
            
            # Document title
            title = Paragraph("LAPORAN TRAFFIC COUNTING DENGAN VISUALISASI", self.styles['CompactTitle'])
            elements.append(title)
            elements.append(Spacer(1, 15))
            print("[DEBUG] Added title and spacer")
            
            # Halaman 1: Summary dan Ringkasan
            if stats:
                print(f"[DEBUG] Adding stats: {stats}")
                elements.append(Paragraph("RINGKASAN STATISTIK", self.styles['CompactSection']))
                
                # Enhanced summary table
                summary_data = [
                    ["Total Records", f"{stats.get('total_records', 0):,}", 
                     "Total Kendaraan", f"{stats.get('total_vehicles', 0):,}"],
                    ["Jalur A (Naik)", f"{stats.get('total_up', 0):,}", 
                     "Jalur B (Turun)", f"{stats.get('total_down', 0):,}"],
                    ["Rata-rata/Hari", f"{stats.get('average_per_day', 0):,.0f}", 
                     "Hari Unik", f"{stats.get('unique_dates', 0):,}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
                summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('BACKGROUND', (0, 1), (0, -1), '#ecf0f1'),
                    ('BACKGROUND', (2, 1), (2, -1), '#ecf0f1'),
                    ('BACKGROUND', (1, 1), (1, -1), '#f8f9fa'),
                    ('BACKGROUND', (3, 1), (3, -1), '#f8f9fa'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('LINEBELOW', (0, -1), (-1, -1), 1, '#bdc3c7'),
                    ('LINEBEFORE', (2, 0), (2, -1), 1, '#bdc3c7'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 15))
                print("[DEBUG] Added summary table")
            
            # Buat visualisasi charts
            charts = self.create_matplotlib_charts(data, stats)
            
            # Halaman 2: Visualisasi Charts
            if charts:
                elements.append(PageBreak())
                elements.append(Paragraph("VISUALISASI DATA", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Grid layout untuk charts
                # Row 1: Line chart (full width)
                if 'line_chart' in charts:
                    line_img = Image(charts['line_chart'], width=7*inch, height=3.5*inch)
                    elements.append(line_img)
                    elements.append(Spacer(1, 10))
                
                # Row 2: Pie chart dan Summary chart (side by side)
                if 'pie_chart' in charts or 'summary_chart' in charts:
                    chart_row_data = []
                    
                    if 'pie_chart' in charts:
                        pie_img = Image(charts['pie_chart'], width=3.2*inch, height=2.4*inch)
                        chart_row_data.append(pie_img)
                    else:
                        chart_row_data.append("")
                    
                    if 'summary_chart' in charts:
                        summary_img = Image(charts['summary_chart'], width=3.2*inch, height=2.4*inch)
                        chart_row_data.append(summary_img)
                    else:
                        chart_row_data.append("")
                    
                    if chart_row_data:
                        chart_row_table = Table([chart_row_data], colWidths=[3.5*inch, 3.5*inch])
                        chart_row_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        elements.append(chart_row_table)
                        elements.append(Spacer(1, 10))
                
                # Row 3: Bar chart (full width)
                if 'bar_chart' in charts:
                    bar_img = Image(charts['bar_chart'], width=7*inch, height=3.5*inch)
                    elements.append(bar_img)
                    elements.append(Spacer(1, 15))
                
                print("[DEBUG] Added visualizations")
            
            # Halaman 3: Data Detail dengan Grid yang Baik
            if data and len(data) > 0:
                elements.append(PageBreak())
                elements.append(Paragraph("DATA DETAIL", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Prepare table dengan deskripsi
                table_data = [["No", "Tanggal", "KM", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi"]]
                
                # Show ALL records
                display_data = data
                
                for i, record in enumerate(display_data, 1):
                    row = [
                        str(i),
                        str(record.get('Tanggal', ''))[-5:] if record.get('Tanggal') else '',
                        str(record.get('Kilometer', ''))[:6],
                        str(record.get('Periode Jam', ''))[:8],
                        f"{int(record.get('Total', 0) or 0):,}",
                        f"{int(record.get('Jalur A', record.get('Naik', 0)) or 0):,}",
                        f"{int(record.get('Jalur B', record.get('Turun', 0)) or 0):,}",
                        str(record.get('Deskripsi', record.get('Keterangan', '')))[:30]
                    ]
                    table_data.append(row)
                
                # Enhanced data table dengan grid yang baik
                data_table = Table(table_data, 
                                 colWidths=[0.4*inch, 0.8*inch, 0.6*inch, 0.9*inch, 
                                            0.7*inch, 0.7*inch, 0.7*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (3, -1), 'CENTER'),
                    ('ALIGN', (4, 0), (6, -1), 'RIGHT'),
                    ('ALIGN', (7, 0), (7, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(data_table)
                
                # Enhanced summary info
                elements.append(Spacer(1, 12))
                
                summary_info = f"""
                <b>📊 DATA SUMMARY</b><br/>
                Total Records: <font color="#e74c3c"><b>{len(display_data)}</b></font><br/>
                Date Range: <font color="#27ae60"><b>{min([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'} - {max([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'}</b></font><br/>
                Total Vehicles: <font color="#2c3e50"><b>{sum([int(r.get('Total', 0) or 0) for r in display_data]):,}</b></font>
                """
                elements.append(Paragraph(summary_info, self.styles['SummaryBox']))
                elements.append(Spacer(1, 20))
                print("[DEBUG] Added enhanced data table with summary")
            
            # Build PDF
            print("[DEBUG] Building PDF document")
            doc.build(elements)
            print("[DEBUG] Visual PDF generation completed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Generating visual PDF: {e}")
            return False

    def generate_compact_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate compact professional PDF report without visualizations"""
        print(f"[DEBUG] Starting PDF generation for {filename}")
        print(f"[DEBUG] Data length: {len(data) if data else 0}")
        print(f"[DEBUG] Stats: {stats}")
        print(f"[DEBUG] Date range: {date_range}")
        try:
            # Setup document with minimal margins
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.6*inch, leftMargin=0.6*inch, 
                                 topMargin=0.6*inch, bottomMargin=0.6*inch)
            
            elements = []
            print(f"[DEBUG] Document template created")
            
            # Create header with logo on left and filter info on right
            logo_path = os.path.join('assets', 'logo_jjcnormal.png')
            print(f"[DEBUG] Checking logo at: {logo_path}")
            
            # Prepare filter information
            filter_text = ""
            if date_range:
                filter_text = f"Tanggal: {date_range}"
            elif data and len(data) > 0:
                # Extract date range from data
                dates = [record.get('Tanggal', '') for record in data if record.get('Tanggal')]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    filter_text = f"Filter: {min_date} - {max_date}"
            
            if os.path.exists(logo_path):
                print("[DEBUG] Logo found, adding to PDF with filter info")
                header_table_data = [
                    [Image(logo_path, width=2*inch, height=0.5*inch), 
                     '', 
                     Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])]
                ]
                
                header_table = Table(header_table_data, colWidths=[2*inch, 3*inch, 2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (2,0), (2,0), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5)
                ]))
                elements.append(header_table)
            else:
                print("[DEBUG] Logo not found at expected path")
                # Add filter info without logo
                if filter_text:
                    filter_para = Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])
                    elements.append(Paragraph("", self.styles['Normal']))  # Spacer
                    elements.append(filter_para)
            
            # Document title (removed period info)
            title = Paragraph("LAPORAN TRAFFIC COUNTING", self.styles['CompactTitle'])
            elements.append(title)
            elements.append(Spacer(1, 15))
            print("[DEBUG] Added title and spacer")
            
            # Summary section in compact table
            if stats:
                print(f"[DEBUG] Adding stats: {stats}")
                elements.append(Paragraph("RINGKASAN", self.styles['CompactSection']))
                
                # Compact 2-column summary
                summary_data = [
                    ["Total Records", f"{stats.get('total_records', 0):,}", 
                     "Total Kendaraan", f"{stats.get('total_vehicles', 0):,}"],
                    ["Jalur A (Naik)", f"{stats.get('total_up', 0):,}", 
                     "Jalur B (Turun)", f"{stats.get('total_down', 0):,}"],
                    ["Rata-rata/Hari", f"{stats.get('average_per_day', 0):,.0f}", 
                     "Hari Unik", f"{stats.get('unique_dates', 0):,}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
                summary_table.setStyle(TableStyle([
                    # Enhanced styling for better visibility
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),  # Increased from 9
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    
                    # Enhanced alignment
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Enhanced borders and backgrounds
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),  # Header background
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),  # Header text color
                    ('BACKGROUND', (0, 1), (0, -1), '#ecf0f1'),  # Left column background
                    ('BACKGROUND', (2, 1), (2, -1), '#ecf0f1'),  # Right column background
                    ('BACKGROUND', (1, 1), (1, -1), '#f8f9fa'),  # Value columns background
                    ('BACKGROUND', (3, 1), (3, -1), '#f8f9fa'),
                    
                    # Enhanced borders
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),  # Header border
                    ('LINEBELOW', (0, -1), (-1, -1), 1, '#bdc3c7'),
                    ('LINEBEFORE', (2, 0), (2, -1), 1, '#bdc3c7'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    
                    # Enhanced padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),  # Increased from 6
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),  # Increased from 4
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 15))
                print("[DEBUG] Added summary table")
            else:
                print("[DEBUG] No stats available to include")
            
            # Add data detail right after summary
            if data and len(data) > 0:
                print(f"[DEBUG] Adding {len(data)} data records")
                elements.append(Paragraph("DATA DETAIL", self.styles['CompactSection']))
                
                # Prepare compact table with description column
                table_data = [["No", "Tanggal", "KM", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi"]]
                
                # Show ALL records (removed the 30 record limit)
                display_data = data
                
                for i, record in enumerate(display_data, 1):
                    row = [
                        str(i),
                        str(record.get('Tanggal', ''))[-5:] if record.get('Tanggal') else '',  # Show only MM-DD
                        str(record.get('Kilometer', ''))[:6],  # Truncate if too long
                        str(record.get('Periode Jam', ''))[:8],
                        f"{int(record.get('Total', 0) or 0):,}",
                        f"{int(record.get('Jalur A', record.get('Naik', 0)) or 0):,}",
                        f"{int(record.get('Jalur B', record.get('Turun', 0)) or 0):,}",
                        str(record.get('Deskripsi', record.get('Keterangan', '')))[:30]  # Ambil dari Deskripsi atau Keterangan, maks 30 karakter
                    ]
                    table_data.append(row)
                
                # Create enhanced data table with better visibility
                data_table = Table(table_data, 
                                 colWidths=[0.4*inch, 0.8*inch, 0.6*inch, 0.9*inch, 
                                            0.7*inch, 0.7*inch, 0.7*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    # Enhanced header styling
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    
                    # Enhanced body styling
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    
                    # Enhanced alignment
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),   # No
                    ('ALIGN', (1, 0), (3, -1), 'CENTER'),   # Date, KM, Period
                    ('ALIGN', (4, 0), (6, -1), 'RIGHT'),    # Numbers
                    ('ALIGN', (7, 0), (7, -1), 'LEFT'),     # Deskripsi
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Enhanced borders and backgrounds
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),  # Header border
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    
                    # Alternating row colors for better readability
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    
                    # Enhanced padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Increased from 3
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),  # Increased from 2
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(data_table)
                
                # Enhanced summary info with better visibility
                elements.append(Spacer(1, 12))
                
                # Create summary box with highlighted information
                summary_info = f"""
                <b>📊 DATA SUMMARY</b><br/>
                Total Records: <font color="#e74c3c"><b>{len(display_data)}</b></font><br/>
                Date Range: <font color="#27ae60"><b>{min([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'} - {max([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'}</b></font><br/>
                Total Vehicles: <font color="#2c3e50"><b>{sum([int(r.get('Total', 0) or 0) for r in display_data]):,}</b></font>
                """
                elements.append(Paragraph(summary_info, self.styles['SummaryBox']))
                elements.append(Spacer(1, 20))
                print("[DEBUG] Added enhanced data table with summary")
            else:
                print("[DEBUG] No data available to include")
            
            # Build PDF
            print("[DEBUG] Building PDF document")
            doc.build(elements)
            print("[DEBUG] PDF generation completed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Generating PDF: {e}")
            return False

    def generate_data_summary_pdf(self, data, stats, filename, date_range=None):
        """Generate PDF khusus untuk halaman total data dengan analisis mendalam"""
        print(f"[DEBUG] Starting data summary PDF generation for {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.6*inch, leftMargin=0.6*inch, 
                                 topMargin=0.6*inch, bottomMargin=0.6*inch)
            
            elements = []
            
            # Header dengan logo
            logo_path = os.path.join('assets', 'logo_jjcnormal.png')
            if os.path.exists(logo_path):
                header_table_data = [
                    [Image(logo_path, width=2*inch, height=0.5*inch), 
                     '', 
                     Paragraph(f"<b>ANALISIS TOTAL DATA</b>", self.styles['CompactMeta'])]
                ]
                
                header_table = Table(header_table_data, colWidths=[2*inch, 3*inch, 2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (2,0), (2,0), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5)
                ]))
                elements.append(header_table)
            
            # Title
            title = Paragraph("ANALISIS TOTAL DATA TRAFFIC COUNTING", self.styles['CompactTitle'])
            elements.append(title)
            elements.append(Spacer(1, 15))
            
            # Halaman 1: Overview Total Data
            elements.append(Paragraph("OVERVIEW TOTAL DATA", self.styles['CompactSection']))
            
            if stats:
                # Total data summary dengan format yang lebih menarik
                total_summary_data = [
                    ["METRIK", "NILAI", "PERSENTASE", "KETERANGAN"],
                    ["Total Records", f"{stats.get('total_records', 0):,}", "100%", "Semua data yang tersimpan"],
                    ["Total Kendaraan", f"{stats.get('total_vehicles', 0):,}", "100%", "Jumlah kendaraan terdeteksi"],
                    ["Jalur A (Naik)", f"{stats.get('total_up', 0):,}", f"{(stats.get('total_up', 0) / max(stats.get('total_vehicles', 1), 1) * 100):.1f}%", "Kendaraan naik"],
                    ["Jalur B (Turun)", f"{stats.get('total_down', 0):,}", f"{(stats.get('total_down', 0) / max(stats.get('total_vehicles', 1), 1) * 100):.1f}%", "Kendaraan turun"],
                    ["Rata-rata/Hari", f"{stats.get('average_per_day', 0):,.0f}", "-", "Rata-rata harian"],
                    ["Hari Unik", f"{stats.get('unique_dates', 0):,}", "-", "Jumlah hari aktif"]
                ]
                
                total_summary_table = Table(total_summary_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 2*inch])
                total_summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(total_summary_table)
                elements.append(Spacer(1, 15))
            
            # Halaman 2: Analisis Harian
            if data and len(data) > 0:
                elements.append(PageBreak())
                elements.append(Paragraph("ANALISIS DATA HARIAN", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Analisis per hari
                daily_analysis = self.analyze_daily_data(data)
                
                # Tabel analisis harian
                daily_table_data = [["Tanggal", "Total", "Jalur A", "Jalur B", "Persentase A", "Persentase B", "Status"]]
                
                for day_data in daily_analysis:
                    total = day_data['total']
                    up = day_data['up']
                    down = day_data['down']
                    up_pct = (up / max(total, 1)) * 100
                    down_pct = (down / max(total, 1)) * 100
                    
                    # Status berdasarkan distribusi
                    if up_pct > 60:
                        status = "Dominan A"
                    elif down_pct > 60:
                        status = "Dominan B"
                    elif abs(up_pct - down_pct) <= 10:
                        status = "Seimbang"
                    else:
                        status = "Normal"
                    
                    row = [
                        day_data['date'][-5:],  # MM-DD format
                        f"{total:,}",
                        f"{up:,}",
                        f"{down:,}",
                        f"{up_pct:.1f}%",
                        f"{down_pct:.1f}%",
                        status
                    ]
                    daily_table_data.append(row)
                
                daily_table = Table(daily_table_data, 
                                  colWidths=[0.8*inch, 0.7*inch, 0.6*inch, 0.6*inch, 
                                             0.8*inch, 0.8*inch, 0.7*inch])
                daily_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (3, -1), 'RIGHT'),
                    ('ALIGN', (4, 0), (6, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.3, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                elements.append(daily_table)
                elements.append(Spacer(1, 15))
                
                # Summary analisis
                summary_analysis = self.generate_analysis_summary(data, stats)
                elements.append(Paragraph("RINGKASAN ANALISIS", self.styles['CompactSection']))
                elements.append(Paragraph(summary_analysis, self.styles['SummaryBox']))
                elements.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(elements)
            print("[DEBUG] Data summary PDF generation completed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Generating data summary PDF: {e}")
            return False

    def analyze_daily_data(self, data):
        """Analisis data per hari"""
        daily_data = {}
        
        for record in data:
            try:
                date_str = record.get('Tanggal', '')
                if not date_str:
                    continue
                
                if date_str not in daily_data:
                    daily_data[date_str] = {'total': 0, 'up': 0, 'down': 0}
                
                total = int(record.get('Total', 0) or 0)
                up = int(record.get('Jalur A', record.get('Naik', 0)) or 0)
                down = int(record.get('Jalur B', record.get('Turun', 0)) or 0)
                
                daily_data[date_str]['total'] += total
                daily_data[date_str]['up'] += up
                daily_data[date_str]['down'] += down
                
            except Exception as e:
                print(f"Error analyzing daily data: {e}")
                continue
        
        # Convert to list dan sort by date
        result = []
        for date_str in sorted(daily_data.keys()):
            result.append({
                'date': date_str,
                'total': daily_data[date_str]['total'],
                'up': daily_data[date_str]['up'],
                'down': daily_data[date_str]['down']
            })
        
        return result

    def generate_analysis_summary(self, data, stats):
        """Generate summary analisis"""
        if not data or not stats:
            return "Tidak ada data untuk dianalisis."
        
        total_vehicles = stats.get('total_vehicles', 0)
        total_up = stats.get('total_up', 0)
        total_down = stats.get('total_down', 0)
        unique_dates = stats.get('unique_dates', 1)
        average_per_day = stats.get('average_per_day', 0)
        
        # Analisis distribusi
        up_percentage = (total_up / max(total_vehicles, 1)) * 100
        down_percentage = (total_down / max(total_vehicles, 1)) * 100
        
        # Analisis tren
        if len(data) >= 2:
            recent_data = data[-min(5, len(data)):]
            older_data = data[:min(5, len(data))]
            
            recent_avg = sum(int(r.get('Total', 0) or 0) for r in recent_data) / len(recent_data)
            older_avg = sum(int(r.get('Total', 0) or 0) for r in older_data) / len(older_data)
            
            if recent_avg > older_avg * 1.1:
                trend = "Meningkat"
            elif recent_avg < older_avg * 0.9:
                trend = "Menurun"
            else:
                trend = "Stabil"
        else:
            trend = "Tidak dapat ditentukan"
        
        summary = f"""
        <b>📈 ANALISIS KESELURUHAN:</b><br/>
        • Total {total_vehicles:,} kendaraan terdeteksi dalam {unique_dates} hari<br/>
        • Rata-rata {average_per_day:.0f} kendaraan per hari<br/>
        • Distribusi: {up_percentage:.1f}% Jalur A, {down_percentage:.1f}% Jalur B<br/>
        • Tren: <font color="#27ae60"><b>{trend}</b></font><br/>
        • Periode: {min([r.get('Tanggal', '') for r in data if r.get('Tanggal')]) if data else 'N/A'} - {max([r.get('Tanggal', '') for r in data if r.get('Tanggal')]) if data else 'N/A'}
        """
        
        return summary

    def generate_complete_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate PDF lengkap dengan semua fitur dalam satu dokumen"""
        print(f"[DEBUG] Starting complete PDF generation for {filename}")
        print(f"[DEBUG] Data length: {len(data) if data else 0}")
        print(f"[DEBUG] Stats: {stats}")
        print(f"[DEBUG] Date range: {date_range}")
        
        try:
            # Setup document dengan minimal margins
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.6*inch, leftMargin=0.6*inch, 
                                 topMargin=0.6*inch, bottomMargin=0.6*inch)
            
            elements = []
            print(f"[DEBUG] Document template created")
            
            # Create header dengan logo
            logo_path = os.path.join('assets', 'logo_jjcnormal.png')
            print(f"[DEBUG] Checking logo at: {logo_path}")
            
            # Prepare filter information
            filter_text = ""
            if date_range:
                filter_text = f"Tanggal: {date_range}"
            elif data and len(data) > 0:
                dates = [record.get('Tanggal', '') for record in data if record.get('Tanggal')]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    filter_text = f"Filter: {min_date} - {max_date}"
            
            if os.path.exists(logo_path):
                print("[DEBUG] Logo found, adding to PDF with filter info")
                header_table_data = [
                    [Image(logo_path, width=2*inch, height=0.5*inch), 
                     '', 
                     Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])]
                ]
                
                header_table = Table(header_table_data, colWidths=[2*inch, 3*inch, 2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (2,0), (2,0), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5)
                ]))
                elements.append(header_table)
            else:
                print("[DEBUG] Logo not found at expected path")
                if filter_text:
                    filter_para = Paragraph(f"<b>{filter_text}</b>", self.styles['CompactMeta'])
                    elements.append(Paragraph("", self.styles['Normal']))
                    elements.append(filter_para)
            
            # Document title
            title = Paragraph("LAPORAN LENGKAP TRAFFIC COUNTING", self.styles['CompactTitle'])
            elements.append(title)
            elements.append(Spacer(1, 15))
            print("[DEBUG] Added title and spacer")
            
            # OVERVIEW TOTAL DATA (tanpa page break)
            if stats:
                print(f"[DEBUG] Adding stats: {stats}")
                elements.append(Paragraph("OVERVIEW TOTAL DATA", self.styles['CompactSection']))
                
                # Total data summary dengan format yang lebih menarik
                total_summary_data = [
                    ["METRIK", "NILAI", "PERSENTASE", "KETERANGAN"],
                    ["Total Records", f"{stats.get('total_records', 0):,}", "100%", "Semua data yang tersimpan"],
                    ["Total Kendaraan", f"{stats.get('total_vehicles', 0):,}", "100%", "Jumlah kendaraan terdeteksi"],
                    ["Jalur A (Naik)", f"{stats.get('total_up', 0):,}", f"{(stats.get('total_up', 0) / max(stats.get('total_vehicles', 1), 1) * 100):.1f}%", "Kendaraan naik"],
                    ["Jalur B (Turun)", f"{stats.get('total_down', 0):,}", f"{(stats.get('total_down', 0) / max(stats.get('total_vehicles', 1), 1) * 100):.1f}%", "Kendaraan turun"],
                    ["Rata-rata/Hari", f"{stats.get('average_per_day', 0):,.0f}", "-", "Rata-rata harian"],
                    ["Hari Unik", f"{stats.get('unique_dates', 0):,}", "-", "Jumlah hari aktif"]
                ]
                
                total_summary_table = Table(total_summary_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 2*inch])
                total_summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(total_summary_table)
                elements.append(Spacer(1, 15))
                print("[DEBUG] Added total data summary table")
            
            # ANALISIS DATA HARIAN (menyambung tanpa page break)
            if data and len(data) > 0:
                elements.append(Paragraph("ANALISIS DATA HARIAN", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Analisis per hari
                daily_analysis = self.analyze_daily_data(data)
                
                # Tabel analisis harian
                daily_table_data = [["Tanggal", "Total", "Jalur A", "Jalur B", "Persentase A", "Persentase B", "Status"]]
                
                for day_data in daily_analysis:
                    total = day_data['total']
                    up = day_data['up']
                    down = day_data['down']
                    up_pct = (up / max(total, 1)) * 100
                    down_pct = (down / max(total, 1)) * 100
                    
                    # Status berdasarkan distribusi
                    if up_pct > 60:
                        status = "Dominan A"
                    elif down_pct > 60:
                        status = "Dominan B"
                    elif abs(up_pct - down_pct) <= 10:
                        status = "Seimbang"
                    else:
                        status = "Normal"
                    
                    row = [
                        day_data['date'][-5:],  # MM-DD format
                        f"{total:,}",
                        f"{up:,}",
                        f"{down:,}",
                        f"{up_pct:.1f}%",
                        f"{down_pct:.1f}%",
                        status
                    ]
                    daily_table_data.append(row)
                
                daily_table = Table(daily_table_data, 
                                  colWidths=[0.8*inch, 0.7*inch, 0.6*inch, 0.6*inch, 
                                             0.8*inch, 0.8*inch, 0.7*inch])
                daily_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (3, -1), 'RIGHT'),
                    ('ALIGN', (4, 0), (6, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.3, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                elements.append(daily_table)
                elements.append(Spacer(1, 15))
                
                # Summary analisis
                summary_analysis = self.generate_analysis_summary(data, stats)
                elements.append(Paragraph("RINGKASAN ANALISIS", self.styles['CompactSection']))
                elements.append(Paragraph(summary_analysis, self.styles['SummaryBox']))
                elements.append(Spacer(1, 20))
                
                print("[DEBUG] Added daily analysis")
            
            # DATA DETAIL (menyambung tanpa page break)
            if data and len(data) > 0:
                elements.append(Paragraph("DATA DETAIL", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Prepare table dengan deskripsi
                table_data = [["No", "Tanggal", "KM", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi"]]
                
                # Show ALL records
                display_data = data
                
                for i, record in enumerate(display_data, 1):
                    row = [
                        str(i),
                        str(record.get('Tanggal', ''))[-5:] if record.get('Tanggal') else '',
                        str(record.get('Kilometer', ''))[:6],
                        str(record.get('Periode Jam', ''))[:8],
                        f"{int(record.get('Total', 0) or 0):,}",
                        f"{int(record.get('Jalur A', record.get('Naik', 0)) or 0):,}",
                        f"{int(record.get('Jalur B', record.get('Turun', 0)) or 0):,}",
                        str(record.get('Deskripsi', record.get('Keterangan', '')))[:30]
                    ]
                    table_data.append(row)
                
                # Enhanced data table dengan grid yang baik
                data_table = Table(table_data, 
                                 colWidths=[0.4*inch, 0.8*inch, 0.6*inch, 0.9*inch, 
                                            0.7*inch, 0.7*inch, 0.7*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), '#2c3e50'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (3, -1), 'CENTER'),
                    ('ALIGN', (4, 0), (6, -1), 'RIGHT'),
                    ('ALIGN', (7, 0), (7, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, '#2c3e50'),
                    ('GRID', (0, 1), (-1, -1), 0.5, '#dee2e6'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', '#f8f9fa']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(data_table)
                
                # Enhanced summary info
                elements.append(Spacer(1, 12))
                
                summary_info = f"""
                <b>📊 DATA SUMMARY</b><br/>
                Total Records: <font color="#e74c3c"><b>{len(display_data)}</b></font><br/>
                Date Range: <font color="#27ae60"><b>{min([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'} - {max([r.get('Tanggal', '') for r in display_data if r.get('Tanggal')]) if display_data else 'N/A'}</b></font><br/>
                Total Vehicles: <font color="#2c3e50"><b>{sum([int(r.get('Total', 0) or 0) for r in display_data]):,}</b></font>
                """
                elements.append(Paragraph(summary_info, self.styles['SummaryBox']))
                elements.append(Spacer(1, 20))
                print("[DEBUG] Added enhanced data table with summary")
            
            # VISUALISASI DATA (di akhir dokumen dengan page break)
            charts = self.create_matplotlib_charts(data, stats)
            
            if charts:
                elements.append(PageBreak())
                elements.append(Paragraph("VISUALISASI DATA", self.styles['CompactSection']))
                elements.append(Spacer(1, 10))
                
                # Grid layout untuk charts
                # Row 1: Line chart (full width)
                if 'line_chart' in charts:
                    line_img = Image(charts['line_chart'], width=7*inch, height=3.5*inch)
                    elements.append(line_img)
                    elements.append(Spacer(1, 10))
                
                # Row 2: Pie chart dan Summary chart (side by side)
                if 'pie_chart' in charts or 'summary_chart' in charts:
                    chart_row_data = []
                    
                    if 'pie_chart' in charts:
                        pie_img = Image(charts['pie_chart'], width=3.2*inch, height=2.4*inch)
                        chart_row_data.append(pie_img)
                    else:
                        chart_row_data.append("")
                    
                    if 'summary_chart' in charts:
                        summary_img = Image(charts['summary_chart'], width=3.2*inch, height=2.4*inch)
                        chart_row_data.append(summary_img)
                    else:
                        chart_row_data.append("")
                    
                    if chart_row_data:
                        chart_row_table = Table([chart_row_data], colWidths=[3.5*inch, 3.5*inch])
                        chart_row_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        elements.append(chart_row_table)
                        elements.append(Spacer(1, 10))
                
                # Row 3: Bar chart (full width)
                if 'bar_chart' in charts:
                    bar_img = Image(charts['bar_chart'], width=7*inch, height=3.5*inch)
                    elements.append(bar_img)
                    elements.append(Spacer(1, 15))
                
                print("[DEBUG] Added visualizations at the end")
            
            # Build PDF
            print("[DEBUG] Building PDF document")
            doc.build(elements)
            print("[DEBUG] Complete PDF generation completed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Generating complete PDF: {e}")
            return False

    