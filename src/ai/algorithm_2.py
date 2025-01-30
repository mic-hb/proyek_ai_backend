from src.game.board import Board
from src.game.piece import PieceTypes

class Algorithm2:
    @staticmethod
    def evaluate(node: Board) -> float:
        """
        Fungsi evaluasi untuk menentukan skor permainan berdasarkan posisi pion macan dan uwong.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
                    contoh: {"macan": [(x1, y1), (x2, y2)], "uwong": [(x3, y3), (x4, y4), ...]}
        :return: skor evaluasi (positif jika menguntungkan macan, negatif jika menguntungkan uwong)
        """
        nilai_macan = 0
        nilai_uwong = 0

        posisi = {"macan": [], "uwong": []}
        for row in range(len(node)):
            for col in range(len(node[row])):
                cell = node[row][col]
                if cell.piece.type == PieceTypes.MACAN:
                    posisi["macan"].append((row, col))
                elif cell.piece.type == PieceTypes.UWONG:
                    posisi["uwong"].append((row, col))

        # Macan: Evaluasi langkah valid
        for macan in posisi['macan']:
            langkah_valid = Algorithm2.get_valid_moves_for_pion(posisi, macan)
            nilai_macan += len(langkah_valid) * 5

            # Ancaman pengepungan
            pion_di_sekitar = Algorithm2.get_pion_di_sekitar(posisi, macan, "uwong")
            nilai_macan -= len(pion_di_sekitar) * 10

            # Peluang untuk melompat
            garis_genap = Algorithm2.get_garis_genap(posisi, macan, "uwong")
            nilai_macan += len(garis_genap) * 15

            # Penalti jika pola ganjil di garis lurus
            garis_ganjil = Algorithm2.get_garis_ganjil(posisi, macan, "uwong")
            nilai_macan -= len(garis_ganjil) * 10

        # Uwong: Evaluasi langkah valid dan pola
        for uwong in posisi['uwong']:
            langkah_valid = Algorithm2.get_valid_moves_for_pion(posisi, uwong)
            nilai_uwong += len(langkah_valid) * 5

            # Bonus untuk pola ganjil
            garis_ganjil = Algorithm2.get_garis_ganjil(posisi, uwong, "uwong")
            nilai_uwong += len(garis_ganjil) * 15

            # Penalti untuk pola genap
            garis_genap = Algorithm2.get_garis_genap(posisi, uwong, "uwong")
            nilai_uwong -= len(garis_genap) * 10

            # Penalti untuk pion terisolasi
            pion_di_sekitar = Algorithm2.get_pion_di_sekitar(posisi, uwong, "uwong")
            if len(pion_di_sekitar) == 0:
                nilai_uwong -= 10

        # Uwong: Evaluasi blokade
        for macan in posisi['macan']:
            langkah_valid = Algorithm2.get_valid_moves_for_pion(posisi, macan)
            blokir = len([move for move in langkah_valid if move in posisi['uwong']])
            nilai_uwong += blokir * 10

        # Evaluasi kemenangan
        if all(len(Algorithm2.get_valid_moves_for_pion(posisi, macan)) == 0 for macan in posisi['macan']):
            # Uwong menang
            return -1000
        if all(len(Algorithm2.get_valid_moves_for_pion(posisi, uwong)) == 0 for uwong in posisi['uwong']):
            # Macan menang
            return 1000

        # Evaluasi total (nilai macan - nilai uwong)
        return nilai_macan - nilai_uwong


    @staticmethod
    def get_valid_moves_for_pion(posisi, pion):
        """
        Mengembalikan daftar langkah valid untuk pion tertentu.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :return: list langkah valid (x, y).
        """
        x, y = pion
        langkah = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),  # Vertikal & Horizontal
            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)  # Diagonal
        ]
        # Filter langkah yang berada di dalam papan dan tidak ada pion lain
        langkah_valid = [
            (lx, ly) for lx, ly in langkah
            if (lx, ly) not in posisi['macan'] and (lx, ly) not in posisi['uwong'] and 0 <= lx < 8 and 0 <= ly < 8
        ]
        return langkah_valid


    @staticmethod
    def get_pion_di_sekitar(posisi, pion, tipe):
        """
        Mengembalikan daftar pion di sekitar pion tertentu.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list pion di sekitar.
        """
        x, y = pion
        sekitar = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)
        ]
        pion_di_sekitar = [p for p in sekitar if p in posisi[tipe]]
        return pion_di_sekitar


    @staticmethod
    def get_garis_genap(posisi, pion, tipe):
        """
        Mengembalikan daftar garis lurus dengan pion jumlah genap.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list garis (daftar pion dalam 1 garis).
        """
        x, y = pion
        arah = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]
        garis_genap = []

        for dx, dy in arah:
            garis = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
                garis.append((nx, ny))
                nx += dx
                ny += dy
            if len(garis) > 0 and len(garis) % 2 == 0:  # Hanya ambil jika jumlahnya genap
                garis_genap.append(garis)

        return garis_genap


    @staticmethod
    def get_garis_ganjil(posisi, pion, tipe):
        """
        Mengembalikan daftar garis lurus dengan pion jumlah ganjil.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list garis (daftar pion dalam 1 garis).
        """
        x, y = pion
        arah = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]
        garis_ganjil = []

        for dx, dy in arah:
            garis = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
                garis.append((nx, ny))
                nx += dx
                ny += dy
            if len(garis) > 0 and len(garis) % 2 != 0:  # Hanya ambil jika jumlahnya ganjil
                garis_ganjil.append(garis)

        return garis_ganjil
