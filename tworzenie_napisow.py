import os
import random
import numpy as np
import math
from typing import Tuple, Dict
import os
from pydub import AudioSegment
from pydub.utils import which


# Ustawienie ścieżki do `ffmpeg`
ffmpeg_path = which("ffmpeg")
if ffmpeg_path is None:
    print("Błąd: `ffmpeg` nie jest dostępny w PATH. Ustaw pełną ścieżkę do `ffmpeg`.")
    AudioSegment.converter = "ffmpeg/ffmpeg.exe"  # Podaj pełną ścieżkę do ffmpeg.exe
else:
    print(f"ffmpeg znaleziono pod ścieżką: {ffmpeg_path}")

# Funkcja do zwracania nazwy pliku z numerem sesji
def get_output_filename(output_folder, base_name):
    session_number = 1
    while True:
        output_filename = os.path.join(output_folder, f"{base_name}_{session_number}_with_audio_with_subtitles.mp4")
        if not os.path.exists(output_filename):
            return output_filename
        session_number += 1

# Funkcja do tworzenia gradientu
def create_gradient_text(txt, font_path, fontsize, gradient_colors, img_size):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    img = Image.new("RGBA", (img_size[0], img_size[1]), (0, 0, 0, 0))  # Powiększamy rozmiar obrazu gradientu
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, fontsize)
    
    # Tworzenie nieregularnego gradientu z losowymi przesunięciami pikseli
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            ratio = x / img.size[0] + (random.random() * 0.1 - 0.05)  # Nieregularność
            r = int(gradient_colors[0][0] * (1 - ratio) + gradient_colors[1][0] * ratio)
            g = int(gradient_colors[0][1] * (1 - ratio) + gradient_colors[1][1] * ratio)
            b = int(gradient_colors[0][2] * (1 - ratio) + gradient_colors[1][2] * ratio)
            draw.point((x, y), fill=(r, g, b, 255))
    
    # Dodanie rozmycia do gradientu
    img = img.filter(ImageFilter.GaussianBlur(radius=0))
    
    text_bbox = draw.textbbox((0, 0), txt, font=font)
    text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
    text_position = ((img.size[0] - text_size[0]) // 2, (img.size[1] - text_size[1]) // 2)
    
    mask = Image.new("L", img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.text(text_position, txt, font=font, fill=255)
    
    gradient_text_img = Image.composite(img, Image.new("RGBA",  img.size, (0, 0, 0, 0)), mask)
    
    return np.array(gradient_text_img)

# Funkcja do konwersji koloru z formatu hex na BGR
def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')  # Usuń znak #
    length = len(hex_color)
    # Zamień HEX na RGB, a następnie przestaw kolejność na BGR
    rgb = tuple(int(hex_color[i:i+length//3], 16) for i in range(0, length, length//3))
    return rgb[::-1]  # Odwróć kolejność kanałów (RGB -> BGR)

# Your provided functions
def glowing_text(image: np.ndarray, text: str, font_path: str,
                 color_map: Dict[str, Tuple[int, int, int]], font_scale: int = 50, blur_radius: int = 0, shadow_radius: int = 0, shadow_offset: int = 0,
                 text_y_offset: int = 0, bloom: bool = True, use_color: bool = True, use_shadow: bool = True, use_font_path: bool = True, detected_language: str = 'en') -> np.ndarray:
    """
    Rysuje tekst z efektem glow na obrazie.
    """
    # Zamiana obrazu OpenCV na format PIL (RGBA)
    import cv2
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    colored_bg = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))

    # Debug: sprawdź, czy `detected_language` jest poprawnie przekazywane
    print(f"Użyty język: {detected_language}")
    
    # Ustawienia fontu - wybór ścieżki na podstawie `use_font_path` oraz `detected_language`
    if use_font_path:
        font = ImageFont.truetype(font_path, font_scale)
    else:
        # Wybór domyślnej ścieżki do czcionki w zależności od języka
        font_path_by_language = {
            'pl': r'movaiassets1\Chunkfive-Ex.ttf',
            'en': r'movaiassets1\LEMONMILK-Bold.otf'
        }
        
        # Wybór ścieżki do czcionki w zależności od wykrytego języka, z domyślnym fontem
        chosen_font_path = font_path_by_language.get(detected_language, 'Arial')
        font = ImageFont.truetype(chosen_font_path, font_scale)

    text_image = Image.new('RGBA', colored_bg.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_image)
    
    # Ustawienie tekstu na środku
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font=font)
    text_x = (text_image.width - text_width) / 2
    text_y = (text_image.height - text_height) / 2 + text_y_offset

    # Split the text into words
    text = text.upper()
    words = text.split()

    # Calculate total width of the text for centering
    total_width = 0
    word_widths = []

    for word in words:
        # Calculate each word's width
        _, _, word_width, word_height = draw.textbbox((0, 0), word, font=font)
        word_widths.append(word_width)
        total_width += word_width

    # Add some space between words (adjustable)
    space_between_words = 15  # Change this value to adjust spacing
    total_width += space_between_words * (len(words) - 1)  # Total width + spaces

    # Calculate starting x position for centering the text
    text_x = (text_image.width - total_width) / 2
    # Use the height of the first word for vertical centering
    _, _, _, text_height = draw.textbbox((0, 0), words[0], font=font)  # Get height of the first word
    text_y = (text_image.height - text_height) / 2 + text_y_offset

    # Nakładanie półprzezroczystych warstw tekstu dla efektu glow
    # Nakładanie półprzezroczystych warstw tekstu dla efektu glow
    if bloom:
        #transparency_values = [230, 80, 70, 60, 50, 40, 30, 20, 10]
        transparency_values = [255, 75, 60, 45, 30, 15]

        for i, alpha in enumerate(transparency_values):
            # Rysowanie każdej warstwy glow
            draw = ImageDraw.Draw(text_image)

            current_x = text_x

            for idx, word in enumerate(words):
                # Get the color for the word from the color_map, or default to white if not found
                word_color = color_map.get(word.upper(), (255, 255, 255))if use_color else (255, 255, 255)
                glow_color = (*word_color, alpha)  # Dodaj przezroczystość do koloru
                
                # Draw the word on the image
                draw.text((current_x, text_y), word, fill=glow_color, font=font, stroke_width=i+1)

                # Move the x position for the next word
                current_x += word_widths[idx] + space_between_words  # Use calculated width + space

            # Apply a subtle blur to the entire text_image after drawing all layers
            blurred_text_image = text_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

           # blurred_text_image = text_image

            # Łączenie bieżącej warstwy glow z obrazem
            colored_bg = Image.alpha_composite(colored_bg, blurred_text_image)

            # Resetowanie text_image do przezroczystości, aby każda nowa warstwa była oddzielna
            text_image = Image.new('RGBA', colored_bg.size, (255, 255, 255, 0))

    # Dodanie cienia, jeśli use_shadow jest włączony
    if use_shadow:
        shadow_offset = shadow_offset  # Offset dla cienia
       # shadow_color = (0, 0, 0, 179)  # Kolor cienia
        shadow_color = (0, 0, 0, 200)
        shadow_image = Image.new('RGBA', colored_bg.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_image)

        # Rysowanie cienia
        current_x = 0
        for word in text.split():
            shadow_draw.text((text_x + current_x + shadow_offset, text_y + shadow_offset), word, fill=shadow_color, font=font)
            current_x += draw.textbbox((0, 0), word, font=font)[2] + 15  # Szerokość słowa + odstęp

        # Zastosowanie rozmycia do cienia
        blurred_shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
        
        # Łączenie cienia z głównym obrazem
        colored_bg = Image.alpha_composite(colored_bg, blurred_shadow_image)

    # Rysowanie wyraźnego tekstu na wierzchu glow
    draw = ImageDraw.Draw(colored_bg)
    current_x = 0

    # Rysowanie wyraźnego tekstu
    for word in text.split():
        word_color = color_map.get(word.upper(), (255, 255, 255)) if use_color else (255, 255, 255)
        draw.text((text_x + current_x, text_y), word, fill=word_color, font=font)
        current_x += draw.textbbox((0, 0), word, font=font)[2] + 15  # Szerokość słowa + odstęp

    # Konwersja końcowego obrazu z powrotem do formatu BGR dla kompatybilności z OpenCV
    final_image = cv2.cvtColor(np.array(colored_bg), cv2.COLOR_RGBA2BGR)

    return final_image

# Helper function to extract time from subtitle entry
def to_milliseconds(time_obj):
    return time_obj.hours * 3600000 + time_obj.minutes * 60000 + time_obj.seconds * 1000 + time_obj.milliseconds

# Function to load color mappings from files
def load_color_map_from_files(lists_files: Tuple[str, str, str], colors: Tuple[str, str, str]) -> Dict[str, Tuple[int, int, int]]:
    color_map = {}
    
    # Load lists and assign colors
    for i, list_file in enumerate(lists_files):
        with open(list_file, 'r') as file:
            words = file.read().strip().split(',')
        color = hex_to_bgr(colors[i])
        for word in words:
            color_map[word.upper()] = color

    return color_map

def add_glowing_subtitles(clip, srt_path, lists_files, colors, font_path, bloom, use_color,  font_scale, use_shadow, shadow_offset,
                           blur_radius, shadow_radius, use_font_path, detected_language, should_oscillate = False): #shadow_offset,
    """
    Dodaje świecące napisy do klipu wideo na podstawie pliku .srt.
    """
    video_fps = clip.fps
    
    # Odczytaj plik .srt z napisami
    import pysrt
    subtitles = pysrt.open(srt_path)
    
    # Załaduj mapę kolorów z plików
    color_map = load_color_map_from_files(lists_files, colors)

    # Sprawdzenie, czy `detected_language` jest pojedynczym stringiem; jeśli nie, ustaw domyślny język.
    if not isinstance(detected_language, str):
        print("Warning: 'detected_language' nie jest tekstem, ustawiono domyślny język 'en'.")
        detected_language = 'en'  # Domyślny język, jeśli `detected_language` nie jest prawidłowy.
    
    # Funkcja przetwarzająca każdą klatkę wideo
    def process_frame(image, t):
        ms_time = int(t * 1000)  # Konwersja czasu na milisekundy
        subtitle_text = ""
        
        # Przeszukaj napisy, aby znaleźć odpowiedni tekst do wyświetlenia
        for sub in subtitles:
            start_ms = to_milliseconds(sub.start)
            end_ms = to_milliseconds(sub.end)
            
            if start_ms <= ms_time <= end_ms:
                subtitle_text = sub.text
                break
        
        if subtitle_text:
            # Parametry oscylacji (efekt pulsującego tekstu)
            oscillation_amplitude = 30  # Amplituda oscylacji
            oscillation_frequency = 0.4  # Częstotliwość oscylacji (w Hz)
            
            if should_oscillate:  # Sprawdza, czy oscylacja jest włączona
               vertical_offset = int(oscillation_amplitude * math.sin(2 * math.pi * oscillation_frequency * t))
            else:
               vertical_offset = 0  # Nie dodawaj przesunięcia, gdy oscylacja jest wyłączona
            
            # Nałóż świecący tekst na aktualną klatkę
            image = glowing_text(
                image.copy(), 
                subtitle_text, 
                font_path, 
                color_map, 
                font_scale=font_scale, 
                text_y_offset=vertical_offset,
                bloom=bloom,           # Przekazanie parametru 'bloom'
                use_color=use_color,   # Przekazanie parametru 'use_color'
                use_shadow = use_shadow,
                shadow_offset = shadow_offset,
                blur_radius = blur_radius,
                shadow_radius = shadow_radius,
                use_font_path = use_font_path,
                detected_language = detected_language
                )
        
        return image
    
    # Zastosuj napisy do każdej klatki wideo
    new_clip_with_subtitles = clip.fl(lambda gf, t: process_frame(gf(t), t))
    
    return new_clip_with_subtitles

# Funkcja do zapisu transkrypcji jako plik SRT, dzielona na grupy słów i obsługująca myślniki
def write_srt_by_word_groups(result, output_srt_path, number_of_words):
    segments = result['segments']  # Zawiera segmenty transkrypcji wraz z czasami
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        idx = 1

        # Iterujemy przez segmenty i dzielimy je na grupy słów z czasami
        for segment in segments:
            if 'words' in segment:  # Sprawdzamy, czy segment zawiera podział na słowa
                words = segment['words']  # Zawiera podział na słowa i ich czasy
                merged_words = merge_words_with_hyphens(words)  # Łączenie słów z myślnikami
                groups = podziel_na_grupy_slow_z_czasami(merged_words, number_of_words)

                # Zapisujemy każdą grupę słów do pliku SRT
                for text, start_time, end_time in groups:
                    f.write(f"{idx}\n")
                    idx += 1
                    start_time_srt = format_time(start_time * 1000)  # Zmieniamy na milisekundy
                    end_time_srt = format_time(end_time * 1000)
                    f.write(f"{start_time_srt} --> {end_time_srt}\n")
                    f.write(f"{text.strip()}\n\n")

# Funkcja do łączenia słów z myślnikami
def merge_words_with_hyphens(words):
    merged_words = []
    previous_word_info = None

    for word_info in words:
        word = word_info['word'].strip()

        # Łączenie słów, które są rozdzielone na części (np. "slowo", "-slow")
        if word.startswith('-') and previous_word_info:
            # Połącz bieżące słowo z poprzednim
            previous_word_info['word'] += word
            previous_word_info['end'] = word_info['end']  # Aktualizujemy czas zakończenia
        else:
            if previous_word_info:
                merged_words.append(previous_word_info)
            previous_word_info = word_info

    # Dodanie ostatniego słowa
    if previous_word_info:
        merged_words.append(previous_word_info)

    return merged_words

# Funkcja do podziału słów na grupy z czasami
def podziel_na_grupy_slow_z_czasami(words, number_of_words):
    paired_words_with_times = []
    i = 0

    while i < len(words):
        start_time = words[i]['start']  # Zaczynamy od czasu pierwszego słowa w grupie
        text = []
        end_time = words[i]['end']  # Domyślnie ustawiamy na czas końca bieżącego słowa

        # Łączymy słowa do określonej liczby
        for j in range(number_of_words):
            if i < len(words):
                text.append(words[i]['word'].strip().replace('.', ''))  # Dodajemy słowa do listy, usuwając nadmiarowe spacje
                end_time = words[i]['end']  # Aktualizujemy czas zakończenia na czas ostatniego słowa w grupie
                i += 1
            else:
                break  # Zatrzymujemy, jeśli nie ma więcej słów

        # Używamy " ".join do połączenia słów i usuwamy nadmiarowe spacje
        paired_words_with_times.append((" ".join(text).replace("  ", " "), start_time, end_time))  # Usuwamy podwójne spacje

    return paired_words_with_times

# Funkcja do formatowania czasu (sekundy zamienione na milisekundy)
def format_time(ms):
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"

# Funkcja do zapisu transkrypcji jako plik TXT
def write_text_file(result, output_txt_path):
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for segment in result['segments']:
            # Łączymy tekst z segmentów, usuwając kropki
            text = segment['text'].replace('.', '').strip()  # Usuwamy kropki i nadmiarowe spacje
            f.write(f"{text} ")  # Dodajemy tekst z segmentu do pliku

def load_srt(srt_file):
    import re
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    subtitles = []
    for match in pattern.finditer(content):
        idx = int(match.group(1))
        start_time = match.group(2).replace(',', '.')
        end_time = match.group(3).replace(',', '.')
        text = match.group(4).replace('\n', ' ')
        subtitles.append({
            'index': idx,
            'start': start_time,
            'end': end_time,
            'text': text
        })
    return subtitles

def srt_time_to_seconds(srt_time):
    h, m, s = srt_time.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def slide_in_and_out_with_resize_and_rotate(clip, side_in, side_out, start_scale, rotation_angle, final_position = (220, 300), final_height=None, in_duration = 0.3, out_duration = 0.3, wobble_amplitude=20, wobble_frequency=1):
    """
    Połączony efekt slide-in (na początek) i slide-out (na koniec) z jednoczesną zmianą rozmiaru oraz obracaniem.
    Podczas wyjścia (slide-out) klip będzie powiększał się i powoli obracał.
    """

    w, h = clip.size
    clip_duration = clip.duration  # Całkowity czas trwania klipu

    def get_numeric_position(position, axis_size):
        if isinstance(position, str) and position == 'center':
           return axis_size // 2  # Zwróć środek osi
        elif isinstance(position, (int, float)):
           return position  # Jeśli to liczba, zwróć ją bez zmian
        else:
           raise ValueError("Pozycja musi być liczbą lub 'center'")

    # Funkcja pozycjonowania dla slide-in
    def position_in(t):
        progress = min(1, t / in_duration)  # Postęp w czasie animacji slide-in

        if side_in == 'left':
            x = int(-w + (progress * w))
            return (x, final_position[1])
        elif side_in == 'right':
            x = int(w - (progress * w))
            return (x, final_position[1])
        elif side_in == 'top':
            x = final_position[0]
            y = int(-h + (progress * h))
            return (x, y)
        elif side_in == 'bottom':
            x = final_position[0]
            y = int(h - (progress * h))
            return (x, y)
        else:
            return final_position

    # Funkcja pozycjonowania dla slide-out
    def position_out(t):
        if t < (clip_duration - out_duration):
            return final_position
        else:
            progress = min(1, (t - (clip_duration - out_duration)) / out_duration)

            if side_out == 'left':
                x = final_position[0] - int(progress * w)
                return (x, final_position[1])
            elif side_out == 'right':
                x = final_position[0] + int(progress * w)
                return (x, final_position[1])
            elif side_out == 'top':
                y = final_position[1] - int(progress * h)
                return (final_position[0], y)
            elif side_out == 'bottom':
                y = final_position[1] + int(progress * h)
                return (final_position[0], y)
            else:
                return final_position

     # Funkcja dodająca efekt lekkiego poruszania się
    def wobble(t):
        """Dodaje efekt lekkiego poruszania się klipu podczas bycia w centrum."""
        if in_duration < t < (clip_duration - out_duration):  # Efekt wobble działa w środku klipu
            # Obliczanie delikatnego przesunięcia sinusoidalnego
            wobble_x = wobble_amplitude * math.sin(2 * math.pi * wobble_frequency * t)
            wobble_y = wobble_amplitude * math.sin(2 * math.pi * wobble_frequency * t + math.pi / 2)
            x = get_numeric_position(final_position[0], w)
            y = get_numeric_position(final_position[1], h)
            return (x + wobble_x, y + wobble_y)
        else:
            return (get_numeric_position(final_position[0], w), get_numeric_position(final_position[1], h))

    # Łączymy pozycjonowanie dla całego klipu z efektem wobble
    def combined_position(t):
        if t <= in_duration:
            return position_in(t)  # Używamy pozycji slide-in
        elif t >= (clip_duration - out_duration):
            return position_out(t)  # Używamy pozycji slide-out
        else:
            return wobble(t)  # Efekt wobble w środku

    # Rozmiar dla slide-in i slide-out
    start_height = 10  # Startowy rozmiar przy slide-in
    final_height = final_height if final_height else h  # Finalna wysokość po slide-in
    out_start_height = final_height  # Rozmiar na początku wyjścia (slide-out)
    out_final_height = int(final_height * start_scale)  # Rozmiar na końcu wyjścia (powiększenie)

    def resizing(t):
        if t <= in_duration:
            progress = min(1, t / in_duration)
            return start_height + (progress * (final_height - start_height))  # Powiększanie w trakcie slide-in
        elif t >= (clip_duration - out_duration):
            progress = min(1, (t - (clip_duration - out_duration)) / out_duration)
            #WYSTARCZY ZMIENIC + NA - ZEBY SIE ZMIENJSZALO I NA ODWROT 
            return out_start_height - (progress * (out_final_height - out_start_height))  # Powiększanie w trakcie slide-out
        else:
            return final_height  # Utrzymanie finalnej wysokości w środku klipu

    # Obrót klipu w czasie
    def rotation(t):
        if t >= (clip_duration - out_duration):
            progress = min(1, (t - (clip_duration - out_duration)) / out_duration)
            return rotation_angle * progress  # Obrót stopniowy, rosnący do podanego kąta
        return 0  # Brak obrotu podczas slide-in

    # Ustawienie pozycji, rozmiaru i obrotu klipu
    clip = clip.set_position(combined_position, relative=False)  # Użyj relative=False, aby ustawić absolutną pozycję
    clip = clip.set_duration(clip_duration)
    clip = clip.resize(height=resizing)
    clip = clip.rotate(lambda t: rotation(t))  # Obrót klipu

    return clip

def download_icons(output_folder_path):
    import requests
    # Parametry
    url = "https://api.freepik.com/v1/icons"

    path_to_txt_file = output_folder_path +'\\neutral_positive_words.txt'

    with open(path_to_txt_file, 'r', encoding='utf-8') as plik:
        all_special_words = plik.read().strip().split(',')

    # Lista kolorów do losowania
    colors = ["gradient", "solid-black", "multicolor", "azure", "black", "blue", "chartreuse", "cyan", 
              "gray", "green", "orange", "red", "rose", "spring-green", "violet", "white", "yellow"]

    # Parametry do wyszukiwania ikonek
    language_search = 'en-US'  # język
    ico_shape = "fill"  # fill, lineal-color, hand-drawn

    # API KEY
    API_KEY = 'FPSX3a7f9fecb8514c5c9a7d8f53aa2813df'

    headers = {
        "x-freepik-api-key": API_KEY,
        "Accept-Language": language_search
    }

    # Tworzenie folderu na emotki
    emojis_folder = os.path.join(output_folder_path, 'emojis')
    os.makedirs(emojis_folder, exist_ok=True)

    # Funkcja do zapisu ikony
    def download_icon(search_term, color, shape, save_path):
        # Ustawienie parametrów wyszukiwania
        querystring = {
            "term": search_term,
            "page": "1",
            "per_page": "1",
            "filters[color]": color,
            "filters[shape]": shape,
            "filters[free_svg]": "all",
            "filters[period]": "all", 
            "thumbnail_size": "512"
        }

        # Wykonanie zapytania
        response = requests.get(url, headers=headers, params=querystring)

        # Sprawdzenie statusu odpowiedzi
        if response.status_code == 200:
            data = response.json()

            # Sprawdzenie, czy istnieją dane
            if data['data']:
                # Wyodrębnienie URL miniaturki
                thumbnail_url = data['data'][0]['thumbnails'][0]['url']

                # Pobranie obrazu
                img_response = requests.get(thumbnail_url)

                if img_response.status_code == 200:
                    # Zapis obrazu
                    with open(save_path, 'wb') as file:
                        file.write(img_response.content)
                    print(f"Obraz zapisany w: {save_path}")
                else:
                    print(f"Nie udało się pobrać obrazu dla terminu: {search_term}")
            else:
                print(f"Brak wyników dla terminu: {search_term}")
        else:
            print(f"Nie udało się pobrać danych z API dla terminu: {search_term}")

    # Iteracja po wszystkich słowach kluczowych
    for word in all_special_words:
        ico_color = random.choice(colors)
        # Tworzenie dynamicznej ścieżki do zapisu pliku
        out_title = f"{word.replace(' ', '_')}.png"  # Zamieniamy spacje na podkreślenia
        save_path = os.path.join(emojis_folder, out_title)

        # Pobieranie ikony dla danego słowa
        download_icon(word, ico_color, ico_shape, save_path)

def add_images_to_video(video, subtitles, images_main_path, default_image_height=300):
    clips = [video]

    
    # Znajdź wszystkie pliki obrazów w folderze
    image_files = [f for f in os.listdir(images_main_path) if f.endswith('.png')]

    for subtitle in subtitles:
        start = srt_time_to_seconds(subtitle['start'])
        end = srt_time_to_seconds(subtitle['end']) + 0.7  # Dodanie zmiennej 'end'
        duration = end - start

        # Przeszukujemy każde słowo w napisach
        for png_file in image_files:
            word = os.path.splitext(png_file)[0]  # Nazwa pliku bez rozszerzenia .png
            
            # Jeśli słowo z nazwy pliku pojawia się w napisach
            if word.lower() in subtitle['text'].lower():
                image_path = os.path.join(images_main_path, png_file)

                # Tworzenie ImageClip dla dopasowanego pliku PNG
                from moviepy.editor import ImageClip
                img_clip = ImageClip(image_path).set_start(start).set_duration(duration)

                # Wybór losowej strony do efektu 'slide-in'
                options = ["top", "bottom", "left", "right"]
                choice = random.choice(options)

                # Dopasowanie wysokości obrazu
                img_clip = img_clip.resize(height=default_image_height)

                # Pozycja końcowa obrazu na ekranie
                final_position = ('center', 'center')  # Możesz zmieniać na dynamiczne pozycje, jeśli chcesz

                # Ostateczna wysokość obrazu
                final_height = default_image_height


                # Użyj funkcji z ruchem nieskończoności i obrotem:
                img_clip = slide_in_and_out_with_resize_and_rotate(
                img_clip, 
                #final_position = final_position ,  # Finalna pozycja obrazu
                side_in=choice, 
                side_out=choice, 
                final_height=final_height, 
                start_scale=0.1,  # Skala startowa dla slide-out (powiększanie)
                rotation_angle=15,  # Obracanie obrazu o 45 stopni
                )


                if img_clip is not None:
                    print(f'Obraz dodany do listy clips: {img_clip}')
                    clips.append(img_clip)

    print("Tworzę CompositeVideoClip")
    from moviepy.editor import CompositeVideoClip
    composite_clip = CompositeVideoClip(clips, size=video.size)
    print("CompositeVideoClip utworzony")
    return composite_clip

# Wczytywanie dokumentów z pliku .txt
def load_documents_from_file(transcript_folder_path):
    with open(transcript_folder_path + '\\final_transcript.txt', 'r', encoding='utf-8') as file:
        documents = file.readlines()  # Odczytuje każdą linię jako osobny dokument
    return documents

# Funkcja przetwarzająca dokumenty i klasyfikująca słowa
def process_documents(documents):
    import nltk
    nltk.data.path.append('nltk_data')
    from nltk.corpus import opinion_lexicon, stopwords
    # Pobranie listy pozytywnych i negatywnych słów
    positive_words = opinion_lexicon.positive()
    negative_words = opinion_lexicon.negative()

    # Inicjalizacja stop words dla języka angielskiego
   # if lang == ('pl'):
       #stop_words = list(stopwords.words('polish'))
    #else:
       #stop_words = list(stopwords.words('english'))

    stop_words = list(stopwords.words('english'))

    # Inicjalizacja tf-idf z usunięciem stop words
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words=stop_words)

    # Dopasowanie i transformacja dokumentów
    tfidf_matrix = tfidf.fit_transform(documents)

    # Wyciąganie słów i ich wag w modelu tf-idf
    feature_names = tfidf.get_feature_names_out()

    # Podział na pozytywne, negatywne, neutralne i pozostałe
    positive_tfidf = {}
    negative_tfidf = {}
    neutral_tfidf = {}
    verbs_tfidf = {}
    adjectives_tfidf = {}
    other_words_tfidf = {}

    # Definiujemy próg TF-IDF, powyżej którego słowa uznamy za neutralne
    neutral_tfidf_threshold = 0.164  # Możesz dostosować ten próg

    # Przejście przez każdy dokument i klasyfikowanie słów
    for doc_id, doc in enumerate(tfidf_matrix):
        print(f"\nDocument {doc_id + 1}")
        feature_index = doc.nonzero()[1]
        tfidf_scores = zip(feature_index, [doc[0, x] for x in feature_index])
        
        # Wybór wszystkich słów, które są w leksykonach pozytywnych, negatywnych lub neutralnych
        for word_idx, score in tfidf_scores:
            word = feature_names[word_idx]

            # Klasyfikowanie bez powtórzeń
            if word in positive_tfidf or word in negative_tfidf or word in neutral_tfidf or word in verbs_tfidf or word in adjectives_tfidf:
                continue  # Pominięcie słów, które już zostały przypisane

            # Klasyfikowanie słów za pomocą pos_tag (części mowy)
            tokens = nltk.word_tokenize(word)
            pos_tags = nltk.pos_tag(tokens)

            # Sprawdzenie części mowy (czasowniki, przymiotniki)
            for token, tag in pos_tags:
                if token in positive_words:
                    positive_tfidf[token] = score
                elif token in negative_words:
                    negative_tfidf[token] = score
                elif score >= neutral_tfidf_threshold:
                    neutral_tfidf[token] = score
                elif tag.startswith('VB'):  # Czasownik (Verb)
                    verbs_tfidf[token] = score
                elif tag.startswith('JJ'):  # Przymiotnik (Adjective)
                    adjectives_tfidf[token] = score
                else:
                    other_words_tfidf[token] = score

    return positive_tfidf, negative_tfidf, neutral_tfidf, verbs_tfidf, adjectives_tfidf, other_words_tfidf

# Funkcja zapisująca słowa do plików
def save_words_to_file(output_folder_path, filename, words_dict):
    file_path = os.path.join(output_folder_path, filename)
    with open(file_path, 'w') as file:
        words = [word for word in words_dict.keys()]
        file.write(",".join(words))

# Funkcja główna
def specialwords(transcript_folder_path, output_folder_path):
    # Wczytanie dokumentów
    documents = load_documents_from_file(transcript_folder_path)

    # Przetwarzanie dokumentów
    positive_tfidf, negative_tfidf, neutral_tfidf, verbs_tfidf, adjectives_tfidf, other_words_tfidf = process_documents(documents)

    # Tworzenie folderu na zapisane pliki
    os.makedirs(output_folder_path, exist_ok=True)

    # Zapis do plików
    save_words_to_file(output_folder_path, 'neutral_positive_words.txt', {**neutral_tfidf, **positive_tfidf})
    save_words_to_file(output_folder_path, 'negative_words.txt', negative_tfidf)
    save_words_to_file(output_folder_path, 'verbs_adjectives.txt', {**verbs_tfidf, **adjectives_tfidf})

    print("\nFiles have been saved successfully.")

def przytnij_wideo_do_pierwszego_audio(video_path, audio_folder, output_folder, output_name = "merged_video_1.mp4"):
    # Pobierz listę plików w folderze audio i wybierz pierwszy plik audio
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith(('.mp3', '.wav', '.m4a'))]
    
    if not audio_files:
        raise FileNotFoundError("Brak plików audio w folderze!")
    
    # Sortujemy pliki, aby wybrać pierwszy (domyślnie sortowane alfabetycznie)
    first_audio_file = os.path.join(audio_folder, sorted(audio_files)[0])
    
    # Załaduj plik wideo
    from moviepy.editor import VideoFileClip
    video_clip = VideoFileClip(video_path)
    
    # Załaduj pierwszy plik audio
    from moviepy.editor import AudioFileClip
    audio_clip = AudioFileClip(first_audio_file)
    
    # Pobierz długość pliku audio
    audio_duration = audio_clip.duration + 2
    
    # Przytnij wideo do długości pliku audio
    trimmed_video_clip = video_clip.subclip(0, min(video_clip.duration, audio_duration))
    
    # Stwórz ścieżkę wyjściową
    output_path = os.path.join(output_folder, output_name)
    
    # Zapisz przycięte wideo
    trimmed_video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # Zamknij klipy, żeby zwolnić zasoby
    video_clip.close()
    audio_clip.close()

