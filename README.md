# Macan-Macanan Game AI

Implementasi AI untuk permainan tradisional Indonesia "Macan-Macanan" dengan menggunakan algoritma Minimax.

## Instalasi dan Penggunaan

### Prasyarat

-   Python 3.12 atau lebih baru
-   pip (Python package manager)

### Instalasi

1. Clone repositori ini
2. Instal dependensi dengan perintah:

```bash
pip install -r requirements.txt
```

3. Jalankan server dengan perintah:

```bash
python main.py
```

## Deskripsi

Proyek ini mengimplementasikan logika permainan dan AI untuk permainan Macan-Macanan, dengan fitur:

-   Implementasi aturan permainan lengkap
-   Multiple algoritma AI untuk lawan komputer
-   Arsitektur client-server berbasis Socket.IO
-   Algoritma Minimax dengan alpha-beta pruning

## Aturan Permainan

### Bidak

-   **MACAN**: Dapat bergerak ke segala arah dan menangkap bidak UWONG
-   **UWONG**: Hanya dapat bergerak satu langkah, bekerja sama untuk mengepung MACAN

### Pergerakan

1. MACAN dapat:

    - Bergerak satu langkah ke segala arah (orthogonal atau diagonal)
    - Menangkap bidak UWONG dengan melompatinya (jumlah UWONG harus genap)
    - Melakukan gerakan khusus melalui ruang sayap

2. UWONG dapat:
    - Bergerak satu langkah
    - Hanya bergerak orthogonal di sel empat-arah
    - Bergerak ke segala arah di sel semua-arah

### Kondisi Kemenangan

-   MACAN menang jika menangkap semua bidak UWONG
-   UWONG menang jika mengepung semua MACAN tanpa ada gerakan valid

## Struktur Proyek
