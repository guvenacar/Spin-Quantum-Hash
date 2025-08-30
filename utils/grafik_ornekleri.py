#!/usr/bin/env python3
"""
Optimize edilmiş QTHash bit stream üretici.
- Lookup table ile trigonometrik hesaplar hızlandırıldı
- Sabit diziler global olarak alındı
- Aynı girdiye her zaman aynı çıktı verir
"""

import os
import time
from collections import Counter
import numpy as np
import math

# ---------------------------
# Global sabitler / lookup table
# ---------------------------
TABANLAR = {'00': 23, '01': 29, '10': 31, '11': 37}

MASK512 = (1 << 512) - 1
MASK30  = (1 << 30) - 1



# Trigonometrik lookup table 0-360 derece
SIN_TABLE = np.sin(np.radians(np.arange(361)))
COS_TABLE = np.cos(np.radians(np.arange(361)))

def sin_deg(angle_deg):
    idx = int(angle_deg) % 360
    return SIN_TABLE[idx]

def cos_deg(angle_deg):
    idx = int(angle_deg) % 360
    return COS_TABLE[idx]

# ---------------------------
# Helpers / utilities
# ---------------------------

def int_to_bits(n: int, bit_length: int = 512) -> str:
    if n < 0:
        n = n & ((1 << bit_length) - 1)
    return bin(int(n))[2:].zfill(bit_length)

def bits_to_int(bs: str) -> int:
    return int(bs, 2)

def rotl_int(x: int, r: int, width: int = 512) -> int:
    r &= (width - 1)
    return ((x << r) & ((1 << width) - 1)) | ((x >> (width - r)) & ((1 << width) - 1))

def bit_rotate_left(x, n, bits=512):
    return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)

def bit_rotate_right(x, n, bits=512):
    return ((x >> n) | (x << (bits - n))) & ((1 << bits) - 1)

# ---------------------------
# baslangic_degeri_qthash_hybrid
# ---------------------------

def baslangic_degeri_qthash_hybrid(blok_string: str, onceki_deger: int = 1, quant_bits: int = 256) -> int:
    if len(blok_string) != 512:
        raise ValueError("Girdi bloğu 512 bit uzunluğunda olmalıdır.")
    MAX_Q = (1 << quant_bits) - 1
    PRIME = (1 << 521) - 1
    baslangic_degeri = int(onceki_deger) % PRIME

    gruplar = [blok_string[i:i+2] for i in range(0, 512, 2)]
    onceki_en_cok = 0

    for i, grup in enumerate(gruplar):
        g = int(grup, 2)
        base = TABANLAR[grup]
        pos = i + 1

        angle = ((g + 1) * (pos + 1)) * (math.pi / 180.0)
        phase = sin_deg((baslangic_degeri % (1 << 30)) / float(1 << 30) * 360.0)
        sin_val = math.sin(angle + phase)
        cos_val = math.cos(angle - phase)

        q_sin = max(1, int(math.floor(((sin_val + 1.0) / 2.0) * MAX_Q)))
        q_cos = max(1, int(math.floor(((cos_val + 1.0) / 2.0) * MAX_Q)))

        exponent = (pos + (q_sin & MASK30))
        powmod = pow(base, exponent, PRIME)
        baslangic_degeri = (baslangic_degeri * powmod) % PRIME

        shift = ((i*2 - 1) + onceki_en_cok * base) % 511
        shift = max(1, shift)
        kaydirma = (q_cos << shift) & MASK512
        baslangic_degeri = (baslangic_degeri ^ kaydirma) & MASK512
        baslangic_degeri = ((baslangic_degeri << shift) & MASK512) | ((baslangic_degeri >> (512 - shift)) & MASK512)

        bit_str = int_to_bits(baslangic_degeri, 512)
        invers = int(''.join('1' if b=='0' else '0' for b in bit_str), 2)
        invers_rotl = rotl_int(invers, i % 512, 512)
        baslangic_degeri ^= invers_rotl

        onceki_en_cok = base

    son_deger = baslangic_degeri & MASK512
    son_deger |= (1 << 511)
    return int(son_deger) if son_deger != 0 else 1

# ---------------------------
# Text to 512-bit block
# ---------------------------

def text_to_512_block(input_text: str) -> str:
    input_bytes = input_text.encode('utf-8')
    binary_string = ''.join(f'{b:08b}' for b in input_bytes)
    padded_binary = binary_string + '1'
    while len(padded_binary) % 512 != 448:
        padded_binary += '0'
    padded_binary += f'{len(binary_string):064b}'
    blocks = [padded_binary[i:i+512] for i in range(0, len(padded_binary), 512)]
    if len(blocks) == 1:
        return blocks[0]
    else:
        acc = int(blocks[0], 2)
        for b in blocks[1:]:
            acc ^= int(b, 2)
        return bin(acc)[2:].zfill(512)

# ---------------------------
# Final bit mix (PERM_512 lookup)
# ---------------------------

def final_bit_mix(h1_int, h2_int):
    # İki 512-bit tam sayıyı XOR'la birleştir
    x = h1_int ^ h2_int

    # Bitleri sola 13 döndür ve XOR ile karıştır
    x ^= bit_rotate_left(x, 13)

    # Bitleri sağa 7 döndür ve XOR ile karıştır
    x ^= bit_rotate_right(x, 7)

    # 17 bit sola kaydır ve MASK512 ile sınırla, sonra XOR ile karıştır
    #x ^= (x << 17) & MASK512

    # Sayıyı 512-bitlik binary stringe çevir → numpy array olarak tut
    # x zaten integer, önce 512 bit string'e çevir
    #x_bin = [int(b) for b in bin(x)[2:].zfill(512)]

    # cross_permute uygula
    #x_bin_perm = cross_permute(x_bin, steps=5)

    # Tekrar integer yap
    #x_perm = int(''.join(str(b) for b in x_bin_perm), 2)
     
    # Sonuç olarak permütasyon uygulanmış 512-bit sayı döndür
    return x


