"""
Konfigurasi Terpusat untuk Deteksi Kendaraan YOLO
Memastikan konsistensi parameter di seluruh aplikasi
Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk)
"""

class DetectionConfig:
    """ Kelas konfigurasi untuk memastikan konsistensi deteksi kendaraan 
    Fokus hanya pada deteksi mobil (tidak termasuk bus dan truk) """ 
    def __init__(self):
        # Parameter deteksi yang konsisten
        self.confidence = 0.25
        self.iou = 0.45
        self.classes = [0]  # hanya car dalam COCO dataset
        
        # Parameter tracking yang konsisten
        self.tracker = "bytetrack.yaml"
        self.persist = True
        
        # Device setting yang konsisten
        self.device = 'auto'  # 'auto', 'cpu', atau 'cuda'
        
        # Parameter counting line
        self.line_ratio = 0.7  # 70% dari atas
        self.detection_zone = 50  # Zona deteksi dalam pixel
        
        # Parameter performance
        self.verbose = False
        
        # Debug mode (tidak mempengaruhi device setting)
        self.debug = False
    
    def set_confidence(self, confidence):
        """Set confidence threshold"""
        self.confidence = max(0.1, min(0.9, confidence))
    
    def set_iou(self, iou):
        """Set IoU threshold"""
        self.iou = max(0.1, min(0.9, iou))
    
    def set_device(self, device):
        """Set device (auto, cpu, cuda)"""
        if device in ['auto', 'cpu', 'cuda']:
            self.device = device
        else:
            self.device = 'auto'
    
    def set_debug(self, debug):
        """Set debug mode (tidak mempengaruhi device)"""
        self.debug = bool(debug)
    
    def get_device_setting(self):
        """Get device setting yang konsisten"""
        if self.device == 'auto':
            return None  # Let YOLO decide
        return self.device
    
    def get_tracking_params(self):
        """Get parameter untuk tracking yang konsisten"""
        return {
            'persist': self.persist,
            'classes': self.classes,
            'tracker': self.tracker,
            'conf': self.confidence,
            'iou': self.iou,
            'verbose': self.verbose,
            'device': self.get_device_setting()
        }
    
    def get_detection_params(self):
        """Get parameter untuk deteksi yang konsisten"""
        return {
            'classes': self.classes,
            'conf': self.confidence,
            'iou': self.iou,
            'verbose': self.verbose,
            'device': self.get_device_setting()
        }
    
    def copy(self):
        """Buat salinan konfigurasi"""
        new_config = DetectionConfig()
        new_config.confidence = self.confidence
        new_config.iou = self.iou
        new_config.classes = self.classes.copy()
        new_config.tracker = self.tracker
        new_config.persist = self.persist
        new_config.device = self.device
        new_config.line_ratio = self.line_ratio
        new_config.detection_zone = self.detection_zone
        new_config.verbose = self.verbose
        new_config.debug = self.debug
        return new_config

# Global config instance
DEFAULT_CONFIG = DetectionConfig()
