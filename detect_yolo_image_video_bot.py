from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import tensorflow as tf
from moviepy.editor import VideoFileClip
import os
import logging
from ultralytics import YOLO
import shutil


from object_detection_tracking_EGGS import video_detect   #######переназначить

tf.config.set_visible_devices([], 'GPU')
tf.config.set_visible_devices(tf.config.get_visible_devices('CPU'), 'CPU')

# возьмем переменные окружения из .env
load_dotenv()

# загружаем токен бота
TOKEN = os.environ.get("TOKEN")
model = YOLO('best.pt')
# функция команды /start
async def start(update, context):
    await update.message.reply_text('Привет! Отправь этому боту фотографию или видео с куриными яйцами для распознавания')
    print(start)


# обработчик изображений
async def scan(update, context):
    try:
        shutil.rmtree('runs')
    except:
        pass

    await update.message.reply_text('Мы получили от тебя фотографию. Идет распознавание изображения с яйцами...')
    print(update)
    if update.message.photo:
        imageurl = await update.message.photo[-1].get_file()
    #достаем ссылку на файл изображения из сообщения
    elif update.message.photo != True:
        imageurl = await update.message.document.get_file()
    print(imageurl)
    ## извлекаем изображение в формате bytearray
    #image = await imageurl.download_as_bytearray()
    image = imageurl
    #пишем наше приложение для
    # текстовое сообщение пользователю
    delete_message = await update.message.reply_text('Изображение получено. Идёт обработка...')
    # получение файла из сообщения
    new_file = image
    # имя файла на сервере
    image_name = str(new_file['file_path']).split("/")[-1]
    #наш новый код:
    # скачиваем файл
    await new_file.download_to_drive(image_name)
    sourceImage = f"{image_name[:-4]}.jpg" #!!!old

    # # распознавание объектов !!!old
    # imageout = detect_image_egg(sourceImage)
    # #image3, image4 = testFunc(sourceImage)

    #new code
    model.track(source= sourceImage,     #f"{image_name[:-4]}.jpg",  # путь к файлу
                conf=0.3,  # порог уверенности
                iou=0.5,  # intersection over union
                show=False,  # показывать ли результат
                save=True,  # сохранять ли результат
                classes=(0, 1) )  # классы для распознавания

    # удаляем предыдущее сообщение от бота
    await context.bot.deleteMessage(message_id=delete_message.message_id,
                                    chat_id=update.message.chat_id)

    # отправляем пользователю результат
    await update.message.reply_text('Распознавание объектов завершено')
    await update.message.reply_photo(f"runs/detect/track/{image_name[:-4]}.jpg")

    #удаляем файл после обработки
    os.remove(sourceImage)


# функция обработки видео
async def tracking(update, context):
    try:

        # текстовое сообщение пользователю
        delete_message = await update.message.reply_text('Мы получили от тебя видео. Идёт обработка...')

        # получение файла из сообщения
        new_file = await update.message.video.get_file()

        # имя файла на сервере
        video_name = str(new_file['file_path']).split("/")[-1]

        # скачиваем файл
        await new_file.download_to_drive(video_name)

        # ширина и высота кадров
        height = update.message.video.height
        width = update.message.video.width

        # проверяем формат видео
        if video_name.endswith('MOV'):
            # конвертация видео из формата .mov в .mp4
            video = VideoFileClip(f"{video_name}")
            video.write_videofile(f"{video_name[:-4]}.mp4")
            print("video= ", video, "video_name= ", video_name, "path/= ", f"{video_name[:-4]}.mp4")
        else:
            # обработка случая, когда формат видео не .MOV
            video = VideoFileClip(f"{video_name}")


        print("video1= ", video, "video_name1= ", video_name, "new_file= ", new_file)

        #отправляем в функцию в файле object_detection_tracking_eggs
        textOut, output_video_path = video_detect(video_name)

        await update.message.reply_text('Распознавание объектов произошло///')

        # конвертация видео из формата .mp4 в .mov
        video = VideoFileClip(f"{output_video_path}")

        video.write_videofile(f"{output_video_path[:-4]}_mov.mov", codec='libx264')
        print("video3= ", video, "path/= ", f"{output_video_path[:-4]}_mov.mov")
        # удаляем предыдущее сообщение от бота
        await context.bot.deleteMessage(message_id=delete_message.message_id,
                                        chat_id=update.message.chat_id)

        # отправляем пользователю результат
        await update.message.reply_text('Распознавание объектов завершено успешно --|||-- ')
        await update.message.reply_text(textOut)
        await update.message.reply_video(f"{output_video_path[:-4]}_mov.mov", width=width, height=height)

    except Exception as e:
        # log the exception
        logging.exception(e)
        # send an error message to the user
        await update.message.reply_text('An error occurred. Please try again later.')
    # os.remove("file_47")

def main():

    # точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start, block=False))
    # добавляем обработчик фото
    application.add_handler(MessageHandler(filters.Document.IMAGE, scan, block=False))
    # добавляем обработчик сообщений с изображениями
    application.add_handler(MessageHandler(filters.PHOTO, scan, block=False))
    # добавляем обработчик видеозаписей
    application.add_handler(MessageHandler(filters.VIDEO, tracking))
    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()


if __name__ == "__main__":
    main()