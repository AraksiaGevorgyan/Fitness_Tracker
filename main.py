from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import pandas as pd


class FitTrack(QWidget):
    def __init__(self):
        super().__init__()

        self.settings()
        self.initUI()
        self.button_click()
        self.load_data()

    def settings(self):
        self.setWindowTitle('FitTrack')
        self.resize(800, 600)

    def initUI(self):
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())

        self.cal_box = QLineEdit()
        self.cal_box.setPlaceholderText("Number of burned calories")

        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter distance ran")

        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a description")

        self.submit_btn = QPushButton('Submit')
        self.add_btn = QPushButton('Add')
        self.delete_btn = QPushButton('Delete')
        self.clear_btn = QPushButton('Clear')

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Date', 'Calories', 'Distance', 'Description'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()

        self.sub_row1.addWidget(QLabel('Date:'))
        self.sub_row1.addWidget(self.date_box)

        self.sub_row2.addWidget(QLabel('Calories: '))
        self.sub_row2.addWidget(self.cal_box)

        self.sub_row3.addWidget(QLabel('KM: '))
        self.sub_row3.addWidget(self.distance_box)

        self.sub_row4.addWidget(QLabel('Description: '))
        self.sub_row4.addWidget(self.description)

        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)

        btn_row1 = QHBoxLayout()
        btn_row2 = QHBoxLayout()

        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.delete_btn)
        btn_row2.addWidget(self.submit_btn)
        btn_row2.addWidget(self.clear_btn)

        self.col1.addLayout(btn_row1)
        self.col1.addLayout(btn_row2)

        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)

        self.master_layout.addLayout(self.col1, 30)
        self.master_layout.addLayout(self.col2, 70)
        self.setLayout(self.master_layout)
        self.apply_styles()

    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.calculate_calories)
        self.clear_btn.clicked.connect(self.reset)

    def load_data(self):
        try:
            self.df = pd.read_csv('fitness.csv')
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['ID', 'Date', 'Calories', 'Distance', 'Description'])

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        for row in self.df.itertuples():
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            self.table.setItem(rowPosition, 0, QTableWidgetItem(str(row.ID)))
            self.table.setItem(rowPosition, 1, QTableWidgetItem(str(row.Date)))
            self.table.setItem(rowPosition, 2, QTableWidgetItem(str(row.Calories)))
            self.table.setItem(rowPosition, 3, QTableWidgetItem(str(row.Distance)))
            self.table.setItem(rowPosition, 4, QTableWidgetItem(str(row.Description)))

    def add_workout(self):
        date = self.date_box.date().toString('yyyy-MM-dd')
        calories = self.cal_box.text()
        distance = self.distance_box.text()
        description = self.description.text()

        if self.df.empty:
            new_id = 1
        else:
            new_id = self.df['ID'].max() + 1

        new_entry = pd.DataFrame([[new_id, date, calories, distance, description]], columns=['ID', 'Date', 'Calories', 'Distance', 'Description'])
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.df.to_csv('fitness.csv', index=False)

        self.date_box.setDate(QDate.currentDate())
        self.cal_box.clear()
        self.distance_box.clear()
        self.description.clear()

        self.load_table()

    def delete_workout(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, 'ERROR', "Please choose a row to delete")
            return

        fit_id = int(self.table.item(selected_row, 0).text())
        self.df = self.df[self.df['ID'] != fit_id]
        self.df.to_csv('fitness.csv', index=False)

        self.load_table()

    def calculate_calories(self):
        try:
            distances = self.df['Distance'].astype(float).tolist()
            calories = self.df['Calories'].astype(float).tolist()

            if len(calories) < 2 or min(calories) == max(calories):
                QMessageBox.warning(self, "Error", "Not enough data or calorie values are identical to normalize.")
                return

            min_calorie = min(calories)
            max_calorie = max(calories)
            normalized_calories = [(calorie - min_calorie) / (max_calorie - min_calorie) for calorie in calories]

            plt.style.use('Solarize_Light2')
            ax = self.figure.subplots()
            ax.scatter(distances, calories, c=normalized_calories, cmap='viridis', label='Data Points')
            ax.set_title('Distance VS Calories')
            ax.set_xlabel('Distance')
            ax.set_ylabel('Calories')
            cbar = ax.figure.colorbar(ax.collections[0], label='Normalized Calories')
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            print(f"ERROR: {e}")
            QMessageBox.warning(self, "Error", 'Please enter some data first!')

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #b8c9e1;
            }

            QLabel {
                color: #333;
                font-size: 14px;
            }

            QLineEdit, QComboBox, QDateEdit {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
            }

            QTableWidget {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
                gridline-color: #444;
            }

            QHeaderView::section {
                background-color: #b8c9e1;
                color: #333;
                padding: 4px;
                border: 1px solid #444;
            }

            QTableWidget::item {
                background-color: #b8c9e1;
                color: #333;
            }

            QTableCornerButton::section {
                background-color: #b8c9e1;
                border: 1px solid #444;
            }

            QPushButton {
                background-color: #4caf50;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        figure_color = '#b8c9e1'
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f'background-color:{figure_color}')

    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.cal_box.clear()
        self.distance_box.clear()
        self.description.clear()
        self.figure.clear()
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication([])
    main = FitTrack()
    main.show()
    app.exec_()
