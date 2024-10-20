from pydub import AudioSegment
from IPython.display import Audio

# Carrega o arquivo MP3
audio = AudioSegment.from_file("/content/The Emptiness Machine (Official Music Video) - Linkin Park.mp3")

# Exporta o áudio para um formato que o Colab pode reproduzir
audio.export("/content/temp.mp3", format="mp3")

# Reproduz o áudio
Audio("/content/temp.mp3")
