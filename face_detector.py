import colorsys
import io
import math
import cv2
import mediapipe as mp
import asyncio
import numpy as np

from enum import Enum

FACE_OUTLINE_IDX = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
    361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
    176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
    162, 21, 54, 103, 67, 109
]

COLORTYPE_IDS = [234, 93, 454, 323, 10, 338, 152]


class ColorType(Enum):
    SPRING_WARM = "Теплая весна"
    SPRING_LIGHT = "Легкая весна"
    SPRING_BRIGHT = "Яркая весна"
    SPRING_SOFT = "Мягкая весна"

    AUTUMN_WARM = "Теплая осень"
    AUTUMN_DARK = "Темная осень"
    AUTUMN_BRIGHT = "Яркая осень"
    AUTUMN_SOFT = "Мягкая осень"

    WINTER_COOL = "Холодная зима"
    WINTER_DARK = "Темная зима"
    WINTER_BRIGHT = "Яркая зима"
    WINTER_LIGHT = "Легкая зима"

    SUMMER_COOL = "Холодное лето"
    SUMMER_LIGHT = "Легкое лето"
    SUMMER_SOFT = "Мягкое лето"
    SUMMER_DARK = "Темное лето"


def get_intensity(rgb):
    # Определяем интенсивность цвета (оттенки яркие или тусклые)
    r, g, b = rgb
    return max(r, g, b) - min(r, g, b)  # Разница между максимальным и минимальным значением


def get_temperature_v2(rgb):
    r, g, b = rgb
    if r > max(g, b):  # Теплый оттенок
        return 'warm'
    elif b > max(r, g):  # Холодный оттенок
        return 'cool'
    else:  # Нейтральный
        return 'neutral'


