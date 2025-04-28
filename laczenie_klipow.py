import os
from PIL import Image
import random
import time
from moviepy.video.fx.all import resize, crop
import logging
import cv2
import numpy as np
import ffmpeg

def get_ffmpeg_path():
    # Odczytaj wartość zmiennej środowiskowej
    ffmpeg_path = os.environ.get('FFMPEG_PATH')
    if ffmpeg_path:
        print(f"FFmpeg path: {ffmpeg_path}")
    else:
        print("FFMPEG_PATH is not set.")

if __name__ == "__main__":
    get_ffmpeg_path()

def convert_mov_to_mp4(input_path, output_path):
    """Konwertuje plik MOV na MP4 bez zmiany rozdzielczości, kodeków czy jakości."""
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, c='copy')  # Kopiowanie strumieni wideo i audio bez rekompresji
            .run(overwrite_output=True)
        )
        print(f"Sukces: {input_path} został skonwertowany do {output_path} bez zmian formatu.")
    except ffmpeg.Error as e:
        print("Błąd konwersji:", e)
    
def prevent_repeated_clips(video_files, selected_videos, is_random):
    available_video_files = [video for video in video_files if video not in selected_videos]
    available_mp4_files = [video for video in available_video_files if os.path.splitext(video)[1].lower() == '.mp4']
    
    # Sprawdzamy, czy mamy dostępne pliki MP4
    if not available_mp4_files:
        # Jeśli brak plików MP4, konwertujemy pliki MOV na MP4
        available_mov_files = [video for video in available_video_files if os.path.splitext(video)[1].lower() == '.mov']
        if not available_mov_files:
            return None, selected_videos  # Brak dostępnych plików MOV i MP4, zwracamy None

        # Konwertujemy pierwszy dostępny plik MOV na MP4
        mov_file = available_mov_files[0]
        mp4_file = os.path.splitext(mov_file)[0] + '.mp4'
        convert_mov_to_mp4(mov_file, mp4_file)
        available_mp4_files.append(mp4_file)  # Dodajemy skonwertowany plik MP4 do listy
        
    if is_random:
        # Losowy wybór, jeśli is_random jest True
        selected_video = random.choice(available_mp4_files)
    else:
        # Sekwencyjny wybór, jeśli is_random jest False
        selected_video = available_mp4_files[0]  # Wybieramy pierwszy dostępny plik

    selected_videos.append(selected_video)  # Dodajemy wybrany plik do listy wybranych
    return selected_video, selected_videos

def get_audio_duration(file_path):
    from pydub import AudioSegment
    try:
        print(f"Próba odczytu długości pliku audio: {file_path}")
        audio = AudioSegment.from_file(file_path)
        return audio.duration_seconds
    except Exception as e:
        print(f"Nie udało się odczytać długości pliku audio {file_path}: {e}")
        return None

def flash_effect(clip, flash_duration):
    from moviepy.editor import vfx
    return clip.fx(vfx.fadein, flash_duration, initial_color=(255, 255, 255)) #bialy 255, 255, 255

def add_flash_transition(clips, flash_duration):
    print("Wybrano efekt: Flash")
    for i, clip in enumerate(clips):
        if i > 0 and clip.duration >= 3:
            clips[i] = flash_effect(clip, flash_duration)
    return clips

def scale_and_crop(clip, target_size):
    """Skaluje i przycina klip do docelowego rozmiaru 9:16, minimalizując utratę jakości."""
    target_width, target_height = target_size
    clip_width, clip_height = clip.size

    # Oblicz współczynniki proporcji
    target_aspect_ratio = target_width / target_height
    clip_aspect_ratio = clip_width / clip_height

    # Skalowanie klipu do zachowania proporcji
    if clip_aspect_ratio > target_aspect_ratio:
        # Wideo jest szersze niż docelowy format 9:16
        new_height = target_height
        new_width = int(new_height * clip_aspect_ratio)
    else:
        # Wideo jest węższe lub takie samo
        new_width = target_width
        new_height = int(new_width / clip_aspect_ratio)

    # Skalowanie klipu
    clip = clip.fx(resize, newsize=(new_width, new_height))

    # Oblicz nadmiar szerokości i wysokości, aby przyciąć
    x_center = new_width // 2
    y_center = new_height // 2

    # Przycinanie do dokładnych wymiarów
    return clip.fx(crop, x_center=x_center, y_center=y_center, width=target_width, height=target_height)

