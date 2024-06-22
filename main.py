import cv2
import math
import mediapipe as mp
import time
import serial

import socket
# host to connect to
host = "localhost"
# port number to connect on
port = 4210
print("[$] Creating socket...")
# Create the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def marker(marker_id, to_get_id):
    if to_get_id == marker_id:
        x1, y1 = marker_conters[0][0]
        #cv2.circle(image, (int(x1), int(y1)), 15, (200, 0, 0), -1)
        x2, y2 = marker_conters[0][1]
        #cv2.circle(image, (int(x2), int(y2)), 15, (0, 255, 0), -1)
        x3, y3 = marker_conters[0][2]
        #cv2.circle(image, (int(x3), int(y3)), 15, (255, 0, 0), -1)
        x4, y4 = marker_conters[0][3]
        #cv2.circle(image, (int(x4), int(y4)), 15, (255, 255, 255), -1)
        xc = (x1 + x3) / 2
        yc = (y1 + y3) / 2
        xc = int(xc)
        yc = int(yc)
        cv2.circle(image, (xc, yc), 5, (255, 0, 0), -1)
        #cv2.line(image, (int(x1), int(y1)), (int(x4), int(y4)), (255, 0, 255), 5)
        hypotenuse = math.sqrt((x4 - x1) ** 2 + (y4 - y1) ** 2)
        #cv2.line(image, (int(x4), int(y1)), (int(x4), int(y4)), (255, 255, 0), 5)
        cathet = math.sqrt((y1 - y4) ** 2)
        #cv2.putText(image, str(xc) + ',' + str(yc), (int(xc), int(yc)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    #(0, 255, 0), 3)
        cosinus = cathet / hypotenuse
        angle = math.acos(cosinus)
        angle_degrees = math.degrees(angle)
        angle_degrees = int(angle_degrees)
        if int(x1) > int(x4) and int(y1) > int(y4):
            angle_degrees = 180 - angle_degrees
        elif int(x1) < int(x4) and int(y1) > int(y4):
            angle_degrees = 180 + angle_degrees
        elif int(x1) < int(x4) and int(y1) < int(y4):
            angle_degrees = 360 - angle_degrees
        #cv2.putText(image, str(angle_degrees), (int(x4), int(y4)), cv2.FONT_HERSHEY_COMPLEX, 1,
                    #(255, 255, 0), 5)

    else:
        xc, yc = -1, -1

    return xc, yc

def get_angle(x1, y1, x2, y2, color):
    angle_degrees = 0

    hypotenuse = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    cathet = math.sqrt((y1 - y2) ** 2)
    # cv2.putText(image, str(xc) + ',' + str(yc), (int(xc), int(yc)), cv2.FONT_HERSHEY_SIMPLEX, 1,
    # (0, 255, 0), 3)
    if hypotenuse != 0:
        cosinus = cathet / hypotenuse
        angle = math.acos(cosinus)
        angle_degrees = math.degrees(angle)
        angle_degrees = int(angle_degrees)
        if int(x1) > int(x2) and int(y1) > int(y2):
            angle_degrees = 180 - angle_degrees
        elif int(x1) < int(x2) and int(y1) > int(y2):
            angle_degrees = 180 + angle_degrees
        elif int(x1) < int(x2) and int(y1) < int(y2):
            angle_degrees = 360 - angle_degrees
        #cv2.putText(image, str(angle_degrees), (int(x2), int(y2)), cv2.FONT_HERSHEY_COMPLEX, 1,
                    #(255,255,255), 5)
    #print("!!!!!!!!!!!!!" ,x1, y1, x2, y2)
    #cv2.line(image, (int(x2), int(y1)), (int(x2), int(y2)), (0, 255, 0), 5)
    #cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), (color), 5)
    return angle_degrees

def write_msg(x):
    arduino.write(bytes(x,  'utf-8'))
    print(x)

def get_distance(x1, y1, x2, y2, color):
    distance = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    #cv2.line(image, (x1, y1), (x2, y2), color, 6)
    return distance

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

key = -1

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

pTime = 0
cTime = 0

msg = ""
mes = ""
stop = 0

best_distance_to_flask = 100

