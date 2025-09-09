import sys
import sqlite3
import os
from datetime import datetime, time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                            QPushButton, QComboBox, QTimeEdit, QLineEdit, QLabel,
                            QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                            QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFont, QColor

class DatabaseManager:
    def __init__(self):
        self.db_name = "okul_zil_programi.db"
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlat ve tabloları oluştur"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Zil programı tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zil_programi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun TEXT NOT NULL,
                tip TEXT NOT NULL,
                baslik TEXT NOT NULL,
                baslangic_saat TEXT NOT NULL,
                bitis_saat TEXT NOT NULL,
                sure INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def zil_ekle(self, gun, tip, baslik, baslangic, bitis, sure):
        """Yeni zil programı ekle"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO zil_programi (gun, tip, baslik, baslangic_saat, bitis_saat, sure)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (gun, tip, baslik, baslangic, bitis, sure))
        
        conn.commit()
        conn.close()
    
    def zilleri_getir(self, gun=None):
        """Zil programlarını getir"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if gun:
            cursor.execute('SELECT * FROM zil_programi WHERE gun = ? ORDER BY baslangic_saat', (gun,))
        else:
            cursor.execute('SELECT * FROM zil_programi ORDER BY gun, baslangic_saat')
        
        ziller = cursor.fetchall()
        conn.close()
        return ziller
    
    def zil_sil(self, zil_id):
        """Zil programını sil"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM zil_programi WHERE id = ?', (zil_id,))
        
        conn.commit()
        conn.close()
    
    def zil_guncelle(self, zil_id, gun, tip, baslik, baslangic, bitis, sure):
        """Zil programını güncelle"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE zil_programi 
            SET gun = ?, tip = ?, baslik = ?, baslangic_saat = ?, bitis_saat = ?, sure = ?
            WHERE id = ?
        ''', (gun, tip, baslik, baslangic, bitis, sure, zil_id))
        
        conn.commit()
        conn.close()

class ZilEkleDialog(QDialog):
    def __init__(self, parent=None, zil_data=None):
        super().__init__(parent)
        self.zil_data = zil_data
        self.init_ui()
        
        if zil_data:
            self.setWindowTitle("Zil Programını Düzenle")
            self.load_data()
        else:
            self.setWindowTitle("Yeni Zil Programı Ekle")
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Gün seçimi
        self.gun_combo = QComboBox()
        self.gun_combo.addItems(['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 
                                'Cuma', 'Cumartesi', 'Pazar'])
        layout.addRow("Gün:", self.gun_combo)
        
        # Tip seçimi
        self.tip_combo = QComboBox()
        self.tip_combo.addItems(['Ders', 'Teneffüs'])
        layout.addRow("Tip:", self.tip_combo)
        
        # Başlık
        self.baslik_edit = QLineEdit()
        self.baslik_edit.setPlaceholderText("Örn: 1. Ders, Öğle Teneffüsü")
        layout.addRow("Başlık:", self.baslik_edit)
        
        # Başlangıç saati
        self.baslangic_time = QTimeEdit()
        self.baslangic_time.setDisplayFormat("HH:mm")
        self.baslangic_time.setTime(QTime(8, 0))
        layout.addRow("Başlangıç Saati:", self.baslangic_time)
        
        # Bitiş saati
        self.bitis_time = QTimeEdit()
        self.bitis_time.setDisplayFormat("HH:mm")
        self.bitis_time.setTime(QTime(8, 45))
        layout.addRow("Bitiş Saati:", self.bitis_time)
        
        # Süre (dakika)
        self.sure_edit = QLineEdit()
        self.sure_edit.setPlaceholderText("Dakika cinsinden")
        layout.addRow("Süre (Dakika):", self.sure_edit)
        
        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
        
        # Süreyi otomatik hesapla
        self.baslangic_time.timeChanged.connect(self.hesapla_sure)
        self.bitis_time.timeChanged.connect(self.hesapla_sure)
    
    def hesapla_sure(self):
        """Başlangıç ve bitiş saatinden süreyi hesapla"""
        baslangic = self.baslangic_time.time()
        bitis = self.bitis_time.time()
        
        # QTime'dan dakikaya çevir
        baslangic_dakika = baslangic.hour() * 60 + baslangic.minute()
        bitis_dakika = bitis.hour() * 60 + bitis.minute()
        
        if bitis_dakika > baslangic_dakika:
            sure = bitis_dakika - baslangic_dakika
            self.sure_edit.setText(str(sure))
    
    def load_data(self):
        """Düzenleme için mevcut veriyi yükle"""
        if self.zil_data:
            gun_index = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 
                        'Cuma', 'Cumartesi', 'Pazar'].index(self.zil_data[1])
            self.gun_combo.setCurrentIndex(gun_index)
            
            tip_index = ['Ders', 'Teneffüs'].index(self.zil_data[2])
            self.tip_combo.setCurrentIndex(tip_index)
            
            self.baslik_edit.setText(self.zil_data[3])
            
            # Saatleri ayarla
            baslangic_parts = self.zil_data[4].split(':')
            self.baslangic_time.setTime(QTime(int(baslangic_parts[0]), int(baslangic_parts[1])))
            
            bitis_parts = self.zil_data[5].split(':')
            self.bitis_time.setTime(QTime(int(bitis_parts[0]), int(bitis_parts[1])))
            
            self.sure_edit.setText(str(self.zil_data[6]))
    
    def get_data(self):
        """Dialog verilerini döndür"""
        return {
            'gun': self.gun_combo.currentText(),
            'tip': self.tip_combo.currentText(),
            'baslik': self.baslik_edit.text(),
            'baslangic': self.baslangic_time.time().toString("HH:mm"),
            'bitis': self.bitis_time.time().toString("HH:mm"),
            'sure': int(self.sure_edit.text()) if self.sure_edit.text().isdigit() else 0
        }

class OkulZilProgrami(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.load_all_data()
        
        # Timer for current time display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_time)
        self.timer.start(1000)  # Her saniye güncelle
    
    def init_ui(self):
        self.setWindowTitle("Okul Zil Programı Yönetimi")
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Üst panel - Mevcut zaman ve kontroller
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Günlük sekmeler
        self.gunler = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        self.tablolar = {}
        
        for gun in self.gunler:
            tab = self.create_gun_tab(gun)
            self.tab_widget.addTab(tab, gun)
        
        # Tüm program sekmesi
        tum_program_tab = self.create_tum_program_tab()
        self.tab_widget.addTab(tum_program_tab, "Tüm Program")
    
    def create_top_panel(self):
        """Üst panel oluştur"""
        panel = QGroupBox("Kontrol Paneli")
        layout = QHBoxLayout()
        
        # Mevcut zaman
        self.zaman_label = QLabel()
        self.zaman_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.update_current_time()
        layout.addWidget(QLabel("Şu anki zaman:"))
        layout.addWidget(self.zaman_label)
        
        layout.addStretch()
        
        # Genel kontrol butonları
        yeni_btn = QPushButton("Yeni Zil Ekle")
        yeni_btn.clicked.connect(self.yeni_zil_ekle)
        layout.addWidget(yeni_btn)
        
        yenile_btn = QPushButton("Yenile")
        yenile_btn.clicked.connect(self.load_all_data)
        layout.addWidget(yenile_btn)
        
        panel.setLayout(layout)
        return panel
    
    def update_current_time(self):
        """Mevcut zamanı güncelle"""
        now = datetime.now()
        self.zaman_label.setText(now.strftime("%H:%M:%S"))
    
    def create_gun_tab(self, gun):
        """Her gün için tab oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel(f"{gun} Zil Programı")
        baslik.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(baslik)
        
        # Tablo
        tablo = QTableWidget()
        tablo.setColumnCount(7)
        tablo.setHorizontalHeaderLabels(['ID', 'Tip', 'Başlık', 'Başlangıç', 'Bitiş', 'Süre', 'İşlemler'])
        
        # Tablo ayarları
        header = tablo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        tablo.setAlternatingRowColors(True)
        tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(tablo)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        ekle_btn = QPushButton(f"{gun} için Zil Ekle")
        ekle_btn.clicked.connect(lambda: self.yeni_zil_ekle(gun))
        btn_layout.addWidget(ekle_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        
        self.tablolar[gun] = tablo
        return widget
    
    def create_tum_program_tab(self):
        """Tüm program sekmesi oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Haftalık Zil Programı")
        baslik.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(baslik)
        
        # Tablo
        self.tum_tablo = QTableWidget()
        self.tum_tablo.setColumnCount(8)
        self.tum_tablo.setHorizontalHeaderLabels(['ID', 'Gün', 'Tip', 'Başlık', 'Başlangıç', 'Bitiş', 'Süre', 'İşlemler'])
        
        # Tablo ayarları
        header = self.tum_tablo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tum_tablo.setAlternatingRowColors(True)
        self.tum_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.tum_tablo)
        widget.setLayout(layout)
        
        return widget
    
    def yeni_zil_ekle(self, gun=None):
        """Yeni zil ekleme dialog'unu aç"""
        dialog = ZilEkleDialog(self)
        if gun:
            gun_index = self.gunler.index(gun)
            dialog.gun_combo.setCurrentIndex(gun_index)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['baslik'] and data['sure'] > 0:
                self.db.zil_ekle(data['gun'], data['tip'], data['baslik'], 
                                data['baslangic'], data['bitis'], data['sure'])
                self.load_all_data()
                QMessageBox.information(self, "Başarılı", "Zil programı eklendi!")
            else:
                QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doğru şekilde doldurun!")
    
    def zil_duzenle(self, zil_id, zil_data):
        """Zil programını düzenle"""
        dialog = ZilEkleDialog(self, zil_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['baslik'] and data['sure'] > 0:
                self.db.zil_guncelle(zil_id, data['gun'], data['tip'], data['baslik'],
                                   data['baslangic'], data['bitis'], data['sure'])
                self.load_all_data()
                QMessageBox.information(self, "Başarılı", "Zil programı güncellendi!")
            else:
                QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doğru şekilde doldurun!")
    
    def zil_sil(self, zil_id, baslik):
        """Zil programını sil"""
        reply = QMessageBox.question(self, "Silme Onayı", 
                                   f"'{baslik}' programını silmek istediğinize emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.zil_sil(zil_id)
            self.load_all_data()
            QMessageBox.information(self, "Başarılı", "Zil programı silindi!")
    
    def create_action_buttons(self, tablo, zil_data):
        """İşlem butonları oluştur"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Düzenle butonu
        duzenle_btn = QPushButton("Düzenle")
        duzenle_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; }")
        duzenle_btn.clicked.connect(lambda: self.zil_duzenle(zil_data[0], zil_data))
        layout.addWidget(duzenle_btn)
        
        # Sil butonu
        sil_btn = QPushButton("Sil")
        sil_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        sil_btn.clicked.connect(lambda: self.zil_sil(zil_data[0], zil_data[3]))
        layout.addWidget(sil_btn)
        
        tablo.setCellWidget(tablo.rowCount() - 1, tablo.columnCount() - 1, widget)
    
    def load_gun_data(self, gun):
        """Belirli bir günün verilerini yükle"""
        tablo = self.tablolar[gun]
        ziller = self.db.zilleri_getir(gun)
        
        tablo.setRowCount(len(ziller))
        
        for row, zil in enumerate(ziller):
            tablo.setItem(row, 0, QTableWidgetItem(str(zil[0])))  # ID
            tablo.setItem(row, 1, QTableWidgetItem(zil[2]))       # Tip
            tablo.setItem(row, 2, QTableWidgetItem(zil[3]))       # Başlık
            tablo.setItem(row, 3, QTableWidgetItem(zil[4]))       # Başlangıç
            tablo.setItem(row, 4, QTableWidgetItem(zil[5]))       # Bitiş
            tablo.setItem(row, 5, QTableWidgetItem(f"{zil[6]} dk")) # Süre
            
            # Tip'e göre renklendirme - QColor kullanarak
            if zil[2] == "Ders":
                bg_color = QColor(227, 242, 253)  # Açık mavi
            else:
                bg_color = QColor(243, 229, 245)  # Açık mor
            
            for col in range(6):
                tablo.item(row, col).setBackground(bg_color)
            
            # İşlem butonları
            self.create_action_buttons(tablo, zil)
    
    def load_tum_program_data(self):
        """Tüm program verilerini yükle"""
        ziller = self.db.zilleri_getir()
        self.tum_tablo.setRowCount(len(ziller))
        
        for row, zil in enumerate(ziller):
            self.tum_tablo.setItem(row, 0, QTableWidgetItem(str(zil[0])))  # ID
            self.tum_tablo.setItem(row, 1, QTableWidgetItem(zil[1]))       # Gün
            self.tum_tablo.setItem(row, 2, QTableWidgetItem(zil[2]))       # Tip
            self.tum_tablo.setItem(row, 3, QTableWidgetItem(zil[3]))       # Başlık
            self.tum_tablo.setItem(row, 4, QTableWidgetItem(zil[4]))       # Başlangıç
            self.tum_tablo.setItem(row, 5, QTableWidgetItem(zil[5]))       # Bitiş
            self.tum_tablo.setItem(row, 6, QTableWidgetItem(f"{zil[6]} dk")) # Süre
            
            # Tip'e göre renklendirme - QColor kullanarak
            if zil[2] == "Ders":
                bg_color = QColor(227, 242, 253)  # Açık mavi
            else:
                bg_color = QColor(243, 229, 245)  # Açık mor
            
            for col in range(7):
                self.tum_tablo.item(row, col).setBackground(bg_color)
            
            # İşlem butonları
            self.create_action_buttons(self.tum_tablo, zil)
    
    def load_all_data(self):
        """Tüm verileri yükle"""
        for gun in self.gunler:
            self.load_gun_data(gun)
        self.load_tum_program_data()

def main():
    app = QApplication(sys.argv)
    
    # Uygulama stili
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #007bff;
        }
        QTableWidget {
            background-color: white;
            alternate-background-color: #f8f9fa;
            gridline-color: #dee2e6;
        }
        QTableWidget::item:selected {
            background-color: #007bff;
            color: white;
        }
        QPushButton {
            padding: 8px 16px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #f8f9fa;
        }
        QPushButton:hover {
            background-color: #e9ecef;
        }
        QPushButton:pressed {
            background-color: #dee2e6;
        }
    """)
    
    window = OkulZilProgrami()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
