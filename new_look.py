import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from tkinter import PhotoImage, filedialog, messagebox
import os
import sys
import json
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
import laczenie_klipow as lk
import tworzenie_napisow as tn
from cryptography.fernet import Fernet

def list_available_drives():
    import string
    """Zwraca listę wszystkich dostępnych dysków."""
    drives = []
    for drive in string.ascii_uppercase:
        if os.path.exists(f'{drive}:/'):
            drives.append(f'{drive}:/')
    return drives

def find_file_in_movaiassets_folder(starting_directory, filename):
    """Przeszukuje katalogi w poszukiwaniu folderu 'movaiassets' i sprawdza, czy zawiera dany plik."""
    for root, dirs, files in os.walk(starting_directory):
        if 'movaiassets' in dirs:  # Jeśli znalazło folder 'movaiassets'
            movaiassets_folder = os.path.join(root, 'movaiassets')
            # Sprawdzamy, czy plik istnieje w folderze 'movaiassets'
            file_path = os.path.join(movaiassets_folder, filename)
            if os.path.exists(file_path):
                return file_path
    return None

def find_file_on_any_drive(filename):
    """Przeszukuje wszystkie dostępne dyski w poszukiwaniu folderu 'movaiassets' z konkretnym plikiem."""
    drives = list_available_drives()
    for drive in drives:
        print(f"Szukanie na dysku: {drive}")
        file_path = find_file_in_movaiassets_folder(drive, filename)
        if file_path:
            return file_path
    return None

def create_text_image(text, font_path=r"movaiassets1\\OnestBlack1602-hint.ttf", font_size=48, outline_thickness=0):
    print(f"Tworzenie obrazu z tekstem: {text}")
    import io
    
    text_color = (255, 255, 255)
    outline_color = (0, 0, 0)
    
    # Załadowanie czcionki
    font = ImageFont.truetype(font_path, font_size)
    
    # Tworzenie obrazka tylko na podstawie wymiarów tekstu
    image_temp = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    draw_temp = ImageDraw.Draw(image_temp)
    bbox = draw_temp.textbbox((0, 0), text, font=font)
    
    # Obliczenie szerokości i wysokości tekstu
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Tworzenie ostatecznego obrazu z uwzględnieniem obramowania
    image = Image.new("RGBA", (text_width + outline_thickness * 2, text_height + outline_thickness * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    if outline_thickness > 0:
        # Rysowanie obwódki tekstu, bez zbędnych iteracji punkt po punkcie
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx != 0 or dy != 0:
                    draw.text((dx + outline_thickness - bbox[0], dy + outline_thickness - bbox[1]), text, font=font, fill=outline_color)

    # Rysowanie samego tekstu
    draw.text((outline_thickness - bbox[0], outline_thickness - bbox[1]), text, font=font, fill=text_color)
    
    # Konwersja obrazu na dane bajtowe
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    
    # Konwersja na format obsługiwany przez Tkinter
    tk_image = PhotoImage(data=image_bytes.read())
    
    return tk_image

class FloatSpinbox(ctk.CTkFrame):
    from typing import Union, Callable
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        button_color = "#15a9f9"
        frame_color = "#121212"
        text_color="white"
        all_frames_border_color = "#f94b2c"
        info_border_color = "#0ec0a2"
        update_color = "#f6a02c"
        ad_border_color = "#483182"

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("#121212", "#121212"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = ctk.CTkButton(self, text="―", text_color=text_color, width=height-6, height=height-6, fg_color=frame_color, border_color=all_frames_border_color, border_width=1,
                                             command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = ctk.CTkEntry(self, width=width-(2*height), text_color=text_color, height=height-6, border_width=0, fg_color=frame_color)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = ctk.CTkButton(self, text="+", text_color=text_color, width=height-6, height=height-6, fg_color=frame_color, border_color=ad_border_color, border_width=1,
                                        command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0.0")

        self.bind_button_hover_buttons(self.subtract_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.add_button, ad_border_color)

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            current_value = float(self.entry.get())
            new_value = current_value + float(self.step_size)
            self.entry.delete(0, "end")
            self.entry.insert(0, str(new_value))
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            current_value = float(self.entry.get())
            new_value = current_value - float(self.step_size)
            self.entry.delete(0, "end")
            self.entry.insert(0, str(new_value))
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))

    def bind_button_hover_buttons(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty
      clicked = {"is_clicked": False}

      button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))  # Zmien kolor na określony i dodaj białą obwódkę
      button.bind("<Leave>", lambda e: button.configure(fg_color="#121212"))  # Przywróć kolor i usuń obwódkę
      button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color))  # Kolor i obwódka po kliknięciu
      button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color="#121212"))  # Przywróć kolor i usuń obwódkę po puszczeniu

# Funkcja do zmiany koloru po kliknięciu przycisku
def change_button_color(button):
    button.configure(fg_color="#0ec0a2")  # Zmienia kolor przycisku na zielony po kliknięciu

# Klasa do przechwytywania standardowego wyjścia (stdout i stderr)
class RedirectOutput:
    def __init__(self, textbox):
        from queue import Queue
        self.textbox = textbox
        self.auto_scroll = True  # Flaga kontrolująca automatyczne przewijanie
        self.queue = Queue()
        self.textbox.bind("<MouseWheel>", self.on_scroll)  # Wiążemy scroll z myszką
        self.start_auto_scroll()  # Uruchamiamy automatyczne przewijanie
        self.start_thread()  # Uruchamiamy wątek do przetwarzania kolejki

    def write(self, message):
        # Dodajemy komunikat do kolejki zamiast bezpośrednio do textboxa
        self.queue.put(message)

    def flush(self):
        pass  # Potrzebne do kompatybilności z sys.stdout

    def on_scroll(self, event):
        # Sprawdza, czy użytkownik przewinął w górę; jeśli tak, zatrzymujemy auto-scroll
        if self.textbox.yview()[1] < 1.0:  # Jeśli nie jesteśmy na samym dole
            self.auto_scroll = False
        else:
            self.auto_scroll = True  # Jeśli jesteśmy na dole, auto-scroll działa
    
    def start_auto_scroll(self):
        # Uruchamiamy cykliczne sprawdzanie pozycji scrolla
        if self.auto_scroll:
            self.textbox.see(ctk.END)
        self.textbox.after(100, self.start_auto_scroll)  # Powtarzamy co 100 ms

    def process_queue(self):
        """Przenosi wiadomości z kolejki do textboxa."""
        while True:
            try:
                # Pobieramy wiadomość z kolejki, jeśli jest dostępna
                message = self.queue.get()
                self.textbox.insert(ctk.END, message)
                if self.auto_scroll:
                    self.textbox.see(ctk.END)
            except Exception as e:
                print(f"Błąd podczas przetwarzania kolejki: {e}")
            self.queue.task_done()  # Oznacza zakończenie przetwarzania wiadomości w kolejce

    def start_thread(self):
        """Uruchamia wątek do przetwarzania kolejki."""
        thread = threading.Thread(target=self.process_queue, daemon=True)
        thread.start()


fg_color = "#000000"
button_color = "#15a9f9"
frame_color = "#121212"
text_color="white"
all_frames_border_color = "#f94b2c"
info_border_color = "#483182"
update_color = "#f6a02c"
ad_border_color = "#04d590"
other_frames_border = "white"
text_color = "white"
terminal_files = "#2b2b2b"
other_frames_border_size = 1.5
white_icons = "movaiassets1\\"

#fg_color = "#ffffff"          # Jaśniejsza wersja czarnego
#button_color = "#007bff"      # Jaśniejsza wersja niebieskiego
#frame_color = "#f0f0f0"        # Jaśniejsza wersja ciemnego szarości
#text_color = "#000000"         # Już jest biały
#all_frames_border_color = "#fe4b61"  # Jaśniejsza wersja czerwonego
#info_border_color = "#0ec0a2"  # Jaśniejsza wersja zielonego
#update_color = "#f6a02c"       # Jaśniejsza wersja pomarańczowego
#ad_border_color = "#04d590"    # Jaśniejsza wersja zielonego
#other_frames_border = "black"
#text_color = "black"
#other_frames_border_size = 1.5
#white_icons = "black_icons\\"

border_size = 0

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login") 
        self.geometry("700x550")

        self.iconbitmap(r'movaiassets1\\movAI-Logo.ico')
        
        self.configure(fg_color=fg_color)
        self.credentials_file = self.get_appdata_path("credentials.json")
        auto_login_enabled = os.path.exists(self.credentials_file)
        self.remember_var = ctk.BooleanVar(value=auto_login_enabled)
        self.encryption_key = self.get_encryption_key()

        self.overrideredirect(True)

        # Tworzenie własnego paska tytułowego
        self.title_bar = ctk.CTkFrame(self, fg_color=fg_color)
        self.title_bar.pack(side="top", fill="x", pady=1, padx=10)
        #self.login_frame.place_forget()

        # Ścieżka do obrazka
        image_path = r"movaiassets1\\movAI Logo.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        logo_image = ctk.CTkImage(resized_image, size=(28, 28))

        self.logo_label = ctk.CTkLabel(master = self, image = logo_image, text = "", fg_color=fg_color)
        self.logo_label.place(relx=0.023, rely=0.014, anchor="n")  # Odstępy

        movai_label_image = create_text_image("movAI", font_size=12, outline_thickness=0)
        self.movai_label = ctk.CTkLabel(master = self, image = movai_label_image, text = "", fg_color=fg_color)
        self.movai_label.place(relx=0.073, rely=0.014, anchor="n")  # Odstępy

        # Przycisk zamknięcia
        self.close_button = ctk.CTkButton(
            self.title_bar, text="✕", command=self.destroy, 
            fg_color=fg_color, text_color=text_color, 
            width=30, height=20  # Ustawienia na kwadratowy kształt
        )
        self.close_button.pack(side="right", padx=5, pady=5)  # Odstępy

        # Przycisk maksymalizacji
        self.minimize_button = ctk.CTkButton(
            self.title_bar, text="―", command=self.zminimalizuj_okno, 
            fg_color=fg_color, text_color=text_color, 
            width=30, height=20  # Ustawienia na kwadratowy kształt
        )
        self.minimize_button.pack(side="right", padx=5, pady=5)  # Odstępy

        self.image_frame = ctk.CTkFrame(self, width=400, height=480, fg_color=fg_color, border_color=info_border_color, border_width=border_size)
        self.image_frame.place(relx=0.3, rely=0.52, anchor="center")
        #self.profile_frame.place_forget()

        # Ścieżka do obrazka
        image_path = r"movaiassets1\\movAI.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        logo_image = ctk.CTkImage(resized_image, size=(390, 473))

        self.logo_label = ctk.CTkLabel(master = self.image_frame, image = logo_image, text = "", fg_color=fg_color)
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")  # Odstępy

        self.image_frame = ctk.CTkFrame(self, width=390, height=2, fg_color=fg_color, border_color=info_border_color, border_width=border_size)
        self.image_frame.place(relx=0.3, rely=0.95, anchor="center")

        self.login_frame = ctk.CTkFrame(self, width=270, height=480, fg_color=fg_color, border_color=info_border_color, border_width=border_size)
        self.login_frame.place(relx=0.79, rely=0.52, anchor="center")

        # Pola logowania
        username_label_image = create_text_image("Username:", font_size=16, outline_thickness=0)
        self.username_label = ctk.CTkLabel(self.login_frame, text="", image = username_label_image)
        self.username_label.place(relx=0.5, rely=0.15, anchor="center")

        self.username_entry = ctk.CTkEntry(self.login_frame, corner_radius=30, width=190, fg_color=fg_color,
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size, text_color=text_color)
        self.username_entry.place(relx=0.5, rely=0.22, anchor="center")
        
        password_label_image = create_text_image("Password:", font_size=16, outline_thickness=0)
        self.password_label = ctk.CTkLabel(self.login_frame, text="", image = password_label_image)
        self.password_label.place(relx=0.5, rely=0.38, anchor="center")

        self.password_entry = ctk.CTkEntry(self.login_frame, corner_radius=30, width=190, fg_color=fg_color,
                                         height=40, show="*", border_color=all_frames_border_color, border_width=other_frames_border_size, text_color=text_color)
        self.password_entry.place(relx=0.5, rely=0.45, anchor="center")
        
        # Przycisk logowania
        login_button_image = create_text_image("Login", font_size=16, outline_thickness=0)
        self.login_button = ctk.CTkButton(self.login_frame, text="", image = login_button_image,fg_color=fg_color, corner_radius=30, width=190, 
                                         height=40, border_color=info_border_color, border_width=other_frames_border_size, command=self.login)
        self.login_button.place(relx=0.5, rely=0.7, anchor="center")

        self.auto_login_checkbox = ctk.CTkCheckBox(master=self.login_frame, text="Remember me", text_color=text_color, variable=self.remember_var, 
                                               onvalue="on", offvalue="off", 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.auto_login_checkbox.place(relx=0.5, rely=0.8, anchor="center")

        if self.remember_var.get():
           self.auto_login()

        # Przeciąganie okna
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_drag)

        # Przechwycenie zdarzenia przywrócenia okna
        self.bind("<Map>", self.przywroc_okno)

        self.bind_button_hover(self.close_button, all_frames_border_color)  # Kolor dla przycisku zamknięcia
        self.bind_button_hover(self.minimize_button, fg_color)  # Kolor dla przycisku minimalizacji
        self.bind_button_hover(self.login_button, info_border_color)
        
    def get_appdata_path(self, filename):
        """Zwraca pełną ścieżkę do pliku w katalogu AppData."""
        appdata_dir = os.getenv('APPDATA')
        if not appdata_dir:
            raise Exception("Nie można znaleźć katalogu AppData.")
        
        app_folder = os.path.join(appdata_dir, "movAI")  # Zamień "MyApp" na nazwę Twojej aplikacji
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)  # Tworzy katalog, jeśli nie istnieje
        return os.path.join(app_folder, filename)

    def get_encryption_key(self):
        """Zwraca klucz szyfrowania, zapisując go w AppData, jeśli go brak."""
        key_file = self.get_appdata_path("key.key")
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
        else:
            with open(key_file, "rb") as f:
                key = f.read()
        return key

    def save_credentials(self, username, password):
        """Zapisuje dane logowania w zaszyfrowanym pliku."""
        cipher = Fernet(self.encryption_key)
        encrypted_data = {
            "username": cipher.encrypt(username.encode()).decode(),
            "password": cipher.encrypt(password.encode()).decode()
        }
        with open(self.credentials_file, "w") as f:
            json.dump(encrypted_data, f)

    def load_credentials(self):
        """Odczytuje dane logowania z zaszyfrowanego pliku."""
        if not os.path.exists(self.credentials_file):
            return None, None
        cipher = Fernet(self.encryption_key)
        with open(self.credentials_file, "r") as f:
            data = json.load(f)
            username = cipher.decrypt(data["username"].encode()).decode()
            password = cipher.decrypt(data["password"].encode()).decode()
        return username, password

    def auto_login(self):
        """Automatyczne logowanie przy włączonym checkboxie."""
        username, password = self.load_credentials()
        if username and password:
            self.username_entry.insert(0, username)
            self.password_entry.insert(0, password)
            self.login()

    def login(self):
        """Obsługa logowania."""
        import requests
        username = self.username_entry.get()
        password = self.password_entry.get()
        url = "https://movai.pl/login_app.php"
        data = {"username": username, "password": password}

        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    messagebox.showinfo("Login", result.get("message", "Zalogowano pomyślnie!"))
                    if self.remember_var.get():
                        self.save_credentials(username, password)
                    self.destroy()
                    main_app = App()
                    main_app.mainloop()
                else:
                    messagebox.showerror("Login Error", result.get("message", "Nieprawidłowy login lub hasło."))
            else:
                messagebox.showerror("Server Error", f"Błąd serwera: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Nie udało się połączyć z serwerem: {e}")

    def zminimalizuj_okno(self):
        self.overrideredirect(False)  # Wyłącz tymczasowo "overrideredirect", aby minimalizacja zadziałała
        self.iconify()  # Zminimalizuj okno
        print("Window minimized.")

    def przywroc_okno(self, event=None):
        if self.state() == "normal":  # Sprawdź, czy okno zostało przywrócone
            self.after(0, lambda: self.overrideredirect(True))  # Przywróć "overrideredirect" po minimalnym opóźnieniu

    def start_move(self, event):
        self.prev_x = event.x
        self.prev_y = event.y

    def on_drag(self, event):
        x = self.winfo_x() - self.prev_x + event.x
        y = self.winfo_y() - self.prev_y + event.y
        self.geometry(f"+{x}+{y}")

    def bind_button_hover(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty
      clicked = {"is_clicked": False}

      button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))  # Zmien kolor na określony i dodaj białą obwódkę
      button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color))  # Przywróć kolor i usuń obwódkę
      button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color))  # Kolor i obwódka po kliknięciu
      button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color=fg_color))  # Przywróć kolor i usuń obwódkę po puszczeniu

