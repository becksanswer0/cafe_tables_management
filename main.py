import tkinter as tk
from tkinter import messagebox
import sqlite3
import tkinter.font as tkFont 
from tkinter import Tk, Button, Label, Frame, Listbox

class Masa:
    def __init__(self, masa_no):
        self.masa_no = masa_no
        self.urunler = {}
        self.dolu = False  # Masa doluluk durumu
        self.veritabanindan_yukle()

    def masaya_urun_ekle(self, urun, fiyat):
        if urun in self.urunler:
            self.urunler[urun] += 1
        else:
            self.urunler[urun] = 1
        self.dolu = True
        self.veritabanina_kaydet(urun)

    def masadan_urun_cikar(self, urun):
        if urun in self.urunler and self.urunler[urun] > 0:
            self.urunler[urun] -= 1
            if self.urunler[urun] == 0:
                del self.urunler[urun]
            self.dolu = bool(self.urunler)  # Masa doluluğunu kontrol et
            self.veritabanina_kaydet(urun, cikart=True)

    def masanin_odemesini_al_ve_kapat(self):
        toplam_tutar = sum([urun_fiyatlari[urun] * miktar for urun, miktar in self.urunler.items()])
        self.urunler.clear()
        self.dolu = False  # Masa boşaltıldı
        self.veritabanini_temizle()
        messagebox.showinfo("Ödeme", f"Masa {self.masa_no} için toplam ödeme: {toplam_tutar} TL. Masa kapatıldı.")

    def veritabanina_kaydet(self, urun, cikart=False):
        conn = sqlite3.connect("bar_masa_takip.db")
        cursor = conn.cursor()

        if cikart:
            cursor.execute("DELETE FROM masa_urunler WHERE masa_no = ? AND urun = ?", (self.masa_no, urun))
        else:
            cursor.execute("INSERT INTO masa_urunler (masa_no, urun, miktar) VALUES (?, ?, ?) ON CONFLICT(masa_no, urun) DO UPDATE SET miktar = ?", 
                           (self.masa_no, urun, self.urunler[urun], self.urunler[urun]))

        conn.commit()
        conn.close()

    def veritabanini_temizle(self):
        conn = sqlite3.connect("bar_masa_takip.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM masa_urunler WHERE masa_no = ?", (self.masa_no,))
        conn.commit()
        conn.close()

    def veritabanindan_yukle(self):
        conn = sqlite3.connect("bar_masa_takip.db")
        cursor = conn.cursor()
        cursor.execute("SELECT urun, miktar FROM masa_urunler WHERE masa_no = ?", (self.masa_no,))
        urunler = cursor.fetchall()
        self.urunler = {urun: miktar for urun, miktar in urunler}
        self.dolu = bool(self.urunler)  # Masa dolu mu kontrol et
        conn.close()

# Ürünler ve fiyatları
urun_fiyatlari = {
    "Efes": 150,
    "Malt": 150,
    "Corona": 250,
    "Efes glütensiz": 250,
    "Amsterdam" : 300,
    "Miller" : 200,
    "Bud" : 200,
    "Becks" : 200,
    "Bomonti Filitresiz" : 200,
    "Belfast" : 200,
    "Özel Seri" : 200,
    "meyveli koktely" : 200,
    "kokteyl" : 400,
    "Viski" : 500,
    "su" : 100,
    "soda" : 100,
    "çerez" : 0,
}

# 12 masa oluştur
masalar = [Masa(i) for i in range(1, 13)]

