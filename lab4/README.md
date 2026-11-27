# Лабораторная работа №4: Анализ и визуализация данных

Вариант **1**: добавление колонки с длиной каждого изображения (`image_length`), сортировка, фильтрация и построение гистограммы по всем отсортированным данным через `matplotlib`.

## Структура

- `src/lab4/dataset.py` — загрузка путей из аннотации или папки, именование колонок, добавление длины изображения, сортировка, фильтрация и сохранение CSV
- `src/lab4/visualization.py` — построение и сохранение гистограммы в `matplotlib`
- `src/lab4/main.py` — точка входа CLI и обработка исключений
- `tests/test_lab4.py` — тесты (`pytest`)

## Установка и проверка (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

pytest
mypy src
ruff check .
```

Если PowerShell блокирует `Activate.ps1` (`PSSecurityException`):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```
Либо без активации: `.\.venv\Scripts\python -m pip install -r requirements.txt` и `.\.venv\Scripts\python -m pytest`.

## Пример запуска

```powershell
$env:PYTHONPATH="src"

# Вариант 1: по CSV-аннотации из 2-й лабы
python -m lab4.main --annotation annotations.csv --output-csv result.csv --output-plot hist.png --min-length 100 --max-length 500

# Вариант 2: напрямую по папке с изображениями
python -m lab4.main --images-dir dataset --output-csv result.csv --output-plot hist.png
```
