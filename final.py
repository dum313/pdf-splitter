# 📦 Импортируем нужные библиотеки
import os
import re
import sys
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, filedialog


def main():
    """Split PDF into separate files using OCR for naming."""
    # 🧭 Указываем путь к poppler (требуется для pdf2image)
    poppler_path = os.path.join(
        os.path.dirname(__file__),
        "poppler-24.08.0",
        "Library",
        "bin",
    )
    # Если указана переменная окружения POPPLER_PATH, используем её
    env_poppler = os.getenv("POPPLER_PATH")
    if env_poppler:
        poppler_path = env_poppler

    # Если задан путь к Tesseract через TESSERACT_CMD, передаём его pytesseract
    env_tesseract = os.getenv("TESSERACT_CMD")
    if env_tesseract:
        pytesseract.pytesseract.tesseract_cmd = env_tesseract

    # 🔕 Отключаем главное окно tkinter (оно нам не нужно)
    Tk().withdraw()

    # 📂 Открываем стандартное окно выбора PDF-файла
    source_pdf = filedialog.askopenfilename(
        title="Выберите PDF-файл для обработки",
        filetypes=[("PDF файлы", "*.pdf")],
    )

    # 🚫 Если пользователь нажал "Отмена" или не выбрал файл — выходим
    if not source_pdf:
        print("Файл не выбран. Завершение работы.")
        sys.exit()

    # 📁 Получаем имя файла без расширения
    pdf_name = os.path.splitext(os.path.basename(source_pdf))[0]

    # 🛠️ Создаём выходную папку рядом с исходным PDF-файлом
    output_folder = os.path.join(os.path.dirname(source_pdf), pdf_name)
    os.makedirs(output_folder, exist_ok=True)

    # 📖 Читаем PDF-файл
    reader = PdfReader(source_pdf)

    # 🖼️ Преобразуем PDF в изображения
    images = convert_from_path(source_pdf, dpi=300, poppler_path=poppler_path)

    # 🔍 Регулярное выражение для поиска ID (например, CICU6332694P)
    flex_pattern = re.compile(r"([A-Z]{4})([A-Z]?)(\d{7})([P])")

    # ✂️ Область, где обычно написан ID на скане (снизу страницы)
    crop_area = (0, 1900, 1000, 2300)

    # ▶️ Обрабатываем все страницы по порядку
    i = 0
    while i < len(reader.pages):
        # 🖼️ Берём текущую страницу и вырезаем нужную область
        image = images[i]
        cropped_image = image.crop(crop_area)

        # 🔡 Распознаём текст (OCR) и очищаем от мусора
        text = pytesseract.image_to_string(cropped_image)
        text_clean = re.sub(r"[\s()\-\n]+", "", text.upper())

        # 🧠 Пытаемся найти ID на странице
        match = flex_pattern.search(text_clean)
        if match:
            part1, extra_letter, part2, last_letter = match.groups()
            identifier = part1 + part2
        else:
            identifier = f"unknown_{i + 1}"
            print(f"⚠️ Страница {i+1}: ID не найден → '{text_clean}'")

        # 📄 Создаём временный PDF-файл
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        # 🔄 Проверяем, не идёт ли дополнительная страница после
        if i + 1 < len(reader.pages):
            next_image = images[i + 1].crop(crop_area)
            next_text = pytesseract.image_to_string(next_image)
            next_clean = re.sub(r"[\s()\-\n]+", "", next_text.upper())

            # Если ID не найден — добавляем как продолжение
            if not flex_pattern.search(next_clean):
                writer.add_page(reader.pages[i + 1])
                i += 2
            else:
                i += 1
        else:
            i += 1

        # 💾 Сохраняем результат в отдельный PDF
        output_path = os.path.join(output_folder, f"{identifier}.pdf")
        with open(output_path, "wb") as out_pdf:
            writer.write(out_pdf)

        print(f"✅ Создан файл: {output_path}")


if __name__ == "__main__":
    main()
