from tkinter import Tk, Button, Label, Frame, Listbox
import tkinter.font as tkFont

root = Tk()
root.title("Ehl-i Nispet Bot")

# Arka plan rengi ve başlık
root.configure(bg='#2C3E50')  # Koyu lacivert tema
header = Label(root, text="Ehl-i Nispet Bot", bg='#2C3E50', fg='#F1C40F', font=("Georgia", 24, "bold"))
header.pack(pady=10)

# Özel fontlar
font_bigger = tkFont.Font(family="Helvetica", size=12)
luxury_font = tkFont.Font(family="Georgia", size=16, weight="bold")

# Masa butonları ve ürün matriksini ayarlamak için bir frame
main_frame = Frame(root, bg='#2C3E50')
main_frame.pack(fill='both', expand=True)

# Masa butonları (örnek tasarım)
masa_button = Button(main_frame, text="Masa 1", width=20, height=5, bg='#34495E', fg='#F1C40F', font=font_bigger, relief="groove")
masa_button.grid(row=0, column=0, padx=10, pady=10)

urun_button = Button(main_frame, text="Efes\n150 TL", width=20, height=5, bg='#34495E', fg='#F1C40F', font=font_bigger, relief="groove")
urun_button.grid(row=0, column=1, padx=10, pady=10)

# Listbox tasarımı (ürün adı ve fiyat)
info_frame = Frame(root, bg='#2C3E50')
info_frame.pack(fill='both', expand=True)

listbox_name = Listbox(info_frame, bg='#34495E', fg='#ECF0F1', font=font_bigger, width=20, height=10)
listbox_name.pack(side="left", padx=10, pady=10)

listbox_price = Listbox(info_frame, bg='#34495E', fg='#ECF0F1', font=font_bigger, width=10, height=10)
listbox_price.pack(side="left", padx=10, pady=10)

# Uygulama döngüsü
root.mainloop()
