# Лабораторная работа №4: Анализ и визуализация данных

Вариант **1**: добавление колонки с длиной каждого изображения (`image_length`), сортировка, фильтрация и построение гистограммы по всем отсортированным данным с помощью `matplotlib`.

## 1. Структура проекта

```text
lab4/
├── src/lab4/
│   ├── dataset.py         # DataFrame, image_length, сортировка, фильтрация, сохранение CSV
│   ├── visualization.py   # Построение и сохранение гистограммы (matplotlib)
│   └── main.py            # Точка входа CLI и обработка ошибок
├── tests/
│   └── test_lab4.py       # Тесты (pytest)
├── dataset/               # Сюда положить фото из 2-й лабы (создаётся вручную)
├── annotations.csv        # Сюда положить CSV из 2-й лабы (если есть)
├── requirements.txt
└── pyproject.toml
```

## 2. Настройка окружения (Windows PowerShell)

Все команды ниже выполняются из корня папки `lab4`.

### Шаг 1. Создайте виртуальное окружение `.venv`

> Не переносите папку `.venv` из других проектов — при переносе пути внутри неё ломаются. Если `.venv` уже была скопирована или работает некорректно, сначала удалите её: `Remove-Item -Recurse -Force .venv`.

```powershell
python -m venv .venv
```

### Шаг 2. Активируйте `.venv`

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell блокирует скрипт с ошибкой `PSSecurityException`:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

### Шаг 3. Установите зависимости в `.venv`

Используйте `.\.venv\Scripts\python -m pip`, чтобы пакеты гарантированно установились именно в виртуальное окружение, а не в глобальный Python:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Убедиться, что команда `python` указывает на `.venv`:

```powershell
.\.venv\Scripts\python -c "import sys, cv2, pandas, matplotlib; print(sys.executable)"
```

## 3. Подготовка данных

1. Создайте папку `lab4\dataset\` и скопируйте туда изображения из 2-й лабораторной (не внутрь `src\lab4\`).
2. Если у вас есть CSV-аннотация из 2-й лабораторной, положите её как `lab4\annotations.csv`.

## 4. Запуск программы

Перед запуском укажите путь к исходникам `src`:

```powershell
$env:PYTHONPATH="src"
```

Запуск по папке с изображениями:

```powershell
.\.venv\Scripts\python -m lab4.main --images-dir dataset --output-csv result.csv --output-plot hist.png --min-length 100 --max-length 500
```

Запуск по CSV-аннотации из 2-й лабораторной:

```powershell
.\.venv\Scripts\python -m lab4.main --annotation annotations.csv --output-csv result.csv --output-plot hist.png --min-length 100 --max-length 500
```

### Основные параметры CLI

- `--images-dir` / `--annotation` — источник данных (папка с фото или CSV-аннотация).
- `--output-csv` — куда сохранить итоговый отсортированный DataFrame (по умолчанию `output/dataset_sorted.csv`).
- `--output-plot` — куда сохранить гистограмму (по умолчанию `output/length_histogram.png`).
- `--min-length`, `--max-length` — границы фильтрации по длине изображения.
- `--descending` — сортировка по убыванию длины.
- `--bins` — количество столбцов гистограммы (по умолчанию `10`).
- `--no-show` — сохранить график без открытия окна `matplotlib`.

## 5. Тесты и проверка кода

```powershell
$env:PYTHONPATH="src"
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src
.\.venv\Scripts\python -m ruff check .
```

## 6. Частые ошибки

- **`ModuleNotFoundError: No module named 'cv2'` (или `pandas` / `matplotlib`)**
  В выводе ошибки виден путь вида `C:\Users\...\Python310\...` вместо `.venv` или зависимости не установлены в текущее окружение. Пересоздайте `.venv`, установите пакеты через `.\.venv\Scripts\python -m pip install -r requirements.txt` и запускайте скрипт через `.\.venv\Scripts\python -m lab4.main ...`.
- **`Activate.ps1 cannot be loaded` (`PSSecurityException`)**
  Выполните `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` или запускайте команды напрямую через `.\.venv\Scripts\python`.

