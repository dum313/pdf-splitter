# 📦 Импортируем нужные библиотеки
import os                   # Для работы с файлами и путями
import re                   # Для работы с регулярными выражениями (поиск ID)
import pytesseract          # Для OCR — распознавания текста на изображениях
from pdf2image import convert_from_path  # Конвертация PDF в изображения
from PyPDF2 import PdfReader, PdfWriter  # Для чтения и создания PDF
from tkinter import Tk, filedialog       # Для открытия окна выбора файла

# 🔹 Отключаем главное окно tkinter (оно не нужно)
Tk().withdraw()

# 🔹 Открываем диалоговое окно для выбора PDF-файла
source_pdf = filedialog.askopenfilename(
    title="Выберите PDF-файл для обработки",
    filetypes=[("PDF файлы", "*.pdf")]
)

# ❌ Если пользователь ничего не выбрал — завершаем работу
if not source_pdf:
    print("Файл не выбран. Завершение.")
    exit()

# 🔹 Генерируем имя папки на основе имени выбранного PDF-файла
# Пример: если файл называется fail1.pdf → папка будет "fail1"
pdf_name = os.path.splitext(os.path.basename(source_pdf))[0]
output_folder = pdf_name
os.makedirs(output_folder, exist_ok=True)

# 🔹 Загружаем PDF-файл
reader = PdfReader(source_pdf)

# 🔹 Конвертируем каждую страницу PDF в изображение (300 dpi — хорошее качество для OCR)
images = convert_from_path(source_pdf, dpi=300)

# 🔹 Регулярное выражение для поиска ID в формате:
# 4 буквы → опц. 1 буква → 7 цифр → буква P (пример: CICU6332694P)
flex_pattern = re.compile(r"([A-Z]{4})([A-Z]?)(\d{7})([P])")

# 🔹 Координаты области, где обычно расположен ID на сканах
# (левый край, верхний край, правый край, нижний край)
crop_area = (0, 1900, 1000, 2300)

# 🔹 Начинаем поочерёдно обрабатывать страницы
i = 0
while i < len(reader.pages):
    # --- Обрабатываем текущую страницу ---
    image = images[i]
    cropped_image = image.crop(crop_area)  # Вырезаем нужную область
    text = pytesseract.image_to_string(cropped_image)  # Распознаём текст
    text_clean = re.sub(r"[\s()\-\n]+", "", text.upper())  # Удаляем пробелы и лишние символы

    # 🔍 Ищем ID на странице
    match = flex_pattern.search(text_clean)
    if match:
        part1, extra_letter, part2, last_letter = match.groups()
        identifier = part1 + part2  # Например: CICU6332694
    else:
        identifier = f"unknown_{i+1}"  # Если ID не найден
        print(f"Стр.{i+1}: ID не найден → '{text_clean}'")

    # --- Создаём новый PDF-файл и добавляем туда текущую страницу ---
    writer = PdfWriter()
    writer.add_page(reader.pages[i])

    # --- Проверяем следующую страницу ---
    if i + 1 < len(reader.pages):
        next_image = images[i+1].crop(crop_area)
        next_text = pytesseract.image_to_string(next_image)
        next_clean = re.sub(r"[\s()\-\n]+", "", next_text.upper())

        # Если на следующей странице НЕТ ID — она дополнительная
        if not flex_pattern.search(next_clean):
            writer.add_page(reader.pages[i+1])  # Добавляем её тоже
            i += 2  # Переходим сразу через 2 страницы
        else:
            i += 1  # Следующая страница — самостоятельная
    else:
        # Последняя страница — одиночная
        i += 1

    # --- Сохраняем результат в файл ---
    output_path = os.path.join(output_folder, f"{identifier}.pdf")
    with open(output_path, "wb") as out_pdf:
        writer.write(out_pdf)

    print(f"✅ Создан файл: {output_path}")
