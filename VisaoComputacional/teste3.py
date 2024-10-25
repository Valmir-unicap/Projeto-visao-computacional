import cv2
import mediapipe as mp
import ctypes
import vlc
import time
import numpy as np



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
motion_history = []


# Função para detectar o gesto circular para play/pause
def detect_circle_motion(hand_landmarks, hand_open):
    global motion_history
    motion_history.append(
        (
            hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
            hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y,
        )
    )

    if len(motion_history) > 10:
        motion_history.pop(0)  # Manter histórico de apenas 10 posições

    # Verificar movimento circular
    if len(motion_history) == 10:
        x_coords, y_coords = zip(*motion_history)
        center = np.mean(x_coords), np.mean(y_coords)
        radius = np.mean(
            [np.linalg.norm((x - center[0], y - center[1])) for x, y in motion_history]
        )

        # Determinar se a mão completou um movimento circular
        if (
            radius > 0.01
            and max(x_coords) - min(x_coords) > 0.02
            and max(y_coords) - min(y_coords) > 0.02
        ):
            motion_history = (
                []
            )  # Reiniciar histórico após detectar o movimento circular
            return "circle_open" if hand_open else "circle_closed"

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

            # Verificar se a mão está aberta
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP
            ]
            ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

            hand_open = (
                thumb_tip.y < index_tip.y
                and index_tip.y < middle_tip.y
                and middle_tip.y < ring_tip.y
                and ring_tip.y < pinky_tip.y
            )

            # Detectar o movimento circular e acionar play/pause
            gesture = detect_circle_motion(hand_landmarks, hand_open)

            # Ações baseadas no gesto circular
            if gesture == "circle_open" and not is_playing:
                print("Play")
                player.play()
                is_playing = True

            elif gesture == "circle_closed" and is_playing:
                print("Pause")
                player.pause()
                is_playing = False

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