def get_first_audio_file(folder_path):
    try:
        folder_path = os.path.abspath(folder_path)
        print(f"Przeszukiwanie folderu: {folder_path}")
        for file in os.listdir(folder_path):
            if file.endswith(('.mp3', '.wav', '.m4a')):  # Możesz dodać inne rozszerzenia
                return os.path.join(folder_path, file)
    except Exception as e:
        print(f"Nie udało się odczytać plików z folderu {folder_path}: {e}")
    return None

def detect_language_from_text(text):
    from langdetect import detect
    # Wykryj język na podstawie transkrypcji tekstowej
    language = detect(text)
   # print(f"Wykryty język: {language}")
    return language

def transcribe_audio_with_whisper(audio_path, language=None):
    # Załaduj model Whisper
    import whisper
    model = whisper.load_model("model/medium.pt")
    print("Model załadowany pomyślnie.")

    # Sprawdź, czy plik audio istnieje
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Plik audio nie istnieje: {audio_path}")

    print(f"Ścieżka do pliku audio: {audio_path}")
    print("Rozpoczynam transkrypcję...")

    # Transkrypcja pierwsza: bez podanego języka
    try:
        result = model.transcribe(audio_path, word_timestamps=True)
        print("Pierwsza transkrypcja zakończona pomyślnie.")
    except Exception as e:
        print(f"Wystąpił błąd podczas transkrypcji: {e}")
        return None, None

    # Zapisz transkrypcję jako tekst, aby wykryć język
    initial_transcription = result['text']
    print("Pierwsza transkrypcja tekstowa:", initial_transcription[:200])  # Pokazuje pierwsze 200 znaków

    # Wykryj język transkrypcji
    detected_language = detect_language_from_text(initial_transcription)

    # Jeśli język jest dostępny, zrób drugą transkrypcję z wykrytym językiem
    if detected_language:
        try:
            result_with_lang = model.transcribe(audio_path, word_timestamps=True, language=detected_language)
            print("Druga transkrypcja zakończona pomyślnie.")
            return result_with_lang, detected_language
        except Exception as e:
            print(f"Wystąpił błąd podczas drugiej transkrypcji z językiem: {e}")
            return None, None

    return None, None

