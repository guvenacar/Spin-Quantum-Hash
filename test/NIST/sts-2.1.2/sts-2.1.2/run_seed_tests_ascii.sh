#!/bin/bash

# NIST testini otomatikleştiren betik.
# Bu parametreler, NIST GitHub sayfasındaki
# data.pi test sonuçlarını (10/10) üretmek için ayarlanmıştır.

STREAM_LEN=20000     # Her bir dizi (sequence) uzunluğu (bit olarak)
NUM_SEQ=100            # Test edilecek toplam dizi sayısı
INPUT_FILE="../../../../results/qthash_test_data.txt" # Test edilecek dosya yolu

# Rapor için hedef dosya ismi
REPORT_DIR="./experiments/AlgorithmTesting"
REPORT_FILE="seed_NIST_Report.txt"

# Kontrol: Dosya mevcut ve yeterince uzun mu?
FILE_SIZE=$(stat --printf="%s" "${INPUT_FILE}")
MIN_SIZE=1000000
if [ ! -f "${INPUT_FILE}" ] || [ "${FILE_SIZE}" -lt "${MIN_SIZE}" ]; then
  echo "Hata: '${INPUT_FILE}' dosyası bulunamadı veya yeterince büyük değil."
  echo "Dosya en az ${MIN_SIZE} bayt (1.000.000 bit) olmalıdır."
  exit 1
fi

echo "NIST testleri başlatılıyor..."

(
  echo "0"                  # [0] Input File seçeneği
  echo "${INPUT_FILE}"      # Test edilecek dosya yolu
  echo "1"                  # [1] Tüm istatistiksel testleri uygula
  echo "0"                  # Varsayılan parametreleri kullan
  echo "${NUM_SEQ}"         # Test edilecek dizi sayısı (10/10 sonucu için)
  echo "0"                  # [0] ASCII giriş formatı
) | ./assess "${STREAM_LEN}"

echo "NIST testleri tamamlandı."

# Test tamamlandıktan sonra raporu kopyala
if [ -f "${REPORT_DIR}/finalAnalysisReport.txt" ]; then
    cp "${REPORT_DIR}/finalAnalysisReport.txt" \
       "${REPORT_DIR}/${REPORT_FILE}"
    echo "ASCII test raporu kaydedildi: ${REPORT_FILE}"
else
    echo "Rapor dosyası bulunamadı: ${REPORT_DIR}/finalAnalysisReport.txt"
fi