# Inicjalizacja głównego okna aplikacji
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MovAI") 
        self.geometry("1200x800")

        self.iconbitmap(r'movaiassets1\\movAI-Logo.ico')
        
        self.configure(fg_color=fg_color)

        self.credentials_file = self.get_appdata_path("credentials.json")

        self.hide_all_frames()

        # Uchwyt do naszego okna
        self.is_minimized = False  # Flaga, czy okno jest zminimalizowane
        self.audio_data_transferred = False
        self.suspend_visibility_check = False
        self.last_audio_file = None  # Przechowuje ostatnio przetworzony plik audio
        self.calculating_audio_length = False
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Inicjalizacja sprawdzania widoczności
        #self.check_visibility()
        
        self.folder_check_var = ctk.StringVar(value="off")
        self.file_check_var = ctk.StringVar(value="off")
        self.audio_folder_check_var = ctk.StringVar(value="off")
        self.png_file_check_var = ctk.StringVar(value="off")
        self.images_folder_check_var = ctk.StringVar(value="off")
        self.flash_check_var = ctk.StringVar(value="off")
        self.fade_check_var = ctk.StringVar(value="off")
        self.glitch_check_var = ctk.StringVar(value="off")
        self.is_random_var = ctk.BooleanVar(value=False)
        self.use_color_check_var = ctk.BooleanVar(value=False)  # Domyślnie False
        self.bloom_check_var = ctk.BooleanVar(value=False)
        self.use_shadow_check_var = ctk.BooleanVar(value=False)
        self.should_oscillate_check_var = ctk.BooleanVar(value=False)
        self.clip_duration_check_var = ctk.StringVar(value="off")
        self.use_font_path = ctk.BooleanVar(value=False)
        
        # Inicjalizacja zmiennych do przechowywania ustawień liczbowych
        self.clip_duration = ctk.DoubleVar(value=1.0) 
        self.font_scale = ctk.IntVar(value=20)
        self.number_of_words = ctk.IntVar(value=1)
        self.flash_duration = ctk.DoubleVar(value=0.3)
        self.fade_duration = ctk.DoubleVar(value=0.3)
        self.glitch_duration = ctk.DoubleVar(value=0.3)
        self.shadow_offset = ctk.DoubleVar(value=5.0)
        self.blur_radius = ctk.DoubleVar(value=6.0)
        self.shadow_radius = ctk.DoubleVar(value=3.0)
        
        self.selected_folder_path = ""
        self.selected_file_path = ""
        self.selected_audio_folder_path = ""
        self.selected_png_file_path = ""
        self.selected_images_folder_path = ""
        self.output_folder_path = ""
        self.font_path = ""

         # Zmienna do przechowywania stanu przejść
        self.use_flash_transition = False
        self.use_fade_transition = False
        self.use_glitch_transition = False
        self.bloom = False
        self.use_color = False
        self.should_oscillate = False
        self.use_shadow = False

        # Usunięcie systemowego paska tytułowego
        self.overrideredirect(True)

        # Wczytanie zapisanego języka lub ustawienie domyślnego
        self.config_file = self.get_config_file_path()

        # Słowniki z tekstami
        self.texts = {
            "en": {
                "click_here": ">> Click Here <<",
                "needed": "Needed:",
                "your_files:": "Your Files:",
                "manual_one_clip_duration": "Manual One Clip Duration",
                "required": "Required:",
                "optional": "Optional:",
                "choose_effects": "Choose Effects",
                "run_process": "Run Process",
                "run_phase_one": "Run Phase One",
                "run_phase_two": "Run Phase Two",
                "save_settings": "Save settings",
                "reset_to_default": "Reset to Default",
                "backgrounds": "Backgrounds",
                "update_news": "Update News",
                "load_save": "Load Save",
                "save_two": "Save Two",
                "save_one": "Save One",
                "save_three": "Save Three",
                "statistics": "Statistics",
                "choose_files": "Choose Files",
                "choose_font_file": "Choose Font File",
                "choose_audio_file": "Choose Audio File",
                "choose_output_folder": "Choose Output Folder",
                "choose_logo": "Choose Logo",
                "set_one_clip_duration": "Set One Clip Duration:",
                "coming_soon": "Coming soon...",
                "amount_of_files": "Amount Of Files",
                "information": "Information",
                "your_files": "Your Files",
                "font_size": "Font Size:",
                "words_in_one_sentence": "Words In One Sentence:",
                "glowing_text": "Glowing Text",
                "glow_intensity": "Glow Intensity:",
                "shadow_text": "Shadow Text",
                "shadow_intensity": "Shadow Intensity:",
                "shadow_offset": "Shadow Offset >>>",
                "special_words": "Special Words",
                "float_effect": "Float Effect",
                "random_merge": "Random Merge",
                "flash_transition": "Flash Transition",
                "flash_duration": "Flash Duration:",
                "fade_transition": "Fade Transition",
                "fade_duration": "Fade Duration:",
                "glitch_transition": "Glitch Transition",
                "glitch_duration": "Glitch Duration:",
                "subtitles_effects": "Subtitles Effects",
                "background_effects": "Background Effects",

                "update": """\
                
                --- APP UPDATE ---
           
    1. Added logout option

    2. Added autologin option

    3. Fixed some of the bugs
                   
            
            
             --- WEBSITE UPDATE ---
    
    1. Graphic update of 
       login window,
       register window and 
       my account window
    
    2. Fixed some bug with login \
                """,
                
                "run_instructions_text": """\
    1. 'Phase One' creates the entire 
        background for your video.
           
    2. 'Phase Two' adds the subtitles 
        and the audio file you've selected.

    3. The 'Save' button saves your file 
       paths and chosen effects, so when 
       you reopen the app later, your saved 
       settings will automatically load.
                   
    4. The 'Reset' button clears all saved 
       settings and file paths.\
                """,

                "greeting_text": """\
    Hi! I'm building this app by myself, 
    and my goal is to make you as happy 
    as possible with it. I'll do my best 
    to provide weekly updates with new 
    features and effects.
                
    The video creation speed depends 
    entirely on your CPU and GPU.
                
    If you have any problems with the app, 
    feel free to contact me via the support 
    email or create a ticket on our 
    Discord server.
                
    Have fun making videos! I hope you 
    can earn some money or get tons 
    of views with them—hehe!
                
    Kamil ;D\
                """,

                "preparation_instructions_text": """\
  1. Download the MP3 file from 
     the video you'd like to remake.
           
  2. Download the files you'd
     like to use as the background.
         
  3. Download the font (in TTF format)
     that you'd like to use for the
     subtitles.

  4. Choose the paths and effects
     you want to apply to your video.
           
  5. When selecting 'Files', a spinbox
     will appear where you can decide
     how long each clip should be.
                   
  6. In 'Amount of Files', you'll see the
     number of files you've selected and
     how many are needed to match the
     length of your audio for the video.\
                """,

                "effect_instructions_text": """\
    1. Choose the effect you'd like to use in your video.
           
    2. If you click 'Random Merge' background files 
       will be randomly selected from the folder. If you 
       don’t use this option, it will automatically select 
       the first files from the folder you've chosen.\
                """
            },
            "pl": {
                "needed": "Potrzebne:",
                "your_files:": "Twoje Pliki:",
                "manual_one_clip_duration": "Czas trwania jednego klipu ręcznie",
                "required": "Wymagane:",
                "optional": "Opcojonalne:",
                "choose_effects": "Wybierz Efekty",
                "run_process": "Uruchom Proces",
                "run_phase_one": "Uruchom Faze Pierwsza",
                "run_phase_two": "Uruchom Faze Druga",
                "save_settings": "Zapisz Ustawienia",
                "reset_to_default": "Resetuj Ustawienia",
                "backgrounds": "Kulisy",
                "update_news": "Aktualnosci",
                "load_save": "Zaladuj Zapis",
                "save_two": "Zapis Dwa",
                "save_one": "Zapis Jeden",
                "save_three": "Zapis Trzy",
                "statistics": "Statystyki",
                "choose_files": "Wybierz Pliki",
                "choose_font_file": "Wybierz Plik Czcionki",
                "choose_audio_file": "Wybierz Plik Audio",
                "choose_output_folder": "Folder Wyjsciowy",
                "choose_logo": "Wybierz Logo",
                "set_one_clip_duration": "Czas Pojedynczego Klipu:",
                "coming_soon": "Wkrotce...",
                "amount_of_files": "Ilosc Plikow",
                "information": "Informacje",
                "your_files": "Twoje Pliki",
                "font_size": "Rozmiar Czcionki:",
                "words_in_one_sentence": "Slowa w Jednym Zdaniu:",
                "glowing_text": "Poswiata",
                "glow_intensity": "Intensywnosc Poswiaty:",
                "shadow_text": "Cien",
                "shadow_intensity": "Intensywnosc Cienia:",
                "shadow_offset": "Przesuniecie Cienia >",
                "special_words": "Specjalne Słowa",
                "float_effect": "Efekt Plywajacy",
                "random_merge": "Losowe Laczenie",
                "flash_transition": "Przejscie Blysku",
                "flash_duration": "Czas Trwania Blysku:",
                "fade_transition": "Przescie Zanikania",
                "fade_duration": "Czas Trwania Zanikania:",
                "glitch_transition": "Przejscie Zaklocenia",
                "glitch_duration": "Czas Trwania Zaklocenia:",
                "subtitles_effects": "Efekty dla Napisow",
                "background_effects": "Efekty dla Tla",

                "update": """\
                
     --- AKTUALIZACJA APLIKACJI ---
           
    1. Dodano opcje wylogowania

    2. Dodano opcje automatycznego 
       logowania

    3. Naprawiono niektore bledy
                   
            
            
      --- AKTUALIZACJA STRONY ---
    
    1. Graficzna aktualizacja 
       okna logowania,
       okna rejestracji oraz
       okna "Moje konto"
    
    2. Naprawiono pewne bledy zwiazane z 
       logowaniem. \
                """,
                
                "run_instructions_text": """\
        1. „Faza pierwsza” tworzy 
           podkład do Twojego wideo.

        2. „Faza druga” dodaje napisy 
           i wybrany plik audio.

        3. „Zapisz” zapisuje pliki i efekty, 
           a po ponownym otwarciu aplikacji 
           ustawienia sie automatycznie 
           wczytaja.

        4. „Resetuj” usuwa zapisane 
           ustawienia i pliki.\
                """,

                "greeting_text": """\
    Czesc! Tworze te aplikacje samodzielnie, 
    a moim celem jest sprawic, abys byl 
    z niej jak najbardziej zadowolony. 
    Postaram sie zapewnic cotygodniowe 
    aktualizacje z nowymi funkcjami 
    i efektami.
                
    Szybkosc tworzenia wideo zalezy obecnie 
    od Twojego procesora, ale planuje dodac 
    mozliwosc uzycia GPU, aby bylo szybciej.
                
    Jesli masz jakiekolwiek problemy, 
    skontaktuj sie ze mna przez e-mail 
    wsparcia lub zglos sie na Discordzie.
                
    Milej zabawy przy tworzeniu wideo! 
    Mam nadzieje, ze uda Ci sie cos zarobic 
    lub zdobyc mnostwo wyswietlen
    dzieki nim – hehe!
                
    Kamil ;D\
                """,

                "preparation_instructions_text": """\
    1. Pobierz plik MP3 z wideo, 
       ktore chcesz przerobic.
           
    2. Pobierz pliki, ktore chcesz 
       wykorzystac jako tlo.

    3. Pobierz czcionke (w formacie TTF), 
       ktorej chcesz uzyc do napisow.

    4. Wybierz sciezki oraz efekty, ktore 
       chcesz zastosowac do swojego wideo.

    5. Po wybraniu „Pliki” pojawi sie pole 
       wyboru, w ktorym mozesz zdecydowac, 
       jak dlugo ma trwac kazdy klip.
                
    6. W „Liczba plikow” zobaczysz liczbe 
       wybranych plikow oraz ile jest ich 
       potrzebnych, aby dopasować dlugosc
       Twojego audio do wideo.\
                """,

                "effect_instructions_text": """\
    1. Wybierz efekt, ktorego chcesz uzyc w swoim wideo.
           
    2. Jesli klikniesz „Losowe laczenie”, pliki tla beda
       losowo wybierane z folderu. Jesli nie uzyjesz 
       tej opcji, automatycznie zostaną wybrane pierwsze 
       pliki z wybranego folderu.\
                """
            }
        }

        # Tworzenie własnego paska tytułowego
        self.title_bar = ctk.CTkFrame(self, fg_color=fg_color)
        self.title_bar.pack(side="top", fill="x", pady=10, padx=10)

        # Ścieżka do obrazka
        image_path = r"movaiassets1\\movAI Logo.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        logo_image = ctk.CTkImage(resized_image, size=(28, 28))

        self.logo_label = ctk.CTkLabel(master = self, image = logo_image, text = "", fg_color=fg_color)
        self.logo_label.place(relx=0.02, rely=0.014, anchor="n")  # Odstępy

        movai_label_image = create_text_image("movAI", font_size=12, outline_thickness=0)
        self.movai_label = ctk.CTkLabel(master = self, image = movai_label_image, text = "", fg_color=fg_color)
        self.movai_label.place(relx=0.05, rely=0.014, anchor="n")  # Odstępy

        # Przycisk zamknięcia
        self.close_button = ctk.CTkButton(
            self.title_bar, text="✕", command=self.destroy, 
            fg_color=fg_color, text_color=text_color, 
            width=30, height=20  # Ustawienia na kwadratowy kształt
        )
        self.close_button.pack(side="right", padx=5, pady=5)  # Odstępy

        # Przycisk minimalizacji
        #self.maximize_button = ctk.CTkButton(
           # self.title_bar, text="☐", command=self.toggle_maximize, 
           # fg_color="#000000", text_color="white", 
           # width=30, height=20  # Ustawienia na kwadratowy kształt
        #)
        #self.maximize_button.pack(side="right", padx=5, pady=5)  # Odstępy

        # Przycisk maksymalizacji
        self.minimize_button = ctk.CTkButton(
            self.title_bar, text="―", command=self.zminimalizuj_okno, 
            fg_color=fg_color, text_color=text_color, 
            width=30, height=20  # Ustawienia na kwadratowy kształt
        )
        self.minimize_button.pack(side="right", padx=5, pady=5)  # Odstępy


        # Ścieżka do obrazka
        image_path = rf"{white_icons}man.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        profile_image = ctk.CTkImage(resized_image, size=(27, 27))

        self.profile_button = ctk.CTkButton(self, text="", image = profile_image, fg_color=fg_color, command=self.show_frame, width=20, height=20)
        self.profile_button.place(relx=0.89, rely=0.01, anchor="n")

        self.profile_frame = ctk.CTkFrame(self, width=250, height=250, fg_color=frame_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.profile_frame.place(relx=0.87, rely=0.07, anchor="n")
        self.profile_frame.place_forget()

        self.button_logout_image = create_text_image("Logout", font_size=14, outline_thickness=0)
        self.button_logout = ctk.CTkButton(master = self.profile_frame, text="", image = self.button_logout_image, fg_color=fg_color, 
        border_color=all_frames_border_color, border_width=other_frames_border_size, command=self.logout, width=100, height=30, corner_radius=30)
        self.button_logout.place(relx=0.74, rely=0.1, anchor="center")

        self.button_language_image = create_text_image("Languages", font_size=14, outline_thickness=0)
        self.language_button = ctk.CTkButton(master = self.profile_frame, text="", image = self.button_language_image, fg_color=fg_color, 
        border_color=all_frames_border_color, border_width=other_frames_border_size, command=self.show_language_frame, width=100, height=30, corner_radius=30)
        self.language_button.place(relx=0.27, rely=0.1, anchor="center")

        self.language_frame = ctk.CTkFrame(self, width=200, height=35, fg_color=frame_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.language_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.language_frame.place_forget()

        self.language_close_button = ctk.CTkButton(
            self.language_frame, text="✕", command=self.hide_language_frame, 
            fg_color=frame_color, text_color=text_color, 
            width=20, height=20  # Ustawienia na kwadratowy kształt
        )
        self.language_close_button.place(relx=0.92, rely=0.15, anchor="center")  # Odstępy

        # Przyciski zmiany języka
        self.button_language_en_image = create_text_image("English", font_size=12, outline_thickness=0)
        self.button_language_en = ctk.CTkButton(master =self.language_frame, text="", image = self.button_language_en_image, command=self.set_english, 
        width=100, height=30, fg_color=frame_color, border_color=all_frames_border_color, border_width=other_frames_border_size, corner_radius=30)
        self.button_language_en.pack(anchor="center", padx=20, pady=5)

        self.button_language_pl_image = create_text_image("Polski", font_size=12, outline_thickness=0)
        self.button_language_pl = ctk.CTkButton(master =self.language_frame, text="", image = self.button_language_pl_image, command=self.set_polish, 
        width=100, height=30, fg_color=frame_color, border_color=all_frames_border_color, border_width=other_frames_border_size, corner_radius=30)
        self.button_language_pl.pack(anchor="center", padx=60, pady=5)  # Dostosuj pady dla odpowiedniej pozycji

        # Zdarzenia na najechanie i opuszczenie przycisku
        self.bind_button_hover(self.close_button, all_frames_border_color)  # Kolor dla przycisku zamknięcia
        self.bind_button_hover(self.minimize_button, fg_color)  # Kolor dla przycisku minimalizacji
        #self.bind_button_hover(self.maximize_button, "#a6a6a6")  # Kolor dla przycisku maksymalizacji
        self.bind_button_hover(self.profile_button, update_color)
        
        self.bind_button_hover_buttons(self.language_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.button_logout, all_frames_border_color)
        self.bind_button_hover_buttons(self.language_close_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.button_language_en, all_frames_border_color)
        self.bind_button_hover_buttons(self.button_language_pl, all_frames_border_color)


        # Zmienna do przechowywania stanu maksymalizacji
        self.is_maximized = False

        # Przeciąganie okna
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_drag)

        # Przechwycenie zdarzenia przywrócenia okna
        self.bind("<Map>", self.przywroc_okno)

        # Ścieżka do obrazka
        image_path = rf"{white_icons}home.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(25, 25))

        self.home_button = ctk.CTkButton(self, text="", image = paths_image, fg_color=fg_color, corner_radius=30, width=20, 
                                         height=20, command=self.combined_for_main)
        self.home_button.place(relx=0.84, rely=0.032, anchor="center")

        self.path_to_file_image = create_text_image(self.texts["en"]["choose_files"], font_size=13, outline_thickness=0)
        self.path_to_file = ctk.CTkButton(self, text="", image = self.path_to_file_image, fg_color=fg_color, corner_radius=30, width=60, 
                                          height=40, command=self.combined_for_files)
        self.path_to_file.place(relx=0.35, rely=0.032, anchor="center")

        self.path_to_effects_image = create_text_image(self.texts["en"]["choose_effects"], font_size=13, outline_thickness=0)
        self.path_to_effects = ctk.CTkButton(self, text="", image = self.path_to_effects_image, fg_color=fg_color, corner_radius=30, width=60, 
                                             height=40, command=self.combined_for_effects)
        self.path_to_effects.place(relx=0.5, rely=0.032, anchor="center")


        self.path_to_run_image = create_text_image(self.texts["en"]["run_process"], font_size=13, outline_thickness=0)
        self.path_to_run = ctk.CTkButton(self, text="", image = self.path_to_run_image, fg_color=fg_color, corner_radius=30, width=60, 
                                         height=40, command=self.combined_for_process)
        self.path_to_run.place(relx=0.65, rely=0.032, anchor="center")

        # RAMKA OD DOLNEGO PASKA ⬇
        self.frame4 = ctk.CTkFrame(master=self, width=1180, height=60, fg_color=frame_color)
        self.frame4.place(relx=0.5, rely=0.955, anchor="center")

         # Label do wyświetlania "PROCESSING"
        self.processing_label = ctk.CTkLabel(master = self.frame4, text="")
        self.processing_label.place(relx=0.5, rely=0.5, anchor="center")

        self.bind_button_hover_with_border(self.path_to_file, fg_color)
        self.bind_button_hover_with_border(self.path_to_effects, fg_color)
        self.bind_button_hover_with_border(self.path_to_run, fg_color)
        self.bind_button_hover_with_border(self.home_button, fg_color)

        # Wywołanie funkcji display_elements, aby wyświetlić elementy
        self.Main_Window()

    def combined_for_main(self):
         self.save_settings()
         self.save_data()
         self.Main_Window()
         self.load_settings()

    def combined_for_files(self):
         self.save_settings()
         self.Choose_Files_Here()
         self.load_settings()

    def combined_for_effects(self):
         self.save_settings()
         self.Choose_Effects_Here()
         self.load_settings()
    
    def combined_for_process(self):
         self.save_settings()
         self.Run_Process_Here()
         self.load_settings()

    def Choose_Files_Here(self):

        self.hide_all_frames()  # Ukrycie wszystkich innych sekcji

        self.selected_audio_folder = None
        self.selected_audio_folder_path = None #630

        self.frame1 = ctk.CTkFrame(master=self, width=327, height=400, corner_radius=10, fg_color=frame_color, 
                                   border_color=all_frames_border_color, border_width=border_size)
        self.frame1.place(relx=0.145, rely=0.12, anchor="n")

        self.frame1_needed = ctk.CTkFrame(master=self.frame1, width=277, height=195, corner_radius=10, fg_color=frame_color, 
                                   border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.frame1_needed.place(relx=0.5, rely=0.32, anchor="center")

        self.frame1_optional = ctk.CTkFrame(master=self.frame1, width=277, height=115, corner_radius=10, fg_color=frame_color, 
                                   border_color=text_color, border_width=other_frames_border_size)
        self.frame1_optional.place(relx=0.5, rely=0.8, anchor="center")
 
        self.files_image = create_text_image(self.texts["en"]["choose_files"], font_size=14, outline_thickness=0)
        self.files_button = ctk.CTkButton(master = self.frame1_needed, text="", image = self.files_image, command=self.select_folder, 
                                          fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.files_button.place(relx=0.5, rely=0.2, anchor="center")

        self.audio_file_image = create_text_image(self.texts["en"]["choose_audio_file"], font_size=14, outline_thickness=0)
        self.audio_file_button = ctk.CTkButton(master = self.frame1_needed, text="", image = self.audio_file_image, command=self.select_audio_folder, 
                                               fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size )
        self.audio_file_button.place(relx=0.5, rely=0.5, anchor="center")

        self.output_folder_image = create_text_image(self.texts["en"]["choose_output_folder"], font_size=14, outline_thickness=0)
        self.output_folder_button = ctk.CTkButton(master = self.frame1_needed, text="", image = self.output_folder_image, command=self.select_output_folder, 
                                                  fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size )
        self.output_folder_button.place(relx=0.5, rely=0.8, anchor="center")

        self.png_file_button_image = create_text_image(self.texts["en"]["choose_logo"], font_size=14, outline_thickness=0)
        self.png_file_button = ctk.CTkButton(master=self.frame1_optional, image = self.png_file_button_image, text="", fg_color=frame_color, corner_radius=30, width=190, 
                                             height=40, border_color=info_border_color, border_width=other_frames_border_size,
                                             command=self.select_png_file)
        self.png_file_button.place(relx=0.5, rely=0.27, anchor="center")

        self.font_file_checkbox = ctk.CTkCheckBox(master=self.frame1_optional, text=self.texts["en"]["choose_font_file"], text_color=text_color, variable=self.use_font_path, 
                                               onvalue=True, offvalue=False, command=self.checkbox_event_font_file, 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.font_file_checkbox.place(relx=0.5, rely=0.73, anchor="center")

        self.font_file_checkbox_on = ctk.CTkCheckBox(master=self.frame1_optional, text="", text_color=text_color, variable=self.use_font_path, 
                                               onvalue=True, offvalue=False, command=self.checkbox_event_font_file, 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.font_file_checkbox_on.place(relx=0.21, rely=0.73, anchor="center")
        self.font_file_checkbox_on.place_forget()

        self.font_file_image = create_text_image(self.texts["en"]["choose_font_file"], font_size=14, outline_thickness=0)
        self.font_file_button = ctk.CTkButton(master = self.frame1_optional, text="", image = self.font_file_image, command=self.select_font_path, 
                                              fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=info_border_color, border_width=other_frames_border_size )
        self.font_file_button.place(relx=0.5, rely=0.73, anchor="center")
        self.font_file_button.place_forget()

        self.frame_numbers = ctk.CTkFrame(master=self, width=327, height=200, corner_radius=10, fg_color=frame_color, 
                                          border_color=all_frames_border_color, border_width=border_size)
        self.frame_numbers.place(relx=0.43, rely=0.186, anchor="center")

        self.frame_spinbox_clip = ctk.CTkFrame(master=self.frame_numbers, width=300, height=65, corner_radius=10, fg_color=frame_color, 
                                          border_color=all_frames_border_color, border_width=border_size)
        self.frame_spinbox_clip.place(relx=0.5, rely=0.83, anchor="center")

        self.clip_duration_checkbox = ctk.CTkCheckBox(master=self.frame_spinbox_clip, text=self.texts["en"]["manual_one_clip_duration"], text_color=text_color, variable=self.clip_duration_check_var, 
                                               onvalue="on", offvalue="off", command=self.checkbox_event_duration, 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.clip_duration_checkbox.place(relx=0.5, rely=0.5, anchor="center")

        self.on_clip_duration_checkbox_on = ctk.CTkCheckBox(master=self.frame_spinbox_clip, text="", text_color=text_color, variable=self.clip_duration_check_var, 
                                               onvalue="on", offvalue="off", command=self.checkbox_event_duration, 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.on_clip_duration_checkbox_on.place(relx=0.2, rely=0.5, anchor="center")
        self.on_clip_duration_checkbox_on.place_forget()

        self.spinbox_clip_image = create_text_image(self.texts["en"]["set_one_clip_duration"], font_size=14, outline_thickness=0)
        self.spinbox_clip_lable = ctk.CTkLabel(master=self.frame_spinbox_clip, image = self.spinbox_clip_image, text="")
        self.spinbox_clip_lable.place(relx=0.5, rely=0.25,anchor="center")
        self.spinbox_clip_lable.place_forget()

        # Użyj FloatSpinbox z customtkinter dla czasu trwania klipu (clip_duration)
        self.clip_duration = FloatSpinbox(master=self.frame_spinbox_clip, width=130, step_size=1)#command=self.combined_for_spinbox
        self.clip_duration.place(relx=0.5, rely=0.68, anchor="center")
        self.clip_duration.set(1)  # Ustaw domyślną wartość na 5
        self.clip_duration.place_forget()

        self.frame_format = ctk.CTkFrame(master=self, width=327, height=212, corner_radius=10, fg_color=frame_color, 
                                   border_color=all_frames_border_color, border_width=border_size)
        self.frame_format.place(relx=0.145, rely=0.907, anchor="s")

        self.format_image = create_text_image(self.texts["en"]["coming_soon"], font_size=20, outline_thickness=0)
        self.format_lable = ctk.CTkLabel(master=self.frame_format, image = self.format_image, text="")
        self.format_lable.place(relx=0.5, rely=0.5,anchor="center")

        self.frame_show_numbers = ctk.CTkFrame(master=self.frame_numbers, width=227, height=80, corner_radius=10, fg_color=frame_color, 
                                          border_color=other_frames_border, border_width=other_frames_border_size)
        self.frame_show_numbers.place(relx=0.5, rely=0.45, anchor="center")

        self.lable_show_numbers = ctk.CTkLabel(master=self.frame_show_numbers, text = "", font=("Arial", 25),
                                               width=220, height=73, corner_radius=10, fg_color=frame_color, 
                                              )
        self.lable_show_numbers.place(relx=0.5, rely=0.5, anchor="center")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}\\folder (1).png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.numbers_lable_image = ctk.CTkLabel(master=self.frame_numbers, image = paths_image, text="", fg_color=frame_color)
        self.numbers_lable_image.place(relx=0.2, rely=0.11,anchor="center")
        self.update()

        self.your_files_image = create_text_image(self.texts["en"]["coming_soon"], font_size=14, outline_thickness=0)
        self.your_files_lable = ctk.CTkLabel(master=self.frame_numbers, image = self.your_files_image, text="")
        self.your_files_lable.place(relx=0.5, rely=0.45,anchor="center")

       #self.your_files_image = create_text_image(self.texts["en"]["your_files:"], font_size=14, outline_thickness=0)
       #self.your_files_lable = ctk.CTkLabel(master=self.frame_numbers, image = self.your_files_image, text="")
       #self.your_files_lable.place(relx=0.3, rely=0.34,anchor="center")

       #self.needed_image = create_text_image(self.texts["en"]["needed"], font_size=14, outline_thickness=0)
       #self.needed_lable = ctk.CTkLabel(master=self.frame_numbers, image =  self.needed_image, text="")
       #self.needed_lable.place(relx=0.69, rely=0.34,anchor="center")

        self.numbers_image = create_text_image(self.texts["en"]["amount_of_files"], font_size=20, outline_thickness=0)
        self.numbers_lable = ctk.CTkLabel(master=self.frame_numbers, image = self.numbers_image, text="")
        self.numbers_lable.place(relx=0.53, rely=0.1,anchor="center")

        self.frame_info = ctk.CTkFrame(master=self, width=327, height=460, corner_radius=10, fg_color=frame_color, 
                                       border_color=info_border_color, border_width=other_frames_border_size)
        self.frame_info.place(relx=0.43, rely=0.62, anchor="center")

        # Tworzymy etykietę z instrukcjami i umieszczamy ją po lewej stronie, na środku wysokości okna
        
        self.files_instructions_label_image = create_text_image(self.texts["en"]["preparation_instructions_text"], font_size=14, outline_thickness=0)
        self.files_instructions_label = ctk.CTkLabel(master=self.frame_info, image = self.files_instructions_label_image, text="", justify="left", anchor="w", fg_color=None)
        self.files_instructions_label.place(relx=0.5, rely=0.52, anchor="center")


        # Ścieżka do obrazka
        image_path = rf"{white_icons}\\file.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.info_lable_image = ctk.CTkLabel(master=self.frame_info, image = paths_image, text="", fg_color=frame_color)
        self.info_lable_image.place(relx=0.25, rely=0.05,anchor="center")
        self.update()

        self.info_image = create_text_image(self.texts["en"]["information"], font_size=20, outline_thickness=0)
        self.info_lable = ctk.CTkLabel(master=self.frame_info, image = self.info_image, text="")
        self.info_lable.place(relx=0.51, rely=0.05,anchor="center")

        self.frame_files = ctk.CTkFrame(master=self, width=493, height=560, corner_radius=10, fg_color=frame_color, 
                                        border_color=all_frames_border_color, border_width=border_size)
        self.frame_files.place(relx=0.785, rely=0.41, anchor="center")

        self.frame_show_files = ctk.CTkFrame(master=self.frame_files, width=393, height=460, corner_radius=10, fg_color=frame_color, 
                                        border_color=other_frames_border, border_width=other_frames_border_size)
        self.frame_show_files.place(relx=0.5, rely=0.5, anchor="center")

        # Dodanie listy plików w ramce
        self.file_listbox = ctk.CTkTextbox(self.frame_show_files, width=390, height=457, text_color=text_color, fg_color=terminal_files)
        self.file_listbox.pack(padx=5, pady=5)

        # Przechowywanie wybranych plików
        self.selected_folder_path = None
        self.selected_file_path = None
        

        # Ścieżka do obrazka
        image_path = rf"{white_icons}\\folder (2).png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.files_lable_image = ctk.CTkLabel(master=self.frame_files, image = paths_image, text="", fg_color=frame_color)
        self.files_lable_image.place(relx=0.37, rely=0.04,anchor="center")
        self.update()

        self.files_image = create_text_image(self.texts["en"]["your_files"], font_size=20, outline_thickness=0)
        self.files_lable = ctk.CTkLabel(master=self.frame_files, image = self.files_image, text="")
        self.files_lable.place(relx=0.53, rely=0.04,anchor="center")

        self.frame_for_ad1 = ctk.CTkFrame(master=self, width=493, height=100, corner_radius=10, fg_color=frame_color,
                                           border_color=ad_border_color, border_width=border_size)
        self.frame_for_ad1.place(relx=0.785, rely=0.845, anchor="center")

         # Tworzenie przycisku z grafiką
        self.button_for_ad_1_image = create_text_image(self.texts["en"]["click_here"], font_size=27, outline_thickness=0)
        self.button_for_ad_1 = ctk.CTkButton(self.frame_for_ad1, image=self.button_for_ad_1_image, text="", border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, fg_color=frame_color, corner_radius=30, command=self.open_link, width=270, height=80)
        self.button_for_ad_1.place(relx=0.5, rely=0.5, anchor="center")

        self.path_frame = ctk.CTkFrame(master=self, width=327, height=45, corner_radius=10, fg_color=frame_color, 
                                       border_color=all_frames_border_color, border_width=border_size)
        self.path_frame.place(relx=0.145, rely=0.117, anchor="s")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}\\paths.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        # Przycisk do wyboru folder
        self.folder_button_image = create_text_image(self.texts["en"]["choose_files"], font_size=20, outline_thickness=0)
        self.folder_lable = ctk.CTkLabel(master=self.path_frame, image = self.folder_button_image, text="")
        self.folder_lable.place(relx=0.53, rely=0.45,anchor="center")

        self.folder_lable_image = ctk.CTkLabel(master=self.path_frame, image = paths_image, text="", fg_color=frame_color)
        self.folder_lable_image.place(relx=0.27, rely=0.45,anchor="center")
        self.update()

        self.frame_for_corners = ctk.CTkFrame(master=self, width=327, height=20,corner_radius=0, fg_color=frame_color)
        self.frame_for_corners.place(relx=0.145, rely=0.13, anchor="s")

        self.frame1_needed_image = create_text_image(self.texts["en"]["required"], font_size=16, outline_thickness=0)
        self.frame1_needed_lable = ctk.CTkLabel(master=self.frame1, image = self.frame1_needed_image, text="")
        self.frame1_needed_lable.place(relx=0.5, rely=0.04,anchor="center")
        
        self.frame1_optional_image = create_text_image(self.texts["en"]["optional"], font_size=16, outline_thickness=0)
        self.frame1_optional_lable = ctk.CTkLabel(master=self.frame1, image = self.frame1_optional_image, text="")
        self.frame1_optional_lable.place(relx=0.5, rely=0.613,anchor="center")

        # Wczytanie zapisanego języka lub ustawienie domyślnego
        self.language = self.load_language() or "en"
        self.set_language(self.language)

        self.load_settings()  # Wczytaj zapisane ustawienia

        self.bind_button_hover_buttons(self.files_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.font_file_button, info_border_color)
        self.bind_button_hover_buttons(self.audio_file_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.output_folder_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.png_file_button, info_border_color)
        self.bind_button_hover_buttons(self.button_for_ad_1, all_frames_border_color)

    #def combined_for_spinbox(self):
        #calculation_thread = threading.Thread(target=self.calculate_audio_length1)
        #calculation_thread.daemon = True  # Ustawienie jako wątek daemon, aby zamknął się z głównym programem
        #calculation_thread.start()
       # self.save_settings()

    def Choose_Effects_Here(self):

        self.hide_all_frames()  # Ukrycie wszystkich innych sekcji

        self.frame_subtitles = ctk.CTkScrollableFrame(master=self, width=373, height=430, corner_radius=10, fg_color=frame_color, 
                                                      border_color=all_frames_border_color, border_width=border_size)
        self.frame_subtitles.place(relx=0.174, rely=0.12, anchor="n")

        self.frame_in_subtitles1 = ctk.CTkFrame(master=self.frame_subtitles, width=303, height=150, corner_radius=10, fg_color=frame_color, 
                                                      border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.frame_in_subtitles1.pack(padx=20, pady=5, anchor="center")

        # Tworzymy napis (label) nad spinboxem
        self.label_for_font_scale_image = create_text_image(self.texts["en"]["font_size"], font_size=14, outline_thickness=0)
        self.label_for_font_scale = ctk.CTkLabel(master=self.frame_in_subtitles1, image = self.label_for_font_scale_image,  text="")
        self.label_for_font_scale.place(relx=0.5, rely=0.12, anchor="center")

        # Użyj FloatSpinbox z customtkinter dla czasu trwania klipu (clip_duration)
        self.font_scale = FloatSpinbox(master=self.frame_in_subtitles1, width=130, step_size=1, command=self.save_settings)
        self.font_scale.place(relx=0.5, rely=0.32, anchor="center")
        self.font_scale.set(20)  # Ustaw domyślną wartość na 5

        # Tworzymy napis (label) nad spinboxem
        self.label_for_number_of_words_image = create_text_image(self.texts["en"]["words_in_one_sentence"], font_size=14, outline_thickness=0)
        self.label_for_number_of_words = ctk.CTkLabel(master=self.frame_in_subtitles1, image = self.label_for_number_of_words_image,  text="")
        self.label_for_number_of_words.place(relx=0.5, rely=0.6, anchor="center")

        # Użyj FloatSpinbox z customtkinter dla czasu trwania klipu (clip_duration)
        self.number_of_words = FloatSpinbox(master = self.frame_in_subtitles1, width=130, step_size=1, command=self.save_settings)
        self.number_of_words.place(relx=0.5, rely=0.8, anchor="center")
        self.number_of_words.set(1)  # Ustaw domyślną wartość na 5

        self.frame_in_subtitles2 = ctk.CTkFrame(master=self.frame_subtitles, width=303, height=300, corner_radius=10, fg_color=frame_color, 
                                                      border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.frame_in_subtitles2.pack(padx=20, pady=5, anchor="center")

        self.bloom_container = ctk.CTkFrame(master=self.frame_in_subtitles2, fg_color=frame_color, width=290, height=70)
        self.bloom_container.place(relx=0.5, rely=0.125, anchor="center")

        self.bloom_checkbox = ctk.CTkCheckBox(master=self.bloom_container, text=self.texts["en"]["glowing_text"], text_color=text_color,
                                                 command=self.checkbox_event2, fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size,
                                                 variable=self.bloom_check_var, 
                                                 onvalue=True, offvalue=False)
        self.bloom_checkbox.place(relx=0.4, rely=0.5, anchor="e")

        self.label_for_bloom_image = create_text_image(self.texts["en"]["glow_intensity"], font_size=14, outline_thickness=0)
        self.label_for_bloom = ctk.CTkLabel(master=self.bloom_container, image = self.label_for_bloom_image,  text="")
        self.label_for_bloom.place(relx=0.7, rely=0.2, anchor="center")
        self.label_for_bloom.place_forget()
        
        self.blur_radius = FloatSpinbox(master=self.bloom_container, width=130, step_size=1, command=self.save_settings)
        self.blur_radius.place(relx=0.7, rely=0.6, anchor="center")
        self.blur_radius.set(6)  # Ustaw domyślną wartość na 5
        self.blur_radius.place_forget()

        self.use_shadow_container = ctk.CTkFrame(master=self.frame_in_subtitles2, fg_color=frame_color, width=290, height=75)
        self.use_shadow_container.place(relx=0.5, rely=0.375, anchor="center")

        self.use_shadow_checkbox = ctk.CTkCheckBox(master=self.use_shadow_container, text=self.texts["en"]["shadow_text"], text_color=text_color,
                                                 command=self.checkbox_event2, fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size,
                                                 variable=self.use_shadow_check_var, 
                                                 onvalue=True, offvalue=False)
        self.use_shadow_checkbox.place(relx=0.4, rely=0.5, anchor="e")

        self.label_for_use_shadow_image = create_text_image(self.texts["en"]["shadow_intensity"], font_size=14, outline_thickness=0)
        self.label_for_use_shadow = ctk.CTkLabel(master=self.use_shadow_container, image = self.label_for_use_shadow_image,  text="")
        self.label_for_use_shadow.place(relx=0.7, rely=0.06, anchor="center")
        self.label_for_use_shadow.place_forget()
        
        self.shadow_radius = FloatSpinbox(master=self.use_shadow_container, width=130, step_size=1, command=self.save_settings)
        self.shadow_radius.place(relx=0.7, rely=0.5, anchor="center")
        self.shadow_radius.set(3)  # Ustaw domyślną wartość na 5
        self.shadow_radius.place_forget()

        self.label_for_shadow_offset_image = create_text_image(self.texts["en"]["shadow_offset"], font_size=14, outline_thickness=0)
        self.label_shadow_offset_shadow = ctk.CTkLabel(master=self.use_shadow_container, image = self.label_for_shadow_offset_image,  text="")
        self.label_shadow_offset_shadow.place(relx=0.7, rely=0.1, anchor="center")
        self.label_shadow_offset_shadow.place_forget()
        
        self.shadow_offset = FloatSpinbox(master=self.use_shadow_container, width=130, step_size=1, command=self.save_settings)
        self.shadow_offset.place(relx=0.7, rely=0.5, anchor="center")
        self.shadow_offset.set(5)  # Ustaw domyślną wartość na 5
        self.shadow_offset.place_forget()

        # Suwak z zakresem od 0 do 9 i skokami co 1
       # slider = ctk.CTkSlider(master=self.use_shadow_container, from_=1, to=5, number_of_steps=5)
       # slider.place(relx=0.4, rely=0.88, anchor="center")


        self.use_color_container = ctk.CTkFrame(master=self.frame_in_subtitles2, fg_color=frame_color, width=290, height=70)
        self.use_color_container.place(relx=0.5, rely=0.625, anchor="center")

        self.use_color_checkbox = ctk.CTkCheckBox(master=self.use_color_container, text=self.texts["en"]["special_words"], text_color=text_color,
                                                 command=self.checkbox_event2, fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size,
                                                 variable=self.use_color_check_var, 
                                                 onvalue=True, offvalue=False)
        self.use_color_checkbox.place(relx=0.425, rely=0.5, anchor="e")

        self.should_oscillate_container = ctk.CTkFrame(master=self.frame_in_subtitles2, fg_color=frame_color, width=290, height=70)
        self.should_oscillate_container.place(relx=0.5, rely=0.874, anchor="center")

        self.should_oscillate_checkbox = ctk.CTkCheckBox(master=self.should_oscillate_container, text=self.texts["en"]["float_effect"], text_color=text_color,
                                                 command=self.checkbox_event2, fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size,
                                                 variable=self.should_oscillate_check_var, 
                                                 onvalue=True, offvalue=False)
        self.should_oscillate_checkbox.place(relx=0.385, rely=0.5, anchor="e")

        self.frame_info_effect = ctk.CTkFrame(master=self, width=399, height=170, corner_radius=10, fg_color=frame_color, 
                                              border_color=info_border_color, border_width=other_frames_border_size)
        self.frame_info_effect.place(relx=0.174, rely=0.695, anchor="n")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}search.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 33))

        self.numbers_lable_image = ctk.CTkLabel(master=self.frame_info_effect, image = paths_image, text="", fg_color=frame_color)
        self.numbers_lable_image.place(relx=0.29, rely=0.11,anchor="center")
        self.update()

        self.info_effect_lable_image = create_text_image(self.texts["en"]["information"], font_size=20, outline_thickness=0)
        self.info_effect_lable = ctk.CTkLabel(master=self.frame_info_effect, image = self.info_effect_lable_image, text="",fg_color=frame_color)
        self.info_effect_lable.place(relx=0.49, rely=0.1,anchor="center")

        self.effect_instructions_label_image = create_text_image(self.texts["en"]["effect_instructions_text"], font_size=14, outline_thickness=0)
        self.effect_instructions_label = ctk.CTkLabel(master=self.frame_info_effect, image = self.effect_instructions_label_image, text="", justify="left", anchor="w", fg_color=None)
        self.effect_instructions_label.place(relx=0.5, rely=0.57, anchor="center")

        self.frame_background = ctk.CTkScrollableFrame(master=self, width=373, height=430, corner_radius=10, fg_color=frame_color, 
                                                       border_color=all_frames_border_color, border_width=border_size)
        self.frame_background.place(relx=0.514, rely=0.12, anchor="n")

        self.frame_in_background1 = ctk.CTkFrame(master=self.frame_background, width=333, height=390, corner_radius=10, fg_color=frame_color, 
                                                      border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.frame_in_background1.pack(padx=20, pady=5, anchor="center")

        # Container dla Flash
        self.is_random_container = ctk.CTkFrame(master=self.frame_in_background1, fg_color=frame_color, width=324, height=70)
        self.is_random_container.place(relx=0.5, rely=0.105, anchor="center")

        self.is_random_checkbox = ctk.CTkCheckBox(master=self.is_random_container, text=self.texts["en"]["random_merge"], text_color=text_color,  command=self.checkbox_event2,  
                                                  fg_color=info_border_color, 
                                                  border_color=info_border_color, border_width=1,
                                             variable= self.is_random_var, onvalue=False, offvalue=True)
        self.is_random_checkbox.place(relx=0.19, rely=0.5, anchor="center")
        self.is_random_checkbox.pack_forget()

        step_size_for_transition = 0.1
        default_transition_time = 0.3

        # Container dla Flash
        self.flash_container = ctk.CTkFrame(master=self.frame_in_background1, fg_color=frame_color, width=324, height=70)
        self.flash_container.place(relx=0.5, rely=0.305, anchor="center")

        self.flash_checkbox = ctk.CTkCheckBox(master=self.flash_container, text=self.texts["en"]["flash_transition"], text_color=text_color, variable=self.flash_check_var, 
                                              onvalue="1", offvalue="0", command=self.checkbox_event2, fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.flash_checkbox.place(relx=0.2, rely=0.5, anchor="center")

        self.label_for_flash_image = create_text_image(self.texts["en"]["flash_duration"], font_size=14, outline_thickness=0)
        self.label_for_flash = ctk.CTkLabel(master=self.flash_container, image = self.label_for_flash_image,  text="")
        self.label_for_flash.place(relx=0.7, rely=0.2, anchor="center")
        self.label_for_flash.place_forget()

        self.flash_duration = FloatSpinbox(master=self.flash_container, width=130, step_size=step_size_for_transition, command=self.save_settings)
        self.flash_duration.place(relx=0.7, rely=0.6, anchor="center")
        self.flash_duration.set(default_transition_time)  # Ustaw domyślną wartość na 5
        self.flash_duration.place_forget()

        self.fade_container = ctk.CTkFrame(master=self.frame_in_background1, fg_color=frame_color, width=324, height=70)
        self.fade_container.place(relx=0.5, rely=0.505, anchor="center")

        self.fade_checkbox = ctk.CTkCheckBox(master=self.fade_container, text=self.texts["en"]["fade_transition"], text_color=text_color, variable=self.fade_check_var, 
                                             onvalue="1", offvalue="0", command=self.checkbox_event2, fg_color=info_border_color, 
                                             border_color=info_border_color, border_width=other_frames_border_size)
        self.fade_checkbox.place(relx=0.2, rely=0.5, anchor="center")

        self.label_for_fade_image = create_text_image(self.texts["en"]["fade_duration"], font_size=14, outline_thickness=0)
        self.label_for_fade = ctk.CTkLabel(master=self.fade_container, image = self.label_for_fade_image,  text="")
        self.label_for_fade.place(relx=0.7, rely=0.2, anchor="center")
        self.label_for_fade.place_forget()
        
        self.fade_duration = FloatSpinbox(master=self.fade_container, width=130, step_size=step_size_for_transition, command=self.save_settings)
        self.fade_duration.place(relx=0.7, rely=0.6, anchor="center")
        self.fade_duration.set(default_transition_time)  # Ustaw domyślną wartość na 5
        self.fade_duration.place_forget()

        self.glitch_container = ctk.CTkFrame(master=self.frame_in_background1, fg_color=frame_color, width=324, height=70)
        self.glitch_container.place(relx=0.5, rely=0.705, anchor="center")

        self.glitch_checkbox = ctk.CTkCheckBox(master=self.glitch_container, text=self.texts["en"]["glitch_transition"], text_color=text_color, variable=self.glitch_check_var, 
                                               onvalue="1", offvalue="0", command=self.checkbox_event2, 
                                               fg_color=info_border_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.glitch_checkbox.place(relx=0.205, rely=0.5, anchor="center")

        self.label_for_glitch_image = create_text_image(self.texts["en"]["glitch_duration"], font_size=14, outline_thickness=0)
        self.label_for_glitch = ctk.CTkLabel(master=self.glitch_container, image = self.label_for_glitch_image,  text="")
        self.label_for_glitch.place(relx=0.7, rely=0.2, anchor="center")
        self.label_for_glitch.place_forget()

        self.glitch_duration = FloatSpinbox(master=self.glitch_container, width=130, step_size=step_size_for_transition, command=self.save_settings)
        self.glitch_duration.place(relx=0.7, rely=0.6, anchor="center")
        self.glitch_duration.set(default_transition_time)  # Ustaw domyślną wartość na 5
        self.glitch_duration.place_forget()


        self.frame_for_ad2 = ctk.CTkFrame(master=self, width=399, height=170, corner_radius=10, fg_color=frame_color, 
                                          border_color=ad_border_color, border_width=border_size)
        self.frame_for_ad2.place(relx=0.514, rely=0.695, anchor="n")

        self.button_for_ad_2_image = create_text_image(self.texts["en"]["click_here"], font_size=27, outline_thickness=0)
        self.button_for_ad_2 = ctk.CTkButton(self.frame_for_ad2, image=self.button_for_ad_2_image, text="", border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, fg_color=frame_color, corner_radius=30, command=self.open_link, width=300, height=100)
        self.button_for_ad_2.place(relx=0.5, rely=0.5, anchor="center")

        self.frame_showcase = ctk.CTkFrame(master=self, width=365, height=670, corner_radius=10, fg_color=frame_color, 
                                           border_color=all_frames_border_color, border_width=border_size)
        self.frame_showcase.place(relx=0.841, rely=0.07, anchor="n")

        self.showcase_lable_image = create_text_image(self.texts["en"]["coming_soon"], font_size=20, outline_thickness=0)
        self.showcase_lable = ctk.CTkLabel(master=self.frame_showcase, image = self.showcase_lable_image, text="",fg_color=frame_color)
        self.showcase_lable.place(relx=0.5, rely=0.5,anchor="center")

        self.frame_for_laber1 = ctk.CTkFrame(master=self, width=399, height=40, corner_radius=10, fg_color=frame_color, 
                                             border_color=all_frames_border_color, border_width=border_size)
        self.frame_for_laber1.place(relx=0.175, rely=0.07, anchor="n")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}Effects.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(37, 37))

        self.numbers_lable_image_2 = ctk.CTkLabel(master=self.frame_for_laber1, image = paths_image, text="", fg_color=frame_color)
        self.numbers_lable_image_2.place(relx=0.24, rely=0.48,anchor="center")
        self.update()

        self.subtitles_lable_image = create_text_image(self.texts["en"]["subtitles_effects"], font_size=20, outline_thickness=0)
        self.subtitles_lable = ctk.CTkLabel(master=self.frame_for_laber1, image = self.subtitles_lable_image, text="",fg_color=frame_color)
        self.subtitles_lable.place(relx=0.49, rely=0.5,anchor="center")

        self.frame_for_laber2 = ctk.CTkFrame(master=self, width=399, height=40, corner_radius=10, fg_color=frame_color, 
                                             border_color=all_frames_border_color, border_width=border_size)
        self.frame_for_laber2.place(relx=0.515, rely=0.07, anchor="n")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}hat.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(30, 30))

        self.numbers_lable_image_1 = ctk.CTkLabel(master=self.frame_for_laber2, image = paths_image, text="", fg_color=frame_color)
        self.numbers_lable_image_1.place(relx=0.19, rely=0.43,anchor="center")
        self.update()

        self.background_lable_image = create_text_image(self.texts["en"]["background_effects"], font_size=20, outline_thickness=0)
        self.background_lable = ctk.CTkLabel(master=self.frame_for_laber2, image = self.background_lable_image, text="",fg_color=frame_color)
        self.background_lable.place(relx=0.49, rely=0.5,anchor="center")

        self.frame_corners1 = ctk.CTkFrame(master=self, width=399, height=20, corner_radius=0, fg_color=frame_color)
        self.frame_corners1.place(relx=0.175, rely=0.11, anchor="n")

        self.frame_corners2 = ctk.CTkFrame(master=self, width=399, height=20, corner_radius=0, fg_color=frame_color)
        self.frame_corners2.place(relx=0.515, rely=0.11, anchor="n")

        # Wczytanie zapisanego języka lub ustawienie domyślnego
        self.language = self.load_language() or "en"
        self.set_language(self.language)

        self.load_settings()  # Wczytaj zapisane ustawienia

        self.bind_button_hover_buttons(self.button_for_ad_2, all_frames_border_color)

       # self.bind_button_hover_checkbox(self.glitch_checkbox, info_border_color)
       # self.bind_button_hover_checkbox(self.fade_checkbox, info_border_color)
       # self.bind_button_hover_checkbox(self.flash_checkbox, info_border_color)
       # self.bind_button_hover_checkbox(self.bloom_checkbox, info_border_color)
       # self.bind_button_hover_checkbox(self.use_color_checkbox, info_border_color)
       # self.bind_button_hover_checkbox(self.should_oscillate_checkbox, info_border_color)

    def Run_Process_Here(self):

        self.hide_all_frames()  # Ukrycie wszystkich innych sekcji

        self.frame_run = ctk.CTkFrame(master=self, width=327, height=360, corner_radius=10, fg_color=frame_color, 
                                      border_color=all_frames_border_color, border_width=border_size)
        self.frame_run.place(relx=0.145, rely=0.07, anchor="n")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}settings.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.run_lable_image_1 = ctk.CTkLabel(master=self.frame_run, image = paths_image, text="", fg_color=frame_color)
        self.run_lable_image_1.place(relx=0.24, rely=0.05,anchor="center")
        self.update()

        self.run_lable_image = create_text_image(self.texts["en"]["run_process"], font_size=20, outline_thickness=0)
        self.run_lable = ctk.CTkLabel(master=self.frame_run, image = self.run_lable_image, text="",fg_color=frame_color)
        self.run_lable.place(relx=0.53, rely=0.05,anchor="center")

        # Napis na przycisku
        self.button_image = create_text_image(self.texts["en"]["run_phase_one"], font_size=14, outline_thickness=0)
        self.merge_button = ctk.CTkButton(master=self.frame_run, image=self.button_image, text="", command=self.combined_for_start_merge, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.merge_button.place(relx=0.5, rely=0.2 , anchor="center")
        
        self.run_process_button_image = create_text_image(self.texts["en"]["run_phase_two"], font_size=14, outline_thickness=0)
        self.run_process_button = ctk.CTkButton(master=self.frame_run, image =self.run_process_button_image,  text="", command=self.combined_for_start_process, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.run_process_button.place(relx=0.5, rely=0.4, anchor="center")

        # Przykładowo, jeśli używasz tkinter lub CTk
        self.save_button_image = create_text_image(self.texts["en"]["save_settings"], font_size=14, outline_thickness=0)
        self.save_button = ctk.CTkButton(master=self.frame_run, image = self.save_button_image,  text="", command=self.save_settings, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.save_button.place(relx=0.5, rely=0.6, anchor="center")  # Umieść przycisk w odpowiednim miejscu

        # Add reset button
        self.reset_button_image = create_text_image(self.texts["en"]["reset_to_default"], font_size=14, outline_thickness=0)
        self.reset_button = ctk.CTkButton(master=self.frame_run, image = self.reset_button_image,  text="", command=self.reset_settings, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=40, border_color=all_frames_border_color, border_width=other_frames_border_size)
        self.reset_button.place(relx=0.5, rely=0.8, anchor="center")  # Adjust packing as necessary

        self.frame_run_info = ctk.CTkFrame(master=self, width=327, height=300, corner_radius=10, fg_color=frame_color, 
                                           border_color=info_border_color, border_width=other_frames_border_size)
        self.frame_run_info.place(relx=0.145, rely=0.53, anchor="n")

        self.run_instructions_label_image = create_text_image(self.texts["en"]["run_instructions_text"], font_size=14, outline_thickness=0)
        self.run_instructions_label = ctk.CTkLabel(master=self.frame_run_info, image = self.run_instructions_label_image, text="", justify="left", anchor="w", fg_color=None)
        self.run_instructions_label.place(relx=0.47, rely=0.54, anchor="center")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}instruction.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.run_info_lable_image = ctk.CTkLabel(master=self.frame_run_info, image = paths_image, text="", fg_color=frame_color)
        self.run_info_lable_image.place(relx=0.26, rely=0.07,anchor="center")
        self.update()

        self.run_info_lable_image = create_text_image(self.texts["en"]["information"], font_size=20, outline_thickness=0)
        self.run_info_lable = ctk.CTkLabel(master=self.frame_run_info, image = self.run_info_lable_image, text="",fg_color=frame_color)
        self.run_info_lable.place(relx=0.515, rely=0.06,anchor="center")

        self.frame_terminal = ctk.CTkFrame(master=self, width=846, height=460, corner_radius=10, fg_color=frame_color, 
                                           border_color=all_frames_border_color, border_width=border_size)
        self.frame_terminal.place(relx=0.64, rely=0.07, anchor="n")

        self.frame_terminal_look = ctk.CTkFrame(master=self.frame_terminal, width=746, height=360, corner_radius=10, fg_color=frame_color, border_color=other_frames_border, border_width=other_frames_border_size)
        self.frame_terminal_look.place(relx=0.5, rely=0.5, anchor="center")

        # Pole tekstowe do wyświetlania komunikatów terminala
        self.terminal_textbox = ctk.CTkTextbox(master=self.frame_terminal_look, width=740, height=350, text_color=text_color, fg_color=terminal_files)
        self.terminal_textbox.pack(padx=5, pady=5)

        # Przekierowujemy standardowe wyjścia (stdout i stderr) do tego textboxa
        sys.stdout = RedirectOutput(self.terminal_textbox)
        sys.stderr = RedirectOutput(self.terminal_textbox)

        # Ścieżka do obrazka
        image_path = rf"{white_icons}settings (1).png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(35, 35))

        self.terminal_lable_image = ctk.CTkLabel(master=self.frame_terminal, image = paths_image, text="", fg_color=frame_color)
        self.terminal_lable_image.place(relx=0.41, rely=0.04,anchor="center")
        self.update()

        self.terminal_lable_image = create_text_image(self.texts["en"]["backgrounds"], font_size=20, outline_thickness=0)
        self.terminal_lable = ctk.CTkLabel(master=self.frame_terminal, image = self.terminal_lable_image, text="",fg_color=frame_color)
        self.terminal_lable.place(relx=0.53, rely=0.05,anchor="center")

        self.frame_for_ad3 = ctk.CTkFrame(master=self, width=846, height=200, corner_radius=10, fg_color=frame_color, 
                                          border_color=ad_border_color, border_width=border_size)
        self.frame_for_ad3.place(relx=0.64, rely=0.655, anchor="n")

        self.button_for_ad_3_image = create_text_image(self.texts["en"]["click_here"], font_size=35, outline_thickness=0)
        self.button_for_ad_3 = ctk.CTkButton(self.frame_for_ad3, image=self.button_for_ad_3_image, text="", border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, fg_color=frame_color, corner_radius=30, command=self.open_link, width=600, height=150)
        self.button_for_ad_3.place(relx=0.5, rely=0.5, anchor="center")


        # Wczytanie zapisanego języka lub ustawienie domyślnego
        self.language = self.load_language() or "en"
        self.set_language(self.language)

        self.load_settings()  # Wczytaj zapisane ustawienia

        self.bind_button_hover_buttons(self.merge_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.run_process_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.save_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.reset_button, all_frames_border_color)
        self.bind_button_hover_buttons(self.button_for_ad_3, all_frames_border_color)

    def Main_Window(self):

        # Wczytanie danych z pliku, jeśli istnieje
        self.data = {}  # Testowe dane
        self.load_data()

        self.hide_all_frames()  # Ukrycie wszystkich innych sekcji  # Ukrycie wszystkich innych sekcji

        self.main_info_frame = ctk.CTkFrame(master=self, width=330, height=460, corner_radius=10, fg_color=frame_color, border_color=info_border_color, border_width=other_frames_border_size)
        self.main_info_frame.place(relx=0.145, rely=0.07, anchor="n")

        # Tworzymy etykietę z instrukcjami i umieszczamy ją po lewej stronie, na środku wysokości okna
        self.main_instructions_label_image = create_text_image(self.texts["en"]["greeting_text"], font_size=14, outline_thickness=0)
        self.main_instructions_label = ctk.CTkLabel(master=self.main_info_frame, image = self.main_instructions_label_image, text="", justify="left", anchor="w", fg_color=None)
        self.main_instructions_label.place(relx=0.48, rely=0.52, anchor="center")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}businessman.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(30, 30))

        self.run_lable_image = ctk.CTkLabel(master=self.main_info_frame, image = paths_image, text="", fg_color=frame_color)
        self.run_lable_image.place(relx=0.27, rely=0.036,anchor="center")
        self.update()

        self.main_info_lable_image = create_text_image(self.texts["en"]["information"], font_size=20, outline_thickness=0)
        self.main_info_lable = ctk.CTkLabel(master=self.main_info_frame, image = self.main_info_lable_image, text="",fg_color=frame_color)
        self.main_info_lable.place(relx=0.515, rely=0.04,anchor="center")

        self.main_update_frame = ctk.CTkFrame(master=self, width=330, height=673, corner_radius=10, fg_color=frame_color, 
                                              border_color=update_color, border_width=border_size)
        self.main_update_frame.place(relx=0.43, rely=0.07, anchor="n")

        self.main_update_lable_image = create_text_image(self.texts["en"]["update"], font_size=14, outline_thickness=0)
        self.main_update_lable1 = ctk.CTkLabel(master=self.main_update_frame, image = self.main_update_lable_image, text="",fg_color=frame_color)
        self.main_update_lable1.place(relx=0.5, rely=0.3,anchor="center")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}update.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(30, 30))

        self.run_lable_image = ctk.CTkLabel(master=self.main_update_frame, image = paths_image, text="", fg_color=frame_color)
        self.run_lable_image.place(relx=0.25, rely=0.025,anchor="center")
        self.update()

        self.main_update_lable_image = create_text_image(self.texts["en"]["update_news"], font_size=20, outline_thickness=0)
        self.main_update_lable = ctk.CTkLabel(master=self.main_update_frame, image = self.main_update_lable_image, text="",fg_color=frame_color)
        self.main_update_lable.place(relx=0.515, rely=0.027,anchor="center")

        self.frame_load_save = ctk.CTkFrame(master=self, width=330, height=200, corner_radius=10, fg_color=frame_color, 
                                            border_color=all_frames_border_color, border_width=border_size)
        self.frame_load_save.place(relx=0.145, rely=0.66, anchor="n")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}rotate.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(30, 30))

        self.run_lable_image_1 = ctk.CTkLabel(master=self.frame_load_save, image = paths_image, text="", fg_color=frame_color)
        self.run_lable_image_1.place(relx=0.33, rely=0.081,anchor="center")
        self.update()

        self.load_save_lable_image = create_text_image(self.texts["en"]["load_save"], font_size=20, outline_thickness=0)
        self.load_save_lable = ctk.CTkLabel(master=self.frame_load_save, image = self.load_save_lable_image, text="",fg_color=frame_color)
        self.load_save_lable.place(relx=0.55, rely=0.075,anchor="center")

        # Dodanie przycisków do ramki
        self.save_button_1_image = create_text_image(self.texts["en"]["save_one"], font_size=14, outline_thickness=0)
        self.save_button_1 = ctk.CTkButton(
            master=self.frame_load_save, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=35, border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size,text="", image = self.save_button_1_image,
            command=self.show_message_1
        )
        self.save_button_1.place(relx=0.5, rely=0.3, anchor="center")

        self.save_button_2_image = create_text_image(self.texts["en"]["save_two"], font_size=14, outline_thickness=0)
        self.save_button_2 = ctk.CTkButton(
            master=self.frame_load_save, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=35, border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, text="", image = self.save_button_2_image,
            command=self.show_message_2
        )
        self.save_button_2.place(relx=0.5, rely=0.55, anchor="center") 

        self.save_button_3_image = create_text_image(self.texts["en"]["save_three"], font_size=14, outline_thickness=0)
        self.save_button_3 = ctk.CTkButton(
            master=self.frame_load_save, fg_color=frame_color, corner_radius=30, width=190, 
                                         height=35, border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, text="", image= self.save_button_3_image,
            command=self.show_message_3
        )
        self.save_button_3.place(relx=0.5, rely=0.8, anchor="center")

        self.statistics_frame = ctk.CTkFrame(master=self, width=496, height=460, corner_radius=10, fg_color=frame_color, 
                                             border_color=all_frames_border_color, border_width=border_size)
        self.statistics_frame.place(relx=0.784, rely=0.07, anchor="n")

        self.wykres_frame = ctk.CTkFrame(master=self.statistics_frame, width=396, height=360, corner_radius=10, fg_color=frame_color, 
                                             border_color=other_frames_border, border_width=1)
        self.wykres_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.update_plot()  # Rysuj wykres

        # Lista danych do wykresu
        self.x = list(range(1, len(self.data) + 1))  # Oś X
        print(f"Początkowe dane: {self.data}")

        # Ścieżka do obrazka
        image_path = rf"{white_icons}stats.png"

        # Załaduj obraz z PIL i zmień jego rozmiar
        image = Image.open(image_path)
        resized_image = image.resize((500, 500))  # Zmień rozmiar na 200x200 pikseli

        # Przekonwertuj obraz na format, który może być wyświetlony w customtkinter
        paths_image = ctk.CTkImage(resized_image, size=(30, 30))

        self.run_lable_image = ctk.CTkLabel(master=self.statistics_frame, image = paths_image, text="", fg_color=frame_color)
        self.run_lable_image.place(relx=0.365, rely=0.04,anchor="center")
        self.update()

        self.statistics_lable_image = create_text_image(self.texts["en"]["statistics"], font_size=20, outline_thickness=0)
        self.statistics_lable = ctk.CTkLabel(master=self.statistics_frame, image = self.statistics_lable_image, text="",fg_color=frame_color)
        self.statistics_lable.place(relx=0.5, rely=0.04,anchor="center")

        self.frame_for_ad4 = ctk.CTkFrame(master=self, width=496, height=200, corner_radius=10, fg_color=frame_color, 
                                          border_color=ad_border_color, border_width=border_size)
        self.frame_for_ad4.place(relx=0.784, rely=0.66, anchor="n")

        # Tworzenie przycisku z grafiką
        self.button_for_ad_4_image = create_text_image(self.texts["en"]["click_here"], font_size=27, outline_thickness=0)
        self.button_for_ad_4 = ctk.CTkButton(self.frame_for_ad4, image=self.button_for_ad_4_image, text="", border_color=all_frames_border_color, 
                                         border_width=other_frames_border_size, fg_color=frame_color, corner_radius=30, command=self.open_link, width=300, height=150)
        self.button_for_ad_4.place(relx=0.5, rely=0.5, anchor="center")

        self.bind_button_hover_buttons(self.save_button_1, all_frames_border_color)
        self.bind_button_hover_buttons(self.save_button_2, all_frames_border_color)
        self.bind_button_hover_buttons(self.save_button_3, all_frames_border_color)
        self.bind_button_hover_buttons(self.button_for_ad_4, all_frames_border_color)

        # Wczytanie zapisanego języka lub ustawienie domyślnego
        self.language = self.load_language() or "en"
        self.set_language(self.language)

        self.load_settings()  # Wczytaj zapisane ustawienia

    def hide_all_frames(self):
     try:
        # Ramki z Main_Window
        self.main_info_frame.place_forget()
        self.main_update_frame.place_forget()
        self.frame_load_save.place_forget()
        self.statistics_frame.place_forget()
        self.frame_for_ad4.place_forget()

        # Ramki z Choose_Files_Here
        self.frame1.place_forget()
        self.frame_numbers.place_forget()
        self.frame_info.place_forget()
        self.frame_files.place_forget()
        self.frame_for_ad1.place_forget()
        self.path_frame.place_forget()
        self.frame_for_corners.place_forget()
        self.frame_format.place_forget()

        # Ramki z Choose_Effects_Here
        self.frame_subtitles.place_forget()
        self.frame_info_effect.place_forget()
        self.frame_background.place_forget()
        self.frame_for_ad2.place_forget()
        self.frame_showcase.place_forget()
        self.frame_for_laber1.place_forget()
        self.frame_for_laber2.place_forget()
        self.frame_corners1.place_forget()
        self.frame_corners2.place_forget()

        # Ramki z Run_Process_Here
        self.frame_run.place_forget()
        self.frame_run_info.place_forget()
        self.frame_terminal.place_forget()
        self.frame_terminal_look.place_forget()
        self.frame_for_ad3.place_forget()

     except AttributeError:
        pass
     
    def toggle_maximize(self):
        if self.is_maximized:
            self.geometry("1200x800")  # Przywróć do domyślnych rozmiarów
            self.center_window()  # Ustaw na środek ekranu
            self.is_maximized = False
        else:
            # Maksymalizuj do pełnego ekranu
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
            self.update_idletasks()  # Uaktualnij zadania, aby wymiary były prawidłowe
            self.center_window()  # Ustaw na środek ekranu
            self.is_maximized = True

    def center_window(self):
        # Obliczanie współrzędnych do wyśrodkowania
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")  # Ustawienie pozycji okna

    def zminimalizuj_okno(self):
        self.overrideredirect(False)  # Wyłącz tymczasowo "overrideredirect", aby minimalizacja zadziałała
        self.iconify()  # Zminimalizuj okno
        print("Window minimized.")

    def combined_for_start_merge(self):
        self.start_merge()
        self.open_link()

    def combined_for_start_process(self):
        self.start_process()
        self.open_link()

    def combined_for_save_settings(self):
        self.save_settings()
        self.open_link()

    def combined_for_reset_settings(self):
        self.reset_settings()
        self.open_link()

    def is_obscured(self, our_window, other_window):
        """Sprawdza, czy inne okno zasłania nasze okno."""
        # Pobierz prostokąty dla obu okien
        our_rect = our_window._rect
        other_rect = other_window._rect

        # Sprawdzenie kolizji prostokątów - czy inne okno nakłada się na nasze
        return (
            other_rect.left < our_rect.right and 
            other_rect.right > our_rect.left and 
            other_rect.top < our_rect.bottom and 
            other_rect.bottom > our_rect.top
        )

    def on_close(self):
        self.destroy()

    def open_link(self):
        import webbrowser
        link = "https://popslowergrocer.com/ia8fyi6g?key=906df76e2c2e70f0ac795aa9c05d642a"  # Podstaw tutaj swój link
        webbrowser.open(link)