def add_fade_transition(clips, fade_duration):
    """
    Dodaje fade in i fade out jako przejście między klipami.
    """
    last_clip = clips[-2]
    current_clip = clips[-1]

    # Dodanie fade out do ostatniego klipu
    last_clip = last_clip.crossfadeout(fade_duration)

    # Dodanie fade in do aktualnego klipu
    current_clip = current_clip.crossfadein(fade_duration)

    # Połączenie klipów z fade in/fade out
    from moviepy.editor import concatenate_videoclips
    transition_clip = concatenate_videoclips([last_clip, current_clip], method="compose")
    
    # Zastąpienie ostatnich dwóch klipów nowym klipem z przejściem fade
    return clips[:-2] + [transition_clip]

# Funkcja do glitchowania każdej klatki
def glitch_frame(frame, glitch_level=2):
    from glitch_this import ImageGlitcher
    # Zamień klatkę na obraz w stylu PIL
    glitcher = ImageGlitcher()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(frame_rgb)

    # Glitchuj obraz z przesunięciem kolorów
    glitched_img = glitcher.glitch_image(pil_img, glitch_level, color_offset=True)

    # Zamień z powrotem na klatkę OpenCV
    glitched_frame = cv2.cvtColor(np.array(glitched_img), cv2.COLOR_RGB2BGR)
    return glitched_frame

# Funkcja do glitchowania klatki jako przejście
def create_glitch_transition(frame, glitch_duration, glitch_level=2, fps=30):

    # Stwórz efekt glitch na jednej klatce
    glitched_frames = []
    for _ in range(int(glitch_duration * fps)):
        glitched_frame = glitch_frame(frame, glitch_level)
        glitched_frames.append(glitched_frame)

    # Utwórz klip z tych glitched klatek
    frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in glitched_frames]
    from moviepy.editor import ImageSequenceClip
    transition_clip = ImageSequenceClip(frames_rgb, fps=fps)
    return transition_clip

