"""
Compact Professional PDF Service
Clean, minimalist design with optimized A4 layout and enhanced visualizations
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

class CompactPDFService:
    """Compact professional PDF service with clean A4 layout and enhanced visualizations"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_compact_styles()
        
    def setup_compact_styles(self):
        """Setup compact, professional typography styles"""
        
        # Document title
        self.styles.add(ParagraphStyle(
            name='CompactTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers  
        self.styles.add(ParagraphStyle(
            name='CompactSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CompactBody',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Helvetica'
        ))
        
        # Meta info
        self.styles.add(ParagraphStyle(
            name='CompactMeta',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3,
            alignment=TA_CENTER,
            textColor=grey,
            fontName='Helvetica'
        ))
        
        # Header right style
        self.styles.add(ParagraphStyle(
            name='HeaderRight',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_RIGHT,
            textColor=grey,
            fontName='Helvetica'
        ))

    def create_compact_chart(self, data):
        """Create single compact chart for PDF with colors"""
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
            
            # Create colored chart
            plt.style.use('seaborn')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
            fig.patch.set_facecolor('white')
            
            # Line chart with attractive colors
            ax1.plot(dates, totals, color='#2E86AB', linewidth=2.5, 
                    marker='o', markersize=5, markeredgecolor='white', 
                    markerfacecolor='#2E86AB', label='Total', alpha=0.9)
            ax1.plot(dates, ups, color='#A23B72', linewidth=2, 
                    marker='s', markersize=4, markeredgecolor='white',
                    markerfacecolor='#A23B72', label='Jalur A', alpha=0.8)
            ax1.plot(dates, downs, color='#F18F01', linewidth=2, 
                    marker='^', markersize=4, markeredgecolor='white',
                    markerfacecolor='#F18F01', label='Jalur B', alpha=0.8)
            
            ax1.set_title('Traffic Trend', fontsize=11, fontweight='bold', 
                        pad=10, color='#2c3e50', loc='left')
            ax1.set_xlabel('Tanggal', fontsize=8, color='#34495e')
            ax1.set_ylabel('Kendaraan', fontsize=8, color='#34495e')
            ax1.legend(fontsize=7, frameon=True, fancybox=True, shadow=True, framealpha=0.9)
            ax1.grid(True, alpha=0.3, linewidth=0.5, color='#bdc3c7')
            ax1.tick_params(labelsize=7, colors='#2c3e50')
            
            # Add gradient background
            ax1.set_facecolor('#f8f9fa')
            
            # Format dates
            if len(dates) <= 10:
                ax1.set_xticks(dates)
                ax1.set_xticklabels([d.strftime('%d/%m') for d in dates], rotation=45)
            else:
                step = max(1, len(dates) // 8)
                sample_dates = dates[::step]
                ax1.set_xticks(sample_dates)
                ax1.set_xticklabels([d.strftime('%d/%m') for d in sample_dates], rotation=45)
            
            # Enhanced pie chart with vibrant colors
            total_up = sum(ups)
            total_down = sum(downs)
            if total_up + total_down > 0:
                sizes = [total_up, total_down]
                labels = ['Jalur A', 'Jalur B']
                colors = ['#E74C3C', '#3498DB']  # Red and Blue
                explode = (0.05, 0.05)  # slightly separate the slices
                
                wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90, explode=explode,
                                                 shadow=True, 
                                                 textprops={'fontsize': 9})
                ax2.set_title('Distribusi Jalur', fontsize=11, fontweight='bold', 
                            pad=10, color='#2c3e50', loc='left')
                
                # Add white outline to pie slices
                for w in wedges:
                    w.set_linewidth(0.5)
                    w.set_edgecolor('white')
            else:
                ax2.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=8, color='#7f8c8d')
                ax2.set_title('Distribusi Jalur', fontsize=11, fontweight='bold', 
                            pad=10, color='#2c3e50', loc='left')
            
            # Add subtle border around the entire figure
            for spine in ax1.spines.values():
                spine.set_color('#bdc3c7')
                spine.set_linewidth(1)
            
            plt.tight_layout()
            
            # Save chart with absolute path and ensure directory exists
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Ensure the temp directory exists
            os.makedirs(temp_dir, exist_ok=True)
            
            plt.savefig(temp_path, dpi=200, bbox_inches='tight', facecolor='white', 
                       edgecolor='none', pad_inches=0.1)
            plt.close()
            
            # Verify file was created and is readable
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path
            else:
                print(f"Chart file not created properly: {temp_path}")
                return None
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None

    def create_daily_comparison_chart(self, data):
        """Create compact daily comparison bar chart"""
        try:
            # Prepare data by day of week
            day_counts = {}
            
            for record in data:
                try:
                    date_str = record.get('Tanggal', '')
                    if not date_str:
                        continue
                        
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_name = date_obj.strftime('%a')
                    total = int(record.get('Total', 0) or 0)
                    
                    if day_name not in day_counts:
                        day_counts[day_name] = []
                    day_counts[day_name].append(total)
                except:
                    continue
            
            if not day_counts:
                return None
            
            # Calculate averages
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            avg_counts = []
            
            for day in days:
                if day in day_counts and day_counts[day]:
                    avg_counts.append(sum(day_counts[day]) / len(day_counts[day]))
                else:
                    avg_counts.append(0)
            
            # Create clean bar chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(6, 2.5))
            
            colors = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e67e22', '#e74c3c', '#1abc9c']
            bars = ax.bar(days, avg_counts, color=colors, alpha=0.8)
            
            # Style the chart
            ax.set_title('Rata-rata Harian', fontsize=10, fontweight='bold', pad=8, color='#2c3e50')
            ax.set_xlabel('Hari', fontsize=8, color='#34495e')
            ax.set_ylabel('Rata-rata', fontsize=8, color='#34495e')
            ax.grid(True, alpha=0.2, linewidth=0.5, color='#bdc3c7')
            ax.tick_params(labelsize=7, colors='#2c3e50')
            ax.set_facecolor('#f8f9fa')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f}', 
                            ha='center', va='bottom', fontsize=7)
            
            plt.tight_layout()
            
            # Save to temp file
            temp_path = self._save_temp_chart()
            if temp_path:
                return temp_path
            return None
            
        except Exception as e:
            print(f"Error creating daily comparison chart: {e}")
            return None
    
    def create_monthly_trend_chart(self, data):
        """Create monthly trend visualization"""
        try:
            # Prepare monthly data
            monthly_counts = {}
            
            for record in data:
                try:
                    date_str = record.get('Tanggal', '')
                    if not date_str:
                        continue
                        
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    total = int(record.get('Total', 0) or 0)
                    up = int(record.get('Jalur A', record.get('Naik', 0)) or 0)
                    down = int(record.get('Jalur B', record.get('Turun', 0)) or 0)
                    
                    if month_key not in monthly_counts:
                        monthly_counts[month_key] = {'total': 0, 'up': 0, 'down': 0}
                    
                    monthly_counts[month_key]['total'] += total
                    monthly_counts[month_key]['up'] += up
                    monthly_counts[month_key]['down'] += down
                except:
                    continue
            
            if not monthly_counts:
                return None
            
            # Sort by month
            sorted_months = sorted(monthly_counts.keys())
            months = [datetime.strptime(m, '%Y-%m').strftime('%b %y') for m in sorted_months]
            totals = [monthly_counts[m]['total'] for m in sorted_months]
            ups = [monthly_counts[m]['up'] for m in sorted_months]
            downs = [monthly_counts[m]['down'] for m in sorted_months]
            
            # Create stacked bar chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(7, 3))
            
            # Create stacked bars
            bars1 = ax.bar(months, ups, color='#E74C3C', alpha=0.8, label='Jalur A')
            bars2 = ax.bar(months, downs, bottom=ups, color='#3498DB', alpha=0.8, label='Jalur B')
            
            # Style the chart
            ax.set_title('Trend Bulanan Traffic', fontsize=10, fontweight='bold', pad=8, color='#2c3e50')
            ax.set_xlabel('Bulan', fontsize=8, color='#34495e')
            ax.set_ylabel('Total Kendaraan', fontsize=8, color='#34495e')
            ax.legend(fontsize=7, frameon=True, fancybox=True, shadow=True)
            ax.grid(True, alpha=0.2, linewidth=0.5, color='#bdc3c7')
            ax.tick_params(labelsize=7, colors='#2c3e50', rotation=45)
            ax.set_facecolor('#f8f9fa')
            
            # Add total labels on top
            for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                total_height = bar1.get_height() + bar2.get_height()
                if total_height > 0:
                    ax.text(bar1.get_x() + bar1.get_width()/2., total_height,
                            f'{int(total_height):,}',
                            ha='center', va='bottom', fontsize=6, fontweight='bold')
            
            plt.tight_layout()
            
            # Save to temp file
            temp_path = self._save_temp_chart()
            if temp_path:
                return temp_path
            return None
            
        except Exception as e:
            print(f"Error creating monthly trend chart: {e}")
            return None
    
    def create_peak_hours_analysis(self, data):
        """Create peak hours analysis visualization"""
        try:
            # Prepare hourly data
            hour_counts = {}
            
            for record in data:
                try:
                    period = record.get('Periode Jam', '')
                    if not period:
                        continue
                        
                    # Extract hour from period (assuming format like '08:00-09:00')
                    hour_str = period.split('-')[0].split(':')[0]
                    hour = int(hour_str)
                    total = int(record.get('Total', 0) or 0)
                    up = int(record.get('Jalur A', record.get('Naik', 0)) or 0)
                    down = int(record.get('Jalur B', record.get('Turun', 0)) or 0)
                    
                    if hour not in hour_counts:
                        hour_counts[hour] = {'total': 0, 'up': 0, 'down': 0, 'count': 0}
                    
                    hour_counts[hour]['total'] += total
                    hour_counts[hour]['up'] += up
                    hour_counts[hour]['down'] += down
                    hour_counts[hour]['count'] += 1
                except:
                    continue
            
            if not hour_counts:
                return None
            
            # Get top 6 peak hours
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1]['total'], reverse=True)[:6]
            
            hours = [f"{h:02d}:00" for h, _ in peak_hours]
            totals = [data['total'] for _, data in peak_hours]
            ups = [data['up'] for _, data in peak_hours]
            downs = [data['down'] for _, data in peak_hours]
            
            # Create grouped bar chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(6, 3))
            
            x = np.arange(len(hours))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, ups, width, label='Jalur A', color='#E74C3C', alpha=0.8)
            bars2 = ax.bar(x + width/2, downs, width, label='Jalur B', color='#3498DB', alpha=0.8)
            
            # Style the chart
            ax.set_title('Top 6 Jam Tersibuk', fontsize=10, fontweight='bold', pad=8, color='#2c3e50')
            ax.set_xlabel('Jam', fontsize=8, color='#34495e')
            ax.set_ylabel('Kendaraan', fontsize=8, color='#34495e')
            ax.set_xticks(x)
            ax.set_xticklabels(hours)
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.2, linewidth=0.5, color='#bdc3c7')
            ax.tick_params(labelsize=7, colors='#2c3e50')
            ax.set_facecolor('#f8f9fa')
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height):,}',
                                ha='center', va='bottom', fontsize=6)
            
            plt.tight_layout()
            
            # Save to temp file
            temp_path = self._save_temp_chart()
            if temp_path:
                return temp_path
            return None
            
        except Exception as e:
            print(f"Error creating peak hours analysis: {e}")
            return None
    
    def create_cumulative_chart(self, data):
        """Create cumulative traffic visualization"""
        try:
            # Prepare cumulative data
            dates, cumulative_totals = [], []
            cumulative_sum = 0
            
            # Sort data by date first
            sorted_data = sorted(data, key=lambda x: x.get('Tanggal', ''))
            
            for record in sorted_data:
                try:
                    date_str = record.get('Tanggal', '')
                    if not date_str:
                        continue
                        
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    total_val = int(record.get('Total', 0) or 0)
                    
                    cumulative_sum += total_val
                    dates.append(date_obj)
                    cumulative_totals.append(cumulative_sum)
                except:
                    continue
            
            if not dates:
                return None
            
            # Create cumulative area chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(6, 2.5))
            
            # Fill area under curve
            ax.fill_between(dates, cumulative_totals, color='#3498DB', alpha=0.3, label='Kumulatif')
            ax.plot(dates, cumulative_totals, color='#2980B9', linewidth=2, marker='o', markersize=3)
            
            # Style the chart
            ax.set_title('Akumulasi Traffic', fontsize=10, fontweight='bold', pad=8, color='#2c3e50')
            ax.set_xlabel('Tanggal', fontsize=8, color='#34495e')
            ax.set_ylabel('Total Kumulatif', fontsize=8, color='#34495e')
            ax.grid(True, alpha=0.2, linewidth=0.5, color='#bdc3c7')
            ax.tick_params(labelsize=7, colors='#2c3e50')
            ax.set_facecolor('#f8f9fa')
            
            # Format dates
            if len(dates) <= 10:
                ax.set_xticks(dates)
                ax.set_xticklabels([d.strftime('%d/%m') for d in dates], rotation=45)
            else:
                step = max(1, len(dates) // 8)
                sample_dates = dates[::step]
                ax.set_xticks(sample_dates)
                ax.set_xticklabels([d.strftime('%d/%m') for d in sample_dates], rotation=45)
            
            # Format y-axis to show numbers in thousands
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
            
            plt.tight_layout()
            
            # Save to temp file
            temp_path = self._save_temp_chart()
            if temp_path:
                return temp_path
            return None
            
        except Exception as e:
            print(f"Error creating cumulative chart: {e}")
            return None
    
    def _save_temp_chart(self):
        """Helper to save chart to temp file"""
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        os.makedirs(temp_dir, exist_ok=True)
        plt.savefig(temp_path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none', pad_inches=0.1)
        plt.close()
        
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return temp_path
        return None
    
    def generate_compact_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate compact professional PDF report with separated visualizations"""
        chart_paths = []
        try:
            # Setup document with minimal margins
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.6*inch, leftMargin=0.6*inch, 
                                 topMargin=0.6*inch, bottomMargin=0.6*inch)
            
            elements = []
            
            # Create header with logo on left and filter/date info on right
            if os.path.exists(os.path.join('assets', 'logo_jjcnormal.png')):
                # Prepare filter info text
                filter_text = f"Filter: {filter_info}" if filter_info else ""
                date_text = f"Dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                
                header_table_data = [
                    [Image(os.path.join('assets', 'logo_jjcnormal.png'), width=2*inch, height=0.5*inch), 
                     '', 
                     Paragraph(f"{filter_text}<br/>{date_text}", 
                              self.styles['HeaderRight'])]
                ]
                
                header_table = Table(header_table_data, colWidths=[2*inch, 3*inch, 2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (2,0), (2,0), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5)
                ]))
                elements.append(header_table)
            
            # Document title (removed period info)
            title = Paragraph("LAPORAN ANALYSIS TRAFFIC", self.styles['CompactTitle'])
            elements.append(title)
            elements.append(Spacer(1, 15))
            
            # Summary section in compact table
            if stats:
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
                    # Styling
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    
                    # Alignment
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Borders - minimal
                    ('LINEBELOW', (0, -1), (-1, -1), 0.5, black),
                    ('LINEBEFORE', (2, 0), (2, -1), 0.5, grey),
                    
                    # Padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 15))
            
            # Add data detail right after summary
            if data and len(data) > 0:
                elements.append(Paragraph("DATA DETAIL", self.styles['CompactSection']))
                
                # Prepare compact table with description column
                table_data = [["No", "Tanggal", "KM", "Periode", "Total", "Jalur A", "Jalur B", "Deskripsi"]]
                
                # Show first 30 records
                display_data = data[:30]
                
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
                
                # Create compact data table with adjusted column widths
                data_table = Table(table_data, 
                                 colWidths=[0.4*inch, 0.8*inch, 0.6*inch, 0.9*inch, 
                                            0.7*inch, 0.7*inch, 0.7*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    
                    # Body styling
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    
                    # Alignment
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),   # No
                    ('ALIGN', (1, 0), (3, -1), 'CENTER'),   # Date, KM, Period
                    ('ALIGN', (4, 0), (6, -1), 'RIGHT'),    # Numbers
                    ('ALIGN', (7, 0), (7, -1), 'LEFT'),     # Deskripsi
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Minimal borders
                    ('LINEBELOW', (0, 0), (-1, 0), 1, black),
                    ('GRID', (0, 1), (-1, -1), 0.25, grey),
                    
                    # Compact padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                elements.append(data_table)
                
                # Compact summary info
                elements.append(Spacer(1, 8))
                summary_text = f"Menampilkan {len(display_data)} dari {len(data)} record total"
                elements.append(Paragraph(summary_text, self.styles['CompactBody']))
                elements.append(Spacer(1, 20))
            
            # Add visualizations on separate page (only 2 charts now)
            if data and len(data) > 0:
                elements.append(PageBreak())  # Start visualizations on new page
                elements.append(Paragraph("VISUALISASI DATA", self.styles['CompactSection']))
                
                # Main trend chart (line + pie)
                main_chart = self.create_compact_chart(data)
                if main_chart:
                    chart_paths.append(main_chart)
                    try:
                        chart_img = Image(main_chart, width=6.5*inch, height=2.8*inch)
                        elements.append(chart_img)
                        elements.append(Spacer(1, 20))
                    except Exception as img_error:
                        print(f"Error adding main chart image: {img_error}")
                
                # Daily comparison chart
                daily_chart = self.create_daily_comparison_chart(data)
                if daily_chart:
                    chart_paths.append(daily_chart)
                    try:
                        chart_img = Image(daily_chart, width=6*inch, height=2.8*inch)
                        elements.append(chart_img)
                        elements.append(Spacer(1, 15))
                    except Exception as img_error:
                        print(f"Error adding daily chart image: {img_error}")
            
            # Build PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
        finally:
            # Clean up temp files
            for path in chart_paths:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as cleanup_error:
                        print("Error cleaning up chart file:", cleanup_error)

    def generate_single_page_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate ultra-compact single page PDF"""
        chart_path = None
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=0.5*inch, leftMargin=0.5*inch, 
                                 topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            elements = []
            
            # Compact header with filter info and creation date
            header_table_data = [
                [Paragraph("TRAFFIC ANALYSIS REPORT", self.styles['CompactTitle']),
                 Paragraph(f"{filter_info if filter_info else ''}<br/>Dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                          ParagraphStyle(name='HeaderRight',
                                        fontSize=7,
                                        alignment=TA_RIGHT,
                                        textColor=grey,
                                        fontName='Helvetica'))]
            ]
            
            header_table = Table(header_table_data, colWidths=[4*inch, 2*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5)
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 10))
            
            # Ultra-compact stats in single row
            if stats:
                stats_data = [[
                    f"Records: {stats.get('total_records', 0):,}",
                    f"Total: {stats.get('total_vehicles', 0):,}",
                    f"Jalur A: {stats.get('total_up', 0):,}",
                    f"Jalur B: {stats.get('total_down', 0):,}",
                    f"Avg/Day: {stats.get('average_per_day', 0):,.0f}"
                ]]
                
                stats_table = Table(stats_data, colWidths=[1.4*inch] * 5)
                stats_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, -1), grey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), white),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                
                elements.append(stats_table)
                elements.append(Spacer(1, 10))
            
            # Compact chart
            if data and len(data) > 0:
                chart_path = self.create_compact_chart(data)
                if chart_path:
                    chart_img = Image(chart_path, width=5.5*inch, height=2*inch)
                    elements.append(chart_img)
                    elements.append(Spacer(1, 8))
            
            # Mini data table - first 15 records only
            if data:
                table_data = [["#", "Date", "Total", "A", "B"]]
                
                for i, record in enumerate(data[:15], 1):
                    row = [
                        str(i),
                        str(record.get('Tanggal', ''))[-5:] if record.get('Tanggal') else '',  # Show only MM-DD
                        f"{int(record.get('Total', 0) or 0):,}",
                        f"{int(record.get('Jalur A', record.get('Naik', 0)) or 0)}",
                        f"{int(record.get('Jalur B', record.get('Turun', 0)) or 0)}"
                    ]
                    table_data.append(row)
                
                mini_table = Table(table_data, colWidths=[0.3*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.6*inch])
                mini_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, black),
                    ('GRID', (0, 1), (-1, -1), 0.25, grey),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                
                elements.append(mini_table)
                
                if len(data) > 15:
                    elements.append(Spacer(1, 5))
                    note = Paragraph(f"Showing first 15 of {len(data)} records", self.styles['CompactMeta'])
                    elements.append(note)
            
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Error generating single page PDF: {e}")
            return False
        finally:
            # Clean up temp file
            if chart_path and os.path.exists(chart_path):
                try:
                    os.remove(chart_path)
                except Exception as cleanup_error:
                    print("Error cleaning up chart file:", cleanup_error)