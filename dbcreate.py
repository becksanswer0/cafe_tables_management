import sqlite3

def veritabani_yarat():
    conn = sqlite3.connect("bar_masa_takip.db")
    cursor = conn.cursor()

    # masa_urunler tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masa_urunler (
            masa_no INTEGER,
            urun TEXT,
            miktar INTEGER,
            PRIMARY KEY (masa_no, urun)
        )
    ''')

    conn.commit()
    conn.close()

# Veritabanını oluştur
veritabani_yarat()
