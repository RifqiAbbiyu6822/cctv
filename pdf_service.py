"""
Ultra Minimalist PDF Service - Clean design without borders or unnecessary elements
Fokus pada typography hierarchy dan white space
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Line
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import seaborn as sns

class MinimalistPDFService:
    """Ultra clean PDF service with minimalist design principles"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_minimalist_styles()
        # Ultra clean color palette
        self.colors = {
            'text_primary': '#1F2937',      # Dark gray for main text
            'text_secondary': '#6B7280',    # Medium gray for secondary text
            'text_muted': '#9CA3AF',        # Light gray for muted text
            'accent': '#3B82F6',            # Clean blue for accents
            'success': '#10B981',           # Clean green
            'warning': '#F59E0B',           # Clean amber
            'background': '#FAFAFA',        # Very light background
            'surface': '#FFFFFF',           # Pure white
            'border': '#F3F4F6'             # Subtle border
        }
        
    def setup_minimalist_styles(self):
        """Setup ultra clean typography styles"""
        
        # Main title - clean and simple
        self.styles.add(ParagraphStyle(
            name='CleanTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=8,
            spaceBefore=0,
            alignment=TA_LEFT,
            textColor=HexColor('#1F2937'),
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Section headers - minimal
        self.styles.add(ParagraphStyle(
            name='CleanSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=16,
            alignment=TA_LEFT,
            textColor=HexColor('#374151'),
            fontName='Helvetica-Bold',
            leading=16
        ))
        
        # Body text - readable and clean
        self.styles.add(ParagraphStyle(
            name='CleanBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=HexColor('#4B5563'),
            fontName='Helvetica',
            leading=14
        ))
        
        # Subtle info text
        self.styles.add(ParagraphStyle(
            name='CleanInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=HexColor('#6B7280'),
            fontName='Helvetica',
            leading=12
        ))
        
        # Right-aligned meta info
        self.styles.add(ParagraphStyle(
            name='CleanMeta',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            alignment=TA_RIGHT,
            textColor=HexColor('#6B7280'),
            fontName='Helvetica',
            leading=12
        ))

    def create_clean_header(self, date_range=None, filter_info=None):
        """Create ultra clean header with minimal elements"""
        elements = []
        
        # Simple logo text (no borders, no boxes)
        logo_text = Paragraph("JJC", ParagraphStyle(
            name='LogoStyle',
            fontSize=20,
            textColor=HexColor('#1F2937'),
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=0
        ))
        
        # Clean meta info
        meta_lines = []
        meta_lines.append(f"Generated: {datetime.now().strftime('%d %B %Y')}")
        if date_range:
            meta_lines.append(f"Period: {date_range}")
        if filter_info:
            meta_lines.append(f"Filter: {filter_info}")
        
        meta_text = "<br/>".join(meta_lines)
        meta_paragraph = Paragraph(meta_text, self.styles['CleanMeta'])
        
        # Simple two-column layout without borders
        header_table = Table([[logo_text, meta_paragraph]], colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            # NO BORDERS - completely clean
        ]))
        
        elements.append(header_table)
        
        # Main title - simple typography
        title = Paragraph("Traffic Analysis Report", self.styles['CleanTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        return elements

    def create_summary_section(self, stats):
        """Create clean summary without cards or borders"""
        elements = []
        
        # Section title
        elements.append(Paragraph("Summary", self.styles['CleanSection']))
        
        if not stats:
            elements.append(Paragraph("No statistical data available", self.styles['CleanInfo']))
            return elements
        
        # Clean statistics layout - just text, no boxes
        stats_items = [
            ("Total Records", stats.get('total_records', 0)),
            ("Total Vehicles", stats.get('total_vehicles', 0)),
            ("Direction A (Up)", stats.get('total_up', 0)),
            ("Direction B (Down)", stats.get('total_down', 0)),
            ("Daily Average", stats.get('average_per_day', 0)),
            ("Unique Days", stats.get('unique_dates', 0))
        ]
        
        # Simple grid layout without borders
        grid_data = []
        for i in range(0, len(stats_items), 2):
            row = []
            # First column
            if i < len(stats_items):
                label1, value1 = stats_items[i]
                row.extend([label1, str(value1)])
            else:
                row.extend(["", ""])
            
            # Second column  
            if i + 1 < len(stats_items):
                label2, value2 = stats_items[i + 1]
                row.extend([label2, str(value2)])
            else:
                row.extend(["", ""])
            
            grid_data.append(row)
        
        stats_table = Table(grid_data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 0.8*inch])
        stats_table.setStyle(TableStyle([
            # Clean typography only - no backgrounds or borders
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#4B5563')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#4B5563')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#1F2937')),
            ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#1F2937')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            # NO BORDERS OR BACKGROUNDS - pure minimalism
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        return elements

    def create_ultra_clean_charts(self, data):
        """Create ultra minimalist charts - smaller size, no borders"""
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
            
            # Ultra clean matplotlib style
            plt.style.use('default')
            plt.rcParams.update({
                'font.family': 'sans-serif',
                'font.size': 8,
                'axes.labelsize': 8,
                'axes.titlesize': 10,
                'xtick.labelsize': 7,
                'ytick.labelsize': 7,
                'legend.fontsize': 8,
                'figure.titlesize': 12,
                'axes.grid': False,  # No grid
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.spines.left': False,  # Remove left spine too for ultra clean look
                'axes.spines.bottom': False,  # Remove bottom spine
                'xtick.bottom': False,  # Remove x ticks
                'ytick.left': False,   # Remove y ticks
                'axes.axisbelow': True,
                'figure.facecolor': 'white',
                'axes.facecolor': 'white'
            })
            
            # Smaller figure size for better integration
            fig = plt.figure(figsize=(6, 4), facecolor='white')
            fig.suptitle('Traffic Visualization', fontsize=11, fontweight='500', 
                        color='#374151', y=0.95)
            
            # Single clean line chart - more space efficient
            ax = fig.add_subplot(111)
            
            # Ultra clean line plot
            ax.plot(dates, totals, linewidth=2, color='#3B82F6', 
                   marker='', markersize=0)  # No markers for cleaner look
            
            # Subtle fill
            ax.fill_between(dates, totals, alpha=0.1, color='#3B82F6')
            
            # Clean labels without borders
            ax.set_title('Daily Traffic Volume', fontweight='500', 
                        color='#4B5563', fontsize=10, pad=15)
            
            # Remove all spines and ticks for ultra clean look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.tick_params(left=False, bottom=False)
            
            # Subtle labels only
            if len(dates) <= 10:
                ax.set_xticks(dates)
                ax.set_xticklabels([d.strftime('%m/%d') for d in dates], 
                                  rotation=0, ha='center', color='#6B7280')
            else:
                # Sample dates for readability
                step = len(dates) // 5
                sample_dates = dates[::step]
                ax.set_xticks(sample_dates)
                ax.set_xticklabels([d.strftime('%m/%d') for d in sample_dates], 
                                  rotation=0, ha='center', color='#6B7280')
            
            # Clean y-axis labels
            ax.set_ylabel('Vehicles', color='#6B7280', fontsize=8)
            y_ticks = ax.get_yticks()
            ax.set_yticklabels([f'{int(y)}' for y in y_ticks], color='#6B7280')
            
            # Tight layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.85, bottom=0.15, left=0.12, right=0.95)
            
            # Save with high quality but smaller size
            temp_path = f"temp_clean_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(temp_path, dpi=200, bbox_inches='tight', facecolor='white', 
                       edgecolor='none', pad_inches=0.1)
            plt.close()
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating clean charts: {e}")
            return None

    def create_data_section(self, data):
        """Create clean data table without borders"""
        elements = []
        
        elements.append(Paragraph("Data Details", self.styles['CleanSection']))
        
        if not data or len(data) == 0:
            elements.append(Paragraph("No data available for display", self.styles['CleanInfo']))
            return elements
        
        # Prepare clean table data
        table_data = [["No", "Date", "KM", "Period", "Total", "Dir A", "Dir B", "Description"]]
        
        # Limit to 30 rows for cleaner presentation
        display_data = data[:30]
        
        for i, record in enumerate(display_data, 1):
            row = [
                str(i),
                str(record.get('Tanggal', '')),
                str(record.get('Kilometer', '')),
                str(record.get('Periode Jam', '')),
                str(record.get('Total', 0) or 0),
                str(record.get('Jalur A', record.get('Naik', 0)) or 0),
                str(record.get('Jalur B', record.get('Turun', 0)) or 0),
                str(record.get('Deskripsi', ''))[:20] + ("..." if len(str(record.get('Deskripsi', ''))) > 20 else "")
            ]
            table_data.append(row)
        
        # Ultra clean table - no borders, minimal styling
        data_table = Table(table_data, colWidths=[0.4*inch, 0.9*inch, 0.6*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.6*inch, 1.5*inch])
        data_table.setStyle(TableStyle([
            # Header - clean typography only
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
            
            # Body - minimal styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#6B7280')),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Date
            ('ALIGN', (2, 0), (6, -1), 'CENTER'),  # Numbers
            ('ALIGN', (7, 0), (7, -1), 'LEFT'),    # Description
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Minimal padding
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            
            # NO BORDERS OR BACKGROUNDS - pure clean design
        ]))
        
        elements.append(data_table)
        
        # Clean summary info
        elements.append(Spacer(1, 12))
        summary_text = f"Displaying {len(display_data)} of {len(data)} total records"
        elements.append(Paragraph(summary_text, self.styles['CleanInfo']))
        
        return elements

    def generate_ultra_clean_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate ultra clean PDF with minimal design"""
        try:
            # Clean document setup
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                 rightMargin=1*inch, leftMargin=1*inch, 
                                 topMargin=0.75*inch, bottomMargin=0.75*inch)
            
            elements = []
            
            # Page 1: Summary and visualization
            elements.extend(self.create_clean_header(date_range, filter_info))
            elements.extend(self.create_summary_section(stats))
            
            # Add chart if data exists - smaller, integrated size
            if data and len(data) > 0:
                elements.append(Paragraph("Visualization", self.styles['CleanSection']))
                
                chart_path = self.create_ultra_clean_charts(data)
                if chart_path:
                    # Smaller chart image for better integration
                    chart_img = Image(chart_path, width=4.5*inch, height=3*inch)
                    elements.append(chart_img)
                    elements.append(Spacer(1, 20))
                    
                    # Clean up temp file
                    try:
                        os.remove(chart_path)
                    except:
                        pass
            
            # Page break before data table
            elements.append(PageBreak())
            
            # Page 2: Data table
            elements.extend(self.create_clean_header(date_range, filter_info))
            elements.extend(self.create_data_section(data))
            
            # Build the clean PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error generating ultra clean PDF: {e}")
            return False

    def generate_matplotlib_clean_pdf(self, data, stats, filename, date_range=None, filter_info=None):
        """Generate PDF using matplotlib with ultra clean design"""
        try:
            with PdfPages(filename) as pdf:
                # Ultra clean matplotlib settings
                plt.rcParams.update({
                    'font.family': 'sans-serif',
                    'font.size': 10,
                    'axes.labelsize': 9,
                    'axes.titlesize': 11,
                    'figure.titlesize': 13,
                    'axes.grid': False,
                    'axes.spines.top': False,
                    'axes.spines.right': False,
                    'axes.spines.left': False,
                    'axes.spines.bottom': False,
                    'xtick.bottom': False,
                    'ytick.left': False,
                })
                
                # Page 1: Clean summary
                fig1 = plt.figure(figsize=(8.27, 11.69), facecolor='white')
                ax = fig1.add_subplot(111)
                ax.axis('off')
                
                # Clean header
                ax.text(0.05, 0.95, 'JJC', fontsize=18, fontweight='bold', 
                       color='#1F2937', va='top', ha='left')
                
                # Meta info - clean and minimal
                y_pos = 0.95
                meta_info = [
                    f'Generated: {datetime.now().strftime("%d %B %Y")}',
                    f'Period: {date_range}' if date_range else None,
                    f'Filter: {filter_info}' if filter_info else None
                ]
                
                for info in meta_info:
                    if info:
                        ax.text(0.95, y_pos, info, fontsize=9, color='#6B7280', 
                               va='top', ha='right')
                        y_pos -= 0.025
                
                # Main title
                ax.text(0.05, 0.85, 'Traffic Analysis Report', fontsize=14, 
                       fontweight='500', color='#374151', va='top', ha='left')
                
                # Summary section
                ax.text(0.05, 0.75, 'Summary', fontsize=12, fontweight='bold', 
                       color='#374151', va='top', ha='left')
                
                if stats:
                    y_start = 0.65
                    stats_items = [
                        ('Total Records', stats.get('total_records', 0)),
                        ('Total Vehicles', stats.get('total_vehicles', 0)),
                        ('Direction A', stats.get('total_up', 0)),
                        ('Direction B', stats.get('total_down', 0)),
                        ('Daily Average', stats.get('average_per_day', 0)),
                        ('Unique Days', stats.get('unique_dates', 0))
                    ]
                    
                    for i, (label, value) in enumerate(stats_items):
                        row = i // 2
                        col = i % 2
                        x_pos = 0.05 + col * 0.45
                        y_pos = y_start - row * 0.06
                        
                        # Clean text without boxes
                        ax.text(x_pos, y_pos, label, fontsize=10, color='#4B5563', va='center')
                        ax.text(x_pos + 0.35, y_pos, str(value), fontsize=10, 
                               fontweight='bold', color='#1F2937', va='center', ha='right')
                
                # Add visualization if data exists
                if data and len(data) > 0:
                    ax.text(0.05, 0.35, 'Visualization', fontsize=12, fontweight='bold', 
                           color='#374151', va='top', ha='left')
                    
                    # Create clean chart
                    chart_path = self.create_ultra_clean_charts(data)
                    if chart_path:
                        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
                        import matplotlib.image as mpimg
                        
                        chart_img = mpimg.imread(chart_path)
                        imagebox = OffsetImage(chart_img, zoom=0.8)
                        ab = AnnotationBbox(imagebox, (0.5, 0.2), frameon=False)
                        ax.add_artist(ab)
                        
                        # Cleanup
                        try:
                            os.remove(chart_path)
                        except:
                            pass
                
                pdf.savefig(fig1, bbox_inches='tight', facecolor='white')
                plt.close()
                
                # Page 2: Clean data table if data exists
                if data and len(data) > 0:
                    fig2 = plt.figure(figsize=(8.27, 11.69), facecolor='white')
                    ax2 = fig2.add_subplot(111)
                    ax2.axis('off')
                    
                    # Header
                    ax2.text(0.05, 0.95, 'JJC', fontsize=18, fontweight='bold', 
                           color='#1F2937', va='top', ha='left')
                    ax2.text(0.95, 0.95, f'Generated: {datetime.now().strftime("%d %B %Y")}', 
                           fontsize=9, color='#6B7280', va='top', ha='right')
                    
                    if date_range:
                        ax2.text(0.95, 0.925, f'Period: {date_range}', 
                               fontsize=9, color='#6B7280', va='top', ha='right')
                    
                    ax2.text(0.05, 0.85, 'Traffic Analysis Report', fontsize=14, 
                           fontweight='500', color='#374151', va='top', ha='left')
                    
                    ax2.text(0.05, 0.75, 'Data Details', fontsize=12, fontweight='bold', 
                           color='#374151', va='top', ha='left')
                    
                    # Prepare clean table
                    headers = ['No', 'Date', 'KM', 'Period', 'Total', 'Dir A', 'Dir B', 'Description']
                    table_data = []
                    
                    for i, record in enumerate(data[:35], 1):  # Limit for clean presentation
                        row = [
                            str(i),
                            str(record.get('Tanggal', '')),
                            str(record.get('Kilometer', '')),
                            str(record.get('Periode Jam', '')),
                            str(record.get('Total', 0) or 0),
                            str(record.get('Jalur A', record.get('Naik', 0)) or 0),
                            str(record.get('Jalur B', record.get('Turun', 0)) or 0),
                            str(record.get('Deskripsi', ''))[:12] + ("..." if len(str(record.get('Deskripsi', ''))) > 12 else "")
                        ]
                        table_data.append(row)
                    
                    # Ultra clean table
                    table = ax2.table(cellText=table_data, colLabels=headers, 
                                     loc='center', cellLoc='center',
                                     bbox=[0.05, 0.15, 0.9, 0.55])
                    
                    table.auto_set_font_size(False)
                    table.set_fontsize(7)
                    table.scale(1, 1.2)
                    
                    # Clean header styling
                    for i in range(len(headers)):
                        table[(0, i)].set_text_props(weight='bold', color='#374151')
                        table[(0, i)].set_facecolor('white')
                        table[(0, i)].set_edgecolor('none')  # No borders
                    
                    # Clean body styling
                    for i in range(1, len(table_data) + 1):
                        for j in range(len(headers)):
                            table[(i, j)].set_facecolor('white')
                            table[(i, j)].set_edgecolor('none')  # No borders
                            table[(i, j)].set_text_props(color='#6B7280')
                    
                    # Clean summary
                    summary_text = f"Displaying {min(35, len(data))} of {len(data)} total records"
                    ax2.text(0.05, 0.1, summary_text, fontsize=9, color='#6B7280', va='top')
                    
                    pdf.savefig(fig2, bbox_inches='tight', facecolor='white')
                    plt.close()
            
            return True
            
        except Exception as e:
            print(f"Error generating matplotlib clean PDF: {e}")
            return False