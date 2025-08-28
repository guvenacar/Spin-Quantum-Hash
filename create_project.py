import os
import subprocess
import sys
from pathlib import Path

def create_virtual_environment():
    """Sanal ortam oluşturur ve etkinleştirir"""
    venv_dir = "venv"
    
    # Sanal ortamı oluştur
    try:
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        print(f"✓ Sanal ortam '{venv_dir}' dizininde oluşturuldu")
        
        # Gereksinimleri yükle
        if sys.platform == "win32":
            pip_path = Path(venv_dir) / "Scripts" / "pip.exe"
        else:
            pip_path = Path(venv_dir) / "bin" / "pip"
        
        if pip_path.exists():
            subprocess.check_call([str(pip_path), "install", "-r", "requirements.txt"])
            print("✓ Gereksinimler sanal ortama yüklendi")
        else:
            print("⚠ Pip bulunamadı, gereksinimler yüklenemedi")
            
        # Aktivasyon komutunu göster
        print("\nSanal ortamı etkinleştirmek için:")
        if sys.platform == "win32":
            print(f"  {venv_dir}\\Scripts\\activate")
        else:
            print(f"  source {venv_dir}/bin/activate")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Sanal ortam oluşturulurken hata: {e}")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

def create_project_structure():
    """İstenen proje yapısını oluşturur"""
    
    # Ana dizinler
    directories = [
        "model",
        "view", 
        "controller",
        "test",
        "utils"
    ]
    
    # Dosyalar
    files = {
        "main.py": "# Ana uygulama giriş noktası\n\nif __name__ == \"__main__\":\n    print(\"Uygulama başlatıldı!\")\n",
        "requirements.txt": "# Gereken paketler\npython-dotenv\nflask\npandas\n",
        ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Virtual environment\nvenv/\nenv/\n.venv/\n\n# IDE\n.vscode/\n.idea/\n\n# Logs\n*.log\n\n# OS\n.DS_Store\nThumbs.db\n",
        ".env": "# Çevre değişkenleri\n# DEBUG=True\n# DATABASE_URL=sqlite:///app.db\n"
    }
    
    # Dizinleri oluştur
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ {directory}/ dizini oluşturuldu")
        
        # Her dizine __init__.py dosyası ekle (Python package yapmak için)
        init_file = Path(directory) / "__init__.py"
        init_file.write_text("# Package initialization\n", encoding='utf-8')
    
    # Dosyaları oluştur ve içeriklerini yaz
    for filename, content in files.items():
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"✓ {filename} dosyası oluşturuldu")
    
    # Her dizine örnek dosyalar ekle
    sample_files = {
        "model": {
            "__init__.py": "# Model package\n", 
            "user_model.py": "# Kullanıcı modeli örneği\nclass User:\n    def __init__(self, name, email):\n        self.name = name\n        self.email = email\n"
        },
        "view": {
            "__init__.py": "# View package\n", 
            "user_view.py": "# Kullanıcı arayüzü örneği\nclass UserView:\n    def display_user(self, user):\n        print(f\"Kullanıcı: {user.name}, Email: {user.email}\")\n"
        },
        "controller": {
            "__init__.py": "# Controller package\n", 
            "user_controller.py": "# Kullanıcı kontrolörü örneği\nclass UserController:\n    def __init__(self):\n        self.users = []\n    \n    def add_user(self, name, email):\n        # Kullanıcı ekleme işlevi\n        pass\n"
        },
        "test": {
            "__init__.py": "# Test package\n", 
            "test_user.py": "# Kullanıcı testleri örneği\nimport unittest\n\nclass TestUser(unittest.TestCase):\n    def test_user_creation(self):\n        self.assertTrue(True)  # Örnek test\n"
        },
        "utils": {
            "__init__.py": "# Utils package\n", 
            "helpers.py": "# Yardımcı fonksiyonlar\ndef format_name(name):\n    \"\"\"İsmi formatlar\"\"\"\n    return name.title() if name else \"\"\n"
        }
    }
    
    for directory, files_dict in sample_files.items():
        for filename, content in files_dict.items():
            file_path = Path(directory) / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ {directory}/{filename} dosyası oluşturuldu")
    
    # Sanal ortamı oluştur
    create_virtual_environment()
    
    print("\n🎉 Proje yapısı ve sanal ortam başarıyla oluşturuldu!")
    print("\nOluşturulan yapı:")
    print("model/")
    print("view/") 
    print("controller/")
    print("test/")
    print("utils/")
    print("main.py")
    print("requirements.txt")
    print(".gitignore")
    print(".env")
    print("venv/")

if __name__ == "__main__":
    create_project_structure()

# Eğer sanal ortam venv oluştururken hata verirse elle oluştumak için aşağıdakileri yap
# Mevcut venv dizinini sil
# rm -rf venv

# # Yeni sanal ortam oluştur
# python3 -m venv venv

# # Gereksinimleri yükle
# source venv/bin/activate
# pip install -r requirements.txt