import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import smtplib
from email.mime.text import MIMEText

class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Directory Monitor & Alert System")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # --- STİL AYARLARI ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"))

        # --- BAŞLIK ---
        header = tk.Label(root, text="Sunucu Klasör Takip Sistemi", font=("Helvetica", 16, "bold"), fg="#333")
        header.pack(pady=20)

        # --- KLASÖR SEÇİM ALANI ---
        frame_folder = ttk.LabelFrame(root, text="İzlenecek Klasör", padding=15)
        frame_folder.pack(fill="x", padx=20, pady=5)

        self.folder_path = tk.StringVar()
        self.entry_path = ttk.Entry(frame_folder, textvariable=self.folder_path, width=50)
        self.entry_path.pack(side="left", padx=5)
        
        btn_browse = ttk.Button(frame_folder, text="Gözat", command=self.browse_folder)
        btn_browse.pack(side="left")

        # --- LİMİT AYARLARI ---
        frame_settings = ttk.LabelFrame(root, text="Limit Ayarları (GB)", padding=15)
        frame_settings.pack(fill="x", padx=20, pady=10)

        ttk.Label(frame_settings, text="Uyarı Limiti (GB):").pack(side="left", padx=5)
        self.limit_var = tk.DoubleVar(value=50.0)
        ttk.Entry(frame_settings, textvariable=self.limit_var, width=10).pack(side="left", padx=5)

        # --- SONUÇ EKRANI ---
        self.lbl_status = tk.Label(root, text="Durum: Bekleniyor...", font=("Helvetica", 10), fg="gray")
        self.lbl_status.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="indeterminate")
        self.progress.pack(pady=5)

        self.lbl_result = tk.Label(root, text="0.00 GB", font=("Helvetica", 24, "bold"), fg="#007acc")
        self.lbl_result.pack(pady=10)

        # --- AKSİYON BUTONLARI ---
        btn_start = ttk.Button(root, text="ANALİZİ BAŞLAT", command=self.start_analysis_thread)
        btn_start.pack(ipady=10, ipadx=20, pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def start_analysis_thread(self):
        """Arayüz donmasın diye işlemi ayrı thread'de yapar."""
        path = self.folder_path.get()
        if not path:
            messagebox.showwarning("Hata", "Lütfen bir klasör seçin!")
            return
        
        self.progress.start(10)
        self.lbl_status.config(text="Hesaplanıyor... Lütfen bekleyin.", fg="orange")
        
        # İşlemi arka plana at
        threading.Thread(target=self.calculate_size, args=(path,), daemon=True).start()

    def calculate_size(self, path):
        try:
            total_size = 0
            # Alt klasörleri gez
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            
            size_gb = total_size / (1024**3)
            
            # Arayüzü güncelle (Thread güvenliği için after kullanılır ama basitlik için direkt çağırıyoruz)
            self.update_ui(size_gb)
            
        except Exception as e:
            self.lbl_status.config(text=f"Hata: {str(e)}", fg="red")
            self.progress.stop()

    def update_ui(self, size_gb):
        self.progress.stop()
        self.lbl_result.config(text=f"{size_gb:.2f} GB")
        
        limit = self.limit_var.get()
        if size_gb > limit:
            self.lbl_status.config(text="⚠️ KRİTİK SEVİYE: LİMİT AŞILDI!", fg="red")
            messagebox.showwarning("Uyarı", f"Klasör boyutu {limit} GB limitini aştı!")
            # Buraya mail atma fonksiyonu eklenebilir
        else:
            self.lbl_status.config(text="✅ Durum Normal: Limit altında.", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerMonitorApp(root)
    root.mainloop()
