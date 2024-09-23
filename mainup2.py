import tkinter as tk
from tkinter import messagebox
import sqlite3
import tkinter.font as tkFont 
from tkinter import Tk, Button, Label, Frame, Listbox

class Masa:
    def __init__(self, masa_no):
        self.masa_no = masa_no
        self.urunler = {}
        self.dolu = False
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
            self.dolu = bool(self.urunler) 
            self.veritabanina_kaydet(urun, cikart=True)

    def masanin_odemesini_al_ve_kapat(self):
        toplam_tutar = sum([urun_fiyatlari[urun] * miktar for urun, miktar in self.urunler.items()])
        self.urunler.clear()
        self.dolu = False 
        self.veritabanini_temizle()
        messagebox.showinfo("Ödeme", f"Masa {self.masa_no} için toplam ödeme: {toplam_tutar} TL. Masa kapatıldı.")

    def veritabanina_kaydet(self, urun, cikart=False, odendi=False):
        conn = sqlite3.connect("bar_masa_takip.db")
        cursor = conn.cursor()

        if cikart:
            cursor.execute("DELETE FROM masa_urunler WHERE masa_no = ? AND urun = ? AND odendi = ?", (self.masa_no, urun, odendi))
        else:
            cursor.execute(
                "INSERT INTO masa_urunler (masa_no, urun, miktar, odendi) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(masa_no, urun, odendi) DO UPDATE SET miktar = ?",
                (self.masa_no, urun, self.urunler[urun], odendi, self.urunler[urun])
            )

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
        self.dolu = bool(self.urunler)
        conn.close()

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

masalar = [Masa(i) for i in range(1, 13)]

