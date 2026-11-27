# Лабораторная работа №3: Работа с многомерными массивами

Вариант **1: (1, 4, 10)** — обработка изображений с помощью **NumPy**, **OpenCV** и **Matplotlib**:
1. **1** — обрезка изображения от левого верхнего угла до заданных размеров (`--width`, `--height`).
2. **4** — поворот изображения на заданный угол (`--angle`).
3. **10** — полупрозрачное наложение второго изображения поверх первого (`--overlay`, `--alpha`).

## Структура

- `src/lab3/transforms.py` — функции преобразований `(1, 4, 10)` над `numpy`-массивами
- `src/lab3/main.py` — чтение и сохранение файлов (`cv2`), вывод размера, визуализация в `matplotlib`, разбор аргументов CLI
- `tests/test_lab3.py` — тесты (`pytest`)

## Установка и запуск (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

pytest
mypy src
ruff check .
```

## Пример запуска

```powershell
$env:PYTHONPATH="src"
python -m lab3.main `
  --input input.jpg `
  --overlay watermark.jpg `
  --output result.jpg `
  --width 400 `
  --height 300 `
  --angle 45 `
  --alpha 0.4
```
