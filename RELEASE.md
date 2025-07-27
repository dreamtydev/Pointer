# 📦 Создание релиза

## Шаги для создания релиза:

### 1. Сборка проекта
```bash
python build.py
```

### 2. Создание архива
После успешной сборки в папке `dist/pointer_app/` будет готовый EXE файл.

Создайте архив `Pointer-Release.zip` со следующим содержимым:
```
Pointer-Release.zip
└── pointer_app/
    ├── pointer_app.exe
    ├── icon.ico
    ├── src/
    │   └── assets/
    │       ├── default.png
    │       ├── default_reverse.png
    │       ├── knock.wav
    │       └── hold.wav
    └── (все остальные файлы из dist/pointer_app/)
```

### 3. Загрузка на GitHub
1. Перейдите в раздел **Releases** на GitHub
2. Нажмите **"Create a new release"**
3. Заполните:
   - **Tag version**: `v1.0.0`
   - **Release title**: `Pointer v1.0.0`
   - **Description**: описание изменений
4. Загрузите архив `Pointer-Release.zip`
5. Опубликуйте релиз

### 4. Обновление README
Убедитесь, что в README.md указана ссылка на последний релиз.

## Структура релиза:
- **EXE файл** - готовое приложение
- **Ассеты** - изображения и звуки
- **Иконка** - иконка приложения
- **Все зависимости** - включены в EXE

## Размер архива:
Ожидаемый размер: ~50-100 MB (включая все зависимости PyQt5) 