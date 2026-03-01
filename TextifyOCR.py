import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pytesseract
from pdf2image import convert_from_path

# ==============================
# TESSERACT YOLU (Windows için)
# ==============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\user\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf")


class OCRApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Textify OCR")
        self.geometry("1000x650")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)

        self.image = None
        self.preview_image = None

        self.create_widgets()

    def create_widgets(self):
        # Başlık
        title = tk.Label(
            self,
            text="OCR - Image to Text",
            font=("Segoe UI", 20, "bold"),
            bg="#2b2b2b",
            fg="#f1f1f1"
        )
        title.pack(pady=10)

        # Drag & Drop Alanı
        self.drop_frame = tk.Label(
            self,
            text="Dosyayı buraya sürükleyip bırakın\n(JPG, PNG, JPEG, PDF)",
            width=60,
            height=5,
            bg="#3c3f41",
            relief="ridge",
            font=("Segoe UI", 12),
            fg="#f1f1f1"
        )
        self.drop_frame.pack(pady=10)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.drop_file)

        # Butonlar
        btn_frame = tk.Frame(self, bg="#2b2b2b")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Dosya Seç", width=15,
                  command=self.select_file, bg="#0984e3",
                  fg="white", activebackground="#0652dd", activeforeground="white").grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Metni Kopyala", width=15,
                  command=self.copy_text, bg="#00b894",
                  fg="white", activebackground="#009975", activeforeground="white").grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="TXT olarak Kaydet", width=15,
                  command=self.save_text, bg="#6c5ce7",
                  fg="white", activebackground="#5a4bcf", activeforeground="white").grid(row=0, column=2, padx=5)

        # İçerik Alanı
        content_frame = tk.Frame(self, bg="#2b2b2b")
        content_frame.pack(pady=10)

        # Görsel Önizleme
        self.preview_label = tk.Label(
            content_frame,
            text="Önizleme",
            width=45,
            height=20,
            bg="#1e1e1e",
            fg="#f1f1f1",
            relief="sunken"
        )
        self.preview_label.grid(row=0, column=0, padx=10)

        # OCR Sonuç Alanı
        self.text_area = ScrolledText(
            content_frame,
            width=60,
            height=20,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#f1f1f1",
            insertbackground="white",  # İmleç rengi
            selectbackground="#555555",
            selectforeground="#ffffff"
        )
        self.text_area.grid(row=0, column=1, padx=10)

    def drop_file(self, event):
        file_path = event.data.strip("{}")
        self.process_file(file_path)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Desteklenen Dosyalar", "*.jpg *.jpeg *.png *.pdf")
            ]
        )
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext not in SUPPORTED_FORMATS:
                raise ValueError("Desteklenmeyen dosya formatı!")

            if ext == ".pdf":
                images = convert_from_path(file_path)
                self.image = images[0]
            else:
                self.image = Image.open(file_path)

            self.show_preview()
            self.run_ocr()

        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def show_preview(self):
        img = self.image.copy()
        img.thumbnail((400, 400))
        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_label.configure(image=self.preview_image)

    def run_ocr(self):
        try:
            self.text_area.delete(1.0, tk.END)
            text = pytesseract.image_to_string(self.image, lang="tur+eng")
            self.text_area.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("OCR Hatası", str(e))

    def copy_text(self):
        text = self.text_area.get(1.0, tk.END)
        if not text.strip():
            messagebox.showwarning("Uyarı", "Kopyalanacak metin yok!")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Başarılı", "Metin panoya kopyalandı!")

    def save_text(self):
        text = self.text_area.get(1.0, tk.END)
        if not text.strip():
            messagebox.showwarning("Uyarı", "Kaydedilecek metin yok!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Başarılı", "Dosya kaydedildi!")


if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()