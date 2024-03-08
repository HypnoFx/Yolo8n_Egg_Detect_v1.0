pip install -r requirements.txt
file .env содержит токен тг бота
файл best.pt файл модели eggs detect,  это веса и сама модель
файл detect_yolo_video_bot телеграм бот - обработчик событий тг
файл helper.py трогать не нужно - это обработчик видео
файл object_detection_tracking - исходный файл обработчик он не участвует в процессе с него просто взят код
файл object_detection_tracjing_EGGS файл обработчик присылаемого видео в функции def video_detect(video_name)
файл requirements.txt - установленные зависимости
файл pip.txt что ставилось
файл yolo8s.pt неиспользуемая модель старая
в папке config/ используется coco_eggs.names, coco.names не используется