class BarTakipApp:
    def __init__(self, root):
        self.root = root
        self.urun_listesi = []
        self.root.configure(bg='#2C3E50') 


        header = tk.Label(root, text="Ehl-i Nispet Bot", bg='#2C3E50', fg='#F1C40F', font=("Georgia", 24, "bold"))
        header.pack(pady=10)

        self.secilen_masa = None
        self.secili_urunler = {} 

        self.masa_buttons = []
        self.urun_buttons = {}

       
        main_frame = tk.Frame(root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True)

     
        self.create_masa_buttons(main_frame)
        self.create_urun_buttons(main_frame)

        self.info_frame = tk.Frame(root, bg='#2C3E50')
        self.info_frame.pack(pady=20, fill=tk.X)
        self.info_frame.config(width=root.winfo_screenwidth() // 4)

        
        self.odenmeyen_urunler_listbox = tk.Listbox(self.info_frame, selectmode=tk.MULTIPLE, font=("Helvetica", 12), bg='#34495E', fg='#ECF0F1', width=30)
        self.odenmeyen_urunler_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.odenmis_urunler_listbox = tk.Listbox(self.info_frame, selectmode=tk.MULTIPLE, font=("Helvetica", 12), bg='#34495E', fg='#ECF0F1', width=30)
        self.odenmis_urunler_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        self.masa_toplami_label = tk.Label(self.info_frame, text="Masa Toplamı: 0 TL", font=("Helvetica", 14), bg='#2C3E50', fg='#F1C40F')
        self.masa_toplami_label.pack(pady=5)

        self.secilenler_toplami_label = tk.Label(self.info_frame, text="Seçilenler Toplamı: 0 TL", font=("Helvetica", 14), bg='#2C3E50', fg='#F1C40F')
        self.secilenler_toplami_label.pack(pady=5)

        self.secili_ode_button = tk.Button(self.info_frame, text="Seçilenleri Öde", command=self.secili_ode, bg='#F1C40F', fg='#2C3E50', font=("Helvetica", 14))
        self.secili_ode_button.pack(pady=5)

        self.masayi_kapat_button = tk.Button(self.info_frame, text="Masayı Kapat", command=self.masayi_kapat, bg='#F1C40F', fg='#2C3E50', font=("Helvetica", 14))
        self.masayi_kapat_button.pack(pady=5)

        self.guncelle_masa_durumlari()

    def create_masa_buttons(self, parent_frame):
        masa_frame = tk.Frame(parent_frame)
        masa_frame.grid(row=0, column=0, padx=15, pady=10)

        for i, masa in enumerate(masalar):
            button = tk.Button(masa_frame, text=f"Masa {masa.masa_no}\n", width=20, height=5, bg='#34495E', fg='#F1C40F', font=("Helvetica", 12), relief="groove", command=lambda m=masa: self.masa_secin(m))
            button.grid(row=i // 3, column=(i % 3), padx=5, pady=5, sticky="w")
            self.masa_buttons.append(button)

        

    def create_urun_buttons(self, parent_frame):
        urun_frame = tk.Frame(parent_frame)
        urun_frame.grid(row=0, column=1, padx=10, pady=10)

        for i, (urun, fiyat) in enumerate(urun_fiyatlari.items()):
            button = tk.Button(urun_frame, text=f"{urun}\n{fiyat} TL", width=20, height=3, bg='#34495E', fg='#F1C40F', font=("Helvetica", 12), relief="groove", command=lambda u=urun, f=fiyat: self.urun_ekle(u, f))
            button.grid(row=i//4, column=(i % 4), padx=5, pady=5)



    def guncelle_masa_durumlari(self):
        for i, masa in enumerate(masalar):
            if masa == self.secilen_masa:
                self.masa_buttons[i].config(bg="blue")
            elif masa.dolu:
                self.masa_buttons[i].config(bg="green")
            else:
                self.masa_buttons[i].config(bg="grey")

    def masa_secin(self, masa):
        self.secilen_masa = masa
        self.guncelle_masa_durumlari()
        self.urunleri_goster()

    def urunleri_goster(self):
        self.urun_listesi = []  # Ürün listesini başlat veya sıfırla
        
        # Ürünleri veritabanından çek
        cursor = self.conn.cursor()
        cursor.execute("SELECT urun, odendi FROM masa_urunler WHERE masa_no = ?", (self.secilen_masa.masa_no,))
        urunler = cursor.fetchall()
        
        # Tablodan çekilen ürünleri urun_listesi'ne ekle
        self.urun_listesi = [{'urun': urun[0], 'odendi': urun[1]} for urun in urunler]
        
        for urun in self.urun_listesi:
            if not urun['odendi']:
                print(f"Ödenmemiş ürün: {urun['urun']}")


    def guncelle_secili_toplam(self, event):
        secili_urunler = [self.urunler_listbox_name.get(i) for i in self.urunler_listbox_name.curselection()]
        toplam_secilen_tutar = sum([urun_fiyatlari[urun] for urun in secili_urunler])
        self.secilenler_toplami_label.config(text=f"Seçilenler Toplamı: {toplam_secilen_tutar} TL")

    def urun_ekle(self, urun, fiyat):
        if self.secilen_masa:
            self.secilen_masa.masaya_urun_ekle(urun, fiyat)
            self.urunleri_goster()

    def secili_ode(self):
        if self.secilen_masa:
            secili_urunler = [self.odenmeyen_urunler_listbox.get(i) for i in self.odenmeyen_urunler_listbox.curselection()]
            toplam_secilen_tutar = sum([urun_fiyatlari[urun] for urun in secili_urunler])

            for urun in secili_urunler:
                self.secilen_masa.masadan_urun_cikar(urun)
                self.secilen_masa.veritabanina_kaydet(urun, odendi=True)

            self.secilenler_toplami_label.config(text=f"Seçilenler Toplamı: {toplam_secilen_tutar} TL")
            self.urunleri_goster()

    def masayi_kapat(self):
        if self.secilen_masa:
            self.secilen_masa.masanin_odemesini_al_ve_kapat()
            self.urunleri_goster()

root = tk.Tk()
app = BarTakipApp(root)
root.mainloop()
