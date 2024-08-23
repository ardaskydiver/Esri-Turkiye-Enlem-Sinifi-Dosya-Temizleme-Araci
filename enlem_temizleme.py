import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.ttk import Progressbar

# Fonksiyonlar
def delete_folder_contents(folder_path):
    """Belirtilen klasördeki tüm içeriği silen fonksiyon."""
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    log(f"Silindi: {file_path}")
                except Exception as e:
                    log(f"Silinemedi: {file_path} - Hata: {str(e)}")
                progress.step(1)
                root.update_idletasks()
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                    log(f"Silindi: {dir_path}")
                except Exception as e:
                    log(f"Silinemedi: {dir_path} - Hata: {str(e)}")
                progress.step(1)
                root.update_idletasks()

def connect_to_computer(computer, user, username, password):
    """Belirtilen bilgisayara ve kullanıcıya ağ sürücüsü ekleyen fonksiyon."""
    net_use_command = f'net use \\\\{computer}\\Users\\{user} /user:{username} {password}'
    result = subprocess.run(net_use_command, shell=True, check=False)
    if result.returncode == 0:
        log(f"Bağlandı: \\\\{computer}\\Users\\{user}")
    else:
        log(f"Bağlantı hatası: \\\\{computer}\\Users\\{user} - Hata kodu: {result.returncode}")

def disconnect_from_computer(computer, user):
    """Belirtilen bilgisayardan ve kullanıcıdan ağ sürücüsünü kaldıran fonksiyon."""
    net_delete_command = f'net use \\\\{computer}\\Users\\{user} /delete'
    result = subprocess.run(net_delete_command, shell=True, check=False)
    if result.returncode == 0:
        log(f"Bağlantı kesildi: \\\\{computer}\\Users\\{user}")
    else:
        log(f"Bağlantı kesme hatası: \\\\{computer}\\Users\\{user} - Hata kodu: {result.returncode}")

def log(message):
    """İşlemleri ve hata kodlarını metin alanına yazdıran fonksiyon."""
    log_text.insert(tk.END, message + "\n")
    log_text.yview(tk.END)
    root.update_idletasks()

def start_deletion():
    # Kullanıcı adı ve şifreyi al
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Eksik Bilgi Girdiniz!", "Lütfen LDAP kullanıcı adınızı ve şifrenizi giriniz.")
        return

    # Seçili bilgisayarları al
    selected_computers = {computer: users for computer, users in computers.items() if vars()[f'var_{computer}'].get()}

    if not selected_computers:
        messagebox.showwarning("Eksik Seçim Yaptınız!", "Lütfen en az bir bilgisayar adı seçiniz.")
        return

    # Progress bar'ı sıfırla
    total_operations = sum([len(users) * (len(folders) + 1) for users in selected_computers.values()])
    progress['maximum'] = total_operations
    progress['value'] = 0

    # Mevcut tüm ağ bağlantılarını sonlandırma komutu
    log("Mevcut ağ bağlantıları sonlandırılıyor...")
    net_use_delete_all_command = 'net use * /delete /y'
    subprocess.run(net_use_delete_all_command, shell=True, check=True)
    log("Mevcut ağ bağlantıları sonlandırıldı.")

    # Her bilgisayar için işlemi gerçekleştirme
    for computer, users in selected_computers.items():
        for user in users:
            for folder in folders:
                # Ağ sürücüsüne bağlanma
                connect_to_computer(computer, user, username, password)

                # Belirtilen klasördeki içerikleri silme
                full_path = f'\\\\{computer}\\Users\\{user}\\{folder}'
                delete_folder_contents(full_path)

                # Ağ sürücüsünü bağlantıdan çıkarma
                disconnect_from_computer(computer, user)

            # EsriTraining klasöründeki içeriği silme
            esri_training_folder = f'\\\\{computer}\\C\\EsriTraining'
            delete_folder_contents(esri_training_folder)
            progress.step(1)
            root.update_idletasks()

    messagebox.showinfo("İşlem Tamamlandı", "Dosya silme işlemi başarıyla tamamlandı.")
    log("İşlem tamamlandı.")

# Bilgisayar adları ve ilgili kullanıcı klasörleri listesi
computers = {
    'Egitim9': ['Egitim2'],
    'Egitim10': ['Egitim9'],
    'Egitim11': ['EGITIM-1'],
    'Egitim12': ['Egitim7'],
    'Egitim13': ['Egitim6'],
    'Egitim14': ['Egitim3'],
    'Egitim15': ['Egitim14'],
    'Egitim16': ['Egitim12'],
    'Egitim17': ['Egitim17'],
    'Egitim18': ['Egitim20'],
    'Egitim19': ['Egitim16'],
    'Egitim20': ['Egitim8']
}

# Silinecek klasörlerin listesi
folders = [
    'Downloads',
    'Desktop',
    'Documents',
    'AppData\\Local\\ESRI',
    'AppData\\Roaming\\Esri',
    'AppData\\Local\\Google\\Chrome\\User Data\\Profile 1',
    'AppData\\Local\\Microsoft\\Edge\\User Data\\Default',
]

# GUI oluşturma
root = tk.Tk()
root.title("Enlem Sınıfı Bilgisayar Temizleme Aracı")

frame_user = tk.Frame(root)
frame_user.pack(pady=10)

label_username = tk.Label(frame_user, text="Kullanıcı Adı:")
label_username.grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame_user)
entry_username.grid(row=0, column=1, padx=5, pady=5)

label_password = tk.Label(frame_user, text="Şifre:")
label_password.grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame_user, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

frame_computers = tk.Frame(root)
frame_computers.pack(pady=10)

label_computers = tk.Label(frame_computers, text="Bilgisayarlar:")
label_computers.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Bilgisayar kutucuklarını iki satır halinde yerleştir
num_computers = len(computers)
num_columns = (num_computers + 1) // 2

for i, (computer, users) in enumerate(computers.items()):
    vars()[f'var_{computer}'] = tk.BooleanVar(value=True)
    chk = tk.Checkbutton(frame_computers, text=computer, variable=vars()[f'var_{computer}'])
    row = i // num_columns + 1  # Satır numarasını hesapla
    col = i % num_columns       # Sütun numarasını hesapla
    chk.grid(row=row, column=col, sticky="w", padx=5, pady=2)

btn_start = tk.Button(root, text="Silme İşlemini Başlat", command=start_deletion)
btn_start.pack(pady=10)

# Progress bar ekleme
progress = Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress.pack(pady=10)

# Log metin alanı
log_text = scrolledtext.ScrolledText(root, width=60, height=15, state=tk.NORMAL, bg="black", fg="white", font=("Courier", 10))
log_text.pack(pady=10)

root.mainloop()