# Funkcja do uzyskania ostatniej klatki z klipu (VideoFileClip) za pomocą OpenCV
def get_last_frame(clip):
    # Tworzymy tymczasowy plik wideo
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_filename = temp_file.name
        clip.write_videofile(temp_filename, codec='libx264', audio=False)
    
    # Otwórz plik wideo przy pomocy OpenCV
    cap = cv2.VideoCapture(temp_filename)
    if not cap.isOpened():
        raise ValueError("Nie udało się otworzyć pliku wideo.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    success, frame = cap.read()
    
    cap.release()
    os.remove(temp_filename)  # Usuń tymczasowy plik wideo

    if success:
        return frame
    else:
        raise ValueError("Nie udało się odczytać ostatniej klatki wideo.")

def apply_transition_effects(clips,  flash_duration, fade_duration, glitch_duration, 
                             use_flash_transition, use_fade_transition, use_glitch_transition):
    clips_with_transitions = []

    for i, clip in enumerate(clips):
        if i > 0:
            # Losowy wybór przejścia, które jest aktywne
            available_transitions = []

            if use_flash_transition:
                available_transitions.append('flash')
            if use_fade_transition:
                available_transitions.append('fade')
            if use_glitch_transition:
                available_transitions.append('glitch')

            if available_transitions:
                chosen_transition = random.choice(available_transitions)

                if chosen_transition == 'flash':
                    clips_with_transitions = add_flash_transition(clips_with_transitions + [clip], flash_duration)

                elif chosen_transition == 'fade':
                    clips_with_transitions = add_fade_transition(clips_with_transitions + [clip], fade_duration)

                elif chosen_transition == 'glitch':
                    last_frame = get_last_frame(clips[i - 1])
                    glitch_clip = create_glitch_transition(last_frame, glitch_duration, glitch_level=2, fps=30)
                    clips_with_transitions.append(glitch_clip)
                    clips_with_transitions.append(clip)
            else:
                clips_with_transitions.append(clip)
        else:
            clips_with_transitions.append(clip)

    return clips_with_transitions

def random_video_merge(audio_file_path, video_files, output_folder, clip_duration, 
                       flash_duration, fade_duration, glitch_duration, use_flash_transition, 
                       use_fade_transition, use_glitch_transition, is_random, num_iterations=1):
    
    output_filename_prefix="merged_video"

    logging.debug(f"Starting random_video_merge with video_files: {video_files}, output_folder: {output_folder}, output_filename_prefix: {output_filename_prefix}")

    # Check if video files exist
    missing_files = [file for file in video_files if not os.path.exists(file)]
    if missing_files:
        logging.error(f"Missing files: {missing_files}")
        return

    # Check for output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.debug(f"Created output folder: {output_folder}")

    
    audio_duration = get_audio_duration(audio_file_path)
    if not audio_duration:
        logging.error("Could not retrieve audio duration.")
        return

    min_duration = audio_duration * 1.1
    max_duration = audio_duration * 1.1

    # Adjust clip_duration based on its value
    if clip_duration < 1:
        num_videos = len(video_files)
        if num_videos > 0:
            clip_duration = max_duration / num_videos
        else:
            logging.error("No video files available to calculate clip duration.")
            return

    # Wczytaj efekty przejść
    #transitions_folder = r"C:\Users\PC\Desktop\YT\efekty"  # Zastąp odpowiednią ścieżką
    #transition_files = [
    #os.path.join(transitions_folder, f)
    #for f in os.listdir(transitions_folder)
   # if os.path.isfile(os.path.join(transitions_folder, f)) and f.endswith(('.mp4', '.gif'))
   # ]
    
   # if not transition_files:
     #   print("Brak plików z efektami przejść w folderze.")

    # Losowanie plików wideo, jeśli is_random jest True
    if is_random:
        random.shuffle(video_files)

    # Pobierz ścieżkę do AppData na pliki tymczasowe
    appdata_path = os.getenv('APPDATA')
    if not appdata_path:
        print("Nie udało się uzyskać ścieżki do AppData.")
        return

    for i in range(num_iterations):
        selected_clips = []
        total_duration = 0
        selected_videos = []

        while total_duration < min_duration or total_duration > max_duration:
            # Wybieranie losowe lub sekwencyjne
            if is_random:
                selected_video, selected_videos = prevent_repeated_clips(video_files, selected_videos, is_random)
            else:
                if len(selected_videos) < len(video_files):
                    selected_video = video_files[len(selected_videos)]  # Sekwencyjne wybieranie plików
                    selected_videos.append(selected_video)
                else:
                    print("Brak dostępnych plików wideo.")
                    break
            
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(selected_video)
            duration = clip.duration

            # Sprawdzanie, czy plik jest dłuższy niż clip_duration
            if duration > clip_duration:
                # Przycinanie do clip_duration
                clip = clip.subclip(0, clip_duration)

            if total_duration + clip.duration <= max_duration:
                # Zmiana proporcji na 9:16
                clip = scale_and_crop(clip, (720, 1280))
                selected_clips.append(clip)
                total_duration += clip.duration
            else:
                clip.close()
                break
            time.sleep(0.2)

        # Dodanie efektów przejść między klipami
        clips_with_transitions = apply_transition_effects(selected_clips, 
                                                          flash_duration, 
                                                          fade_duration, 
                                                          glitch_duration, 
                                                          use_flash_transition, 
                                                          use_fade_transition, 
                                                          use_glitch_transition)

        # Ustawienie nazwy wyjściowej dla pliku wideo
        output_filename = f"{output_filename_prefix}_{i+1}.mp4"
        output_path = os.path.join(output_folder, output_filename)

        # Łączenie wybranych klipów wideo
        temp_audio_path = os.path.join(appdata_path, "video_temp_audio.mp4")
        from moviepy.editor import concatenate_videoclips
        final_clip = concatenate_videoclips(clips_with_transitions, method="compose")
        
        # Zapisanie końcowego klipu do pliku w wybranym folderze
        final_clip.write_videofile(output_path, codec="libx264", fps=60, bitrate="5000k", threads=4, preset="medium", audio=False, temp_audiofile=temp_audio_path, verbose=True)

        print(f"Plik wideo {output_path} został połączony i zapisany w folderze: {output_folder}")

        # Zamknięcie obiektów VideoFileClip
        final_clip.close()