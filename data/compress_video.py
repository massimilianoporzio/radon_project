import os

from moviepy import VideoFileClip
from moviepy.video.fx import Resize  # <--- NUOVO IMPORT NECESSARIO

# --- CONFIGURAZIONE ---
# Usa os.path per trovare il file sicuramente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "208837_tiny.mp4")  # Assicurati che il nome sia esatto
OUTPUT_FILE = os.path.join(BASE_DIR, "login-bg.mp4")
TARGET_WIDTH = 720

print(f"Sto cercando il file qui: {INPUT_FILE}")

try:
    # Carica il video
    clip = VideoFileClip(INPUT_FILE)
    print(f"Video caricato! Durata: {clip.duration}s, Risoluzione: {clip.w}x{clip.h}")

    # --- RIDIMENSIONAMENTO (Logica MoviePy 2.0) ---
    # Invece di clip.resize(), usiamo clip.with_effects([Resize(...)])
    if clip.w > clip.h:
        # Video Orizzontale
        clip_resized = clip.with_effects([Resize(width=TARGET_WIDTH)])
    else:
        # Video Verticale
        clip_resized = clip.with_effects([Resize(height=TARGET_WIDTH)])

    print("Ridimensionamento applicato. Inizio compressione...")

    # --- SALVATAGGIO ---
    clip_resized.write_videofile(
        OUTPUT_FILE,
        codec="libx264",
        audio=False,  # Rimuove l'audio
        bitrate="1000k",  # 1 MB/s
        preset="medium",
        fps=24,
        threads=4,  # Usa 4 core per fare prima
    )
    print(f"Fatto! File salvato in: {OUTPUT_FILE}")

except OSError:
    print("ERRORE: Il file non è stato trovato. Controlla il nome o spostalo nella cartella data.")
except Exception as e:
    print(f"ERRORE GENERICO: {e}")
