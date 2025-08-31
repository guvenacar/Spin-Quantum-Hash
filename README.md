# Spin-Quantum-Hash – Quantum-Inspired 512-bit Hash Generator

This project is a Python program that generates **Spin-Quantum-Hash**, inspired by classical hash functions.
The goal is to take a given text and deterministically produce a 512-bit hash.

# Security of QTHash Against Quantum Algorithms

When evaluating the security of a cryptographic primitive against quantum computers, the first algorithms that come to mind are **Shor’s algorithm** and **Grover’s algorithm**.

- **Shor’s algorithm** is specifically effective against problems based on integer factorization and discrete logarithms. It allows efficient solving of these problems on a quantum computer, which breaks the mathematical foundations of RSA and elliptic curve cryptography (ECC). Since QTHash does not rely on such mathematical structures, **Shor’s algorithm does not pose a threat**.

- **Grover’s algorithm** provides a quadratic speedup for brute-force searches. In classical brute-force, a 256-bit key space requires ~2^256 operations. With Grover’s algorithm, this is reduced to ~2^128 quantum operations. Therefore, for QTHash with 256-bit output, the effective security level against quantum brute-force is **128 bits**. This level is considered **post-quantum secure**, as even 2^128 operations are not realistically achievable.

---

### Conclusion
QTHash is not based on algebraic structures vulnerable to Shor’s algorithm. Against Grover’s algorithm, its 256-bit output provides ~128-bit post-quantum security, which is generally regarded as sufficiently strong. Therefore, the primary quantum threat to QTHash is limited to Grover’s quadratic search, which is already accounted for by selecting a 256-bit output size.


---

## Features

* **Deterministic:** Always produces the same hash output for the same input.
* **Quantum-Analog:** The internal logic is designed with quantum superposition and entanglement analogies (mathematically not quantum, only an analogy).
* **512-bit Output:** The hash output is always a 512-bit value.
* **Easy to Use:** Generates a hash and analyzes it with a single text input.
* **Frequency Analysis:** Analyzes the frequency distribution of hash characters.

---

## Requirements

* Python 3.8 or higher
* Numpy

Installation (Linux / macOS / Windows):

```bash
pip install numpy
```

---

## Usage

```bash
python3 spin_kuantum_hash.py
```

The program generates a hash for a default `Sample text` and performs character frequency analysis.

### Example Output

```
Input text: Sample text
hash: 3a1f5c9b... (128-character hexadecimal)
--- Character Frequency Analysis ---
'0': 10 times (7.81%)
'1': 9 times (7.03%)
...
```

---

## Functions

* `generate_super_hybrid_quantum_hash_v2(input_text: str) -> str`
  Takes the input text and returns a 512-bit hash value as a hexadecimal string.

* `analyze_hash_frequency(hash_string: str)`
  Calculates the frequency distribution of hash characters and prints it to the screen.

* `text_to_512_block(input_text: str) -> str`
  Converts the input text into 512-bit blocks.

* `baslangic_degeri_qthash_hybrid(blok_string: str, onceki_deger: int = 1)`
  Generates an initial value from a 512-bit block.

---

## Analogical Notes

* The code simulates **entanglement and superposition** concepts from quantum mechanics in an analog way.
* It is not a true quantum computation; it runs on classical computers.

---

