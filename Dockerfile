FROM python:3.12.2

# Установим рабочую директорию внутри контейнера
WORKDIR /bot

# Скопируем все файлы в рабочую директорию
COPY . .

# Обновим setuptools и установим необходимые зависимости
RUN pip3 install --upgrade setuptools
RUN pip3 install aiogram paho-mqtt python-dotenv

# Установим CMD для запуска приложения
CMD ["python", "run.py"]