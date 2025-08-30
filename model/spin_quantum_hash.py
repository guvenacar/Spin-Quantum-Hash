#!/usr/bin/env python3
"""
Optimized Quantum-inspired Hash Generator.
- Trigonometric calculations are accelerated using lookup tables
- Constants are stored globally
- Always produces the same output for the same input
"""

import numpy as np
import math
from collections import Counter

# ---------------------------
# Global constants / lookup table
# ---------------------------
BASES = {'00': 23, '01': 29, '10': 31, '11': 37}
MASK512 = (1 << 512) - 1
MASK30  = (1 << 30) - 1

# Trigonometric lookup table 0-360 degrees
SIN_TABLE = np.sin(np.radians(np.arange(361)))
COS_TABLE = np.cos(np.radians(np.arange(361)))

def sin_deg(angle_deg):
    idx = int(angle_deg) % 360
    return SIN_TABLE[idx]

def cos_deg(angle_deg):
    idx = int(angle_deg) % 360
    return COS_TABLE[idx]

# ---------------------------
# Helper functions
# ---------------------------

def int_to_bits(n: int, bit_length: int = 512) -> str:
    if n < 0:
        n = n & ((1 << bit_length) - 1)
    return bin(int(n))[2:].zfill(bit_length)

def rotl_int(x: int, r: int, width: int = 512) -> int:
    r &= (width - 1)
    return ((x << r) & ((1 << width) - 1)) | ((x >> (width - r)) & ((1 << width) - 1))

def bit_rotate_left(x, n, bits=512):
    return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)

def bit_rotate_right(x, n, bits=512):
    return ((x >> n) | (x << (bits - n))) & ((1 << bits) - 1)

# ---------------------------
# Initial value generator
# ---------------------------

def initial_value_qthash_hybrid(block_string: str, previous_value: int = 1, quant_bits: int = 256) -> int:
    if len(block_string) != 512:
        raise ValueError("Input block must be 512 bits long.")
    MAX_Q = (1 << quant_bits) - 1
    PRIME = (1 << 521) - 1
    init_val = int(previous_value) % PRIME

    groups = [block_string[i:i+2] for i in range(0, 512, 2)]
    prev_base = 0

    for i, group in enumerate(groups):
        g = int(group, 2)
        base = BASES[group]
        pos = i + 1

        angle = ((g + 1) * (pos + 1)) * (math.pi / 180.0)
        phase = sin_deg((init_val % (1 << 30)) / float(1 << 30) * 360.0)
        sin_val = math.sin(angle + phase)
        cos_val = math.cos(angle - phase)

        q_sin = max(1, int(math.floor(((sin_val + 1.0) / 2.0) * MAX_Q)))
        q_cos = max(1, int(math.floor(((cos_val + 1.0) / 2.0) * MAX_Q)))

        exponent = (pos + (q_sin & MASK30))
        powmod = pow(base, exponent, PRIME)
        init_val = (init_val * powmod) % PRIME

        shift = ((i*2 - 1) + prev_base * base) % 511
        shift = max(1, shift)
        rotated = (q_cos << shift) & MASK512
        init_val = (init_val ^ rotated) & MASK512
        init_val = ((init_val << shift) & MASK512) | ((init_val >> (512 - shift)) & MASK512)

        bit_str = int_to_bits(init_val, 512)
        invers = int(''.join('1' if b=='0' else '0' for b in bit_str), 2)
        invers_rotl = rotl_int(invers, i % 512, 512)
        init_val ^= invers_rotl

        prev_base = base

    final_val = init_val & MASK512
    final_val |= (1 << 511)
    return int(final_val) if final_val != 0 else 1

# ---------------------------
# Convert text to 512-bit block
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
# Final bit mixing
# ---------------------------

def final_bit_mix(h1_int, h2_int):
    x = h1_int ^ h2_int
    x ^= bit_rotate_left(x, 13)
    x ^= bit_rotate_right(x, 7)
    return x

# ---------------------------
# Hash generator
# ---------------------------

def generate_super_hybrid_quantum_hash_v2(input_text: str) -> str:
    initial_block = text_to_512_block(input_text)
    seed_int = initial_value_qthash_hybrid(initial_block, previous_value=1)
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
    GROUPS = {0: [0,0], 1: [0,1], 2:[1,0], 3:[1,1]}

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
        
        two_bits = GROUPS[prob.index(max(prob))]
        h1_bits.extend(two_bits)

    h1_int = int(''.join(str(b) for b in h1_bits), 2)
    h1_inverted_bits = ''.join(str(1 - b) for b in h1_bits).zfill(512)
    h2_int = initial_value_qthash_hybrid(h1_inverted_bits, previous_value=seed_int)
    final_int = final_bit_mix(h1_int, h2_int)

    return f'{final_int:0128x}'

# ---------------------------
# Frequency analysis function
# ---------------------------

def analyze_hash_frequency(hash_string: str):
    hash_string = hash_string.lower()
    frequency = Counter(hash_string)
    sorted_frequency = sorted(frequency.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Character Frequency Analysis ---")
    total_chars = len(hash_string)
    for char, count in sorted_frequency:
        percentage = (count / total_chars) * 100
        print(f"'{char}': {count:3} times ({percentage:.2f}%)")

# ---------------------------
# CLI / Example run
# ---------------------------

if __name__ == "__main__":
    s = "Sample text"
    print("Input text:", s)
    h = generate_super_hybrid_quantum_hash_v2(s)
    print("hash:", h)