# Funkcja do pokazania ramki
    def show_frame(self):
        self.profile_frame.place(relx=0.885, rely=0.07, anchor="n")
        self.profile_frame.lift()
        
        self.bind("<Button-1>", self.hide_frame)

    def show_language_frame(self):
        self.language_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.language_frame.lift()
        self.bind("<Button-1>", self.hide_language_frame)

    def get_config_file_path(self):
        """Zwraca pełną ścieżkę do pliku konfiguracyjnego w AppData."""
        appdata_path = os.getenv("APPDATA")  # Pobiera ścieżkę do folderu AppData
        config_file_path = os.path.join(appdata_path, "config.json")
        
        # Upewnij się, że folder istnieje, jeśli nie, stwórz go
        if not os.path.exists(os.path.dirname(config_file_path)):
            os.makedirs(os.path.dirname(config_file_path))
        
        return config_file_path

    def set_language(self, lang):
        """Ustawia teksty w odpowiednim języku."""
        self.language = lang
        self.save_language(lang)  # Zapisuje wybrany język
        
        # Ustawienie tekstów dla checkboxów
        
        # Ustawienie tekstów dla innych komponentów
        if hasattr(self, 'title_bar') and self.title_bar.winfo_ismapped():
           self.path_to_file_image = create_text_image(self.texts[lang]["choose_files"], font_size=13, outline_thickness=0)
           self.path_to_file.configure(image=self.path_to_file_image)
           self.path_to_effects_image = create_text_image(self.texts[lang]["choose_effects"], font_size=13, outline_thickness=0)
           self.path_to_effects.configure(image=self.path_to_effects_image)
           self.path_to_run_image = create_text_image(self.texts[lang]["run_process"], font_size=13, outline_thickness=0)
           self.path_to_run.configure(image=self.path_to_run_image)
        else:
           print("Przycisk path_to_effects nie jest widoczny.")

        if hasattr(self, 'main_info_frame') and self.main_info_frame.winfo_ismapped():
           self.main_instructions_label_image = create_text_image(self.texts[lang]["greeting_text"], font_size=14, outline_thickness=0)
           self.main_instructions_label.configure(image=self.main_instructions_label_image)
           self.main_info_lable_image = create_text_image(self.texts[lang]["information"], font_size=20, outline_thickness=0)
           self.main_info_lable.configure(image=self.main_info_lable_image)
           self.main_update_lable_image = create_text_image(self.texts[lang]["update_news"], font_size=20, outline_thickness=0)
           self.main_update_lable.configure(image=self.main_update_lable_image)
           self.load_save_lable_image = create_text_image(self.texts[lang]["load_save"], font_size=20, outline_thickness=0)
           self.load_save_lable.configure(image=self.load_save_lable_image)
           self.save_button_1_image = create_text_image(self.texts[lang]["save_one"], font_size=14, outline_thickness=0)
           self.save_button_1.configure(image=self.save_button_1_image)
           self.save_button_2_image = create_text_image(self.texts[lang]["save_two"], font_size=14, outline_thickness=0)
           self.save_button_2.configure(image=self.save_button_2_image)
           self.save_button_3_image = create_text_image(self.texts[lang]["save_three"], font_size=14, outline_thickness=0)
           self.save_button_3.configure(image=self.save_button_3_image)
           self.statistics_lable_image = create_text_image(self.texts[lang]["statistics"], font_size=20, outline_thickness=0)
           self.statistics_lable.configure(image=self.statistics_lable_image)
           self.main_update_lable_image = create_text_image(self.texts[lang]["update"], font_size=14, outline_thickness=0)
           self.main_update_lable1.configure(image=self.main_update_lable_image)
           if lang == "pl":
               self.load_save_lable.place(relx=0.55, rely=0.09,anchor="center") 
               self.run_lable_image_1.place(relx=0.28, rely=0.081,anchor="center") 
               self.main_update_lable1.place(relx=0.5, rely=0.35,anchor="center")
           else:
               self.load_save_lable.place(relx=0.55, rely=0.075,anchor="center")
               self.run_lable_image_1.place(relx=0.33, rely=0.081,anchor="center")
               self.main_update_lable1.place(relx=0.5, rely=0.3,anchor="center")
        else:
           print("Przycisk path_to_effects nie jest widoczny.")

        if hasattr(self, 'frame1') and self.frame1.winfo_ismapped():
            self.files_image = create_text_image(self.texts[lang]["choose_files"], font_size=14, outline_thickness=0)
            self.files_button.configure(image=self.files_image)
            self.font_file_image = create_text_image(self.texts[lang]["choose_font_file"], font_size=14, outline_thickness=0)
            self.font_file_button.configure(image=self.font_file_image)
            self.audio_file_image = create_text_image(self.texts[lang]["choose_audio_file"], font_size=14, outline_thickness=0)
            self.audio_file_button.configure(image=self.audio_file_image)
            self.output_folder_image = create_text_image(self.texts[lang]["choose_output_folder"], font_size=14, outline_thickness=0)
            self.output_folder_button.configure(image=self.output_folder_image)
            self.png_file_button_image = create_text_image(self.texts[lang]["choose_logo"], font_size=14, outline_thickness=0)
            self.png_file_button.configure(image=self.png_file_button_image)
            self.spinbox_clip_image = create_text_image(self.texts[lang]["set_one_clip_duration"], font_size=14, outline_thickness=0)
            self.spinbox_clip_lable.configure(image=self.spinbox_clip_image)
            self.format_image = create_text_image(self.texts[lang]["coming_soon"], font_size=20, outline_thickness=0)
            self.format_lable.configure(image=self.format_image)
            self.needed_image = create_text_image(self.texts[lang]["needed"], font_size=14, outline_thickness=0)
            self.needed_lable.configure(image=self.needed_image)
            self.your_files_image = create_text_image(self.texts[lang]["your_files:"], font_size=14, outline_thickness=0)
            self.your_files_lable.configure(image=self.your_files_image)
            self.clip_duration_checkbox.configure(text=self.texts[lang]["manual_one_clip_duration"])
            self.font_file_checkbox.configure(text=self.texts[lang]["choose_font_file"])
            self.frame1_needed_image = create_text_image(self.texts[lang]["required"], font_size=16, outline_thickness=0)
            self.frame1_needed_lable.configure(image=self.frame1_needed_image)
            self.frame1_optional_image = create_text_image(self.texts[lang]["optional"], font_size=16, outline_thickness=0)
            self.frame1_optional_lable.configure(image=self.frame1_optional_image)
            
            self.numbers_image = create_text_image(self.texts[lang]["amount_of_files"], font_size=20, outline_thickness=0)
            self.numbers_lable.configure(image=self.numbers_image)
            self.info_image = create_text_image(self.texts[lang]["information"], font_size=20, outline_thickness=0)
            self.info_lable.configure(image=self.info_image)
            self.files_image = create_text_image(self.texts[lang]["your_files"], font_size=20, outline_thickness=0)
            self.files_lable.configure(image=self.files_image)
            self.folder_button_image = create_text_image(self.texts[lang]["choose_files"], font_size=20, outline_thickness=0)
            self.folder_lable.configure(image=self.folder_button_image )
            self.files_instructions_label_image = create_text_image(self.texts[lang]["preparation_instructions_text"], font_size=14, outline_thickness=0)
            self.files_instructions_label.configure(image=self.files_instructions_label_image)
            if lang == "pl":
               self.numbers_lable_image.place(relx=0.26, rely=0.11,anchor="center")
            else:
               self.numbers_lable_image.place(relx=0.2, rely=0.11,anchor="center")
        else:
           print("Przycisk path_to_effects nie jest widoczny.")

        if hasattr(self, 'frame_subtitles') and self.frame_subtitles.winfo_ismapped():
            self.effect_instructions_label_image = create_text_image(self.texts[lang]["effect_instructions_text"], font_size=14, outline_thickness=0)
            self.effect_instructions_label.configure(image=self.effect_instructions_label_image)
            self.label_for_font_scale_image = create_text_image(self.texts[lang]["font_size"], font_size=14, outline_thickness=0)
            self.label_for_font_scale.configure(image=self.label_for_font_scale_image)
            self.label_for_number_of_words_image = create_text_image(self.texts[lang]["words_in_one_sentence"], font_size=14, outline_thickness=0)
            self.label_for_number_of_words.configure(image=self.label_for_number_of_words_image)
            self.bloom_checkbox.configure(text=self.texts[lang]["glowing_text"])
            self.label_for_bloom_image = create_text_image(self.texts[lang]["glow_intensity"], font_size=14, outline_thickness=0)
            self.label_for_bloom.configure(image=self.label_for_bloom_image)
            self.use_shadow_checkbox.configure(text=self.texts[lang]["shadow_text"])
            self.label_for_use_shadow_image = create_text_image(self.texts[lang]["shadow_intensity"], font_size=14, outline_thickness=0)
            self.label_for_use_shadow.configure(image=self.label_for_use_shadow_image)
            self.use_color_checkbox.configure(text=self.texts[lang]["special_words"])
            self.should_oscillate_checkbox.configure(text=self.texts[lang]["float_effect"])
            self.info_effect_lable_image = create_text_image(self.texts[lang]["information"], font_size=20, outline_thickness=0)
            self.info_effect_lable.configure(image=self.info_effect_lable_image)
            self.is_random_checkbox.configure(text=self.texts[lang]["random_merge"])
            self.flash_checkbox.configure(text=self.texts[lang]["flash_transition"])
            self.fade_checkbox.configure(text=self.texts[lang]["fade_transition"])
            self.glitch_checkbox.configure(text=self.texts[lang]["glitch_transition"])
            self.showcase_lable_image = create_text_image(self.texts[lang]["coming_soon"], font_size=20, outline_thickness=0)
            self.showcase_lable.configure(image=self.showcase_lable_image)
            self.subtitles_lable_image = create_text_image(self.texts[lang]["subtitles_effects"], font_size=20, outline_thickness=0)
            self.subtitles_lable.configure(image=self.subtitles_lable_image)
            self.background_lable_image = create_text_image(self.texts[lang]["background_effects"], font_size=20, outline_thickness=0)
            self.background_lable.configure(image=self.background_lable_image)
            self.label_for_shadow_offset_image = create_text_image(self.texts[lang]["shadow_offset"], font_size=14, outline_thickness=0)
            self.label_shadow_offset_shadow.configure(image=self.label_for_shadow_offset_image)
            
            self.label_for_flash_image = create_text_image(self.texts[lang]["flash_duration"], font_size=14, outline_thickness=0)
            self.label_for_flash.configure(image=self.label_for_flash_image)
            self.label_for_fade_image = create_text_image(self.texts[lang]["fade_duration"], font_size=14, outline_thickness=0)
            self.label_for_fade.configure(image=self.label_for_fade_image)
            self.label_for_glitch_image = create_text_image(self.texts[lang]["glitch_duration"], font_size=14, outline_thickness=0)
            self.label_for_glitch.configure(image=self.label_for_glitch_image)
            if lang == "pl":
               self.use_color_checkbox.place(relx=0.487, rely=0.5, anchor="e")
               self.should_oscillate_checkbox.place(relx=0.476, rely=0.5, anchor="e")
               self.is_random_checkbox.place(relx=0.21, rely=0.5, anchor="center")
               self.flash_checkbox.place(relx=0.2, rely=0.5, anchor="center")
               self.fade_checkbox.place(relx=0.225, rely=0.5, anchor="center")
               self.glitch_checkbox.place(relx=0.24, rely=0.5, anchor="center")
               self.numbers_lable_image_1.place(relx=0.25, rely=0.43,anchor="center")
               self.numbers_lable_image_2.place(relx=0.2, rely=0.48,anchor="center")
            else:
               self.use_color_checkbox.place(relx=0.425, rely=0.5, anchor="e")
               self.should_oscillate_checkbox.place(relx=0.385, rely=0.5, anchor="e")
               self.is_random_checkbox.place(relx=0.19, rely=0.5, anchor="center")
               self.flash_checkbox.place(relx=0.2, rely=0.5, anchor="center")
               self.fade_checkbox.place(relx=0.2, rely=0.5, anchor="center")
               self.glitch_checkbox.place(relx=0.205, rely=0.5, anchor="center")
               self.numbers_lable_image_1.place(relx=0.19, rely=0.43,anchor="center")
               self.numbers_lable_image_2.place(relx=0.24, rely=0.48,anchor="center")
        else:
           print("Przycisk path_to_effects nie jest widoczny.")

        if hasattr(self, 'frame_run') and self.frame_run.winfo_ismapped():
            self.run_instructions_label_image = create_text_image(self.texts[lang]["run_instructions_text"], font_size=14, outline_thickness=0)
            self.run_instructions_label.configure(image=self.run_instructions_label_image)
            self.run_lable_image = create_text_image(self.texts[lang]["run_process"], font_size=20, outline_thickness=0)
            self.run_lable.configure(image=self.run_lable_image)
            self.button_image = create_text_image(self.texts[lang]["run_phase_one"], font_size=14, outline_thickness=0)
            self.merge_button.configure(image=self.button_image)
            self.run_process_button_image = create_text_image(self.texts[lang]["run_phase_two"], font_size=14, outline_thickness=0)
            self.run_process_button.configure(image=self.run_process_button_image)
            self.save_button_image = create_text_image(self.texts[lang]["save_settings"], font_size=14, outline_thickness=0)
            self.save_button.configure(image=self.save_button_image)
            self.reset_button_image = create_text_image(self.texts[lang]["reset_to_default"], font_size=14, outline_thickness=0)
            self.reset_button.configure(image=self.reset_button_image)
            self.run_info_lable_image = create_text_image(self.texts[lang]["information"], font_size=20, outline_thickness=0)
            self.run_info_lable.configure(image=self.run_info_lable_image)
            self.terminal_lable_image = create_text_image(self.texts[lang]["backgrounds"], font_size=20, outline_thickness=0)
            self.terminal_lable.configure(image=self.terminal_lable_image)
            if lang == "pl":
               self.run_lable_image_1.place(relx=0.2, rely=0.05,anchor="center")
               self.terminal_lable.place(relx=0.48, rely=0.05,anchor="center")
            else:
               self.run_lable_image_1.place(relx=0.24, rely=0.05,anchor="center")
               self.terminal_lable.place(relx=0.53, rely=0.05,anchor="center")
        else:
           print("Przycisk path_to_effects nie jest widoczny.")

    def set_english(self):
        """Ustawia język angielski."""
        self.set_language("en")

    def set_polish(self):
        """Ustawia język polski."""
        self.set_language("pl")

    def save_language(self, lang):
        """Zapisuje wybrany język do pliku konfiguracyjnego w AppData."""
        config_data = {"language": lang}
        with open(self.config_file, "w") as config_file:
            json.dump(config_data, config_file)

    def load_language(self):
        """Wczytuje zapisany język z pliku konfiguracyjnego w AppData."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as config_file:
                config_data = json.load(config_file)
                return config_data.get("language")
        return None
    
    def get_appdata_path(self, filename):
        """Zwraca pełną ścieżkę do pliku w katalogu AppData."""
        appdata_dir = os.getenv('APPDATA')
        if not appdata_dir:
            raise Exception("Nie można znaleźć katalogu AppData.")

        app_folder = os.path.join(appdata_dir, "movAI")
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)
        return os.path.join(app_folder, filename)

    def logout(self):
        """Wylogowuje użytkownika i wraca do ekranu logowania."""
        try:
            # Usuń zapisane dane logowania
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                messagebox.showinfo("Logout", "Wylogowano pomyślnie. Dane logowania zostały usunięte.")
            else:
                messagebox.showinfo("Logout", "Brak zapisanych danych logowania.")

            # Zamknij aktualne okno
            self.destroy()

            # Otwórz nowe okno logowania
            login_window = LoginWindow()
            login_window.mainloop()

        except Exception as e:
            messagebox.showerror("Error", f"Wystąpił błąd podczas wylogowywania: {e}")


# Funkcja do ukrycia ramki
    def hide_frame(self, event):
        self.profile_frame.place_forget()
        self.unbind("<Button-1>")

    def hide_language_frame(self):
        self.language_frame.place_forget()
        self.unbind("<Button-1>")
    
    # Metoda aktualizująca dane
    def update_data(self, audio_duration):
        current_date = datetime.now().date()  # Bieżąca data

        # Dodaj przekazaną długość audio do danych dla wykresu
        if current_date not in self.data:
           self.data[current_date] = 0.0  # Inicjalizuj sumę dla nowej daty
        self.data[current_date] += audio_duration  # Sumuj wartości

        print(f"Dodano czas trwania pliku audio: {audio_duration} do dnia: {current_date}, aktualne dane: {self.data}")
    
        # Ogranicz długość danych do ostatnich 7 dni
        self.remove_old_dates()

        self.save_data()  # Zapisz dane do pliku
        self.update_plot()  # Rysuj wykres
        #self.after(5000, self.update_data)  # Wywołaj ponownie po 5 sekundach

    # Metoda zapisywania danych do pliku z sumowaniem wartości
    def save_data(self):
        # Sprawdź, czy istnieje już plik data.json
        app_data_path = os.getenv('APPDATA')  # Możesz zmienić 'my_app' na nazwę swojego projektu
        os.makedirs(app_data_path, exist_ok=True)  # Utwórz folder, jeśli nie istnieje

    # Ścieżka do pliku data.json
        file_path = os.path.join(app_data_path, 'data.json')

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    # Wczytaj istniejące dane
                    existing_data = json.load(f)
                    # Przekształć klucze na obiekty datetime dla porównania dat
                    existing_data = {datetime.fromisoformat(date): values for date, values in existing_data.items()}
                except Exception as e:
                    print(f"Błąd podczas wczytywania danych: {e}")
                    existing_data = {}
        else:
            existing_data = {}

        # Sumowanie wartości dla istniejących dat
        for date, value in self.data.items():
            if date in existing_data:
                existing_data[date] += value  # Sumowanie wartości dla tej samej daty
            else:
                existing_data[date] = value  # Dodaj nową datę, jeśli jej nie ma

        # Zapisz zaktualizowane dane do pliku
        with open(file_path, 'w') as f:
            # Zapisz jako słownik z datami w formacie ISO
            json.dump({date.isoformat(): values for date, values in existing_data.items()}, f)

    # Metoda usuwająca dane starsze niż 7 dni
    def remove_old_dates(self):
        today = datetime.now().date()
        cutoff_date = today - timedelta(days=7)  # Ustal datę graniczną
        # Usuń daty starsze niż 7 dni
        self.data = {date: values for date, values in self.data.items() if date >= cutoff_date}
        print(f"Aktualne dane po usunięciu: {self.data}")

    # Metoda wczytywania danych z pliku
    def load_data(self):
        app_data_path = os.getenv('APPDATA')  # Możesz zmienić 'my_app' na nazwę swojego projektu
        os.makedirs(app_data_path, exist_ok=True)  # Utwórz folder, jeśli nie istnieje

        # Ścieżka do pliku data.json
        file_path = os.path.join(app_data_path, 'data.json')

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    self.data = json.load(f)
                    # Przekształć daty z powrotem w obiekty datetime
                    self.data = {datetime.fromisoformat(date).date(): values for date, values in self.data.items()}
                except Exception as e:
                    print(f"Błąd podczas wczytywania danych: {e}")
                    self.data = {}  # Jeśli wystąpił błąd, zresetuj dane 
                    
    def calculate_audio_data(self):
        audio_file = self.get_first_audio_file(self.selected_audio_folder_path)
        # Odczytaj pierwszy plik audio
        if audio_file and audio_file != self.last_audio_file:
           self.last_audio_file = audio_file  # Zaktualizuj ostatni plik
           self.audio_data_transferred = False  # Zresetuj flagę, aby przetworzyć nowy plik
           
        if audio_file:
            # Odczytaj długość pliku audio
            duration = self.get_audio_duration(audio_file)
            if duration:
                # Pomnóż przez 1.1
                modified_duration = duration * 1.1

                self.update_data(audio_duration=modified_duration)
           
    def calculate_audio_length(self):
        self.calculate_audio_data()

    # Metoda rysująca wykres
    def update_plot(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        # Rysowanie wykresu
        fig, ax = plt.subplots(figsize=(4.1, 3.79), facecolor=frame_color)
        ax.set_facecolor(frame_color)  # Pobieranie bieżącej osi

        # Rysowanie wykresu dla każdego dnia
        all_dates = []
        all_values = []

        for i in range(7):
            date = (datetime.now().date() - timedelta(days=i))
            all_dates.append(date)

            if date in self.data:
                # Jeśli istnieją dane dla tej daty, dodaj wszystkie wartości
                all_values.append(self.data[date])
            else:
                all_values.append(0)  # Brak danych dla tej daty

        # Filtruj tylko pierwsze 7 wartości, aby nie było przekroczenia
        all_values = all_values[:7]

        # Rysowanie wykresu dla każdego dnia
        
        # Rysowanie wykresu słupkowego
        ax.bar(all_dates, all_values, color=info_border_color)

        # Ustawienie koloru obramowania wykresu
        for spine in ax.spines.values():
            spine.set_edgecolor(text_color)  # Ustaw kolor obramowania, np. na czerwony
            spine.set_linewidth(1)      # Opcjonalnie ustaw grubość obramowania

        # Ustawienie koloru liczb na osi X i Y
        ax.tick_params(axis='x', colors=text_color)  # Kolor liczb na osi X, np. zielony
        ax.tick_params(axis='y', colors=text_color)  # Kolor liczb na osi Y, np. zielony

         # Dodawanie adnotacji do słupków
        for date, value in zip(all_dates, all_values):
            ax.text(date, value, f'{value:.2f}s', ha='center', va='bottom', fontsize=8, color=text_color)


         # Umożliwienie wyświetlania etykiet dla ostatnich 7 dni
        ax.set_xticks(all_dates)  # Ustawianie znaczników na osi X
        ax.set_xticklabels([date.strftime('%m-%d') for date in all_dates], fontsize=8)

        # Dodawanie tytułu i etykiet
        #ax.set_title('Line Chart with Annotations', color='white')
        #ax.set_xlabel('X-axis Label', color='white')
        #ax.set_ylabel('Y-axis Label', color='white')
    
        # Wyświetlanie siatki w kolorze białym
        ax.grid(False)

        # Umożliwienie osadzenia wykresu w tkinter
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()  # Zniszcz poprzedni widget canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self.wykres_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Metoda do przeciągania okna
    def start_move(self, event):
        self.prev_x = event.x
        self.prev_y = event.y

    def on_drag(self, event):
        x = self.winfo_x() - self.prev_x + event.x
        y = self.winfo_y() - self.prev_y + event.y
        self.geometry(f"+{x}+{y}")

    def bind_button_hover(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty
      clicked = {"is_clicked": False}

      button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))  # Zmien kolor na określony i dodaj białą obwódkę
      button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color))  # Przywróć kolor i usuń obwódkę
      button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color))  # Kolor i obwódka po kliknięciu
      button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color=fg_color))  # Przywróć kolor i usuń obwódkę po puszczeniu

    def bind_button_hover_buttons(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty

      button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))  # Zmien kolor na określony i dodaj białą obwódkę
      button.bind("<Leave>", lambda e: button.configure(fg_color=frame_color))  # Przywróć kolor i usuń obwódkę
      button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color))  # Kolor i obwódka po kliknięciu
      button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color=frame_color))  # Przywróć kolor i usuń obwódkę po puszczeniu

    def bind_button_hover_checkbox(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty
      clicked = {"is_clicked": False}

      button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color))  # Zmien kolor na określony i dodaj białą obwódkę
      button.bind("<Leave>", lambda e: button.configure(fg_color=info_border_color))  # Przywróć kolor i usuń obwódkę
      button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color))  # Kolor i obwódka po kliknięciu
      button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color=info_border_color))  # Przywróć kolor i usuń obwódkę po puszczeniu

    def bind_button_hover_with_border(self, button, hover_color):
      # Zmienna, która śledzi, czy przycisk został kliknięty
       clicked = {"is_clicked": False}

       button.bind("<Enter>", lambda e: button.configure(fg_color=hover_color, border_color=info_border_color, border_width=other_frames_border_size))  # Zmien kolor na określony i dodaj białą obwódkę
       button.bind("<Leave>", lambda e: button.configure(fg_color=fg_color, border_width=0))  # Przywróć kolor i usuń obwódkę
       button.bind("<Button-1>", lambda e: button.configure(fg_color=hover_color, border_color=info_border_color, border_width=other_frames_border_size))  # Kolor i obwódka po kliknięciu
       button.bind("<ButtonRelease-1>", lambda e: button.configure(fg_color=fg_color, border_width=0))  # Przywróć kolor i usuń obwódkę po puszczeniu

    def przywroc_okno(self, event=None):
        if self.state() == "normal":  # Sprawdź, czy okno zostało przywrócone
            self.after(0, lambda: self.overrideredirect(True))  # Przywróć "overrideredirect" po minimalnym opóźnieniu

    def animate_processing_text(self):
        self.processing = True
        stages = ["PROCESSING", "PROCESSING.", "PROCESSING..", "PROCESSING..."]
        index = 0
        while self.processing:
            text_image = create_text_image(stages[index], font_size=14, outline_thickness=0)
            self.processing_label.configure(image=text_image)
            self.update_idletasks()
            time.sleep(0.5)  # Szybkość zmiany kropki
            index = (index + 1) % len(stages)
    
    def show_process_done(self):
        # Pokazanie napisu "PROCESS DONE" na 2 sekundy
        done_image = create_text_image("PROCESS DONE :D", font_size=14, outline_thickness=0)
        self.processing_label.configure(image=done_image)
        self.update_idletasks()
        time.sleep(3)
        self.processing_label.configure(image="")  # Wyczyść napis po 2 sekundach

     # Funkcja licząca słowa w pliku
      
    # Funkcje wyświetlające komunikat dla przycisków
    def show_message_1(self):
        self.suspend_visibility_check = True
        messagebox.showinfo("Information", "Coming Soon...")
        self.suspend_visibility_check = False
        self.check_visibility()

    def show_message_2(self):
        self.suspend_visibility_check = True
        messagebox.showinfo("Information", "Coming Soon...")
        self.suspend_visibility_check = False
        self.check_visibility()

    def show_message_3(self):
        self.suspend_visibility_check = True
        messagebox.showinfo("Information", "Coming Soon...")
        self.suspend_visibility_check = False
        self.check_visibility()
    
# DEF DLA Choose_Files_Here ⬇
    
    def select_output_folder(self):
        self.suspend_visibility_check = True
        folder_selected = filedialog.askdirectory()
        self.suspend_visibility_check = False
        #self.check_visibility()
        if folder_selected:
            self.output_folder = folder_selected
            self.output_folder_path = folder_selected
            print("Wybrano folder wyjściowy:", folder_selected)
        else:
            messagebox.showerror("Błąd", "Proszę wybrać folder wyjściowy.")
            self.output_folder = None
       # self.save_settings()

    def checkbox_event_duration(self):
        if self.clip_duration_check_var.get() == "on":
            self.clip_duration_checkbox.place_forget()
            self.spinbox_clip_lable.place(relx=0.5, rely=0.25,anchor="center")
            self.clip_duration.place(relx=0.5, rely=0.68, anchor="center")
            self.on_clip_duration_checkbox_on.place(relx=0.2, rely=0.5, anchor="center")
            
        else:
            self.spinbox_clip_lable.place_forget()
            self.clip_duration.place_forget()
            self.on_clip_duration_checkbox_on.place_forget()
            self.clip_duration_checkbox.place(relx=0.5, rely=0.5, anchor="center")
            self.clip_duration.set(0)

    def checkbox_event_font_file(self):
        if self.use_font_path.get() == True:
            self.font_file_checkbox.place_forget()
            self.font_file_checkbox_on.place(relx=0.21, rely=0.73, anchor="center")
            self.font_file_button.place(relx=0.5, rely=0.73, anchor="center")
        else:
            self.font_file_checkbox_on.place_forget()
            self.font_file_button.place_forget()
            self.font_file_checkbox.place(relx=0.5, rely=0.73, anchor="center")
            
    def get_mp4_files(self, folder_path):
        return [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]

    def select_folder(self):
        self.use_one_file = False
        self.suspend_visibility_check = True
        folder_selected = filedialog.askopenfilenames()
        self.suspend_visibility_check = False
       # self.check_visibility()

        if folder_selected:
            # Filtrujemy pliki MP4 i MOV
            mp4_files = [file for file in folder_selected if os.path.splitext(file)[1].lower() == '.mp4']
            mov_files = [file for file in folder_selected if os.path.splitext(file)[1].lower() == '.mov']

            # Łączymy listy MP4 i MOV
            all_video_files = mp4_files + mov_files

            if all_video_files:
                self.selected_folder = folder_selected
                self.selected_folder_path = folder_selected
                self.selected_mp4_files = all_video_files  # Teraz ta lista zawiera zarówno MP4, jak i MOV
                self.display_files(all_video_files)  
                print("Wybrano folder:", folder_selected)
                print("Pliki MP4 i MOV w wybranym folderze:")
                for file in all_video_files:
                    print(file)
                # Automatyczne obliczenie i wyświetlenie wyniku
                self.calculate_audio_length()
            else:
                messagebox.showerror("Błąd", "Wybrany folder nie zawiera plików MP4 ani MOV.")
                print("Wybrany folder nie zawiera plików MP4 ani MOV.")
                self.selected_folder = None
                self.selected_mp4_files = []  # Wyczyść listę, jeśli folder nie zawiera plików MP4 ani MOV
       # self.save_settings()

    def select_audio_folder(self):
        self.suspend_visibility_check = True
        folder_selected = filedialog.askdirectory()
        self.suspend_visibility_check = False
       # self.check_visibility()
        if folder_selected:
            self.selected_audio_folder = folder_selected
            self.selected_audio_folder_path = folder_selected
            print("Wybrano folder z plikiem audio:", folder_selected)
       # self.save_settings()

            # Automatyczne obliczenie i wyświetlenie wyniku
            self.calculate_audio_length()

    def get_audio_duration(self, file_path):
        from pydub import AudioSegment
        try:
            print(f"Próba odczytu długości pliku audio: {file_path}")
            audio = AudioSegment.from_file(file_path)
            return audio.duration_seconds
        except Exception as e:
            print(f"Nie udało się odczytać długości pliku audio {file_path}: {e}")
            return None
    
    def get_first_audio_file(self, folder_path):
        try:
            folder_path = os.path.abspath(folder_path)
            print(f"Przeszukiwanie folderu: {folder_path}")
            for file in os.listdir(folder_path):
                if file.endswith(('.mp3', '.wav', '.m4a')):  # Możesz dodać inne rozszerzenia
                    return os.path.join(folder_path, file)
        except Exception as e:
            print(f"Nie udało się odczytać plików z folderu {folder_path}: {e}")
        return None

    def get_video_duration(self, video_file):
        from moviepy.editor import VideoFileClip
        
        # Użycie VideoFileClip do uzyskania długości pliku wideo
        try:
            with VideoFileClip(video_file) as video:
                return video.duration  # Długość w sekundach
        except Exception as e:
            self._update_label(f"Błąd przy odczycie długości wideo: {e}")
            return 0  # Zwraca 0 w przypadku błędu

    def _update_label(self, text):
        """Metoda pomocnicza do aktualizacji tekstu etykiety."""
        if self.lable_show_numbers:
            self.lable_show_numbers.configure(text=text, text_color = text_color)

    def select_font_path(self):
     self.suspend_visibility_check = True
     self.font_path = filedialog.askopenfilename(filetypes=[("Pliki czcionek", "*.ttf;*.otf")])
     self.suspend_visibility_check = False
    # self.check_visibility()
     if self.font_path:
        print(f"Wybrano ścieżkę do czcionki: {self.font_path}")

    def display_files(self, files):
        from mutagen import File as MutagenFile
        """Wyświetla listę plików audio/wideo w widżecie listbox."""
        # Sprawdzenie, czy listbox jest zainicjalizowany
        if not self.file_listbox:
            raise ValueError("Listbox nie został zainicjalizowany!")

        # Czyszczenie zawartości listboxa
        self.file_listbox.delete("1.0", "end")

        # Iteracja po plikach i wyświetlanie informacji
        for file in files:
            try:
                if os.path.isfile(file):  # Sprawdzenie, czy plik istnieje
                    # Próba odczytu jako plik audio
                    try:
                        audio = MutagenFile(file)
                        if audio is not None and hasattr(audio.info, 'length'):
                            length = audio.info.length  # Długość pliku audio w sekundach
                            self.file_listbox.insert("end", f"{file} - {length:.2f} s (Audio)\n")
                            continue  # Przechodzimy do kolejnego pliku
                    except Exception as audio_error:
                        # Ignorujemy, jeśli plik nie jest audio
                        pass

                    # Próba odczytu jako plik wideo
                    try:
                        from moviepy.editor import VideoFileClip
                        with VideoFileClip(file) as video:
                            length = video.duration  # Długość pliku wideo w sekundach
                            self.file_listbox.insert("end", f"{file} - {length:.2f} s (Video)\n")
                    except Exception as video_error:
                        # Wyświetlenie błędu dla pliku wideo
                        self.file_listbox.insert("end", f"{file} - Błąd wideo: {str(video_error)}\n")
                else:
                    # Wyświetlenie błędu dla nieistniejącego pliku
                    self.file_listbox.insert("end", f"{file} - plik nie istnieje\n")
            except Exception as e:
                # Ogólny błąd dla pliku
                self.file_listbox.insert("end", f"{file} - Błąd: {str(e)}\n")
  
    def select_png_file(self):
        self.suspend_visibility_check = True
        file_selected = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        self.suspend_visibility_check = False
       # self.check_visibility()
        if file_selected:
            self.selected_png_file = file_selected
            self.selected_png_file_path = file_selected
            print("Wybrano plik PNG:", file_selected)
        self.save_settings()

    # DEF DLA Choose_Effects_Here ⬇

    def checkbox_event2(self):
        if self.flash_check_var.get() == "1":
            self.label_for_flash.place(relx=0.7, rely=0.2, anchor="center")
            self.flash_duration.place(relx=0.7, rely=0.6, anchor="center")
            self.use_flash_transition = True
        else:
            self.flash_duration.place_forget()
            self.label_for_flash.place_forget()
            self.use_flash_transition = False

        if self.fade_check_var.get() == "1":
            self.label_for_fade.place(relx=0.7, rely=0.2, anchor="center")
            self.fade_duration.place(relx=0.7, rely=0.6, anchor="center")
            self.use_fade_transition = True
        else:
            self.fade_duration.place_forget()
            self.label_for_fade.place_forget()
            self.use_fade_transition = False

        if self.glitch_check_var.get() == "1":
            self.label_for_glitch.place(relx=0.7, rely=0.2, anchor="center")
            self.glitch_duration.place(relx=0.7, rely=0.6, anchor="center")
            self.use_glitch_transition = True
        else:
            self.glitch_duration.place_forget()
            self.label_for_glitch.place_forget()
            self.use_glitch_transition = False

        if self.bloom_check_var.get() == True: 
            self.label_for_bloom.place(relx=0.7, rely=0.2, anchor="center")
            self.blur_radius.place(relx=0.7, rely=0.6, anchor="center")
            self.bloom = True
        else:
            self.bloom = False
            self.label_for_bloom.place_forget()
            self.blur_radius.place_forget()

        if self.use_shadow_check_var.get() == True: 
            self.shadow_radius.place(relx=0.7, rely=0.4, anchor="center")
            self.label_for_use_shadow.place(relx=0.7, rely=0.1, anchor="center")
            self.label_shadow_offset_shadow.place(relx=0.23, rely=0.85, anchor="center")
            self.shadow_offset.place(relx=0.7, rely=0.83, anchor="center")
            self.use_shadow = True
        else:
            self.shadow_radius.place_forget()
            self.label_for_use_shadow.place_forget()
            self.shadow_offset.place_forget()
            self.label_shadow_offset_shadow.place_forget()
            self.use_shadow = False

        if self.use_color_check_var.get() == True: 
            self.use_color = True
        else:
            self.use_color = False

        if self.should_oscillate_check_var.get() == True:
            self.should_oscillate = True
        else:
            self.should_oscillate = False

        if self.is_random_var.get() == True:
            self.is_random = True
        else:
            self.is_random = False

    # DEF DLA Run_Process_Here ⬇

    def start_merge(self):
        # Tworzymy nowy wątek do uruchomienia procesu
        process_thread = threading.Thread(target=self.merge_videos)
        threading.Thread(target=self.animate_processing_text).start()
        process_thread.start()

    def merge_videos(self):
        if self.selected_folder_path and self.output_folder_path: 
            try:   

                # Tutaj wywołujemy funkcję random_video_merge z odpowiednimi argumentami
                lk.random_video_merge(
                video_files=self.selected_folder_path,
                output_folder=self.output_folder_path,
                audio_folder_path=self.selected_audio_folder_path,
                clip_duration = int(self.clip_duration.get()),
                flash_duration = float(self.flash_duration.get()), 
                fade_duration = float(self.fade_duration.get()), 
                glitch_duration = float(self.glitch_duration.get()),
                use_flash_transition = self.use_flash_transition, 
                use_fade_transition = self.use_fade_transition, 
                use_glitch_transition = self.use_glitch_transition, 
                is_random = self.is_random,
                num_iterations=1,  # Możesz ustawić liczbę iteracji, jeśli chcesz
                )

                # Po zakończeniu procesu
                self.processing = False  # Zatrzymaj animację napisu "PROCESSING"
                self.show_process_done()
                
            except ValueError:
                messagebox.showerror("Błąd", "Proszę podać poprawną wartość liczbową dla czasu trwania.")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się połączyć plików wideo: {e}")
                
            finally:
                self.processing = False  # Zatrzymaj animację napisu "PROCESSING"
                self.processing_label.configure(image="")  # Wyczyść napis
        else:
            messagebox.showerror("Błąd", "Proszę wybrać folder z plikami MP4 oraz folder wyjściowy.")

    def start_process(self):
        # Tworzymy nowy wątek do uruchomienia procesu
        process_thread = threading.Thread(target=self.run_process_videos_with_audio)
        threading.Thread(target=self.animate_processing_text).start()
        process_thread.start()

    def run_process_videos_with_audio(self):
        
        if self.selected_audio_folder_path and self.output_folder_path:
            try:
                print("=== Start of run_process_videos_with_audio ===")
                print("self.output_folder_path:", self.output_folder_path)
                print("self.font_path:", self.font_path)
                print("self.bloom:", self.bloom)
                print("self.use_color:", self.use_color)
                print("self.should_oscillate:", self.should_oscillate)
                print("self.use_shadow:", self.use_shadow)
                print("self.blur_radius:", self.blur_radius)
                print("self.shadow_radius:", self.shadow_radius)
                print("self.number_of_words:", self.number_of_words)
                print("self.font_scale:", self.font_scale)

                # Debugowanie przed wywołaniem tn.process_videos_with_audio
                print("Finalna wartość font_path przed wywołaniem funkcji:", self.font_path)

                # Wywołanie funkcji process_videos_with_audio
                tn.process_videos_with_audio(
                    num_repeats=1,
                    video_folder_path=self.output_folder_path,
                    audio_folder_path=self.selected_audio_folder_path,
                    subtitles_folder_path=self.output_folder_path,
                    transcript_folder_path=self.output_folder_path,
                    logo_path=self.selected_png_file_path,
                    output_folder_path=self.output_folder_path,
                    #images_main_path=self.selected_images_folder_path,  # assuming images are in the video folder
                    font_path=self.font_path,
                    bloom = self.bloom, 
                    use_color=self.use_color,  
                    should_oscillate=self.should_oscillate, 
                    use_shadow = self.use_shadow,
                    shadow_offset = int(self.shadow_offset.get()),
                    #shadow_offset = 3,
                    blur_radius = int(self.blur_radius.get()),
                    shadow_radius = int(self.shadow_radius.get()),
                    number_of_words=int(self.number_of_words.get()),
                    font_scale=int(self.font_scale.get()),
                    use_font_path = self.use_font_path
                )
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas przetwarzania: {e}")
            finally:
                self.processing = False  # Zatrzymaj animację napisu "PROCESSING"
                self.processing_label.configure(image="")  # Wyczyść napis
                print("=== End of run_process_videos_with_audio ===")
        else:
            messagebox.showerror("Błąd", "Proszę wybrać folder z plikami audio, plik PNG oraz folder wyjściowy.")

    def load_settings(self):
        appdata_folder = os.getenv('APPDATA')
        settings_file = os.path.join(appdata_folder, 'settings.json')
        default_transition_time = 0.3
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings = json.load(f)
                
                self.folder_check_var.set(settings.get("folder_check", "off"))
                self.file_check_var.set(settings.get("file_check", "off"))
                self.audio_folder_check_var.set(settings.get("audio_folder_check", "off"))
                self.png_file_check_var.set(settings.get("png_file_check", "off"))
                self.images_folder_check_var.set(settings.get("images_folder_check", "off"))
                self.clip_duration.set(int(settings.get("clip_duration", 1)))
                
                # Odczyt checkboxów
                self.glitch_check_var.set(settings.get("glitch", 0))  # Domyślnie niezaznaczone
                self.flash_check_var.set(settings.get("flash", 0))
                self.fade_check_var.set(settings.get("fade", 0))

                # Odczyt wartości spinboxów
                self.flash_duration.set(float(settings.get("flash_duration", default_transition_time)))
                self.fade_duration.set(float(settings.get("fade_duration", default_transition_time)))
                self.glitch_duration.set(float(settings.get("glitch_duration", default_transition_time)))

                self.is_random_var.set(settings.get("is_random", False))
                self.use_color_check_var.set(settings.get("use_color", False))  # Domyślnie False
                self.bloom_check_var.set(settings.get("bloom", False))
                self.should_oscillate_check_var.set(settings.get("should_oscillate", False))
                self.use_shadow_check_var.set(settings.get("use_shadow", False))
                self.font_scale.set(float(settings.get("font_scale", 20)))
                self.number_of_words.set(int(settings.get("number_of_words", 1)))
                self.shadow_offset.set(int(settings.get("shadow_offset", 5)))
                self.blur_radius.set(float(settings.get("blur_radius", 6)))
                self.shadow_radius.set(float(settings.get("shadow_radius", 3)))
                self.use_font_path.set(settings.get("use_font_file", False))
                
                # Odczyt ścieżek
                self.selected_folder_path = settings.get("selected_folder_path", "")
                self.selected_file_path = settings.get("selected_file_path", "")
                self.selected_audio_folder_path = settings.get("selected_audio_folder_path", "")
                self.selected_png_file_path = settings.get("selected_png_file_path", "")
                self.selected_images_folder_path = settings.get("selected_images_folder_path", "")
                self.output_folder_path = settings.get("output_folder_path", "")
                self.font_path = settings.get("font_path", "")
                # Aktualizacja flag na podstawie ustawień
                self.use_flash_transition = settings.get("use_flash_transition", False)
                self.use_fade_transition = settings.get("use_fade_transition", False)
                self.use_glitch_transition = settings.get("use_glitch_transition", False)
                self.use_color = settings.get("use_color", False)
                self.bloom = settings.get("bloom", False)
                self.should_oscillate = settings.get("should_oscillate", False)
                self.use_shadow = settings.get("use_shadow", False)
                self.is_random = settings.get("is_random", False)

                print("Wczytane ustawienia:", settings)  # Dodaj debugowanie
        else:
         print("Brak pliku settings.json, używam domyślnych ustawień.")  # Dodaj debugowanie

    def save_settings(self):
        settings = {
            "folder_check": self.folder_check_var.get(),
            "file_check": self.file_check_var.get(),
            "audio_folder_check": self.audio_folder_check_var.get(),
            "png_file_check": self.png_file_check_var.get(),
            "images_folder_check": self.images_folder_check_var.get(),
            "clip_duration": self.clip_duration.get(),
            "flash_duration": self.flash_duration.get(),
            "fade_duration": self.fade_duration.get(),
            "glitch_duration": self.glitch_duration.get(),
            "flash":self.flash_check_var.get(),
            "fade":self.fade_check_var.get(),
            "glitch":self.glitch_check_var.get(),
            "is_random":self.is_random_var.get(),
            "use_color":self.use_color_check_var.get(),
            "bloom":self.bloom_check_var.get(),
            "use_shadow": self.use_shadow_check_var.get(),
            "should_oscillate":self.should_oscillate_check_var.get(),
            "font_scale":self.font_scale.get(),
            "number_of_words":self.number_of_words.get(),
            "shadow_offset": self.shadow_offset.get(),
            "blur_radius": self.blur_radius.get(),
            "shadow_radius": self.shadow_radius.get(),
            "use_font_file": self.use_font_path.get(),
            
            # Zapis ścieżek
            "selected_folder_path": self.selected_folder_path,
            "selected_file_path": self.selected_file_path,
            "selected_audio_folder_path": self.selected_audio_folder_path,
            "selected_png_file_path": self.selected_png_file_path,
           # "selected_images_folder_path": self.selected_images_folder_path,
            "output_folder_path": self.output_folder_path,
            "font_path": self.font_path,
            "use_flash_transition": self.use_flash_transition,
            "use_fade_transition": self.use_fade_transition,
            "use_glitch_transition": self.use_glitch_transition,
            "use_color": self.use_color,
            "bloom": self.bloom, 
            "should_oscillate": self.should_oscillate, 
            "is_random": self.is_random,
        }
        appdata_folder = os.getenv('APPDATA')
        settings_file = os.path.join(appdata_folder, 'settings.json')
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        print("Zapisane ustawienia:", settings)

    def reset_settings(self):
        default_transition_time = 0.3
        # Reset variables to their default values
        self.folder_check_var.set("off")
        self.file_check_var.set("off")
        self.audio_folder_check_var.set("off")
        self.png_file_check_var.set("off")
        self.images_folder_check_var.set("off")
        self.clip_duration.set(1)
        self.flash_duration.set(default_transition_time)
        self.fade_duration.set(default_transition_time)
        self.glitch_duration.set(default_transition_time)
        self.flash_check_var.set("0")
        self.fade_check_var.set("0")
        self.glitch_check_var.set("0")
        self.use_flash_transition = False
        self.use_fade_transition = False
        self.use_glitch_transition = False
        self.use_font_path.set(False)
        self.is_random_var.set(False)
        self.use_color_check_var.set(False)
        self.bloom_check_var.set(False)
        self.should_oscillate_check_var.set(False)
        self.is_random = False
        self.use_color = False
        self.bloom = False
        self.should_oscillate = False
        self.use_shadow_check_var.set(False)
        self.font_scale.set(20)
        self.number_of_words.set(1)
        self.shadow_offset.set(5)
        self.blur_radius.set(6)
        self.shadow_radius.set(3)

        # Reset paths to empty
        self.selected_folder_path = ""
        self.selected_file_path = ""
        self.selected_audio_folder_path = ""
        self.selected_png_file_path = ""
        self.selected_images_folder_path = ""
        self.output_folder_path = ""
        self.font_path = ""
        # Ukryj widżety
        self.flash_duration.pack_forget()
        self.fade_duration.pack_forget()
        self.glitch_duration.pack_forget()

        print("Ustawienia zostały zresetowane do wartości domyślnych.")

if __name__ == "__main__":
    #login_window = LoginWindow()
    #login_window.mainloop()
    app_window = App()
    app_window.mainloop()
   