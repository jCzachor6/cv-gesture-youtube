import cv2
import numpy as np
import math
import json
import time
import shortcuts as sc

message_counter = 0
counter = 0
values = [0, 0, 0]
last_value = 0

#Przechowywanie wartości z trzech ostatnich klatek.
def count(counter, current_value):
    values[counter] = current_value
    counter += 1
    if (counter == 3):
        counter = 0
    return counter

#Przerwanie działania programu po wciśnięciu przycisku Escape
def quit_on_esc():
    k = cv2.waitKey(10)
    if k == 27:
        return True
    else:
        return False

#Odczytywanie polega na pobraniu maksymalnej wartości ilości kropek z ostatnich 3 klatek, a następnie gdy
#ilość zmieni się na 0 to wywołuje odpowiadającą funkcje gestu.
def retreive_gesture(last_value, message_counter):
    if(current_value!= values[counter] and current_value == 0):
        val = max(values)
        if(last_value != val):
            print(json_message(message_counter, val))
            sc.call_shortcut(val)
            message_counter += 1
            last_value = val
        else:
            last_value = -1
    return last_value, message_counter

#Wypisanie gestu w formacie JSON
def json_message(message_counter, message_type):
    return json.dumps({'count': message_counter, 'message': message_type})

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    #Przechwyć obraz do zmiennej img
    ret, img = cap.read()
    #Rysuj kwadrat na obrazie img
    cv2.rectangle(img, (300, 300), (100, 100), (0, 255, 0), 0)
    #Wycięcie potrzebnego fragmentu obrazu
    crop_img = img[100:300, 100:300]

    #1. Przerobienie wyciętego obrazu na o odcieniach szarości
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    #2. Rozmycie obrazu szarego
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    #3. Zastosowanie binaryzacji + Metody OTSU
    _, thresh1 = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    #4. Konturowanie obrazu binarnego
    _, contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    #5. Wyznaczenie najbardziej odległych konturów w obrazie binarnym i obrysowanie kwadratu na podstawie najbardziej
    #skrajnych punktów dłoni
    max_area = -1
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if (area > max_area):
            max_area = area
            ci = i
    cnt = contours[ci]
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)

    #Obrysowanie dłoni otoczką wypukłą
    hull = cv2.convexHull(cnt)
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)

    #Znalezienie skrajnych punktów z wylicznonej powierzchni między dłonią a otoczką wypukłą dłoni.
    hull = cv2.convexHull(cnt, returnPoints=False)
    defects = cv2.convexityDefects(cnt, hull)
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    # Przeliczenie tych defektów których kąty między sąsiednimi punktami są mniejsze od 90 stopni. (Punkty wewnętrzne)
    current_value = 0
    if(defects is not None):
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
            if angle <= 90:
                current_value += 1
                cv2.circle(crop_img, far, 1, [0, 0, 255], -1)
            cv2.line(crop_img, start, end, [0, 255, 0], 2)

    #Nalicz kolejną wartość licznika counter
    counter = count(counter, current_value)

    #Odczytaj gest
    last_value, message_counter = retreive_gesture(last_value, message_counter)

    #Wyświetl obraz z kamery
    cv2.imshow('Gesture', img)
    #Złóż rysunek 'drawing' i 'crop_img' w jeden i wyświetl
    all_img = np.hstack((drawing, crop_img))
    cv2.imshow('Contours', all_img)
    #Złóż rysunek 'Gray' i 'Blurred' w jeden i wyświetl
    all_img_gray = np.hstack((grey, blurred))
    cv2.imshow('Gray and blurred', all_img_gray)

    if quit_on_esc():
        break
    time.sleep(0.05)