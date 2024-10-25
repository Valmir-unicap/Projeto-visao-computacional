import cv2
import mediapipe as mp
import ctypes
import vlc

# Inicializar MediaPipe para rastreamento das mãos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

libvlc_path = (
    "C:/Program Files/VideoLAN/VLC/libvlc.dll"  # Ajuste se necessário para 64-bit
)
ctypes.CDLL(libvlc_path)

# Inicializar VLC player
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(
    "O que é Levantamento de Requisitos - Tópicos de Engenharia de Software.mp4"
)  # Coloque o caminho do arquivo de vídeo ou música

player.set_media(media)

# Variáveis de controle
is_playing = False
volume = 50  # Volume inicial (entre 0 e 100)
player.audio_set_volume(volume)

# Função para detectar o gesto com base nas posições da mão
def detect_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Play: mão totalmente aberta
    if (
        thumb_tip.y < wrist.y
        and index_tip.y < wrist.y
        and middle_tip.y < wrist.y
        and ring_tip.y < wrist.y
        and pinky_tip.y < wrist.y
    ):
        return "play"

    # Pause: mão totalmente fechada
    if (
        thumb_tip.y > index_tip.y
        and index_tip.y > middle_tip.y
        and middle_tip.y > ring_tip.y
        and ring_tip.y > pinky_tip.y
    ):
        return "pause"

    # Avançar 10 segundos: polegar para a direita
    if thumb_tip.x > wrist.x and abs(thumb_tip.y - wrist.y) < 0.1:
        return "next_10s"

    # Retroceder 10 segundos: polegar para a esquerda
    if thumb_tip.x < wrist.x and abs(thumb_tip.y - wrist.y) < 0.1:
        return "back_10s"

    # Aumentar volume: indicador apontando para cima
    if index_tip.y < wrist.y and abs(index_tip.x - wrist.x) < 0.1:
        return "volume_up"

    # Diminuir volume: indicador apontando para baixo
    if index_tip.y > wrist.y and abs(index_tip.x - wrist.x) < 0.1:
        return "volume_down"

    return None

# Abrir a câmera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Espelhar a imagem horizontalmente para corrigir a inversão
    frame = cv2.flip(frame, 1)

    # Converter imagem para RGB (necessário para MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processar imagem para detecção da mão
    result = hands.process(rgb_frame)

    # Se detectar uma mão
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Desenhar os pontos de referência da mão na imagem
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detectar o gesto com base nos landmarks
            gesture = detect_gesture(hand_landmarks)

            # Ações baseadas nos gestos
            if gesture == "play" and not is_playing:
                print("Play")
                player.play()
                is_playing = True

            elif gesture == "pause" and is_playing:
                print("Pause")
                player.pause()
                is_playing = False

            elif gesture == "next_10s":
                print("Forward 10s")
                player.set_time(player.get_time() + 10000)  # Avançar 10 segundos

            elif gesture == "back_10s":
                print("Rewind 10s")
                player.set_time(player.get_time() - 10000)  # Voltar 10 segundos

            elif gesture == "volume_up":
                print("Increase Volume")
                volume = min(100, volume + 10)
                player.audio_set_volume(volume)

            elif gesture == "volume_down":
                print("Decrease Volume")
                volume = max(0, volume - 10)
                player.audio_set_volume(volume)

    # Mostrar a imagem da câmera
    cv2.imshow("Hand Tracking", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
hands.close()
player.stop()
