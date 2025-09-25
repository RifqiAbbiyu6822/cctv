"""
Clean Minimalist PDF Service - Fixed Layout
Professional black & white design with proper spacing and alignment
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, grey, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Line
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

class PDFService:
    """Clean minimalist PDF service with proper layout"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_clean_styles()
        
    def setup_clean_styles(self):
        """Setup clean, professional typography styles"""
        
        # Clean title
        self.styles.add(ParagraphStyle(
            name='BasicTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='BasicSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='BasicBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Helvetica'
        ))
        
        # Meta info
        self.styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            alignment=TA_CENTER,
            textColor=grey,
            fontName='Helvetica'
        ))

    def create_basic_charts(self, data):
        """Create single clean chart"""
        try:
            # Prepare data
            dates, totals, ups, downs = [], [], [], []
            
            for record in data:
                try:
                    date_str = record.get('Tanggal', '')
                    if not date_str or date_str.strip() == '':
                        continue
                        
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    total_val = int(record.get('Total', 0) or 0)
                    up_val = int(record.get('Jalur A', record.get('Naik', 0)) or 0)
                    down_val = int(record.get('Jalur B', record.get('Turun', 0)) or 0)
                    
                    dates.append(date_obj)
                    totals.append(total_val)
                    ups.append(up_val)
                    downs.append(down_val)
                except:
                    continue
            
            if not dates:
                return None
            
            # Create clean chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            
            # Clean colorful lines
            ax.plot(dates, totals, color='#2563eb', linewidth=3, marker='o', markersize=6, label='Total Kendaraan')
            ax.plot(dates, ups, color='#dc2626', linewidth=2, marker='s', markersize=4, label='Jalur A (Naik)')
            ax.plot(dates, downs, color='#ea580c', linewidth=2, marker='^', markersize=4, label='Jalur B (Turun)')
            
            # Clean styling
            ax.set_title('Grafik Traffic Harian', fontsize=16, fontweight='bold', color='black', pad=20)
            ax.set_xlabel('Tanggal', fontsize=12, color='black')
            ax.set_ylabel('Jumlah Kendaraan', fontsize=12, color='black')
            
            # Professional legend
            ax.legend(fontsize=10, frameon=True, fancybox=False, shadow=False, 
                     facecolor='white', edgecolor='black', loc='upper left')
            
            # Clean grid
            ax.grid(True, alpha=0.3, color='gray', linewidth=0.5, linestyle='-')
            ax.set_facecolor('white')
            
            # Clean axes
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(1)
            ax.tick_params(colors='black', labelsize=10)
            
            # Format dates properly
            if len(dates) <= 15:
                ax.set_xticks(dates)
                ax.set_xticklabels([d.strftime('%d/%m') for d in dates], rotation=45)
            else:
                step = len(dates) // 10
                sample_dates = dates[::step]
                ax.set_xticks(sample_dates)
                ax.set_xticklabels([d.strftime('%d/%m') for d in sample_dates], rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            temp_path = f"temp_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating charts: {e}")
            return None

    def generate_simple_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate clean, professional PDF report"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.75*inch, leftMargin=0.75*inch, 
                                 topMargin=0.75*inch, bottomMargin=0.75*inch)
            
            elements = []
            
            # Clean header
            title = Paragraph("Laporan Traffic Analysis", self.styles['BasicTitle'])
            elements.append(title)
            elements.append(Spacer(1, 10))
            
            # Meta information
            if date_range:
                date_para = Paragraph(f"Periode: {date_range}", self.styles['MetaInfo'])
                elements.append(date_para)
            
            if filter_info:
                filter_para = Paragraph(f"Filter: {filter_info}", self.styles['MetaInfo'])
                elements.append(filter_para)
            
            generated_para = Paragraph(f"Dibuat: {datetime.now().strftime('%d %B %Y, %H:%M')}", self.styles['MetaInfo'])
            elements.append(generated_para)
            elements.append(Spacer(1, 30))
            
            # Summary section with clean table
            if stats:
                elements.append(Paragraph("Ringkasan Data", self.styles['BasicSection']))
                
                summary_data = [
                    ["Metric", "Nilai"],
                    ["Total Records", f"{stats.get('total_records', 0):,}"],
                    ["Total Kendaraan", f"{stats.get('total_vehicles', 0):,}"],
                    ["Jalur A (Naik)", f"{stats.get('total_up', 0):,}"],
                    ["Jalur B (Turun)", f"{stats.get('total_down', 0):,}"],
                    ["Rata-rata per Hari", f"{stats.get('average_per_day', 0):,.1f}"],
                    ["Hari Unik", f"{stats.get('unique_dates', 0):,}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
                summary_table.setStyle(TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    
                    # Data rows
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    
                    # Alignment
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Borders
                    ('LINEBELOW', (0, 0), (-1, 0), 2, black),
                    ('LINEABOVE', (0, -1), (-1, -1), 1, black),
                    ('LINEBEFORE', (0, 0), (0, -1), 1, black),
                    ('LINEAFTER', (-1, 0), (-1, -1), 1, black),
                    
                    # Padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 30))
            
            # Add chart
            if data and len(data) > 0:
                chart_path = self.create_basic_charts(data)
                if chart_path:
                    elements.append(Paragraph("Visualisasi Data", self.styles['BasicSection']))
                    chart_img = Image(chart_path, width=6*inch, height=3.75*inch)
                    elements.append(chart_img)
                    elements.append(Spacer(1, 30))
                    
                    # Clean up temp file
                    try:
                        os.remove(chart_path)
                    except:
                        pass
            
            # Page break before data table
            elements.append(PageBreak())
            
            # Data table
            if data and len(data) > 0:
                elements.append(Paragraph("Detail Data", self.styles['BasicSection']))
                
                # Prepare table headers
                table_data = [["No", "Tanggal", "KM", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi"]]
                
                # Limit data for readability
                display_data = data[:50]
                
                for i, record in enumerate(display_data, 1):
                    row = [
                        str(i),
                        str(record.get('Tanggal', '')),
                        str(record.get('Kilometer', '')),
                        str(record.get('Periode Jam', '')),
                        f"{int(record.get('Total', 0) or 0):,}",
                        f"{int(record.get('Jalur A', record.get('Naik', 0)) or 0):,}",
                        f"{int(record.get('Jalur B', record.get('Turun', 0)) or 0):,}",
                        str(record.get('Deskripsi', ''))[:30] + ("..." if len(str(record.get('Deskripsi', ''))) > 30 else "")
                    ]
                    table_data.append(row)
                
                # Create clean data table
                data_table = Table(table_data, colWidths=[0.4*inch, 0.9*inch, 0.6*inch, 0.9*inch, 0.7*inch, 0.7*inch, 0.7*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    
                    # Body styling
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    
                    # Alignment
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),   # No
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),   # Date
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),   # KM
                    ('ALIGN', (3, 0), (3, -1), 'CENTER'),   # Period
                    ('ALIGN', (4, 0), (6, -1), 'RIGHT'),    # Numbers
                    ('ALIGN', (7, 0), (7, -1), 'LEFT'),     # Description
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Clean borders
                    ('LINEBELOW', (0, 0), (-1, 0), 2, black),
                    ('GRID', (0, 1), (-1, -1), 0.5, grey),
                    
                    # Padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(data_table)
                
                # Summary info
                elements.append(Spacer(1, 15))
                summary_text = f"Menampilkan {len(display_data)} dari {len(data)} total record"
                elements.append(Paragraph(summary_text, self.styles['BasicBody']))
            
            # Build PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def generate_matplotlib_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate clean matplotlib PDF"""
        try:
            with PdfPages(filename) as pdf:
                # Single clean page
                fig = plt.figure(figsize=(8.27, 11.69))
                fig.patch.set_facecolor('white')
                
                # Title
                fig.suptitle('Laporan Traffic Analysis', fontsize=18, fontweight='bold', y=0.95)
                
                # Create subplots
                gs = fig.add_gridspec(3, 2, height_ratios=[0.3, 1, 0.5], hspace=0.3, wspace=0.2)
                
                # Meta info
                ax_meta = fig.add_subplot(gs[0, :])
                ax_meta.axis('off')
                
                meta_text = f"Periode: {date_range or 'N/A'}\nDibuat: {datetime.now().strftime('%d %B %Y, %H:%M')}"
                ax_meta.text(0.5, 0.5, meta_text, ha='center', va='center', fontsize=11)
                
                # Chart
                if data and len(data) > 0:
                    ax_chart = fig.add_subplot(gs[1, :])
                    
                    # Prepare data
                    dates, totals, ups, downs = [], [], [], []
                    for record in data:
                        try:
                            date_str = record.get('Tanggal', '')
                            if date_str:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                dates.append(date_obj)
                                totals.append(int(record.get('Total', 0) or 0))
                                ups.append(int(record.get('Jalur A', record.get('Naik', 0)) or 0))
                                downs.append(int(record.get('Jalur B', record.get('Turun', 0)) or 0))
                        except:
                            continue
                    
                    if dates:
                        ax_chart.plot(dates, totals, 'o-', color='#2563eb', linewidth=2, label='Total')
                        ax_chart.plot(dates, ups, 's-', color='#dc2626', linewidth=1.5, label='Jalur A')
                        ax_chart.plot(dates, downs, '^-', color='#ea580c', linewidth=1.5, label='Jalur B')
                        
                        ax_chart.set_title('Traffic Harian', fontsize=14, fontweight='bold')
                        ax_chart.set_xlabel('Tanggal')
                        ax_chart.set_ylabel('Jumlah Kendaraan')
                        ax_chart.legend()
                        ax_chart.grid(True, alpha=0.3)
                
                # Summary table
                if stats:
                    ax_summary = fig.add_subplot(gs[2, :])
                    ax_summary.axis('off')
                    
                    summary_text = f"""
                    Total Records: {stats.get('total_records', 0):,}     Total Kendaraan: {stats.get('total_vehicles', 0):,}
                    Jalur A: {stats.get('total_up', 0):,}     Jalur B: {stats.get('total_down', 0):,}     Rata-rata/Hari: {stats.get('average_per_day', 0):,.1f}
                    """
                    
                    ax_summary.text(0.5, 0.5, summary_text, ha='center', va='center', 
                                  fontsize=10, family='monospace')
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
            
            return True
            
        except Exception as e:
            print(f"Error generating matplotlib PDF: {e}")
            return False