# Określona ilość powtórzeń
num_repeats = 1

def process_videos_with_audio(num_repeats, video_folder_path, audio_folder_path, subtitles_folder_path,
                              transcript_folder_path, logo_path, output_folder_path, font_path, bloom, shadow_offset,
                              use_color, number_of_words, should_oscillate, font_scale, use_shadow, #shadow_offset, 
                              blur_radius, use_font_path,
                              shadow_radius):
    
    print("video_folder_path:", video_folder_path)
    print("audio_folder_path:", audio_folder_path)
    print("subtitles_folder_path:", subtitles_folder_path)
    print("transcript_folder_path:", transcript_folder_path)
    print("logo_path:", logo_path)
    print("output_folder_path:", output_folder_path)

    # Pobierz ścieżkę do AppData na pliki tymczasowe
    appdata_path = os.getenv('APPDATA')
    if not appdata_path:
        print("Nie udało się uzyskać ścieżki do AppData.")
        return

    for _ in range(num_repeats):
        
        # Wybór plików wideo o określonej nazwie
        video_files = [f for f in os.listdir(video_folder_path) if f.startswith("merged_video_") and f.endswith(".mp4")]
        if len(video_files) == 0:
            raise ValueError("Brak plików wideo o nazwie 'merged_video_' w wybranym folderze.")

       # Wybór jednego losowego pliku
        chosen_video = random.choice(video_files)

        audio_path = get_first_audio_file(audio_folder_path)

        result, detected_language = transcribe_audio_with_whisper(audio_path)

        print(f"Transkrypcja z wykrytym językiem '{detected_language}' zakończona.")

        # Określenie folderu i nazw plików
        output_folder = output_folder_path  # Podaj ścieżkę do folderu, w którym chcesz zapisać pliki
        output_filename_srt = "final_video_with_logo_with_audio.srt"
        output_srt_path = os.path.join(output_folder, output_filename_srt)
        print(f"Zapisz plik SRT w: {output_srt_path}")

        # Określenie nazwy pliku TXT
        output_filename_txt = "final_transcript.txt"
        output_txt_path = os.path.join(output_folder, output_filename_txt)
        print(f"Zapisz plik TXT w: {output_txt_path}")

        # Zapisz wynik w pliku SRT, dzieląc na grupy słów (np. 5 słów w grupie)
        print("Zapisz wynik w pliku SRT...")
        write_srt_by_word_groups(result, output_srt_path, number_of_words)
        print("Zapis pliku SRT zakończony.")

        # Zapisz wynik w pliku TXT
        print("Zapisz wynik w pliku TXT...")
        write_text_file(result, output_txt_path)
        print("Zapis pliku TXT zakończony.")

        # Wywołanie funkcji specialnych napisow
        print("Wywołanie funkcji specjalnych napisów...")
        specialwords(transcript_folder_path, output_folder_path)

        # Ładowanie plików wideo
        print("Ładowanie pliku wideo...")
        from moviepy.editor import VideoFileClip
        video_clip1 = VideoFileClip(os.path.join(video_folder_path, chosen_video))
        print("Plik wideo załadowany.")

        # Łączenie klipów wideo
        print("Łączenie klipów wideo...")
        from moviepy.editor import concatenate_videoclips
        final_clip = concatenate_videoclips([video_clip1])
        print("Łączenie klipów zakończone.")

        # Ładowanie pliku audio
        print("Ładowanie pliku audio...")
        from moviepy.editor import AudioFileClip
        audio_clip = AudioFileClip(audio_path)
        print("Plik audio załadowany.")

        # Przycinanie pliku wideo do długości pliku audio
        print("Przycinanie pliku wideo do długości pliku audio...")
        trimmed_video = final_clip.subclip(0, audio_clip.duration)
        print("Przycinanie zakończone.")

        # Przyciszanie pliku audio
        print("Dostosowanie głośności pliku audio...")
        muted_audio = audio_clip.volumex(1)  # Dostosuj poziom głośności tutaj
        print("Głośność dostosowana.")

        if logo_path:
            # Jeśli logo jest wybrane, dodaj je do wideo
            print("Dodawanie logo do wideo...")
            from moviepy.editor import CompositeVideoClip, ImageClip
            logo = ImageClip(logo_path).set_duration(trimmed_video.duration).resize(height=int(trimmed_video.h * 0.07))
            logo_position = ((trimmed_video.w - logo.w) // 2, trimmed_video.h - logo.h - int(trimmed_video.h * 0.05))
            final_clip_with_logo = CompositeVideoClip([trimmed_video, logo.set_position(logo_position)])
            print("Logo dodane.")
        else:
            # Jeśli logo nie jest wybrane, pomiń dodawanie logo
            print("Logo nie zostało wybrane, kontynuowanie bez logo...")
            final_clip_with_logo = trimmed_video

        # Ustawienie przyciętego dźwięku dla przyciętego klipu wideo
        print("Ustawienie dźwięku dla klipu wideo...")
        final_clip_with_logo = final_clip_with_logo.set_audio(muted_audio)

        #download_icons(output_folder_path)

        # Dodanie obrazów do wideo
       # final_clip_with_images = add_images_to_video(final_clip_with_logo, load_srt(sciezka_wyjsciowego_pliku), images_main_path = output_folder_path / 'emojis' )

        # Dodanie napisów na wierzchu
        #final_clip_with_subtitles = CompositeVideoClip([final_clip_with_images, subtitles])

        final_clip_with_subtitles = final_clip_with_logo

        lists_files = (output_folder_path +'\\neutral_positive_words.txt', output_folder_path +'\\negative_words.txt', output_folder_path +'\\verbs_adjectives.txt')  # Paths to the files with lists of words

        print("Dodawanie świecących napisów...")
        final_clip_with_subtitles = add_glowing_subtitles(
        final_clip_with_subtitles,   # Klip wideo z wcześniej dodanymi efektami
        srt_path = subtitles_folder_path + '\\final_video_with_logo_with_audio.srt',  # Ścieżka do pliku SRT
        lists_files = lists_files,  # Pliki z listami specjalnych słów
        colors = ['#13ef00', '#ff1700', '#00E0FF'],  # Kolory świecących napisów
        font_path=font_path,  # Ścieżka do czcionki
        font_scale = font_scale,  # Skala czcionki
        bloom = bloom,          # Przekazanie zmiennej 'bloom'
        use_color = use_color,   # Przekazanie zmiennej 'use_color'
        should_oscillate = should_oscillate, #poruszanie sie slow gora dol
        use_shadow = use_shadow,
        shadow_offset = shadow_offset,
       # shadow_offset = 3,
        blur_radius = blur_radius,
        #blur_radius = 6,
        shadow_radius = shadow_radius,
        use_font_path = use_font_path,
        detected_language = detected_language,
        )
        print("Dodawanie świecących napisów zakończone.")


        # Ścieżka do pliku wynikowego
        output_file_base_name = "final_video_with_logo"
        output_file_path = get_output_filename(output_folder_path, output_file_base_name)
        print(f"Ścieżka do pliku wynikowego: {output_file_path}")

        # Zapis klipu wideo z logiem do pliku
        # Łączenie wybranych klipów wideo
        print("Zapis klipu wideo z logiem...")
        temp_audio_path = os.path.join(appdata_path, "video_temp_audio.mp4")
        final_clip_with_subtitles.write_videofile(output_file_path, codec="libx264", audio_codec="aac", temp_audiofile=temp_audio_path)
        print("Zapis klipu zakończony.")

        # Usuwanie folderu z emotkami po zakończeniu procesu
       # shutil.rmtree(os.path.join(output_folder_path, 'emojis'))
       # print(f"Folder 'emojis' został usunięty.")

        # Zwolnienie pamięci
        print("Zwalnianie pamięci...")
        final_clip_with_subtitles.close()
        video_clip1.close()
        audio_clip.close()
        print("Pamięć zwolniona.")

        # Usunięcie plików wideo po połączeniu
        print("Usuwanie tymczasowych plików...")
        os.remove(os.path.join(video_folder_path, chosen_video))
        os.remove(os.path.join(video_folder_path, "final_video_with_logo_with_audio.srt"))
        os.remove(os.path.join(video_folder_path, "final_transcript.txt"))
        os.remove(os.path.join(video_folder_path, "negative_words.txt"))
        os.remove(os.path.join(video_folder_path, "neutral_positive_words.txt"))
        os.remove(os.path.join(video_folder_path, "verbs_adjectives.txt"))
        print("Tymczasowe pliki usunięte.")


print("Transkrypcja i tworzenie wideo zakończone.")