xc_7, yc_7, xc_8, yc_8, xc_9, yc_9, xc_10, yc_10 = -1, -1, -1, -1, -1, -1, -1, -1

mpHands = mp.solutions.hands
hands = mpHands.Hands(False, max_num_hands=1)
npDraw = mp.solutions.drawing_utils

colbs = [0, 0, 0, 0]

arduino = serial.Serial(port='COM8',  baudrate=115200, timeout=.1)
client_socket.bind((host, port))
message = "0"
print("start")
while message!="1" and message!="2":
    buffer_size = 4096
    data1 = client_socket.recvfrom(buffer_size)
    message = data1[0].decode()
    address = data1[1]
    print(message)
print("Hello world!")
write_msg(str(message))
time.sleep(3)

while key != 27:

    isRead, image = cap.read()
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    corners, ids, service = detector.detectMarkers(image_gray)
    cv2.aruco.drawDetectedMarkers(image, corners)
    for i in range(len(corners)):
        marker_conters = corners[i]
        marker_id = ids[[0]]
        cv2.putText(image, str(ids), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)
        ids_len = len(ids)
        #for i in range(ids_len):
        if ids[[i]] == 7:
            xc_7, yc_7 = marker(ids[[i]], 7)
        if ids[[i]] == 8:
            xc_8, yc_8 = marker(ids[[i]], 8)
        if ids[[i]] == 9:
            xc_9, yc_9 = marker(ids[[i]], 9)
        if ids[[i]] == 10:
            if key == 49:
                colbs[0], colbs[1] = marker(ids[[i]], 10)
            elif key == 50:
                colbs[2], colbs[3] = marker(ids[[i]], 10)

        if message == "1":
            xc_10, yc_10 = colbs[0], colbs[1]
        elif message == "2":
            xc_10, yc_10 = colbs[2], colbs[3]

        cv2.circle(image, (xc_10, yc_10), 5, (0, 0, 0), -1)

        if 7 in ids and 8 in ids and 9 in ids:
            angle_7_8 = get_angle(xc_7, yc_7, xc_8, yc_8, (200, 50, 40))
            distance_7_8 = get_distance(xc_7, yc_7, xc_8, yc_8, (200, 50, 40))
            cv2.line(image, (xc_7, yc_7), (xc_8, yc_8), (255, 0, 0), 6)
            angle_8_9 = get_angle(xc_8, yc_8, xc_9, yc_9, (0, 200, 0))
            distance_8_9 = get_distance(xc_8, yc_8, xc_9, yc_9, (0, 200, 0))
            cv2.line(image, (xc_8, yc_8), (xc_9, yc_9), (0, 255, 0), 6)
            #angle_7_9 = get_angle(xc_7, yc_7, xc_9, yc_9, (20, 20, 200))
            #distance_7_9 = get_distance(xc_7, yc_7, xc_9, yc_9, (20, 20, 200))

        if 9 in ids and xc_10 > 0:
            distance_to_flask = get_distance(xc_9, yc_9, xc_10, yc_10, (0, 0, 255))
            #print(distance_to_flask)
            if distance_to_flask <= best_distance_to_flask:
                cv2.rectangle(image, (xc_10 - best_distance_to_flask, yc_10 - best_distance_to_flask), (xc_10 + best_distance_to_flask, yc_10 + best_distance_to_flask), (0, 255, 0), 5)
                mes = "7"
            elif distance_to_flask > best_distance_to_flask:
                cv2.rectangle(image, (xc_10 - best_distance_to_flask, yc_10 - best_distance_to_flask), (xc_10 + best_distance_to_flask, yc_10 + best_distance_to_flask), (0, 0, 255), 5)
                mes = "8"

    results = hands.process(image_rgb)
    if results.multi_hand_landmarks:
        mes = '4'
    else:
        mes = '5'

    cTime = time.time()
    fps = 1 // (cTime - pTime)
    pTime = cTime
    stop += 1
    # print("stop = ", stop)
    # print("fps = ", fps)
    if stop == fps:
        stop = 0
        write_msg(mes)
        # if mes == '4':
        #     print("stop")
        # elif mes == '5':
        #     print("run")

    #print(key)
    cv2.imshow('window', image)
    key = cv2.waitKey(5)

cap.release()