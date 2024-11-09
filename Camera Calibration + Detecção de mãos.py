import cv2
import mediapipe as mp
import numpy as np
import vlc
import ctypes

# Parâmetros para calibração
chessboard_size = (7, 6)  # Número de cantos internos no padrão de xadrez
frame_size = (640, 480)   # Tamanho da imagem de vídeo

# Definir pontos do padrão de xadrez 3D
obj_points = []  # Pontos 3D no mundo real
img_points = []  # Pontos 2D na imagem

objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Capturar frames para calibração
cap = cv2.VideoCapture(0)
total_frames_needed = 20
found = 0

while found < total_frames_needed:  # Captura 20 frames de xadrez para calibração
    ret, frame = cap.read()
    if not ret:
        break

    # Espelhar a imagem horizontalmente para corrigir a inversão
    frame = cv2.flip(frame, 1)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        obj_points.append(objp)
        img_points.append(corners)
        found += 1

        # Desenhar o padrão de xadrez
        cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)

    # Exibir o progresso da calibração
    progress_text = f"Calibração: {found}/{total_frames_needed} frames capturados"
    cv2.putText(frame, progress_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
    
    cv2.imshow('Calibração da Câmera', frame)
    cv2.waitKey(100)

# Fechar janela de calibração
cap.release()
cv2.destroyAllWindows()

# Calibração da câmera
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, frame_size, None, None)


# Inicializar MediaPipe para rastreamento das mãos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Caminho para a libvlc
libvlc_path = "C:/Program Files/VideoLAN/VLC/libvlc.dll"
ctypes.CDLL(libvlc_path)

# Inicializar VLC player
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new("Linkin Park v2.0 Emily Armstrong  FULL SHOW HD LIVE 9 5 2024.mp4")  # Caminho do arquivo
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
        motion_history.pop(0)

    if len(motion_history) == 10:
        x_coords, y_coords = zip(*motion_history)
        center = np.mean(x_coords), np.mean(y_coords)
        radius = np.mean(
            [np.linalg.norm((x - center[0], y - center[1])) for x, y in motion_history]
        )

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

# Abrir a câmera e aplicar a calibração
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Aplicar a correção de distorção
    frame = cv2.undistort(frame, camera_matrix, dist_coeffs)

    # Espelhar a imagem horizontalmente
    frame = cv2.flip(frame, 1)

    # Converter para RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processar imagem para detecção da mão
    result = hands.process(rgb_frame)

    # Se detectar uma mão
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
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

            gesture = detect_circle_motion(hand_landmarks, hand_open)

            if gesture == "circle_open" and not is_playing:
                action_text = "Play"
                print(action_text)
                player.play()
                is_playing = True

            elif gesture == "circle_open" and is_playing:
                action_text = "Pause"
                print(action_text)
                player.pause()
                is_playing = False

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

    # Exibir texto da ação
    display_action_text(frame, action_text)
    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
hands.close()
player.stop()

