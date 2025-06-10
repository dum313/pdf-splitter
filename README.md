# PDF Splitter with OCR

**PDF Splitter with OCR** — инструмент для разделения многостраничных PDF-документов на отдельные файлы. Каждая страница преобразуется в изображение, обрабатывается Tesseract OCR, из текста извлекается уникальный идентификатор и страница сохраняется в отдельный PDF с этим именем.

## Быстрый старт

1. Создайте виртуальное окружение. Пример для Linux/MacOS:
   ```bash
   python3 -m venv venv
   ```
   Для Windows:
   ```cmd
   py -3 -m venv venv
   ```
2. Активируйте его:
   - Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```
   - Windows (cmd):
     ```cmd
     venv\Scripts\activate
     ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Запустите программу:
   ```bash
   python final.py
   ```
   Откроется диалог выбора исходного PDF, а готовые страницы будут сохранены в папке рядом с оригиналом.


```bash
source venv_tk/bin/activate
```

## Лицензия

Проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE).

## Poppler и Tesseract

Для работы скрипта требуются Poppler (для `pdf2image`) и Tesseract OCR.

- **Poppler**
  - Windows: скачайте архив на странице [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) и распакуйте рядом с `final.py` (папка `poppler-24.08.0` уже указана в коде) либо добавьте путь к `bin` в переменную окружения `PATH` и измените переменную `poppler_path` в `final.py`.
  - Linux/MacOS: установите через пакетный менеджер (`apt install poppler-utils` или `brew install poppler`).
- **Tesseract OCR**
  - Windows: скачайте установщик с [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) или установите `choco install tesseract`.
  - Linux/MacOS: `apt install tesseract-ocr` или `brew install tesseract`.
  Если исполняемый файл не находится в `PATH`, пропишите его путь в `pytesseract.pytesseract.tesseract_cmd` внутри `final.py`.

После установки Poppler и Tesseract запустите скрипт ещё раз, чтобы разделить PDF на страницы.
