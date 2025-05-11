import colorsys
import io
import math
import cv2
import mediapipe as mp
import asyncio
import numpy as np

from enum import Enum

PUPIL_RADIUS = 5  # радиус вокруг зрачка
COLOR_THRESHOLD = 30  # порог похожести цвета (евклидово расстояние)

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
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return s * 100  # Возвращаем насыщенность в процентах


def get_temperature_v2(rgb):
    r, g, b = [x / 255.0 for x in rgb]  # Нормализация
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    hue_deg = h * 360

    # Примерное разделение:
    # Тёплые: 0–60 и 300–360 (красные, оранжевые, тёпло-розовые)
    # Холодные: 60–180 (зеленые, голубые, синие)
    # Остальные — нейтральные/спорные

    if (hue_deg < 60) or (hue_deg >= 300):
        return 'warm'
    elif 60 <= hue_deg <= 180:
        return 'cool'
    else:
        return 'neutral'


def get_brightness(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_dominant_color(image, tolerance=10):
    pixels = image.reshape(-1, 3)
    groups = []

    for pixel in pixels:
        found = False
        for group in groups:
            if np.linalg.norm(pixel - group['color']) < tolerance:
                group['pixels'].append(pixel)
                group['color'] = np.mean(group['pixels'], axis=0)  # обновить усреднённо
                found = True
                break
        if not found:
            groups.append({'pixels': [pixel], 'color': pixel.astype(float)})

    largest_group = max(groups, key=lambda g: len(g['pixels']))
    return np.array(largest_group['color'], dtype=np.uint8)


def extract_region_color(image, center, radius=5):
    h, w = image.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    region = image[mask == 255]
    return region


def filter_region_by_color(region_coords, image, target_color, threshold):
    matched_pixels = []
    for (x, y) in region_coords:
        color = image[y, x]
        if np.linalg.norm(color - target_color) < threshold:
            matched_pixels.append((x, y))
    return matched_pixels


def landmark_to_pixel(landmark, img_width, img_height):
    return int(landmark.x * img_width), int(landmark.y * img_height)


def get_polygon_points(landmarks, indices, img_width, img_height):
    return [landmark_to_pixel(landmarks[i], img_width, img_height) for i in indices]


def create_polygon_mask(image_shape, points):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], 255)
    return mask


def restrict_area_by_radius(center, max_radius, coords):
    restricted = []
    for x, y in coords:
        if np.linalg.norm(np.array([x, y]) - np.array(center)) <= max_radius:
            restricted.append((x, y))
    return restricted


def get_circular_pupil_from_filtered_pixels(image, iris_points, pupil_point, iris_coords, pupil_color, color_threshold=30, max_ratio=0.5):
    # 1. Фильтрация по цвету
    similar_pixels = filter_region_by_color(iris_coords, image, pupil_color, color_threshold)

    if not similar_pixels:
        return [], iris_coords

    # 2. Вычисляем расстояния от zрачка до всех цветово-похожих точек
    distances = [np.linalg.norm(np.array(pupil_point) - np.array(p)) for p in similar_pixels]
    max_found_radius = max(distances)

    # 3. Среднее расстояние от зрачка до границ радужки (по 4 точкам)
    iris_distances = [np.linalg.norm(np.array(pupil_point) - np.array(p)) for p in iris_points]
    max_allowed_radius = np.mean(iris_distances) * max_ratio

    # 4. Ограниченный радиус
    radius = min(max_found_radius, max_allowed_radius)

    # 5. Строим маску круга с центром в зрачке
    h, w = image.shape[:2]
    pupil_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(pupil_mask, pupil_point, int(radius), 255, -1)

    # 6. Определяем пиксели зрачка и радужки без зрачка
    pupil_area = [(x, y) for (x, y) in iris_coords if pupil_mask[y, x] == 255]
    iris_without_pupil = list(set(iris_coords) - set(pupil_area))

    return pupil_area, iris_without_pupil


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

    print("=== Температура цвета (color temperature) ===")
    print(f"Hair: {hair_temp}")
    print(f"Face: {face_temp}")
    print(f"Eyes: {eyes_temp}")

    print("\n=== Интенсивность цвета (color intensity) ===")
    print(f"Hair: {hair_intensity:.2f}")
    print(f"Face: {face_intensity:.2f}")
    print(f"Eyes: {eyes_intensity:.2f}")

    print("\n=== Яркость (brightness) ===")
    print(f"Hair: {hair_brightness:.2f}")
    print(f"Face: {face_brightness:.2f}")
    print(f"Eyes: {eyes_brightness:.2f}")

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

        left_iris_indices = [469, 470, 471, 472]
        right_iris_indices = [474, 475, 476, 477]
        left_pupil = landmark_to_pixel(landmarks[468], w, h)
        right_pupil = landmark_to_pixel(landmarks[473], w, h)

        eye_colors = []
        for eye_label, iris_indices, pupil_point in [
            ("Left", left_iris_indices, left_pupil),
            ("Right", right_iris_indices, right_pupil)
        ]:
            iris_points = get_polygon_points(landmarks, iris_indices, w, h)

            # Цвет зрачка
            pupil_region = extract_region_color(image, pupil_point, PUPIL_RADIUS)
            pupil_color = get_dominant_color(pupil_region)

            # Маска радужки
            iris_mask = create_polygon_mask(image.shape, iris_points)
            iris_coords = np.column_stack(np.where(iris_mask == 255))
            iris_coords = [(x, y) for y, x in iris_coords]

            # Затем только среди них ищем по цвету
            pupil_area, iris_without_pupil = get_circular_pupil_from_filtered_pixels(
                image, iris_points, pupil_point, iris_coords,
                pupil_color, color_threshold=COLOR_THRESHOLD,
                max_ratio=0.3
            )

            # Радужка без зрачка
            iris_without_pupil = list(set(iris_coords) - set(pupil_area))
            iris_colors = np.array([image[y, x] for (x, y) in iris_without_pupil])
            if len(iris_colors) > 0:
                print(iris_colors)
                iris_color = get_dominant_color(iris_colors)

                eye_colors.append(iris_color)

                print(eye_label, iris_color)

            # Визуализация: контур радужки
            cv2.polylines(image, [np.array(iris_points)], isClosed=True, color=(255, 255, 0), thickness=1)

            # Визуализация: зрачок (красным)
            for (x, y) in pupil_area:
                cv2.circle(image, (x, y), 1, (0, 0, 255), -1)

        eye_rgb = np.mean(eye_colors, axis=0)[::-1]

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
