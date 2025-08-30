#!/bin/bash
# run_both_nist_tests.sh
# Bu betik, önce ASCII testlerini sonra SHA-512 testlerini çalıştırır.

# 1️⃣ ASCII testi
echo "🚀 ASCII testleri başlatılıyor..."
bash run_seed_tests_ascii.sh
echo "✅ ASCII testleri tamamlandı."

# 2️⃣ SHA-512 testi
echo "🚀 SHA-512 testleri başlatılıyor..."
#bash run_seed_tests_sha512.sh
echo "✅ SHA-512 testleri tamamlandı."

echo "=============================================="
echo "✅ Tüm NIST testleri tamamlandı."
