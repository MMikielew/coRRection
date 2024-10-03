from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout

def initialize_views(obj):
    # Main layout
    obj.main_layout = QVBoxLayout()

    # Vertical layout
    obj.vlayout = QVBoxLayout()

    # First horizontal row of elements
    obj.first_row = QHBoxLayout()

    # Buttons layout
    obj.c_buttons_layout = QHBoxLayout()
    obj.m_buttons_layout = QHBoxLayout()
    obj.a_buttons_layout = QHBoxLayout()
    obj.pre_mean_buttons_layout = QHBoxLayout()
    obj.hrv_options_layout_1 = QHBoxLayout()
    obj.hrv_options_layout_2 = QHBoxLayout()

    # Plot layout
    obj.RR_layout = QHBoxLayout()

    # Main layout
    obj.setLayout(obj.main_layout)