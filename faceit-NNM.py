import csv
import sys
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QTextEdit,

)
from PyQt5.QtWidgets import QComboBox, QFormLayout, QDialog
from PyQt5.QtCore import Qt
import datetime
import logging
from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

logging.basicConfig(level=logging.INFO)

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menedżer Statystyk Gry")
        self.setWindowIcon(QIcon("ikona.ico"))

        # Inicjalizacja numeru meczu i lista do przechowywania statystyk
        self.match_number = self.get_last_match_number()  # Uzyskaj numer z ostatniego wiersza CSV
        self.session_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Identyfikator sesji

        self.match_data = []

        # Ustaw domyślny rozmiar okna
        self.setFixedSize(1040, 900)

        # Główny layout
        main_layout = QVBoxLayout()

        # Etykieta z numerem aktualnego meczu
        self.match_label = QLabel(f"Aktualny mecz: {self.match_number}")
        main_layout.addWidget(self.match_label)


        # Przycisk do rozpoczęcia nowego meczu
        self.new_match_button = QPushButton("Wprowadź Nowy Mecz")
        self.new_match_button.clicked.connect(self.start_new_match)  # Przypisanie zdarzenia
        main_layout.addWidget(self.new_match_button)


        # Sekcja do wprowadzania danych
        self.input_section = QWidget()
        self.input_section_layout = QVBoxLayout()
        self.input_section.setLayout(self.input_section_layout)
        self.hide_input_section()  # Ukryj sekcję na początku

        # Tabela do wprowadzania danych
        self.table = QTableWidget(5, 8)  # 5 wierszy, 8 kolumn
        column_headers = ["Gracz", "Kills", "Assists", "Deaths", "K/R Ratio", "K/D Ratio", "Headshots", "Headshots %"]
        self.table.setHorizontalHeaderLabels(column_headers)

        # Dodaj graczy do tabeli (pierwsza kolumna)
        players = ["magix877", "jasiumek87", "kejeicaM", "Szymeeeeek", "Kampur3929"]
        for i, player in enumerate(players):
            item = QTableWidgetItem(player)
            self.table.setItem(i, 0, item)

        self.input_section_layout.addWidget(self.table)

        # Layout do wprowadzania danych
        input_data_layout = QHBoxLayout()
        input_data_layout.addWidget(QLabel("Wklej statystyki:"))
        self.stats_input = QLineEdit()
        input_data_layout.addWidget(self.stats_input)

        # Dodaj przyciski do wprowadzania danych
        add_button = QPushButton("Dodaj do Gracza")
        add_button.clicked.connect(self.add_to_player)
        input_data_layout.addWidget(add_button)

        # Przycisk powrotu do menu

        back_button = QPushButton("Powróć do Menu")
        back_button.clicked.connect(self.hide_input_section)
        input_data_layout.addWidget(back_button)

        # Przycisk zakończenia meczu
        self.end_match_button = QPushButton("Zakończ Mecz")  # Użyj `self` do przypisania do atrybutu klasy
        self.end_match_button.clicked.connect(self.end_match_and_save)  # Przypisanie zdarzenia
        input_data_layout.addWidget(self.end_match_button)  # Dodaj do układu
        self.end_match_button.setEnabled(False)

        self.input_section_layout.addLayout(input_data_layout)
        main_layout.addWidget(self.input_section)

        # Dodaj widok pliku CSV
        self.load_data_from_csv()

        self.summary_section = QWidget()
        self.summary_layout = QVBoxLayout()  # Inicjalizuj `summary_layout`
        self.summary_section.setLayout(self.summary_layout)
        self.summary_section.setVisible(True)  # Ensure it's visible
        self.summary_section.setStyleSheet("background-color: grey;")  # Temporary background color
        self.update_summary_section()
        main_layout.addWidget(self.summary_section) # Dodaj sekcję do głównego layoutu
        # Zaktualizuj sekcję sumaryczną
        self.update_summary_section()  # Upewnij się, że sekcja jest poprawnie dodana i zaktualizowana

        self.csv_view = QTextEdit()
        self.csv_view.setReadOnly(True)  # Widżet tylko do odczytu
        #self.update_csv_view()  # Wyświetl zawartość CSV
        #main_layout.addWidget(self.csv_view)
        # Ustaw główny widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # Funkcja do rozpoczęcia nowego meczu
    def start_new_match(self):
        #self.hide_input_section()  # Ukryj sekcję do wprowadzania danych
        self.end_match_button.setEnabled(False)
        # Wyczyść tabelę, pozostawiając tylko nazwy graczy
        for row in range(self.table.rowCount()):
            for col in range(1, self.table.columnCount()):
                item = QTableWidgetItem("")  # Puste elementy
                self.table.setItem(row, col, item)
        self.update_summary_section()
        #self.match_number += 1  # Zwiększenie numeru meczu
        self.match_label.setText(f"Aktualny mecz: {self.match_number}")  # Aktualizacja etykiety
        self.show_input_section()  # Pokaż sekcję do wprowadzania danych



    def get_last_match_number(self):
        file_path = "match_data.csv"
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                csv_data = list(csv_reader)
                if len(csv_data) > 1:
                    last_row = csv_data[-1]
                    return int(last_row[0])
                else:
                    logging.info("CSV file is empty or has only header, starting from 0.")
                    return 0
        except (FileNotFoundError, IndexError):
            logging.info("CSV file not found or index error, starting from 0.")
            return 0

    def end_match_and_save(self):
        # Zapisz dane do pliku CSV
        self.match_number += 1
        file_path = "match_data.csv"  # Stała nazwa pliku
        with open(file_path, "a", newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            if file.tell() == 0:  # Jeśli plik jest pusty, dodaj nagłówki
                csv_writer.writerow(
                    ["Mecz", "Sesja", "Gracz", "Kills", "Assists", "Deaths", "K/R Ratio", "K/D Ratio", "Headshots",
                     "Headshots %"]
                )

            for data in self.match_data:
                csv_writer.writerow([
                    self.match_number,
                    self.session_date,  # Dodaj sesję
                    data["Gracz"],
                    data["Kills"],
                    data["Assists"],
                    data["Deaths"],
                    data["K/R Ratio"],
                    data["K/D Ratio"],
                    data["Headshots"],
                    data["Headshots %"],
                ])

        # Wyczyść dane meczu
        self.match_data.clear()  # Po zapisie wyczyść dane

        # Aktualizuj sekcję sumaryczną i widok CSV
        self.update_summary_section()
        self.update_csv_view()
        self.start_new_match()  # Rozpocznij nowy mecz

    # Funkcja dodawania danych do gracza

    from PyQt5.QtWidgets import QMessageBox

    def add_to_player(self):
        raw_data = self.stats_input.text()  # Pobierz dane z pola tekstowego
        stats = raw_data.split("\t")  # Rozdziel według tabulatorów

        # Sprawdź, czy mamy co najmniej 7 wartości
        if len(stats) < 7:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Warning)
            error_box.setText("Wklej dokładnie 7 statystyk, rozdzielonych tabulatorem.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec_()
            return  # Wyjście w przypadku niewystarczających danych

        # Pierwsza wartość to nick gracza i pierwsza statystyka
        first_value = stats[0]

        if "\n" in first_value:
            nick, first_stat = first_value.split("\n", 1)
        else:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Warning)
            error_box.setText("Błąd formatu: oczekiwana spacja między nickiem gracza a pierwszą statystyką.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec_()
            return

        # Znajdź wiersz w tabeli dla danego gracza
        row_index = None
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item and item.text().strip().lower() == nick.strip().lower():
                row_index = i
                break

        if row_index is not None:
            # Sprawdź, czy gracz już ma statystyki
            existing_stat = next(
                (record for record in self.match_data if record["Gracz"].strip().lower() == nick.strip().lower()), None)

            if existing_stat:
                # Wyświetl okno dialogowe z pytaniem, czy nadpisać dane
                overwrite_box = QMessageBox()
                overwrite_box.setIcon(QMessageBox.Question)
                overwrite_box.setText(f"Statystyki dla {nick} są już wprowadzone. Czy chcesz je nadpisać?")
                overwrite_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                response = overwrite_box.exec_()

                if response == QMessageBox.Yes:
                    # Nadpisz istniejące statystyki
                    existing_stat["Kills"] = first_stat
                    existing_stat["Assists"] = stats[1]
                    existing_stat["Deaths"] = stats[2]
                    existing_stat["K/R Ratio"] = stats[3]
                    existing_stat["K/D Ratio"] = stats[4]
                    existing_stat["Headshots"] = stats[5]
                    existing_stat["Headshots %"] = stats[6]

                    # Nadpisz dane w tabeli
                    for col_index, value in enumerate([first_stat] + stats[1:], 1):
                        item = QTableWidgetItem(value)
                        self.table.setItem(row_index, col_index, item)

                    # Aktywuj przycisk "Zakończ Mecz" po nadpisaniu danych
                    self.end_match_button.setEnabled(True)
                else:
                    # Jeśli użytkownik wybierze "Nie", wyświetl komunikat
                    error_box = QMessageBox()
                    error_box.setIcon(QMessageBox.Information)
                    error_box.setText(f"Statystyki dla {nick} pozostają niezmienione.")
                    error_box.setStandardButtons(QMessageBox.Ok)
                    error_box.exec_()

            else:
                # Dodaj dane, jeśli gracz nie ma statystyk
                data_to_add = [first_stat] + stats[1:]
                for col_index, value in enumerate(data_to_add, 1):
                    item = QTableWidgetItem(value)
                    self.table.setItem(row_index, col_index, item)

                # Dodaj dane do listy match_data
                self.match_data.append({
                    "Gracz": nick,
                    "Kills": data_to_add[0],
                    "Assists": data_to_add[1],
                    "Deaths": data_to_add[2],
                    "K/R Ratio": data_to_add[3],
                    "K/D Ratio": data_to_add[4],
                    "Headshots": data_to_add[5],
                    "Headshots %": data_to_add[6],
                })

                # Aktywuj przycisk "Zakończ Mecz" po dodaniu danych
                self.end_match_button.setEnabled(True)
        else:
            # Komunikat, jeśli gracza nie znaleziono w tabeli
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Warning)
            error_box.setText(f"Gracza {nick} nie znaleziono w tabeli.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec_()
        self.stats_input.clear()


    def load_data_from_csv(self):
        file_path = "match_data.csv"  # Stała nazwa pliku
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Pomijaj nagłówek
                session_stats = defaultdict(lambda: {
                    "Kills": 0,
                    "Assists": 0,
                    "Deaths": 0,
                    "K/R Ratio": 0,
                    "K/D Ratio": 0,
                    "Headshots": 0,
                    "Headshots %": 0,
                    "Matches": 0,
                    "Sessions": 0,
                })

                # Wczytaj dane z pliku CSV
                for row in csv_reader:
                    if len(row) >= 10:  # Upewnij się, że jest wystarczająco dużo danych
                        session_date = row[1]  # Data sesji
                        player = row[2]  # Nazwa gracza

                        session_stats[session_date]["Kills"] += int(row[3])
                        session_stats[session_date]["Assists"] += int(row[4])
                        session_stats[session_date]["Deaths"] += int(row[5])
                        session_stats[session_date]["K/R Ratio"] += float(row[6])
                        session_stats[session_date]["K/D Ratio"] += float(row[7])
                        session_stats[session_date]["Headshots"] += int(row[8])
                        session_stats[session_date]["Headshots %"] += float(row[9])
                        session_stats[session_date]["Matches"] += 1
                        session_stats[session_date]["Sessions"] += 1

                # Zwracaj statystyki sesji
                return session_stats

        except FileNotFoundError:
            logging.error("CSV file not found")
            return None

        except Exception as e:
            logging.error(f"An error occurred while loading CSV data: {e}")
            return None

    def update_csv_view(self):
        # Odczytaj zawartość pliku CSV i wyświetl w widżecie tekstowym
        file_path = "match_data.csv"  # Stała nazwa pliku
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                csv_content = file.read()  # Odczytaj cały plik
                self.csv_view.setPlainText(csv_content)  # Wyświetl zawartość
        except FileNotFoundError:
            # Jeśli plik nie istnieje, wyświetl komunikat o braku danych
            self.csv_view.setPlainText("Brak danych do wyświetlenia.")

    def update_summary_section(self):
        file_path = "match_data.csv"
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Pomiń nagłówek

                # Słowniki dla statystyk ogólnych i sesji
                overall_player_stats = defaultdict(lambda: {
                    "Kills": 0,
                    "Assists": 0,
                    "Deaths": 0,
                    "K/R Ratio": 0,
                    "K/D Ratio": 0,
                    "Headshots": 0,
                    "Headshots %": 0,
                    "Matches": 0,
                })

                session_player_stats = defaultdict(lambda: {
                    "Kills": 0,
                    "Assists": 0,
                    "Deaths": 0,
                    "K/R Ratio": 0,
                    "K/D Ratio": 0,
                    "Headshots": 0,
                    "Headshots %": 0,
                    "Matches": 0,
                })

                # Oblicz statystyki ogólne i sesji
                for row in csv_reader:
                    if len(row) >= 10:
                        session_date = row[1]
                        player = row[2]

                        # Dodaj dane do statystyk ogólnych
                        overall_player_stats[player]["Kills"] += int(row[3])
                        overall_player_stats[player]["Assists"] += int(row[4])
                        overall_player_stats[player]["Deaths"] += int(row[5])
                        overall_player_stats[player]["K/R Ratio"] += float(row[6])
                        overall_player_stats[player]["K/D Ratio"] += float(row[7])
                        overall_player_stats[player]["Headshots"] += int(row[8])
                        overall_player_stats[player]["Headshots %"] += float(row[9])
                        overall_player_stats[player]["Matches"] += 1

                        # Dodaj dane do statystyk sesji, jeśli jest to obecna sesja
                        if session_date == self.session_date:
                            session_player_stats[player]["Kills"] += int(row[3])
                            session_player_stats[player]["Assists"] += int(row[4])
                            session_player_stats[player]["Deaths"] += int(row[5])
                            session_player_stats[player]["K/R Ratio"] += float(row[6])
                            session_player_stats[player]["K/D Ratio"] += float(row[7])
                            session_player_stats[player]["Headshots"] += int(row[8])
                            session_player_stats[player]["Headshots %"] += float(row[9])
                            session_player_stats[player]["Matches"] += 1

                            # Czyszczenie sekcji podsumowania
                while self.summary_layout.count():
                    item = self.summary_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # Stwórz układ poziomy
                hbox_layout = QHBoxLayout()

                # Utwórz sekcje dla ogólnych statystyk i sesji
                overall_section = QWidget()
                overall_layout = QVBoxLayout()
                overall_section.setLayout(overall_layout)

                session_section = QWidget()
                session_layout = QVBoxLayout()
                session_section.setLayout(session_layout)

                # Dodaj etykietę z informacją o sesji
                session_label = QLabel(f"Obecna sesja: {self.session_date}")
                session_layout.addWidget(session_label)  # Dodaj do sekcji sesyjnej

                # Dodaj statystyki ogólne
                for player, stats in overall_player_stats.items():
                    kr_ratio_overall = stats["K/R Ratio"] / stats["Matches"]
                    kd_ratio_overall = stats["K/D Ratio"] / stats["Matches"]

                    summary_text_overall = (
                        f"{player}:\n"
                        f" - Kills: {stats['Kills']}\n"
                        f" - Assists: {stats['Assists']}\n"
                        f" - Deaths: {stats['Deaths']}\n"
                        f" - K/R Ratio: {kr_ratio_overall:.2f}\n"
                        f" - K/D Ratio: {kd_ratio_overall:.2f}\n"
                        f" - Headshots: {stats['Headshots']}\n"
                        f" - Headshots %: {stats['Headshots %']:.2f}\n"
                    )

                    overall_layout.addWidget(QLabel(summary_text_overall))  # Dodaj do sekcji ogólnej

                # Dodaj statystyki sesji
                for player, stats in session_player_stats.items():
                    kr_ratio_session = stats["K/R Ratio"] / stats["Matches"]
                    kd_ratio_session = stats["K/D Ratio"] / stats["Matches"]

                    summary_text_session = (
                        f"{player}:\n"
                        f" - Kills: {stats['Kills']}\n"
                        f" - Assists: {stats['Assists']}\n"
                        f" - Deaths: {stats['Deaths']}\n"
                        f" - K/R Ratio: {kr_ratio_session:.2f}\n"
                        f" - K/D Ratio: {kd_ratio_session:.2f}\n"
                        f" - Headshots: {stats['Headshots']}\n"
                        f" - Headshots %: {stats['Headshots %']:.2f}\n"
                    )

                    session_layout.addWidget(QLabel(summary_text_session))  # Dodaj do sekcji sesyjnej

                # Dodaj sekcje do układu poziomego
                hbox_layout.addWidget(overall_section)  # Dodaj do lewej kolumny
                hbox_layout.addWidget(session_section)  # Dodaj do prawej kolumny

                self.summary_layout.addLayout(hbox_layout)  # Dodaj układ poziomy do sekcji podsumowania

        except FileNotFoundError:
            self.summary_layout.addWidget(QLabel("Brak danych"))  # Obsługa braku pliku

    # Funkcja do ukrywania sekcji wprowadzania danych
    def hide_input_section(self):
        self.input_section.hide()  # Ukryj sekcję wprowadzania danych

    # Funkcja do pokazywania sekcji wprowadzania danych
    def show_input_section(self):
        self.input_section.show()  # Pokaż sekcję wprowadzania danych




# Uruchomienie aplikacji PyQt5
app = QApplication(sys.argv)
window = MainAppWindow()  # Stwórz okno główne
window.show()  # Pokaż okno
app.exec_()  # Uruchom pętlę główną
