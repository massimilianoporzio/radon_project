import os

from moviepy import VideoFileClip

# CONFIGURAZIONE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "login-bg.mp4")  # Il tuo file da 3.6MB
OUTPUT_FILE = os.path.join(BASE_DIR, "login-bg.webp")

print(f"Converto {INPUT_FILE} in WebP...")

try:
    # Carica il video
    clip = VideoFileClip(INPUT_FILE)

    # --- TRUCCHI PER RIDURRE IL PESO DEL WEBP ---
    # Le immagini animate pesano più dei video. Dobbiamo abbassare i Frame Per Secondo.
    # 10 FPS sono sufficienti per l'acqua che scorre e dimezzano il peso.
    clip_low_fps = clip.with_fps(10)

    # Scriviamo il file
    clip_low_fps.write_videofile(
        OUTPUT_FILE,
        codec="libwebp",  # Fondamentale
        preset="default",
        # loop=0 significa loop infinito
        ffmpeg_params=["-loop", "0"],
    )

    print(f"Finito! Ora metti {OUTPUT_FILE} in static/images/ e aggiorna settings.py")

except Exception as e:
    print(f"Errore: {e}")
