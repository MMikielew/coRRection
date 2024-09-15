from PyQt6.QtWidgets import QPushButton, QButtonGroup, QRadioButton, QLabel, QLineEdit

def initialize_hrv_options(obj):
    obj.param_hrv_label = QLabel("Set active signal length:")
    obj.h1 = QRadioButton("Full examination", obj)
    obj.h2 = QRadioButton("Selected length", obj)

    obj.hrv_group = QButtonGroup(obj)
    obj.hrv_group.addButton(obj.h1)
    obj.hrv_group.addButton(obj.h2)
    obj.h1.setChecked(True)

    obj.recount = QPushButton(obj)
    obj.recount.setText("Set boundaries")
    obj.recount.clicked.connect(lambda:obj.update_hrv_params())

    obj.start_label = QLabel("Initial interval")
    obj.end_label = QLabel("Last interval")

    obj.textbox_start = QLineEdit(obj)
    obj.textbox_start.setText("0")
    obj.textbox_end = QLineEdit(obj)
    obj.textbox_end.setText("0")

    for h in [obj.param_hrv_label, obj.h1, obj.h2, obj.recount]:
        obj.hrv_options_layout_1.addWidget(h)
    
    for h in [obj.start_label, obj.textbox_start, obj.end_label, obj.textbox_end]:
        obj.hrv_options_layout_2.addWidget(h)

