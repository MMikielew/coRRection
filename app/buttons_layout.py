"""
Module responsible for buttons creation
"""
from PyQt6.QtWidgets import QPushButton, QButtonGroup, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

def create_buttons_layout(obj):
    """
    Function responsible for buttons creation
    """
    obj.save_layout = QHBoxLayout()
    obj.save_label = QLabel("Save signal, HRV params and summary of correction applied")

    obj.save_btn = QPushButton(obj)
    obj.save_btn.setText("Save")
    obj.save_btn.clicked.connect(lambda:obj.save_data())

    obj.main_layout.addLayout(obj.save_layout)
    obj.save_layout.addWidget(obj.save_label, alignment=Qt.AlignmentFlag.AlignRight)
    obj.save_layout.addWidget(obj.save_btn)
    
    obj.methods_group = QButtonGroup(obj)
    for i, m in enumerate([obj.m1, obj.m2, obj.m3, obj.m4]):
        obj.methods_group.addButton(m)
        obj.m_buttons_layout.addWidget(m)

    obj.m_buttons_layout.addLayout(obj.pre_mean_buttons_layout)

    obj.pre_mean_buttons_layout.addWidget(obj.m5)
    obj.methods_group.addButton(obj.m5)
    obj.pre_mean_buttons_layout.addWidget(obj.pre_mean_count)

    obj.m1.setChecked(True)

    for t in [obj.diff_man, obj.Tarvainen, obj.quotient, obj.square,
                obj.t1_auto, obj.t2_auto, obj.t3_auto]:
        obj.c_buttons_layout.addWidget(t)

    obj.del_btn2 = QPushButton(obj)
    obj.del_btn2.setText("Correct chosen")
    obj.del_btn2.clicked.connect(lambda:obj.delete_chosen_artifacts())
    obj.c_buttons_layout.addWidget(obj.del_btn2)


