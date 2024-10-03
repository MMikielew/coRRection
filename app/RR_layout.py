"""
Module responsible for plots placement
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from graph import create_graph

def create_RR_layout(obj):
    """
    Function handling buttons placement
    """
    create_graph(obj)
    obj.RR_layout.addWidget(obj.graphWidget)
    obj.hrv_label = QLabel("Waiting for signal")
    #obj.hrv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #obj.RR_layout.addWidget(obj.hrv_label) to uncomment if HRV back
    obj.RR_layout.addWidget(obj.poincareWidget)
