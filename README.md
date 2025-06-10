# PDF Splitter with OCR

**PDF Splitter with OCR** — инструмент для разделения многостраничных PDF-документов на отдельные файлы. Каждая страница преобразуется в изображение, обрабатывается Tesseract OCR, из текста извлекается уникальный идентификатор и страница сохраняется в отдельный PDF с этим именем.

Если при сохранении обнаруживается файл с таким названием, программа добавит суффикс `_1`, `_2` и т.д., сообщив об этом в консоль.

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
  - Установите Poppler так, чтобы утилита `pdftoppm` находилась в системной переменной `PATH`. Если она доступна, скрипт определит Poppler автоматически.
  - Windows: скачайте архив на странице [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases), распакуйте его в удобное место и добавьте подкаталог `bin` в `PATH`.
  - Linux/MacOS: установите Poppler через пакетный менеджер (`apt install poppler-utils` или `brew install poppler`).
  - При необходимости путь к Poppler можно задать вручную через переменную окружения `POPPLER_PATH`.
- **Tesseract OCR**
   - Windows: скачайте установщик с [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) или установите `choco install tesseract`.
   - Linux/MacOS: `apt install tesseract-ocr` или `brew install tesseract`.
   Если исполняемый файл не находится в `PATH`, пропишите его путь в `pytesseract.pytesseract.tesseract_cmd` внутри `final.py`
   или задайте переменную окружения `TESSERACT_CMD` с этим путём.

После установки Poppler и Tesseract запустите скрипт ещё раз, чтобы разделить PDF на страницы.
