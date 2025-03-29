# 📦 Импортируем нужные библиотеки
import os  # Для работы с файлами, путями и папками
import re  # Для поиска ID с помощью регулярных выражений
import pytesseract  # Для распознавания текста на изображениях (OCR)
from pdf2image import convert_from_path  # Преобразование PDF в изображения
from PyPDF2 import PdfReader, PdfWriter  # Для чтения и создания PDF-файлов
from tkinter import Tk, filedialog  # Для открытия окна выбора файла

# 🔧 Указываем путь к Poppler (он идёт в комплекте с установщиком)
# Папка poppler-24.08.0 должна быть рядом с final.exe
poppler_path = os.path.join(
    os.path.dirname(__file__),  # Получаем папку, где находится .exe
    "poppler-24.08.0",
    "Library",
    "bin",  # Внутри неё ищем bin с pdfinfo.exe
)

# 🔹 Отключаем основное окно tkinter (чтобы не появлялось)
Tk().withdraw()

# 🔹 Открываем диалоговое окно для выбора PDF-файла
source_pdf = filedialog.askopenfilename(
    title="Выберите PDF-файл для обработки",  # Заголовок окна
    filetypes=[("PDF файлы", "*.pdf")],  # Ограничим выбор только PDF
)

# ❌ Если пользователь закрыл окно или не выбрал файл
if not source_pdf:
    print("Файл не выбран. Завершение.")
    exit()

# 📁 Создаём выходную папку в той же директории, где был PDF
# Пример: C:\Docs\fail1.pdf → C:\Docs\fail1\
pdf_name = os.path.splitext(os.path.basename(source_pdf))[0]  # Берём имя файла без .pdf
output_folder = os.path.join(
    os.path.dirname(source_pdf), pdf_name
)  # Папка рядом с исходным PDF
os.makedirs(output_folder, exist_ok=True)  # Создаём её (если ещё нет)

# 📖 Загружаем PDF-файл
reader = PdfReader(source_pdf)

# 🖼️ Конвертируем PDF в изображения (300 dpi = хорошее качество)
# Обязательно указываем путь к Poppler
images = convert_from_path(source_pdf, dpi=300, poppler_path=poppler_path)

# 🔎 Регулярка для поиска ID — формат:
# 4 заглавные буквы, опциональная буква, 7 цифр, буква "P"
# Пример: RPSU6332694P или CICU6332694P
flex_pattern = re.compile(r"([A-Z]{4})([A-Z]?)(\d{7})([P])")

# 🧾 Область, где на сканах обычно написан этот ID (обрезаем нижнюю часть страницы)
crop_area = (0, 1900, 1000, 2300)  # (левая, верхняя, правая, нижняя границы)

# ▶️ Начинаем обработку всех страниц по порядку
i = 0
while i < len(reader.pages):
    # --- Обрабатываем текущую страницу ---
    image = images[i]  # Получаем изображение текущей страницы
    cropped_image = image.crop(crop_area)  # Вырезаем нижнюю часть (где ID)
    text = pytesseract.image_to_string(
        cropped_image
    )  # Распознаём текст через Tesseract
    text_clean = re.sub(
        r"[\s()\-\n]+", "", text.upper()
    )  # Удаляем пробелы, символы и делаем заглавным

    # 🔍 Пытаемся найти ID
    match = flex_pattern.search(text_clean)
    if match:
        part1, extra_letter, part2, last_letter = match.groups()
        identifier = part1 + part2  # Например: CICU6332694
    else:
        identifier = f"unknown_{i+1}"  # Если не нашли ID
        print(f"Стр.{i+1}: ID не найден → '{text_clean}'")

    # 📄 Создаём PDF-файл, куда будем сохранять страницу (или пару)
    writer = PdfWriter()
    writer.add_page(reader.pages[i])  # Добавляем текущую страницу

    # --- Проверим, нужна ли следующая страница ---
    if i + 1 < len(reader.pages):
        # Вырезаем и распознаём текст на следующей странице
        next_image = images[i + 1].crop(crop_area)
        next_text = pytesseract.image_to_string(next_image)
        next_clean = re.sub(r"[\s()\-\n]+", "", next_text.upper())

        # Если ID не найден — это дополнительная страница (например, продолжение инструкции)
        if not flex_pattern.search(next_clean):
            writer.add_page(reader.pages[i + 1])  # Добавляем и её
            i += 2  # Пропускаем сразу 2 страницы
        else:
            i += 1  # Идём к следующей отдельно
    else:
        i += 1  # Последняя страница

    # 💾 Сохраняем результат в выходную папку
    output_path = os.path.join(output_folder, f"{identifier}.pdf")
    with open(output_path, "wb") as out_pdf:
        writer.write(out_pdf)

    print(f"✅ Создан файл: {output_path}")
