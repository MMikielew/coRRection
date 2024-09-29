""" 
moduł odpowiedzialny za obsługę wykresu
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

def create_new_graph(obj):
    """ 
    funkcja tworząca widget zawierający wszystkie elementy wykresów
    """
    # inicjalizacja okna obługującego wykresy
    obj.graphWidget = pg.PlotWidget()
    obj.graphWidget.setBackground('w')
    # tytuł okna
    obj.graphWidget.setWindowTitle('Registered signal')
    # inicjalizacja pierwszego wykresu z zakresem oraz opisami osi
    obj.plot_label = obj.graphWidget.plotItem
    obj.plot_label.setYRange(-100, 1000, padding=0)
    obj.plot_label.setXRange(-100, 30000, padding=0)
    obj.plot_label.setLabels(left = 'RR [ms]', bottom = 'Interval number')

    # inicjalizacja drugiego wykresu wyświetlajacego artefakty
    obj.plot_art = pg.ViewBox()

    # inicjalizacja go wykresu wyświetlajacego 
    obj.p3 = pg.ViewBox()
    obj.hrv_range = pg.ViewBox()

    # inicjalizacja wykresu odpowiedzialnego za wyświetlenie aktualnego kliknięcia kursora
    obj.plot_cursor = pg.ViewBox()
    
    # dodanie widoków do wykresu oraz połączenie ich osi
    for p in [obj.plot_art, obj.p3, obj.hrv_range, obj.plot_cursor]:
        obj.plot_label.scene().addItem(p)
        p.setXLink(obj.plot_label)
        p.setYLink(obj.plot_label)

   
    # dodanie etykiety wyświetlającej współrzędne 
    obj.label = pg.TextItem(text="X: {} \nY: {}".format(0, 0))
    obj.graphWidget.addItem(obj.label)
    obj.graphWidget.scene().sigMouseMoved.connect(obj.mouse_moved)
    obj.graphWidget.scene().sigMouseClicked.connect(obj.mouse_clicked)

    # zmiana widoku po aktualizacji wykresu
    def updateViews():
        # dopasowanie wszystkich wykresów do widoku wykresu 1
        for p in [obj.plot_art, obj.p3, obj.hrv_range, obj.plot_cursor]:
            p.setGeometry(obj.plot_label.vb.sceneBoundingRect())
            p.linkedViewChanged(obj.plot_label.vb, p.XAxis)

    updateViews()
    obj.plot_label.vb.sigResized.connect(updateViews)

def add_point_to_graph(obj):
    obj.plot_cursor.clear()
    RR_values = np.array([interval.value for interval in obj.examination.RR_intervals])
    obj.cursor_coords = pg.ScatterPlotItem([obj.coords_x], [RR_values[obj.coords_x]],
                                       brush=pg.mkBrush(0, 255, 0, 120),
                                       size = 12,
                                       hoverable=True)
    obj.plot_cursor.addItem(obj.cursor_coords)

