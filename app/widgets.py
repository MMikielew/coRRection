"""
Module responsible for widgets creation
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QRadioButton, QButtonGroup,
                             QComboBox)

from buttons_layout import create_buttons_layout
from RR_layout import create_RR_layout
from hrv_options import initialize_hrv_options
from communiques import create_communiques


def create_widgets(obj) -> None:
    """
    Adding widgets
    """
    obj.main_layout.addLayout(obj.first_row)

    # Loading new file
    obj.file_btn = QPushButton(obj)
    obj.file_btn.resize(100, 50)
    obj.file_btn.setText("Load file (.txt, .csv, .xlsx or .xls)")
    obj.first_row.addWidget(obj.file_btn)
    obj.file_btn.clicked.connect(obj.open_dialog)

    # Layout: identify artifact
    obj.identification_layout = QHBoxLayout()
    obj.identification_label = QLabel("Options for artifacts identification:")
    obj.identification_label.setStyleSheet('color: red')
    obj.identification_layout.addWidget(obj.identification_label)

    # Manual settings for T1-T3
    obj.textbox_layout = QHBoxLayout()
    obj.label_art1 = QLabel("T1: Difference between two neighboring RRi [ms]")
    obj.label_art2 = QLabel("T2: Long RRi before short one [ms]")
    obj.label_art3 = QLabel("T3: Short RRi before long one [ms]")
    obj.textbox_art1 = QLineEdit(obj)
    obj.textbox_art1.setText("200")
    obj.textbox_art2 = QLineEdit(obj)
    obj.textbox_art2.setText("400")
    obj.textbox_art3 = QLineEdit(obj)
    obj.textbox_art3.setText("400")
    for el in [obj.label_art1, obj.textbox_art1,
               obj.label_art2, obj.textbox_art2,
               obj.label_art3, obj.textbox_art3]:
        obj.textbox_layout.addWidget(el)
  
    # Add HRV layout
    obj.main_layout.addLayout(obj.hrv_options_layout_1)
    obj.main_layout.addLayout(obj.hrv_options_layout_2)

    obj.main_layout.addLayout(obj.identification_layout)
    obj.main_layout.addLayout(obj.textbox_layout)
    initialize_hrv_options(obj)

    # artifacts detedction layout
    obj.main_layout.addLayout(obj.a_buttons_layout)

    # Button that allows for auto T1-T3 detection
    obj.auto_art = QPushButton(obj)
    obj.auto_art.setText("T1-T3 auto-finding")
    obj.auto_art.clicked.connect(lambda:obj.auto_detect())
    obj.a_buttons_layout.addWidget(obj.auto_art)

    # Button that allows for auto Tarvainen detection
    obj.poin_art = QPushButton(obj)
    obj.poin_art.setText("Tarvainen auto-finding")
    obj.poin_art.clicked.connect(lambda:obj.auto_tarvainen())
    obj.a_buttons_layout.addWidget(obj.poin_art)

    # Button that allows for auto Quotient detection
    obj.quot_art = QPushButton(obj)
    obj.quot_art.setText("Quotient filtering auto-finding")
    obj.quot_art.clicked.connect(lambda:obj.auto_poincare())
    obj.a_buttons_layout.addWidget(obj.quot_art)

    # Button that allows for auto square detection
    obj.square_art = QPushButton(obj)
    obj.square_art.setText("Square filtering auto-finding")
    obj.square_art.clicked.connect(lambda:obj.auto_square())
    obj.a_buttons_layout.addWidget(obj.square_art)

    obj.art_btn = QPushButton(obj)
    obj.art_btn.setText("Mark manually")
    obj.art_btn.clicked.connect(lambda:obj.choose_artifact())
    obj.a_buttons_layout.addWidget(obj.art_btn)       
    
    obj.del_btn = QPushButton(obj)
    obj.del_btn.setText("Delete single selection")
    obj.del_btn.clicked.connect(lambda:obj.del_artifact([obj.coords_x]))
    obj.a_buttons_layout.addWidget(obj.del_btn)    

    # Button that allows for clearing detections
    obj.clear_art = QPushButton(obj)
    obj.clear_art.setText("Clear all detections")
    obj.clear_art.clicked.connect(lambda:obj.clear_artifacts())
    obj.a_buttons_layout.addWidget(obj.clear_art)

    obj.label_marks_correction = QLabel("Modify artifacts manually: ")

    # Add RR layout
    create_RR_layout(obj)
    obj.main_layout.addLayout(obj.RR_layout)
    obj.main_layout.addWidget(obj.hrv_label)

    # Sections titles
    obj.correction_layout = QHBoxLayout()
    obj.correction_label = QLabel("Options for artifacts correction:")
    obj.correction_label.setStyleSheet('color: red')
    obj.correction_layout.addWidget(obj.correction_label)
    obj.main_layout.addLayout(obj.correction_layout)

    # Add corrction buttons
    obj.main_layout.addLayout(obj.c_buttons_layout)
    obj.main_layout.addLayout(obj.m_buttons_layout)

    # Add radio buttons for artifact correction method
    obj.m1 = QRadioButton("linear interpolation", obj)
    obj.m2 = QRadioButton("cubic splain", obj)
    obj.m3 = QRadioButton("deletion", obj)
    obj.m4 = QRadioButton("moving average", obj)
    obj.m5 = QRadioButton("pre mean", obj)

    # Options for pre-mean correction method
    obj.pre_mean_count = QComboBox()
    obj.pre_mean_count.addItems(["2", "3", "4", "5", "6", "7", "8", "9", "10"])
    obj.pre_mean_count.setCurrentText("4")

    # Checkboxes for detected artifact to remove
    obj.Tarvainen = QCheckBox("Tarvainen")
    obj.quotient = QCheckBox("Quotient")
    obj.square = QCheckBox("Square")
    obj.t1_auto = QCheckBox("T1")
    obj.t2_auto = QCheckBox("T2")
    obj.t3_auto = QCheckBox("T3")
    obj.diff_man = QCheckBox("Manual")
    obj.checkbox_list = [obj.Tarvainen, obj.quotient, obj.square, obj.t1_auto, obj.t2_auto, obj.t3_auto, obj.diff_man]
    
    create_buttons_layout(obj)
    create_communiques(obj)
