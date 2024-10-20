!pip install pydub
from pydub import AudioSegment
from IPython.display import Audio
import IPython

# Carrega o arquivo MP3
audio = AudioSegment.from_file("/content/The Emptiness Machine (Official Music Video) - Linkin Park.mp3")

# Exporta o áudio para um formato que o Colab pode reproduzir
audio.export("/content/temp.mp3", format="mp3")

# Função para reproduzir a música a partir de um determinado tempo
def play_from_time(start_time=0):
    # Convert start_time to milliseconds 
    start_time_ms = start_time * 1000  
    # Slice the audio to begin at the desired start time
    sliced_audio = audio[start_time_ms:]  
    # Export the sliced audio to a temporary file for playback
    sliced_audio.export("/content/temp_sliced.mp3", format="mp3") 
    # Play the sliced audio
    return IPython.display.Audio("/content/temp_sliced.mp3", autoplay=True) 

# Para tocar a música a partir do início
play_audio = play_from_time(0)

# Para avançar 10 segundos
def skip_audio():
    # Avança 10 segundos
    new_start_time = 100 # seconds
    return play_from_time(new_start_time)

# Exibir a música inicial
play_audio

# Para avançar a música em 10 segundos, você pode chamar:
# skip_audio()
