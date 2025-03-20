import sys
import os

import numpy as np
import cv2

# Globalne zmienne (używane w interakcji)
left_points = []
right_points = []
left_img = None
right_img = None
left_img_copy = None
right_img_copy = None
current_image = 0  # 0 -> lewy obraz, 1 -> prawy obraz


def click_event(event, x, y, flags, param):
    global left_points, right_points, left_img_copy, right_img_copy, current_image
    if event == cv2.EVENT_LBUTTONDOWN:
        if current_image == 0 and len(left_points) < 4:
            left_points.append((x, y))
            cv2.circle(left_img_copy, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(left_img_copy, str(len(left_points)), (x + 10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Image", left_img_copy)
        elif current_image == 1 and len(right_points) < 4:
            right_points.append((x, y))
            cv2.circle(right_img_copy, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(right_img_copy, str(len(right_points)), (x + 10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Image", right_img_copy)


def compute_center(points):
    pts = np.array(points, dtype=np.float32)
    return np.mean(pts, axis=0)


def crop_center(img, center, crop_width, crop_height):
    cx, cy = center
    cx = int(round(cx))
    cy = int(round(cy))
    half_w = crop_width // 2
    half_h = crop_height // 2
    x1 = cx - half_w
    y1 = cy - half_h
    # Korekta, aby nie wychodzić poza obraz
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = x1 + crop_width
    y2 = y1 + crop_height
    if x2 > img.shape[1]:
        x2 = img.shape[1]
        x1 = x2 - crop_width
    if y2 > img.shape[0]:
        y2 = img.shape[0]
        y1 = y2 - crop_height
    return img[y1:y2, x1:x2]


def process_pair(left_image_path, right_image_path, output_prefix):
    """
    Przetwarza jedną parę obrazów (lewy: gm.png, prawy: osm.png).
    Użytkownik interaktywnie klika 4 punkty na każdym obrazie.
    Następnie obrazy są przycinane tak, aby zaznaczony obiekt znalazł się w środku.
    Wynik zapisywany jest pod nazwami: output_prefix + '_gm.png' oraz output_prefix + '_osm.png'.
    """
    global left_points, right_points, left_img, right_img, left_img_copy, right_img_copy, current_image

    # Reset globalnych zmiennych
    left_points = []
    right_points = []
    current_image = 0

    # Wczytanie obrazów
    left_img = cv2.imread(left_image_path)
    right_img = cv2.imread(right_image_path)
    if left_img is None or right_img is None:
        print(f"Błąd wczytania obrazów:\n {left_image_path}\n {right_image_path}")
        return

    left_img_copy = left_img.copy()
    right_img_copy = right_img.copy()

    # Tworzymy okno interaktywne
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 600, 600)
    cv2.moveWindow("Image", 100, 100)
    cv2.setMouseCallback("Image", click_event)

    print("\n======================================")
    print(f"Przetwarzanie pary:\n  Lewy: {left_image_path}\n  Prawy: {right_image_path}")
    print("W trybie jednego okna:")
    print(" - Kliknij 4 punkty na LEWYM obrazie (domyślnie wyświetlany).")
    print(" - Następnie naciśnij strzałkę w prawo (→), aby przełączyć na PRAWY obraz i kliknij 4 punkty.")
    print(" - Użyj strzałki w lewo (←), aby wrócić do LEWEGO obrazu.")
    print(" - Po zaznaczeniu 4 punktów na obu obrazach, naciśnij ESC aby zatwierdzić.")

    # Startujemy od lewego obrazu
    current_image = 0
    cv2.imshow("Image", left_img_copy)

    # Używamy waitKeyEx, aby odczytywać kody klawiszy rozszerzonych (dla Windows: ←=2424832, →=2555904)
    while True:
        key = cv2.waitKeyEx(1)
        # Lewa strzałka
        if key == 2424832:
            current_image = 0
            cv2.imshow("Image", left_img_copy)
        # Prawa strzałka
        elif key == 2555904:
            current_image = 1
            cv2.imshow("Image", right_img_copy)
        # ESC - zatwierdzenie lub przerwanie
        elif key == 27:
            break

        # Jeśli użytkownik zaznaczył 4 punkty na obu obrazach, przerywamy pętlę
        if len(left_points) == 4 and len(right_points) == 4:
            break

    cv2.destroyWindow("Image")

    if len(left_points) != 4 or len(right_points) != 4:
        print("Nie wybrano wystarczającej liczby punktów dla obu obrazów. Pomijam tę parę.")
        return

    # Obliczenie środków zaznaczonego obiektu
    center_left = compute_center(left_points)
    center_right = compute_center(right_points)
    print("Środek lewego obrazu:", center_left)
    print("Środek prawego obrazu:", center_right)

    # Obliczenie maksymalnego rozmiaru przycięcia, aby nie wychodziło poza obraz
    h_left, w_left = left_img.shape[:2]
    h_right, w_right = right_img.shape[:2]

    avail_width_left = 2 * min(center_left[0], w_left - center_left[0])
    avail_height_left = 2 * min(center_left[1], h_left - center_left[1])
    avail_width_right = 2 * min(center_right[0], w_right - center_right[0])
    avail_height_right = 2 * min(center_right[1], h_right - center_right[1])

    crop_width = int(min(avail_width_left, avail_width_right))
    crop_height = int(min(avail_height_left, avail_height_right))
    print("Rozmiar przycięcia:", crop_width, "x", crop_height)

    # Przycinanie obrazów
    cropped_left = crop_center(left_img, center_left, crop_width, crop_height)
    cropped_right = crop_center(right_img, center_right, crop_width, crop_height)

    # Zapis wyników
    output_left = output_prefix + "_gm.png"
    output_right = output_prefix + "_osm.png"
    cv2.imwrite(output_left, cropped_left)
    cv2.imwrite(output_right, cropped_right)
    print("Zapisano przycięte obrazy jako:")
    print(" ", output_left)
    print(" ", output_right)


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <folder_path>")
        sys.exit(1)

    data_folder = sys.argv[1]

    if not os.path.isdir(data_folder):
        print("Podana ścieżka nie jest folderem.")
        sys.exit(1)

    # Lista podfolderów (np. "0", "1", "2", …)
    subfolders = sorted([d for d in os.listdir(data_folder)
                         if os.path.isdir(os.path.join(data_folder, d))])
    if not subfolders:
        print("Nie znaleziono podfolderów w podanym folderze.")
        sys.exit(1)

    for sub in subfolders:
        subfolder_path = os.path.join(data_folder, sub)
        # Spodziewamy się, że w podfolderze znajdują się dwa obrazy: gm.png i osm.png
        left_image_path = os.path.join(subfolder_path, "gm.png")
        right_image_path = os.path.join(subfolder_path, "osm.png")
        if not (os.path.isfile(left_image_path) and os.path.isfile(right_image_path)):
            print(f"Pomiń folder {subfolder_path} - nie znaleziono gm.png lub osm.png")
            continue

        # Sprawdzamy, czy pliki wynikowe już istnieją
        output_prefix = os.path.join(subfolder_path, "cropped")
        output_left = output_prefix + "_gm.png"
        output_right = output_prefix + "_osm.png"
        if os.path.isfile(output_left) and os.path.isfile(output_right):
            print(f"Pomijam folder {subfolder_path} - pliki cropped już istnieją.")
            continue

        process_pair(left_image_path, right_image_path, output_prefix)

    print("\nPrzetwarzanie zakończone.")


if __name__ == "__main__":
    main()
