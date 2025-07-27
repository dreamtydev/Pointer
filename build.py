import os
import sys
import subprocess
import shutil

def main():
    print("🔨 Сборка Pointer в EXE файл...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Рабочая директория: {script_dir}")
    
    if not os.path.exists("pointer_app.py"):
        print("❌ Файл pointer_app.py не найден!")
        return 1
    
    if not os.path.exists("pointer_app.spec"):
        print("❌ Файл pointer_app.spec не найден!")
        return 1
    
    try:
        import PyInstaller
        print("✅ PyInstaller найден")
    except ImportError:
        print("❌ PyInstaller не найден. Устанавливаем...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    if os.path.exists("dist"):
        print("🧹 Очищаем папку dist...")
        shutil.rmtree("dist")
    
    if os.path.exists("build"):
        print("🧹 Очищаем папку build...")
        shutil.rmtree("build")
    
    print("📦 Собираем проект...")
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller", "pointer_app.spec"
    ])
    
    if result.returncode == 0:
        print("✅ Сборка завершена успешно!")
        print("📁 EXE файл находится в папке dist/pointer_app/")
        
        exe_path = "dist/pointer_app/pointer_app.exe"
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 Размер EXE файла: {size:.1f} MB")
    else:
        print("❌ Ошибка при сборке!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 