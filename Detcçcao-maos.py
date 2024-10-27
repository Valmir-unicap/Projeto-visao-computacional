import cv2
import mediapipe as mp
import ctypes
import vlc
import numpy as np

# Inicializar MediaPipe para rastreamento das mãos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

libvlc_path = "C:/Program Files/VideoLAN/VLC/libvlc.dll"  # Ajuste se necessário para 64-bit
ctypes.CDLL(libvlc_path)

# Inicializar VLC player
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new("O que é Levantamento de Requisitos - Tópicos de Engenharia de Software.mp4")  # Caminho do arquivo
player.set_media(media)

# Variáveis de controle
is_playing = False
volume = 50  # Volume inicial (entre 0 e 100)
player.audio_set_volume(volume)
motion_history = []
action_text = ""  # Texto para exibir a ação

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
            motion_history = []
            return "circle_open" if hand_open else "circle_closed"

    return None

# Função para exibir o texto de ação na tela
def display_action_text(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, text, (10, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

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
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
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
                action_text = "Play"
                print(action_text)
                player.play()
                is_playing = True

            elif gesture == "circle_closed" and is_playing:
                action_text = "Pause"
                print(action_text)
                player.pause()
                is_playing = False

            # Outros gestos para volume e avanço/recuo
            elif index_tip.x > 0.7:
                action_text = "Forward 10s"
                print(action_text)
                player.set_time(player.get_time() + 10000)

            elif index_tip.x < 0.3:
                action_text = "Rewind 10s"
                print(action_text)
                player.set_time(player.get_time() - 10000)

            elif index_tip.y < 0.2:
                action_text = "Increase Volume"
                print(action_text)
                volume = min(100, volume + 10)
                player.audio_set_volume(volume)

            elif index_tip.y > 0.8:
                action_text = "Decrease Volume"
                print(action_text)
                volume = max(0, volume - 10)
                player.audio_set_volume(volume)

    # Exibir texto da ação na imagem da câmera
    display_action_text(frame, action_text)

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
