"""
Moduł służący utworzeniu układu wykresu oraz parametrów RR
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from new_graph import create_new_graph

def create_RR_layout(obj):
    """
    funkcja odpowiedzialna za rozmieszczenie przycisków
    """
    # utworzenie wykresu
    create_new_graph(obj)
    obj.RR_layout.addWidget(obj.graphWidget)

    # etykieta zawierająca informacje o sygnale
    obj.hrv_label = QLabel("Waiting for signal")
    #obj.hrv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #obj.RR_layout.addWidget(obj.hrv_label) to uncomment if HRV back
    obj.RR_layout.addWidget(obj.poincareWidget)