# ---------------------------
# Generate Super Hybrid Quantum Hash
# ---------------------------

def generate_super_hybrid_quantum_hash_v2(input_text: str) -> str:
    initial_block = text_to_512_block(input_text)
    seed_int = baslangic_degeri_qthash_hybrid(initial_block, onceki_deger=1)
    seed_frac = (seed_int & MASK512) / float(1 << 512)

    A = math.sin(seed_frac * math.pi) * 10.0 + 1.0
    B = math.cos(seed_frac * math.pi) * 10.0 + 1.0
    C = ((seed_int >> 256) & ((1 << 256) - 1)) / float(1 << 256) * math.pi
    D = (seed_int & ((1 << 256) - 1)) / float(1 << 256) * 10.0

    x_positions = [(i*2.0) + ((int(initial_block[i*2:i*2+2],2)*7+23)%40+10)/10.0 + (int(initial_block[i*2:i*2+2],2)/5.0) for i in range(256)]
    x_interpolated = np.linspace(min(x_positions), max(x_positions)+1, 2560)
    y_interpolated = A * np.sin(B * x_interpolated + C) + D * np.sin(x_interpolated / 10.0)
    slopes = np.gradient(y_interpolated, x_interpolated)
    angles_deg = np.degrees(np.arctan(slopes))
 
    h1_bits = []
    GRUPNO = {0: [0,0], 1: [0,1], 2:[1,0], 3:[1,1]}

    for i in range(256):
        idx = np.abs(x_interpolated - x_positions[i]).argmin()
        angle_deg = angles_deg[idx]
        alfa1_rad = math.radians(angle_deg)

        prob = [
            math.cos(alfa1_rad) * math.cos(math.radians(360 - angle_deg)),
            math.cos(alfa1_rad) * math.sin(math.radians(270 - angle_deg)),
            math.sin(alfa1_rad) * math.cos(math.radians(180 - angle_deg)),
            math.sin(alfa1_rad) * math.sin(math.radians(90 - angle_deg))
        ]
        
        two_bits = GRUPNO[prob.index(max(prob))]
        h1_bits.extend(two_bits)   # listeye doğrudan [0,1] ekliyor

    # int'e çevir
    h1_int = int(''.join(str(b) for b in h1_bits), 2)

    # NOT işlemi
    h1_inverted_bits = ''.join(str(1 - b) for b in h1_bits).zfill(512)

    # ikinci hash
    h2_int = baslangic_degeri_qthash_hybrid(
        h1_inverted_bits,
        onceki_deger=seed_int
    )

    # final karıştırma
    final_int = final_bit_mix(h1_int, h2_int)



    return f'{final_int:0128x}'

# ---------------------------
# NIST Veri üretimi
# ---------------------------

def generate_qthash_bit_stream(filename: str, num_sequences: int = 100, bits_per_sequence: int = 2_000_000):
    os.makedirs('results', exist_ok=True)
    chunk_size = 512
    total_bits_needed = num_sequences * bits_per_sequence

    out_path = os.path.join('results', filename)
    with open(out_path, 'w') as f:
        total_bits_written = 0
        i = 0
        start_ts = time.time()

        while total_bits_written < total_bits_needed:
            data = f'{i}-{time.time_ns()}'
            hash_hex = generate_super_hybrid_quantum_hash_v2(data)
            int_bits = bin(int(hash_hex,16))[2:].zfill(512)
            f.write(int_bits)
            total_bits_written += chunk_size
            i += 1

            if i % 1000 == 0:
                elapsed = time.time() - start_ts
                progress = (total_bits_written / total_bits_needed) * 100
                mb_written = total_bits_written / 8 / 1e6
                rate = mb_written / elapsed if elapsed>0 else 0
                print(f"İlerleme: {progress:.1f}% ({total_bits_written/1e6:.1f} Mbit) - ~{rate:.2f} MB/s")

    final_size_mb = os.path.getsize(out_path) / 1e6
    print(f"✅ {total_bits_written/1e6:.1f} Mbit içeren '{filename}' dosyası oluşturuldu.")
    print(f"📁 Dosya boyutu: {final_size_mb:.2f} MB")

# ---------------------------
# Analiz
# ---------------------------

def analyze_hash_frequency(hash_string: str):
    hash_string = hash_string.lower()
    frequency = Counter(hash_string)
    sorted_frequency = sorted(frequency.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Karakter Frekans Analizi ---")
    total_chars = len(hash_string)
    for char, count in sorted_frequency:
        percentage = (count / total_chars) * 100
        print(f"'{char}': {count:3} kez ({percentage:.2f}%)")

# ---------------------------
# CLI / Örnek çalıştırma
# ---------------------------

if __name__ == "__main__":
    s = "NIST bit stream üretimi (yorum satırını kaldırarak kullanabilirsin)"
    print("Girilen metin:", s)
    h = generate_super_hybrid_quantum_hash_v2(s)
    print("hash:", h)
    analyze_hash_frequency(h)

    # NIST bit stream üretimi (yorum satırını kaldırarak kullanabilirsin)
    generate_qthash_bit_stream("qthash_test_data.txt", num_sequences=100, bits_per_sequence=2_000_0)