def get_brightness(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b  # Формула яркости


def determine_color_type(hair_rgb, face_rgb, eyes_rgb):
    print(f'hair_rgb={hair_rgb}, face_rgb={face_rgb}, eyes_rgb={eyes_rgb}')

    # Определение температуры для каждого элемента
    hair_temp = get_temperature_v2(hair_rgb)
    face_temp = get_temperature_v2(face_rgb)
    eyes_temp = get_temperature_v2(eyes_rgb)

    # Определяем интенсивность каждого элемента
    hair_intensity = get_intensity(hair_rgb)
    face_intensity = get_intensity(face_rgb)
    eyes_intensity = get_intensity(eyes_rgb)

    # Оценка яркости для каждого элемента
    hair_brightness = get_brightness(hair_rgb)
    face_brightness = get_brightness(face_rgb)
    eyes_brightness = get_brightness(eyes_rgb)

    # Общее распределение температуры
    is_warm = (hair_temp == 'warm' or face_temp == 'warm' or eyes_temp == 'warm')
    is_cool = (hair_temp == 'cool' or face_temp == 'cool' or eyes_temp == 'cool')

    # Классификация по цветотипам с подтипами
    if is_warm and not is_cool:
        if hair_brightness < 130:
            return ColorType.AUTUMN_DARK if (hair_intensity > 50) else ColorType.AUTUMN_SOFT
        elif hair_brightness > 170:
            return ColorType.SPRING_BRIGHT
        else:
            return ColorType.SPRING_WARM
    elif not is_warm and is_cool:
        if hair_brightness < 130:
            return ColorType.WINTER_DARK
        elif hair_brightness > 170:
            return ColorType.WINTER_BRIGHT
        else:
            return ColorType.SUMMER_COOL
    elif is_warm and is_cool:
        # Когда есть смесь теплых и холодных оттенков
        if hair_brightness < 130:
            return ColorType.AUTUMN_BRIGHT
        elif hair_brightness > 170:
            return ColorType.SUMMER_LIGHT
        else:
            return ColorType.SUMMER_SOFT
    else:
        return ColorType.SUMMER_LIGHT  # Если все нейтрально или сбалансировано


class FaceDetector:
    def __init__(self):
        self._mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, max_num_faces=1)

    async def highlight_face(self, image):
        h, w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = await asyncio.to_thread(self._mesh.process, rgb_image)

        if not results.multi_face_landmarks:
            return

        face_landmarks = results.multi_face_landmarks[0]

        landmarks = face_landmarks.landmark

        # left_eye_coords = (int(landmarks[474].x * w), int(landmarks[474].y * h))
        # right_eye_coords = (int(landmarks[469].x * w), int(landmarks[469].y * h))

        def average_color(img, coords, size=5):
            # Функция для расчета среднего цвета по списку координат
            total_color = [0, 0, 0]  # Для накопления сумм цветов
            count = 0

            for (x, y) in coords:
                x1 = max(x - size // 2, 0)
                y1 = max(y - size // 2, 0)
                x2 = min(x + size // 2 + 1, img.shape[1])
                y2 = min(y + size // 2 + 1, img.shape[0])
                region = img[y1:y2, x1:x2]
                avg_bgr = region.mean(axis=(0, 1))
                total_color[0] += avg_bgr[0]
                total_color[1] += avg_bgr[1]
                total_color[2] += avg_bgr[2]
                count += 1

            avg_bgr = [int(c / count) for c in total_color]
            return tuple(avg_bgr[::-1])

        left_eye_coords = [
            # (int(landmarks[468].x * w), int(landmarks[468].y * h)),  # зрачок
            (int(landmarks[469].x * w), int(landmarks[469].y * h)),
            (int(landmarks[470].x * w), int(landmarks[470].y * h)),
            (int(landmarks[471].x * w), int(landmarks[471].y * h)),
            (int(landmarks[472].x * w), int(landmarks[472].y * h)),
        ]

        right_eye_coords = [
            # (int(landmarks[473].x * w), int(landmarks[473].y * h)),  # зрачок
            (int(landmarks[474].x * w), int(landmarks[474].y * h)),
            (int(landmarks[475].x * w), int(landmarks[475].y * h)),
            (int(landmarks[476].x * w), int(landmarks[476].y * h)),
            (int(landmarks[477].x * w), int(landmarks[477].y * h))
        ]

        left_pupil = (int(landmarks[468].x * w), int(landmarks[468].y * h))
        right_pupil = (int(landmarks[473].x * w), int(landmarks[473].y * h))

        # Маски для глаз
        mask_left = np.zeros_like(image)
        mask_right = np.zeros_like(image)

        # Преобразуем координаты в формат для рисования многоугольников
        left_eye_points = np.array(left_eye_coords, np.int32)
        right_eye_points = np.array(right_eye_coords, np.int32)

        # Закрашиваем области радужки в масках (без учета зрачков)
        cv2.fillPoly(mask_left, [left_eye_points], (255, 255, 255))
        cv2.fillPoly(mask_right, [right_eye_points], (255, 255, 255))

        # Маски для зрачков (исключаем область вокруг зрачков)
        mask_left_pupil = np.zeros_like(image)
        mask_right_pupil = np.zeros_like(image)

        # Задаем маленькие области вокруг зрачков
        cv2.circle(mask_left_pupil, left_pupil, 10, (0, 0, 0), -1)
        cv2.circle(mask_right_pupil, right_pupil, 10, (0, 0, 0), -1)

        cv2.circle(image, left_pupil, 10, (0, 0, 0), -1)
        cv2.circle(image, right_pupil, 10, (0, 0, 0), -1)

        # Убираем пиксели зрачков из маски радужки
        mask_left = cv2.bitwise_and(mask_left, cv2.bitwise_not(mask_left_pupil))
        mask_right = cv2.bitwise_and(mask_right, cv2.bitwise_not(mask_right_pupil))

        left_eye_region = cv2.bitwise_and(image, mask_left)
        right_eye_region = cv2.bitwise_and(image, mask_right)

        # Чтобы не учитывать белые пиксели маски, используем только те пиксели, которые имеют значения (не белые)
        left_eye_pixels = left_eye_region[np.all(left_eye_region != 0, axis=-1)]  # Пиксели, не равные (0, 0, 0)
        right_eye_pixels = right_eye_region[np.all(right_eye_region != 0, axis=-1)]  # Пиксели, не равные (0, 0, 0)

        # Определение среднего цвета радужки (пиксели внутри маски, игнорируя зрачки)
        if len(left_eye_pixels) > 0:
            # Для каждого канала (R, G, B) вычисляем среднее значение
            left_eye_color = np.mean(left_eye_pixels.reshape(-1, 3), axis=0)
        else:
            left_eye_color = [0, 0, 0]  # Если пикселей нет, вернем черный

        if len(right_eye_pixels) > 0:
            # Для каждого канала (R, G, B) вычисляем среднее значение
            right_eye_color = np.mean(right_eye_pixels.reshape(-1, 3), axis=0)
        else:
            right_eye_color = [0, 0, 0]  # Если пикселей нет, вернем черный

        # avg_left_eye_rgb = average_color(image, left_eye_coords)
        # avg_right_eye_rgb = average_color(image, right_eye_coords)

        eye_rgb = tuple(int((c1 + c2) / 2) for c1, c2 in zip(left_eye_color, right_eye_color))

        colors = []
        for idx in COLORTYPE_IDS:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            region = image[y - 3:y + 3, x - 3:x + 3]
            if region.size != 0:
                avg_bgr = np.mean(region.reshape(-1, 3), axis=0)
                colors.append(avg_bgr)

        skin_rgb = np.mean(colors, axis=0)[::-1]

        left_cheek_x = int(landmarks[234].x * w)
        right_cheek_x = int(landmarks[454].x * w)

        forehead_point = landmarks[10]
        x = int(forehead_point.x * w)
        y = int(forehead_point.y * h)

        # Ограничиваем ширину блоком между скулами
        face_width = right_cheek_x - left_cheek_x
        box_width = face_width

        # Параметры прямоугольника над лбом
        vertical_offset = int(h * 0.15)
        box_height = int(h * 0.05)

        top = max(y - vertical_offset, 0)
        bottom = min(top + box_height, h)
        left = max(x - box_width // 2, left_cheek_x)
        right = min(x + box_width // 2, right_cheek_x)

        # Вырезаем область волос
        hair_region = image[top:bottom, left:right]

        # Фильтруем по яркости (исключаем кожу)
        hair_pixels = hair_region.reshape(-1, 3)
        brightness = hair_pixels.mean(axis=1)
        dark_pixels = hair_pixels[brightness < 180]

        hair_rgb = None
        color_type = None
        if len(dark_pixels) > 0:
            avg_bgr = dark_pixels.mean(axis=0)
            hair_rgb = tuple(int(c) for c in avg_bgr[::-1])

            color_type = determine_color_type(hair_rgb, skin_rgb, eye_rgb)

        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

        outline_points = []
        for idx in FACE_OUTLINE_IDX:
            lm = face_landmarks.landmark[idx]
            point = (int(lm.x * w), int(lm.y * h))
            outline_points.append(point)

        outline_points = np.array(outline_points, np.int32)
        cv2.polylines(image, [outline_points], isClosed=True, color=(0, 255, 255), thickness=2)

        for (x, y) in left_eye_coords:
            cv2.circle(image, (int(x), int(y)), 2, (0, 0, 255), -1)

        for (x, y) in right_eye_coords:
            cv2.circle(image, (int(x), int(y)), 2, (255, 0, 0), -1)

        _, img_encoded = cv2.imencode('.png', image)
        img_bytes = img_encoded.tobytes()

        img_io = io.BytesIO(img_bytes)

        return {
            'highlighted_photo': img_io,
            'hair_rgb': hair_rgb,
            'skin_rgb': skin_rgb,
            'eye_rgb': eye_rgb,
            'color_type': color_type
        }
