#model/wave_seed_generator.py

import hashlib
import math
from math import pi 

# -------------------- HELPER FONKSİYONLAR --------------------

def int_to_bits(n, bit_length=512):
    """Integer'ı 0/1 bit dizisine çevirir (MSB-first, sabit uzunluk)"""
    if n < 0:
        n = n & ((1 << bit_length) - 1)
    return bin(int(n))[2:].zfill(bit_length)

# -------------------- YENİ MODİFİYE EDİLMİŞ FONKSİYON --------------------

def generate_spin_quantum_data(input_string: str) -> tuple:
    """
    Girdi dizesine dayalı olarak açı, x ve y konumlarını üretir.
    
    Args:
        input_string: 512 bitlik bir ikili dize.
        
    Returns:
        3 elemanlı bir tuple: (açılar_listesi, x_konumları, y_konumları)
    """
    if len(input_string) != 512:
        raise ValueError("Girdi bloğu 512 bit uzunluğunda olmalıdır.")

    baslangic_degeri = int(input_string, 2)
    tabanlar = {'00': 23, '01': 29, '10': 31, '11': 37}
    gruplar = [input_string[i:i+2] for i in range(0, 512, 2)]

    angles = []
    x_positions = []
    y_positions = []
    
    # Kendi içinde bir 'dalga fonksiyonu' gibi davranan bir model
    A = math.sin(baslangic_degeri / (1 << 512) * pi) + 1.0
    B = math.cos(baslangic_degeri / (1 << 512) * pi) + 1.0
    C = (baslangic_degeri >> 256) / (1 << 256) * pi
    D = (baslangic_degeri & ((1 << 256) - 1)) / (1 << 256) * 10

    for i, grup in enumerate(gruplar):
        g = int(grup, 2)
        base = tabanlar[grup]
        pos = i + 1

        x_val = pos * (base / 50.0) + (g / 10.0)
        x_positions.append(x_val)
        
        y_val = A * math.sin(B * x_val + C) + D * math.sin(x_val / 10)

        y_positions.append(y_val)
        
        dy_dx = A * B * math.cos(B * x_val + C) + D * (1/10) * math.cos(x_val/10)
        angle_in_degrees = math.degrees(math.atan(dy_dx))
        
        angles.append(angle_in_degrees)
        
    return (angles, x_positions, y_positions)


# -------------------- ÖRNEK KULLANIM --------------------

if __name__ == "__main__":
    test_string = "Merhaba dünya"
    input_hash = hashlib.sha512(test_string.encode('utf-8')).hexdigest()
    input_bits = bin(int(input_hash, 16))[2:].zfill(512)
    
    angles, x_positions, y_positions = generate_qthash_data(input_bits)
    
    # Sadece ilk birkaç değeri gösterelim
    print("Üretilen Açı, X ve Y Değerleri:")
    for i in range(5):
        print(f"Elektron {i+1}: Açı = {angles[i]:.2f}°, X = {x_positions[i]:.2f}, Y = {y_positions[i]:.2f}")
    
    print("\nToplam üretilen açı sayısı:", len(angles))
    print("Toplam üretilen x konumu sayısı:", len(x_positions))
    print("Toplam üretilen y konumu sayısı:", len(y_positions))