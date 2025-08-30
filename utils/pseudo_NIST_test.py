#!/usr/bin/env python3
import os
import numpy as np

# ---------------------------
# 512-bit rastgele üretim (numpy)
# ---------------------------
def generate_random_512bit_np(n=1):
    """
    n adet 512-bit rastgele blok üretir.
    Dönen değer shape=(n,512) boolean array
    """
    return np.random.randint(0, 2, size=(n, 512), dtype=np.uint8)

def bits_to_hex_np(bits):
    """
    bits: shape=(512,) veya (n,512)
    Dönen değer: hex string veya string listesi
    """
    if bits.ndim == 1:
        val = int(''.join(bits.astype(str)), 2)
        return f"{val:0128x}"
    else:
        hex_list = []
        for row in bits:
            val = int(''.join(row.astype(str)), 2)
            hex_list.append(f"{val:0128x}")
        return hex_list

# ---------------------------
# Frekans analizi ve dengeleme (numpy)
# ---------------------------
HEX_CHARS = np.array(list("0123456789abcdef"))

def hex_to_counts_np(hex_str):
    arr = np.array(list(hex_str))
    counts = np.array([np.sum(arr == c) for c in HEX_CHARS])
    return counts

def frekans_duzenle_np(counts, tolerans=2):
    avg = counts.mean()
    diff = counts - avg
    # aşırı farkları yumuşat
    counts = counts - diff//2
    counts = np.clip(counts, 0, None)
    return counts.astype(int)

def counts_to_hex_string(counts):
    # counts 16 eleman
    hex_chars = []
    for i, c in enumerate(counts):
        hex_chars.extend([HEX_CHARS[i]]*c)
    # 128 karaktere kes veya doldur
    s = ''.join(hex_chars)
    return s[:128].ljust(128, '0')


import random

def rastgele_hex_dizini():
    hex_dizisi = list("0123456789abcdef")  # kullanılacak karakterler
    olasiliklar = list(range(26, 39))      # 26–38 arası olasılıklar
    olasilik_sayac = {o: 0 for o in olasiliklar}  # her olasılık en çok 3 defa
    adimlar = list(range(512))             # 0–511 adımlar
    yeni_hex_dizini = [""] * 512           # boş dizi (512 uzunlukta)

    while "" in yeni_hex_dizini and hex_dizisi:
        # 1) rastgele bir karakter seç
        char = random.choice(hex_dizisi)
        hex_dizisi.remove(char)

        # 2) olasılıklardan uygun olanları seç
        uygun_olasiliklar = [o for o in olasiliklar if olasilik_sayac[o] < 3]
        if not uygun_olasiliklar:
            break  # çıkış

        olasilik = random.choice(uygun_olasiliklar)
        olasilik_sayac[olasilik] += 1

        # eğer 3 defa olduysa listeden çıkar
        if olasilik_sayac[olasilik] >= 3:
            olasiliklar.remove(olasilik)

        # 3) adımlardan bu kadar rastgele seçim yap
        secilen_adimlar = random.sample(adimlar, min(olasilik, len(adimlar)))

        # 4) bu adımlara seçilen karakteri yaz
        for idx in secilen_adimlar:
            yeni_hex_dizini[idx] = char
            adimlar.remove(idx)

    # Eğer hala boş kalan yer varsa dolduralım (safety)
    kalan = [i for i, v in enumerate(yeni_hex_dizini) if v == ""]
    for i in kalan:
        yeni_hex_dizini[i] = random.choice("0123456789abcdef")

    return "".join(yeni_hex_dizini)


# Örnek kullanım
hex_cikti = rastgele_hex_dizini()
print("Nihai hex çıktısı (512 karakter):")
print(hex_cikti)
print("Uzunluk:", len(hex_cikti))


# ---------------------------
# Hex -> bit
# ---------------------------
def hex_to_bits(hex_string):
    return bin(int(hex_string,16))[2:].zfill(512)

# ---------------------------
# 2Mbit × 100 blok üretimi (vektörize)
# ---------------------------
def generate_large_nist_stream_fast(filename="results/nist_2Mbit_100_blocks_fast.txt",
                                    blocks=100, bits_per_block=2_000_000):
    os.makedirs("results", exist_ok=True)
    chunk_size = 512
    hashes_per_block = bits_per_block // chunk_size

    with open(filename, "w") as f:
        for block_idx in range(blocks):
            for _ in range(hashes_per_block):
                #bits = generate_random_512bit_np()[0]
                bits = hex_to_bits(rastgele_hex_dizini())
                # hex_str = bits_to_hex_np(bits)
                # counts = hex_to_counts_np(hex_str)
                # counts_balanced = frekans_duzenle_np(counts)
                # hex_balanced = counts_to_hex_string(counts_balanced)
                # bits_final = hex_to_bits(hex_balanced)
                f.write(bits)
            print(f"✅ Blok {block_idx+1}/{blocks} yazıldı ({bits_per_block/1e6} Mbit)")
    print(f"\n🎉 Toplam {blocks} blok (≈{blocks*bits_per_block/1e6:.0f} Mbit) '{filename}' oluşturuldu.")

# ---------------------------
# CLI / Örnek çalıştırma
# ---------------------------
if __name__ == "__main__":
    # Küçük test
    bits = generate_random_512bit_np()[0]
    hex_str = bits_to_hex_np(bits)
    print("Üretilen küçük hex:", hex_str)
    counts = hex_to_counts_np(hex_str)
    counts_balanced = frekans_duzenle_np(counts)
    hex_balanced = counts_to_hex_string(counts_balanced)
    print("Dengelenmiş hex:", hex_balanced)

    # Büyük NIST hazır bit stream üretimi
    generate_large_nist_stream_fast()
