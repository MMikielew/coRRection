from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout

def initialize_views(obj):
    # główny układ aplikacji
    obj.main_layout = QVBoxLayout()

    # układ wertykalny 
    obj.vlayout = QVBoxLayout()

    # układ początkowej linii
    obj.first_row = QHBoxLayout()

    # układ przycisków
    obj.c_buttons_layout = QHBoxLayout()
    obj.m_buttons_layout = QHBoxLayout()
    obj.a_buttons_layout = QHBoxLayout()
    obj.pre_mean_buttons_layout = QHBoxLayout()
    obj.hrv_options_layout_1 = QHBoxLayout()
    obj.hrv_options_layout_2 = QHBoxLayout()

    # układ wykresu i parametrów
    obj.RR_layout = QHBoxLayout()

    # ustawienie głównego układu
    obj.setLayout(obj.main_layout)