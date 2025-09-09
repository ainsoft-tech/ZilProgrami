#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Okul Zil Programı – PyQt5 + SQLite3
7 gün, ders/teneffüs tanım + düzenle + sil
Ses: zil_sesleri/ders.wav  |  teneffus.wav
"""

import sys, sqlite3, os, threading, time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTimeEdit, QSpinBox,
                             QLabel, QComboBox, QListWidget, QMessageBox,
                             QGroupBox, QGridLayout, QFileDialog)
from PyQt5.QtCore import QTime, pyqtSignal, QObject, Qt, QUrl
from PyQt5.QtMultimedia import QSoundEffect

DB_FILE       = "zil_programi.db"
SES_KLASORU   = "zil_sesleri"

# ---------- VT ----------
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS zil (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                gun       INTEGER NOT NULL,
                tur       TEXT NOT NULL,
                bas_saat  TEXT NOT NULL,
                sure      INTEGER NOT NULL
            )
        """)
        conn.commit()

# ---------- Ses ----------
class ZilPlayer(QObject):
    def __init__(self, klasor=SES_KLASORU):
        super().__init__()
        self.klasor = klasor
        self.ders_se  = QSoundEffect()
        self.ten_se   = QSoundEffect()
        self._yukle()

    def _yukle(self):
        ders_wav = os.path.join(self.klasor, "ders.wav")
        ten_wav  = os.path.join(self.klasor, "teneffus.wav")
        for wav, obj, ad in [(ders_wav, self.ders_se, "ders"),
                             (ten_wav,  self.ten_se, "teneffus")]:
            if os.path.isfile(wav):
                obj.setSource(QUrl.fromLocalFile(wav))
                obj.setVolume(1.0)
            else:
                print(f"[UYARI] {wav} bulunamadı – bip kullanılacak")
                obj = None

    def cal(self, tur: str, _sure: int):
        se = self.ten_se if tur == "TENEFFUS" else self.ders_se
        if se and se.source().isValid():
            se.play()
        else:
            try:
                import winsound
                winsound.Beep(1000, 700)
            except Exception:
                pass

# ---------- Thread ----------
class ZilThread(threading.Thread, QObject):
    ring = pyqtSignal(str, int)
    def __init__(self, player: ZilPlayer):
        threading.Thread.__init__(self, daemon=True)
        QObject.__init__(self)
        self.player = player
        self.ring.connect(self.player.cal)
        self._running = True
    def run(self):
        while self._running:
            now = datetime.now()
            weekday = now.weekday()
            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = dict_factory
                cur = conn.execute(
                    "SELECT * FROM zil WHERE gun=? ORDER BY bas_saat", (weekday,)
                )
                rows = cur.fetchall()
            for row in rows:
                bas = datetime.strptime(row["bas_saat"], "%H:%M")
                bas = now.replace(hour=bas.hour, minute=bas.minute, second=0, microsecond=0)
                bitis = bas + timedelta(minutes=row["sure"])
                if bas <= now < bitis:
                    self.ring.emit(row["tur"], row["sure"])
                    delta = (bitis - now).total_seconds()
                    time.sleep(max(delta, 1))
                    break
            time.sleep(5)
    def stop(self):
        self._running = False

