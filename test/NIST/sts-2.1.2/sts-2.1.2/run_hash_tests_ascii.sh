STREAM_LEN=512
NUM_SEQ=1000
INPUT_FILE="data/nist_seed_data.txt"

(
  echo "0"                  # Input File
  echo "${INPUT_FILE}"      # dosya yolu
  echo "1"                  # tüm testleri uygula
  echo "0"                  # parametreleri değiştirme
  echo "${NUM_SEQ}"         # 1000 sequence
  echo "0"                  # ASCII (0/1 karakterleri)
) | ./assess "${STREAM_LEN}"
