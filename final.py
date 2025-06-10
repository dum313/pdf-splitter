# 📦 Импортируем нужные библиотеки
import os  # Работа с файлами и путями (например, создаём папки, получаем имена файлов)
import argparse  # Парсинг аргументов командной строки
import re  # Работа с текстом — поиск нужного шаблона (ID) с помощью регулярных выражений
import sys
import pytesseract  # Это OCR — умеет распознавать текст на картинках (например, сканы PDF)
from pdf2image import convert_from_path  # Преобразует PDF-страницы в изображения
from PyPDF2 import PdfReader, PdfWriter  # Чтение и создание PDF-файлов
from tkinter import Tk, filedialog  # Открывает окно выбора файла

# 🔧 Читаем аргументы командной строки
parser = argparse.ArgumentParser(description="Split PDF by pages using OCR")
parser.add_argument(
    "--poppler-path",
    dest="poppler_path",
    help="Путь к бинарникам poppler (если отличается от стандартного)",
)
args = parser.parse_args()

# 🧭 Указываем путь к poppler (требуется для pdf2image) — ищем его рядом с final.exe
default_poppler = os.path.join(
    os.path.dirname(__file__),  # Получаем папку, где лежит этот скрипт или .exe
    "poppler-24.08.0",          # Это папка, которую ты положил рядом с программой
    "Library",
    "bin",                       # Там находится нужный файл pdfinfo.exe
)
poppler_path = args.poppler_path or default_poppler

# 🔕 Отключаем главное окно tkinter (оно нам не нужно, хотим только диалог выбора файла)
Tk().withdraw()

# 📂 Открываем стандартное окно выбора PDF-файла
source_pdf = filedialog.askopenfilename(
    title="Выберите PDF-файл для обработки",
    filetypes=[("PDF файлы", "*.pdf")]  # Ограничиваем выбор только PDF-файлами
)

# 🚫 Если пользователь нажал "Отмена" или не выбрал файл — выходим из программы
if not source_pdf:
    print("Файл не выбран. Завершение работы.")
    sys.exit()

# 📁 Получаем имя файла без расширения, чтобы использовать как имя выходной папки
pdf_name = os.path.splitext(os.path.basename(source_pdf))[0]

# 🛠️ Создаём выходную папку рядом с исходным PDF-файлом
output_folder = os.path.join(os.path.dirname(source_pdf), pdf_name)
os.makedirs(output_folder, exist_ok=True)  # Если папки нет — создаст, если есть — ничего страшного

# 📖 Читаем PDF-файл
reader = PdfReader(source_pdf)

# 🖼️ Преобразуем PDF в изображения (300 dpi — оптимальное качество для OCR)
images = convert_from_path(source_pdf, dpi=300, poppler_path=poppler_path)

# 🔍 Регулярное выражение для поиска ID (например, CICU6332694P)
# Шаблон: 4 заглавные буквы, опц. ещё 1 буква, 7 цифр и буква P
flex_pattern = re.compile(r"([A-Z]{4})([A-Z]?)(\d{7})([P])")

# ✂️ Область, где обычно написан ID на скане (снизу страницы)
# Значения подобраны вручную: (левая, верхняя, правая, нижняя граница)
crop_area = (0, 1900, 1000, 2300)

# ▶️ Обрабатываем все страницы по порядку
i = 0
while i < len(reader.pages):
    # 🖼️ Берём текущую страницу и вырезаем нужную область
    image = images[i]
    cropped_image = image.crop(crop_area)

    # 🔡 Распознаём текст (OCR) и очищаем от мусора
    text = pytesseract.image_to_string(cropped_image)
    text_clean = re.sub(r"[\s()\-\n]+", "", text.upper())  # Удаляем пробелы и символы

    # 🧠 Пытаемся найти ID на странице
    match = flex_pattern.search(text_clean)
    if match:
        part1, extra_letter, part2, last_letter = match.groups()
        identifier = part1 + part2  # Получаем, например: CICU6332694
    else:
        identifier = f"unknown_{i+1}"  # Если ID не найден
        print(f"⚠️ Страница {i+1}: ID не найден → '{text_clean}'")

    # 📄 Создаём временный PDF-файл
    writer = PdfWriter()
    writer.add_page(reader.pages[i])  # Добавляем текущую страницу

    # 🔄 Проверяем, не идёт ли дополнительная страница после
    if i + 1 < len(reader.pages):
        next_image = images[i + 1].crop(crop_area)
        next_text = pytesseract.image_to_string(next_image)
        next_clean = re.sub(r"[\s()\-\n]+", "", next_text.upper())

        # Если ID не найден — добавляем как продолжение
        if not flex_pattern.search(next_clean):
            writer.add_page(reader.pages[i + 1])
            i += 2  # Переходим на 2 страницы вперёд
        else:
            i += 1  # Переходим на следующую страницу
    else:
        i += 1  # Последняя страница

    # 💾 Сохраняем результат в отдельный PDF
    output_path = os.path.join(output_folder, f"{identifier}.pdf")
    with open(output_path, "wb") as out_pdf:
        writer.write(out_pdf)

    print(f"✅ Создан файл: {output_path}")