# ---------- GUI ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Okul Zil Programı")
        self.resize(500, 700)
        init_db()
        self.player = ZilPlayer()
        self.ses_klasoru = SES_KLASORU

        top = QGroupBox("Zil Tanımları")
        lay_top = QGridLayout(top)

        self.cmb_gun = QComboBox()
        self.cmb_gun.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])

        self.time_bas = QTimeEdit(); self.time_bas.setDisplayFormat("HH:mm"); self.time_bas.setTime(QTime(8, 0))
        self.spin_sure = QSpinBox(); self.spin_sure.setRange(1, 180); self.spin_sure.setValue(40); self.spin_sure.setSuffix(" dk")

        self.btn_ders   = QPushButton("+ Ders")
        self.btn_ten    = QPushButton("+ Teneffüs")
        self.btn_sil    = QPushButton("Seçileni Sil")
        self.btn_guncel = QPushButton("Güncelle")
        self.btn_ses_kl = QPushButton("Ses Klasörü Seç…")

        # ------ yükseklik & stil ------
        TUM_YUKSEKLIK, BUTON_FONT = 36, "14px"
        buton_stil = f"QPushButton{{font-size:{BUTON_FONT};padding:6px;}}"
        for w in (self.btn_ders, self.btn_ten, self.btn_sil, self.btn_guncel, self.btn_ses_kl):
            w.setFixedHeight(TUM_YUKSEKLIK); w.setStyleSheet(buton_stil)
        for w in (self.cmb_gun, self.time_bas, self.spin_sure):
            w.setFixedHeight(TUM_YUKSEKLIK)
        # --------------------------------

        lay_top.addWidget(QLabel("Gün:"), 0, 0); lay_top.addWidget(self.cmb_gun, 0, 1)
        lay_top.addWidget(QLabel("Başlangıç:"), 1, 0); lay_top.addWidget(self.time_bas, 1, 1)
        lay_top.addWidget(QLabel("Süre:"), 2, 0); lay_top.addWidget(self.spin_sure, 2, 1)
        lay_top.addWidget(self.btn_ders, 3, 0); lay_top.addWidget(self.btn_ten, 3, 1)
        lay_top.addWidget(self.btn_sil, 4, 0); lay_top.addWidget(self.btn_guncel, 4, 1)
        lay_top.addWidget(self.btn_ses_kl, 5, 0, 1, 2)

        self.liste = QListWidget()
        self.liste.itemDoubleClicked.connect(self.listeye_tikla)
        self.liste.setFixedHeight(220)

        central = QWidget()
        v = QVBoxLayout(central)
        v.addWidget(top); v.addWidget(self.liste)
        self.setCentralWidget(central)
        self.status = self.statusBar(); self.status.showMessage(f"Ses klasörü: {self.ses_klasoru}")

        # bağlantılar
        self.cmb_gun.currentIndexChanged.connect(self.doldur)
        self.btn_ders.clicked.connect(lambda: self.ekle("DERS"))
        self.btn_ten.clicked.connect(lambda: self.ekle("TENEFFUS"))
        self.btn_sil.clicked.connect(self.sil)
        self.btn_guncel.clicked.connect(self.guncelle)
        self.btn_ses_kl.clicked.connect(self.ses_klasoru_sec)

        self.doldur()
        self.zil_thread = ZilThread(self.player)
        self.zil_thread.start()
        self.duzenleme_id = None

    # ---------- fonksiyonlar ----------
    def doldur(self):
        self.liste.clear()
        gun = self.cmb_gun.currentIndex()
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = dict_factory
            cur = conn.execute("SELECT * FROM zil WHERE gun=? ORDER BY bas_saat", (gun,))
            self.gunluk_veri = cur.fetchall()
            for row in self.gunluk_veri:
                self.liste.addItem(f"{row['bas_saat']}  {row['tur']}  ({row['sure']} dk)")

    def ekle(self, tur):
        gun = self.cmb_gun.currentIndex()
        saat = self.time_bas.time().toString("HH:mm")
        sure = self.spin_sure.value()
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT INTO zil (gun, tur, bas_saat, sure) VALUES (?,?,?,?)", (gun, tur, saat, sure))
            conn.commit()
        self.doldur()

    def sil(self):
        sec = self.liste.currentRow()
        if sec < 0: return
        sil_id = self.gunluk_veri[sec]["id"]
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM zil WHERE id=?", (sil_id,))
            conn.commit()
        self.doldur()

    def listeye_tikla(self, item):
        sec = self.liste.row(item)
        if sec < 0: return
        row = self.gunluk_veri[sec]
        self.duzenleme_id = row["id"]
        self.time_bas.setTime(QTime.fromString(row["bas_saat"], "HH:mm"))
        self.spin_sure.setValue(row["sure"])
        self.btn_guncel.setStyleSheet("background-color: #aaffaa;")

    def guncelle(self):
        if self.duzenleme_id is None:
            QMessageBox.information(self, "Bilgi", "Önce listeden çift tıklayın.")
            return
        saat = self.time_bas.time().toString("HH:mm")
        sure = self.spin_sure.value()
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("UPDATE zil SET bas_saat=?, sure=? WHERE id=?", (saat, sure, self.duzenleme_id))
            conn.commit()
        self.duzenleme_id = None
        self.btn_guncel.setStyleSheet("")
        self.doldur()

    def ses_klasoru_sec(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Ses Klasörü Seç", self.ses_klasoru)
        if new_dir:
            self.ses_klasoru = new_dir
            self.player = ZilPlayer(self.ses_klasoru)
            self.status.showMessage(f"Ses klasörü: {self.ses_klasoru}")

    def closeEvent(self, event):
        self.zil_thread.stop()
        event.accept()

# ---------- main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())