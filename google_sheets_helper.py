"""
Helper module untuk Google Sheets API
Menggunakan service account credentials untuk mengakses spreadsheet
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional

class GoogleSheetsManager:
    """Manager untuk operasi Google Sheets
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)"""
    
    def __init__(self, credentials_path: str = "credentials/credentials.json"):
        """
        Inisialisasi Google Sheets Manager
        
        Args:
            credentials_path: Path ke file credentials.json
        """
        self.credentials_path = credentials_path
        self.gc = None
        self.spreadsheet = None
        self.worksheet = None
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Baut8fnhzC251DjUj4vEYKZQITUvY2IkNjXmU6AMFQk/edit?hl=id&gid=0#gid=0"
        self.spreadsheet_id = "1Baut8fnhzC251DjUj4vEYKZQITUvY2IkNjXmU6AMFQk"
        
    def authenticate(self) -> bool:
        """
        Authentikasi dengan Google Sheets API
        
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            if not os.path.exists(self.credentials_path):
                print(f"Credentials file not found: {self.credentials_path}")
                return False
            
            # Setup credentials
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            # Authorize gspread client
            self.gc = gspread.authorize(creds)
            
            # Open spreadsheet
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # Get or create worksheet
            try:
                self.worksheet = self.spreadsheet.worksheet("Data Counting")
                print("Worksheet 'Data Counting' ditemukan")
                # Pastikan header memiliki kolom 'Deskripsi'
                header_row = self.worksheet.row_values(1)
                if 'Deskripsi' not in header_row:
                    print("Menambahkan kolom 'Deskripsi' ke header...")
                    if not header_row:
                        header_row = ["ID", "Tanggal", "Kilometer", "Periode Jam", "Total", "Jalur A", "Jalur B", "Deskripsi", "Waktu Input"]
                    else:
                        # Sisipkan 'Deskripsi' sebelum 'Waktu Input' jika ada, atau append di akhir
                        if 'Waktu Input' in header_row:
                            idx = header_row.index('Waktu Input')
                            header_row.insert(idx, 'Deskripsi')
                        else:
                            header_row.append('Deskripsi')
                    self.worksheet.delete_rows(1)
                    self.worksheet.insert_row(header_row, 1)
            except gspread.WorksheetNotFound:
                print("Worksheet 'Data Counting' tidak ditemukan, membuat baru...")
                self.worksheet = self.spreadsheet.add_worksheet("Data Counting", 1000, 10)
                # Set headers
                headers = ["ID", "Tanggal", "Kilometer", "Periode Jam", "Total", "Jalur A", "Jalur B", "Deskripsi", "Waktu Input"]
                self.worksheet.append_row(headers)
                print("Headers berhasil ditambahkan")
            
            print("Successfully authenticated with Google Sheets")
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False
    
    def save_counting_data(self, data: Dict) -> bool:
        """
        Simpan data counting ke spreadsheet
        
        Args:
            data: Dictionary berisi data counting
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            if not self.worksheet:
                print("Worksheet not initialized")
                return False
            
            # Generate ID (auto increment)
            try:
                all_records = self.worksheet.get_all_records()
                # Skip header row, jadi ID dimulai dari 1
                new_id = len(all_records) + 1
            except Exception as e:
                print(f"Error getting records for ID generation: {e}")
                new_id = 1
            
            # Format data untuk disimpan dengan validasi
            row_data = [
                new_id,
                str(data.get('tanggal', '')),
                str(data.get('kilometer', '')),
                str(data.get('periode_jam', '')),
                int(data.get('total', 0)),
                int(data.get('naik', 0)),
                int(data.get('turun', 0)),
                str(data.get('deskripsi', '') or data.get('notes', '')),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            print(f"Saving row data: {row_data}")  # Debug log
            
            # Append row ke spreadsheet
            self.worksheet.append_row(row_data)
            
            print(f"Data saved successfully with ID: {new_id}")
            return True
            
        except Exception as e:
            print(f"Failed to save data: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def check_duplicate_time(self, tanggal: str, periode_jam: str, kilometer: str) -> bool:
        """
        Cek apakah sudah ada data dengan tanggal, periode jam, dan kilometer yang sama.
        Returns True jika duplikat ditemukan.
        """
        try:
            if not self.worksheet:
                return False
            records = self.worksheet.get_all_records()
            for record in records:
                if not record:
                    continue
                rec_tanggal = str(record.get('Tanggal', '')).strip()
                rec_periode = str(record.get('Periode Jam', '')).strip()
                rec_km = str(record.get('Kilometer', '')).strip()
                if rec_tanggal == str(tanggal).strip() and rec_periode == str(periode_jam).strip() and rec_km == str(kilometer).strip():
                    return True
            return False
        except Exception as e:
            print(f"Failed to check duplicate: {str(e)}")
            return False
    
    def get_all_data(self) -> List[Dict]:
        """
        Ambil semua data dari spreadsheet
        
        Returns:
            List[Dict]: List semua data counting
        """
        try:
            if not self.worksheet:
                print("Worksheet not initialized")
                return []
            
            records = self.worksheet.get_all_records()
            
            # Filter out empty or invalid records
            valid_records = []
            for record in records:
                if record and isinstance(record, dict):
                    # Skip record jika semua field kosong
                    if any(str(record.get(key, '')).strip() for key in ['Tanggal', 'Total', 'Jalur A', 'Jalur B']):
                        valid_records.append(record)
            
            return valid_records
            
        except Exception as e:
            print(f"Failed to get data: {str(e)}")
            return []
    
    def get_data_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Ambil data berdasarkan range tanggal
        
        Args:
            start_date: Tanggal mulai (format: YYYY-MM-DD)
            end_date: Tanggal akhir (format: YYYY-MM-DD)
            
        Returns:
            List[Dict]: List data dalam range tanggal
        """
        try:
            all_data = self.get_all_data()
            filtered_data = []
            
            for record in all_data:
                record_date = record.get('Tanggal', '')
                if start_date <= record_date <= end_date:
                    filtered_data.append(record)
            
            return filtered_data
            
        except Exception as e:
            print(f"Failed to get data by date range: {str(e)}")
            return []
    
    def get_summary_stats(self) -> Dict:
        """
        Ambil statistik summary dari semua data
        
        Returns:
            Dict: Statistik summary
        """
        try:
            all_data = self.get_all_data()
            
            if not all_data:
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
            for record in all_data:
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
                    total_vehicles += int(record.get('Total', 0) or 0)
                    total_up += int(record.get('Jalur A', 0) or 0)
                    total_down += int(record.get('Jalur B', 0) or 0)
                except (ValueError, TypeError):
                    # Skip record jika ada error konversi
                    continue
            
            # Hitung rata-rata per hari
            dates = set(record.get('Tanggal', '') for record in valid_data if record.get('Tanggal', '').strip())
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
            
        except Exception as e:
            print(f"Failed to get summary stats: {str(e)}")
            return {
                'total_records': 0,
                'total_vehicles': 0,
                'total_up': 0,
                'total_down': 0,
                'average_per_day': 0,
                'unique_dates': 0
            }

def create_sample_credentials():
    """Buat file credentials.json template"""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
    }
    
    credentials_dir = "credentials"
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)
    
    credentials_path = os.path.join(credentials_dir, "credentials.json")
    
    with open(credentials_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Template credentials created at: {credentials_path}")
    print("Please replace the template values with your actual Google Service Account credentials")

if __name__ == "__main__":
    # Test the Google Sheets manager
    manager = GoogleSheetsManager()
    
    if manager.authenticate():
        print("Authentication successful!")
        
        # Test data
        test_data = {
            'tanggal': '2024-01-01',
            'kilometer': '12+100',
            'periode_jam': '19.00-12.00',
            'total': 150,
            'naik': 75,
            'turun': 75
        }
        
        # Uncomment to test saving data
        # manager.save_counting_data(test_data)
        
        # Get summary stats
        stats = manager.get_summary_stats()
        print("Summary Stats:", stats)
    else:
        print("Authentication failed!")
        create_sample_credentials()