# Tkinter menüsü oluştur
class BarTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='#2C3E50')  # Arka plan koyu lacivert tema

        # Başlık
        header = tk.Label(root, text="Ehl-i Nispet Bot", bg='#2C3E50', fg='#F1C40F', font=("Georgia", 24, "bold"))
        header.pack(pady=10)

        self.secilen_masa = None
        self.secili_urunler = {}  # Seçilen ürünleri takip et

        self.masa_buttons = []
        self.urun_buttons = {}

        # Ana frame
        main_frame = tk.Frame(root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Masa butonlarını oluştur
        self.create_masa_buttons(main_frame)

        # Ürün butonlarını oluştur
        self.create_urun_buttons(main_frame)

        # Masadaki ürünleri ve toplam tutarı gösterecek kutucuk
        self.info_frame = tk.Frame(root, bg='#2C3E50')
        self.info_frame.pack(pady=20, fill=tk.X)
        self.info_frame.config(width=root.winfo_screenwidth() // 4)  # Kutucuğun genişliğini ayarla

        # Ürün listboxları
        self.urunler_listbox_name = tk.Listbox(self.info_frame, selectmode=tk.MULTIPLE, font=("Helvetica", 12), bg='#34495E', fg='#ECF0F1', width=30)
        self.urunler_listbox_name.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.urunler_listbox_price = tk.Listbox(self.info_frame, selectmode=tk.MULTIPLE, font=("Helvetica", 12), bg='#34495E', fg='#ECF0F1', width=10)
        self.urunler_listbox_price.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Toplamları gösterecek label'lar
        self.masa_toplami_label = tk.Label(self.info_frame, text="Masa Toplamı: 0 TL", font=("Helvetica", 14), bg='#2C3E50', fg='#F1C40F')
        self.masa_toplami_label.pack(pady=5)

        self.secilenler_toplami_label = tk.Label(self.info_frame, text="Seçilenler Toplamı: 0 TL", font=("Helvetica", 14), bg='#2C3E50', fg='#F1C40F')
        self.secilenler_toplami_label.pack(pady=5)

        self.secili_ode_button = tk.Button(self.info_frame, text="Seçilenleri Öde", command=self.secili_ode, bg='#F1C40F', fg='#2C3E50', font=("Helvetica", 14))
        self.secili_ode_button.pack(pady=5)

        self.masayi_kapat_button = tk.Button(self.info_frame, text="Masayı Kapat", command=self.masayi_kapat, bg='#F1C40F', fg='#2C3E50', font=("Helvetica", 14))
        self.masayi_kapat_button.pack(pady=5)

        # Masa durumlarını güncelle
        self.guncelle_masa_durumlari()

    def create_masa_buttons(self, parent_frame):
        # Masaları yatay ve dikdörtgen şeklinde düzenleyelim (4 sütun ve 3 satır)
        masa_frame = tk.Frame(parent_frame)
        masa_frame.grid(row=0, column=0, padx=20, pady=20)  # Sol tarafa hizala

        for i, masa in enumerate(masalar):
            button = tk.Button(masa_frame, text=f"Masa {masa.masa_no}\n", width=20, height=5, bg='#34495E', fg='#F1C40F', font=("Helvetica", 12), relief="groove", command=lambda m=masa: self.masa_secin(m))
            button.grid(row=i//4, column=(i % 4), padx=5, pady=5, sticky="w")
            self.masa_buttons.append(button)

        

    def create_urun_buttons(self, parent_frame):
        urun_frame = tk.Frame(parent_frame)
        urun_frame.grid(row=0, column=1, padx=20, pady=20)  # Masa matriksinin sağına hizala

        for i, (urun, fiyat) in enumerate(urun_fiyatlari.items()):
            button = tk.Button(urun_frame, text=f"{urun}\n{fiyat} TL", width=20, height=3, bg='#34495E', fg='#F1C40F', font=("Helvetica", 12), relief="groove", command=lambda u=urun, f=fiyat: self.urun_ekle(u, f))
            button.grid(row=i//4, column=(i % 4), padx=5, pady=5)



    def guncelle_masa_durumlari(self):
        # Her masanın dolu ya da boş olmasına göre rengini güncelle
        for i, masa in enumerate(masalar):
            if masa == self.secilen_masa:
                self.masa_buttons[i].config(bg="blue")  # Seçilen masa mavi
            elif masa.dolu:
                self.masa_buttons[i].config(bg="green")  # Dolu masa yeşil
            else:
                self.masa_buttons[i].config(bg="grey")   # Boş masa gri

    def masa_secin(self, masa):
        self.secilen_masa = masa
        self.guncelle_masa_durumlari()
        self.urunleri_goster()

    def urunleri_goster(self):
        if self.secilen_masa:
            self.urunler_listbox_name.delete(0, tk.END)
            self.urunler_listbox_price.delete(0, tk.END)
            self.secili_urunler.clear()

            for urun, miktar in self.secilen_masa.urunler.items():
                for _ in range(miktar):
                    self.urunler_listbox_name.insert(tk.END, urun)  # Ürün ismi
                    self.urunler_listbox_price.insert(tk.END, urun_fiyatlari[urun])  # Ürün fiyatı

            # Masa toplamını güncelle
            toplam_tutar = sum([urun_fiyatlari[urun] * miktar for urun, miktar in self.secilen_masa.urunler.items()])
            self.masa_toplami_label.config(text=f"Masa Toplamı: {toplam_tutar} TL")

    def urun_ekle(self, urun, fiyat):
        if self.secilen_masa:
            self.secilen_masa.masaya_urun_ekle(urun, fiyat)
            self.urunleri_goster()

    def secili_ode(self):
        if self.secilen_masa:
            # Ürün isimlerinin olduğu listboxtan seçilenleri alıyoruz
            secili_urunler = [self.urunler_listbox_name.get(i) for i in self.urunler_listbox_name.curselection()]
            toplam_secilen_tutar = sum([urun_fiyatlari[urun] for urun in secili_urunler])
    
            # Seçilen ürünler için işlem yap
            for urun in secili_urunler:
                self.secilen_masa.masadan_urun_cikar(urun)
    
            # Seçilenler toplamını güncelle
            self.secilenler_toplami_label.config(text=f"Seçilenler Toplamı: {toplam_secilen_tutar} TL")
    
            # Masadaki ürünleri güncelle
            self.urunleri_goster()


    def masayi_kapat(self):
        if self.secilen_masa:
            self.secilen_masa.masanin_odemesini_al_ve_kapat()
            self.urunleri_goster()

# Uygulamayı çalıştır
root = tk.Tk()
app = BarTakipApp(root)
root.mainloop()
