# 📦 Импортируем нужные библиотеки
import os
import re
import sys
import shutil
import argparse
import glob
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, filedialog
from tqdm import tqdm

# 🔍 Регулярное выражение для поиска ID (например, CICU6332694P)
flex_pattern = re.compile(r"([A-Z]{4})([A-Z]?)(\d{7})([P])")


def search_common_paths(name: str) -> str | None:
    """Return executable path from typical install directories."""
    candidates = []
    if os.name == "nt":
        if name == "tesseract":
            candidates.extend(
                [
                    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                    r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
                ]
            )
        if name == "pdftoppm":
            candidates.extend(
                [
                    r"C:\\Program Files\\poppler\\bin\\pdftoppm.exe",
                    r"C:\\Program Files (x86)\\poppler\\bin\\pdftoppm.exe",
                ]
            )
            candidates.extend(
                glob.glob(
                    r"C:\\Program Files\\poppler-*\\Library\\bin\\pdftoppm.exe"
                )
            )
            candidates.extend(
                glob.glob(
                    r"C:\\Program Files (x86)\\poppler-*\\Library\\bin\\pdftoppm.exe"
                )
            )
    else:
        for base in ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]:
            candidates.append(os.path.join(base, name))

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def extract_identifier(text: str) -> str:
    """Return cleaned identifier from OCR text or empty string."""

    text_clean = re.sub(r"[\s()\-\n]+", "", text.upper())
    match = flex_pattern.search(text_clean)
    if match:
        part1, _extra_letter, part2, _last_letter = match.groups()
        return part1 + part2
    return ""


def main():
    """Split PDF into separate files using OCR for naming."""

    # 🔍 Проверяем доступность необходимых утилит
    tesseract_cmd = shutil.which("tesseract")
    pdftoppm_cmd = shutil.which("pdftoppm")
    pdftoppm_in_path = pdftoppm_cmd is not None
    if not tesseract_cmd:
        tesseract_cmd = search_common_paths("tesseract")
    if not pdftoppm_cmd:
        pdftoppm_cmd = search_common_paths("pdftoppm")

    if not tesseract_cmd and not os.getenv("TESSERACT_CMD"):
        print(
            "⚠️ Tesseract OCR не найден. "
            "Установите Tesseract или задайте "
            "переменную окружения TESSERACT_CMD."
        )
        sys.exit(1)

    if not pdftoppm_cmd and not os.getenv("POPPLER_PATH"):
        print(
            "⚠️ Утилита pdftoppm не найдена. "
            "Установите Poppler, добавьте путь к pdftoppm в PATH "
            "или задайте переменную окружения POPPLER_PATH."
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Split PDF into separate files using OCR for naming."
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Путь к исходному PDF-файлу",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Директория для сохранения страниц",
    )
    args = parser.parse_args()

    # 🧭 Путь к Poppler по умолчанию не указан
    poppler_path = None

    # Если указана переменная окружения POPPLER_PATH, используем её
    env_poppler = os.getenv("POPPLER_PATH")
    if env_poppler:
        poppler_path = env_poppler
    elif pdftoppm_cmd and not pdftoppm_in_path:
        poppler_path = os.path.dirname(pdftoppm_cmd)
    # Попытка использовать локальную копию Poppler больше не предпринимается

    # Если задан путь к Tesseract через TESSERACT_CMD, передаём его pytesseract
    env_tesseract = os.getenv("TESSERACT_CMD")
    if env_tesseract:
        pytesseract.pytesseract.tesseract_cmd = env_tesseract
    elif tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    needs_gui = not args.input or not args.output
    if needs_gui:
        # 🔕 Отключаем главное окно tkinter (оно нам не нужно)
        Tk().withdraw()

    # 📂 Определяем исходный PDF
    if args.input:
        source_pdf = args.input
    else:
        source_pdf = filedialog.askopenfilename(
            title="Выберите PDF-файл для обработки",
            filetypes=[("PDF файлы", "*.pdf")],
        )
        if not source_pdf:
            print("Файл не выбран. Завершение работы.")
            sys.exit()

    # 📁 Получаем имя файла без расширения
    pdf_name = os.path.splitext(os.path.basename(source_pdf))[0]

    # 🗂️ Папка для сохранения результатов
    if args.output:
        chosen_dir = args.output
    else:
        chosen_dir = filedialog.askdirectory(
            title="Куда сохранить результат",
            initialdir=os.path.dirname(source_pdf),
        )
        if not chosen_dir:
            # Если папка не выбрана, используем папку рядом с исходным файлом
            chosen_dir = os.path.dirname(source_pdf)

    # 🛠️ Создаём выходную папку внутри выбранной директории
    output_folder = os.path.join(chosen_dir, pdf_name)
    os.makedirs(output_folder, exist_ok=True)

    # 📖 Читаем PDF-файл
    reader = PdfReader(source_pdf)

    # ✂️ Область, где обычно написан ID на скане (снизу страницы)
    crop_area = (0, 1900, 1000, 2300)

    # ▶️ Обрабатываем все страницы по порядку
    i = 0
    total_pages = len(reader.pages)
    progress_bar = tqdm(total=total_pages, desc="Обработка", unit="стр.")
    while i < total_pages:
        processed_pages = 1
        # 🖼️ Загружаем изображение текущей страницы
        current_image = convert_from_path(
            source_pdf,
            dpi=300,
            poppler_path=poppler_path,
            first_page=i + 1,
            last_page=i + 1,
        )[0]
        cropped_image = current_image.crop(crop_area)

        # 🔡 Распознаём текст (OCR)
        text = pytesseract.image_to_string(cropped_image)

        # 🧠 Извлекаем ID со страницы
        identifier = extract_identifier(text)
        if not identifier:
            text_clean = re.sub(r"[\s()\-\n]+", "", text.upper())
            identifier = f"unknown_{i + 1}"
            print(f"⚠️ Страница {i+1}: ID не найден → '{text_clean}'")

        # 📄 Создаём временный PDF-файл
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        # 🔄 Проверяем, не идёт ли дополнительная страница после
        if i + 1 < total_pages:
            next_image = convert_from_path(
                source_pdf,
                dpi=300,
                poppler_path=poppler_path,
                first_page=i + 2,
                last_page=i + 2,
            )[0].crop(crop_area)
            next_text = pytesseract.image_to_string(next_image)
            next_clean = re.sub(r"[\s()\-\n]+", "", next_text.upper())

            # Если ID не найден — добавляем как продолжение
            if not flex_pattern.search(next_clean):
                writer.add_page(reader.pages[i + 1])
                i += 2
                processed_pages = 2
            else:
                i += 1
        else:
            i += 1

        # 💾 Сохраняем результат в отдельный PDF
        output_path = os.path.join(output_folder, f"{identifier}.pdf")

        # If file exists, append counter suffix until name is unique
        if os.path.exists(output_path):
            base, ext = os.path.splitext(output_path)
            counter = 1
            new_output_path = f"{base}_{counter}{ext}"
            while os.path.exists(new_output_path):
                counter += 1
                new_output_path = f"{base}_{counter}{ext}"
            print(
                "ℹ️ Имя файла изменено из-за дубликата:",
                f"{os.path.basename(output_path)} -> "
                f"{os.path.basename(new_output_path)}",
            )
            output_path = new_output_path

        with open(output_path, "wb") as out_pdf:
            writer.write(out_pdf)

        print(f"✅ Создан файл: {output_path}")
        progress_bar.update(processed_pages)

    progress_bar.close()


if __name__ == "__main__":
    main()
