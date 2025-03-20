import cv2
import numpy as np
import sys

# Globalne zmienne
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

def main():
    global left_img, right_img, left_img_copy, right_img_copy, current_image
    if len(sys.argv) < 3:
        print("Usage: python app.py <left_image_path> <right_image_path>")
        sys.exit(1)
    
    left_path = sys.argv[1]
    right_path = sys.argv[2]

    left_img = cv2.imread(left_path)
    right_img = cv2.imread(right_path)
    if left_img is None or right_img is None:
        print("Error loading images. Check the file paths!")
        sys.exit(1)

    # Kopie do zaznaczania punktów
    left_img_copy = left_img.copy()
    right_img_copy = right_img.copy()

    # Tworzymy jedno okno i ustawiamy callback myszy
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 600, 600)
    cv2.moveWindow("Image", 100, 100)
    cv2.setMouseCallback("Image", click_event)

    # Startujemy od lewego obrazu
    current_image = 0
    cv2.imshow("Image", left_img_copy)
    print("Tryb jednego okna:")
    print("- Kliknij 4 punkty na LEWYM obrazie.")
    print("- Następnie przełącz się na PRAWY obraz za pomocą strzałki w prawo i kliknij 4 punkty.")
    print("- Użyj strzałki w lewo, aby wrócić do lewego obrazu.")
    print("- Naciśnij ESC, aby zakończyć (gdy obie strony mają już po 4 punkty).")

    while True:
        key = cv2.waitKeyEx(1)
        # Klawisze strzałek (dla systemu Windows: lewa = 2424832, prawa = 2555904)
        if key == 2424832:  # lewa strzałka
            current_image = 0
            cv2.imshow("Image", left_img_copy)
        elif key == 2555904:  # prawa strzałka
            current_image = 1
            cv2.imshow("Image", right_img_copy)
        elif key == 27:  # ESC
            break

        if len(left_points) == 4 and len(right_points) == 4:
            break

    cv2.destroyWindow("Image")

    # Obliczanie środków zaznaczonego obiektu
    center_left = compute_center(left_points)
    center_right = compute_center(right_points)
    print("Środek lewego obrazu:", center_left)
    print("Środek prawego obrazu:", center_right)

    # Obliczanie maksymalnego możliwego rozmiaru przycięcia, tak aby obiekt znalazł się w centrum
    h_left, w_left = left_img.shape[:2]
    h_right, w_right = right_img.shape[:2]

    avail_width_left = 2 * min(center_left[0], w_left - center_left[0])
    avail_height_left = 2 * min(center_left[1], h_left - center_left[1])
    avail_width_right = 2 * min(center_right[0], w_right - center_right[0])
    avail_height_right = 2 * min(center_right[1], h_right - center_right[1])

    crop_width = int(min(avail_width_left, avail_width_right))
    crop_height = int(min(avail_height_left, avail_height_right))
    print("Rozmiar przycięcia:", crop_width, "x", crop_height)

    # Przycinamy obrazy
    cropped_left = crop_center(left_img, center_left, crop_width, crop_height)
    cropped_right = crop_center(right_img, center_right, crop_width, crop_height)

    # Zapisujemy wyniki
    cv2.imwrite("cropped_left.jpg", cropped_left)
    cv2.imwrite("cropped_right.jpg", cropped_right)
    print("Przycięte obrazy zapisane jako 'cropped_left.jpg' oraz 'cropped_right.jpg'.")

if __name__ == "__main__":
    main()
