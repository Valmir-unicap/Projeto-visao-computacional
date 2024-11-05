# Calibra através de uma imagem de tabuleiro de xadrez

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
 
found = 0
while found < 20:  # Captura 20 frames de xadrez para calibração
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
 
    cv2.imshow('Calibração da Câmera', frame)
    cv2.waitKey(100)
 
# Fechar janela de calibração
cap.release()
cv2.destroyAllWindows()
 
# Calibração da câmera
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, frame_size, None, None)
