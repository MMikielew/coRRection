"""
module containing Window definition
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6 import QtCore

from artifacts import find_art_tarvainen, find_art_quotient, find_art1, find_art2, find_art3, remove_artifacts, find_art_quotient
from examination import Examination
from hrv import count_hrv, create_hrv_summary
from widgets import create_widgets
from new_graph import add_point_to_graph
from view_manager import initialize_views

class Window(QWidget):
    """
    Główne okno aplikacji
    """
    def __init__(self):
        super().__init__()
        # dostosowanie wielkości okna
        self.resize(700, 500)
        self.setStyleSheet("QLabel{font-size: 8pt;}")
        
        # tytuł aplikacji
        self.setWindowTitle("Application to correct artifacts in RR intervals")
        # ścieżka do obsługiwanego pliku
        self.fname = ""
        # badanie
        self.examination = Examination()
        self.create_poincare()
        initialize_views(self)
        # zmienna przechowująca aktywne elementy wykresu //chyba nie jest dłużej potrzebne
        self.active_plot_items = []
        self.chosen_artifacts = []
        self.method = "lin"
        # zmienne przechowująca współrzędne pierwszego punktu do oznaczenia
        self.coords_x = None
        self.coords_y = None
        
        # stworzenie początkowych widgetów
        
        create_widgets(self)
       

    def open_dialog(self):
        """
        funkcja odpowiedzialna za wybór pliku z okna dialogowego
        """
        dialog = QFileDialog()
        self.fname, _ = dialog.getOpenFileName(
            self,
            "Open File",
        )
        if self.fname:
            self.examination = Examination(self.fname)
            self.h1.setChecked(True)
            self.coords_x = None
            self.update_plot()
            # wpisanie numerów pierwszego i ostatniego interwału do textboxów 
            self.textbox_start.setText("0")
            self.textbox_end.setText(f"{str(len(self.examination.RR_intervals)-1)}")

    def mouse_moved(self, evt):
        """
        funkcja wychwytująca ruch myszki w obrębie wykresu
        """
        vb = self.graphWidget.plotItem.vb
        if self.graphWidget.sceneBoundingRect().contains(evt):
            mouse_point = vb.mapSceneToView(evt)
            self.label.setHtml(f"<p style='color:white'>X: {mouse_point.x()} <br> Y: {mouse_point.y()}</p>")

    def mouse_clicked(self, evt):
        """
        funkcja wychwytująca kliknięcie myszki w obrębie wykresu
        """
        vb = self.graphWidget.plotItem.vb
        scene_coords = evt.scenePos()
        if self.graphWidget.sceneBoundingRect().contains(scene_coords):
            mouse_point = vb.mapSceneToView(scene_coords)
            diff_y = np.abs(np.array([interval.value for interval in self.examination.RR_intervals]) - mouse_point.y())
            diff_x = np.abs(np.array(range(len(self.examination.RR_intervals))) - mouse_point.x())
            idx = (np.abs(diff_x + diff_y)).argmin()
            self.coords_x = idx
            add_point_to_graph(self)

    def update_hrv_params(self):
        """
        funkcja odpowiadajaca za przeliczenie parametrow hrv i wyswietlenie nowych wartosci
        """
        new_params = create_hrv_summary(count_hrv(self))
        self.hrv_label.setText(new_params)
   
    def choose_artifact(self):
        """
        funkcja oznaczająca nowy artefakt
        """
        if self.coords_x:
            self.examination.artifacts["Manual"].append(self.coords_x)
            self.plot_artifacts()

    def del_artifact(self, points_to_del):
        """ 
        funkcja usuwająca wybrane artefakty
        """
        for key in self.examination.artifacts.keys():
            if len(points_to_del) > 0:
                for point in points_to_del:
                    if point in self.examination.artifacts[key]:
                        self.examination.artifacts[key].remove(point)
        
        self.plot_artifacts()

    def save_data(self):
        """
        function o save data in .txt format
        """
        dialog = QFileDialog()
        file_name = f"{self.examination.path[:-4]}_clean" if self.h1.isChecked() == True else f"{self.examination.path[:-4]}_short_clean"
        fname, _ = dialog.getSaveFileName(
            self,
            "Open File",
            f"{file_name}",
        )
        if len(fname)> 0:
            if ".txt" in fname:
                fname = fname[:-4]
            if self.h1.isChecked() == True:
                self.examination.save_to_txt(f"{fname}.txt")
            else:
                self.examination.save_to_txt(f"{fname}.txt", range=[self.exam_start, self.exam_stop])
            with open(f'{fname}_stats.txt', 'w') as f:
                f.write(f"number of removed artifacts: {self.examination.original_len - len(self.examination.RR_intervals)}\n")
                f.write(f"number of corrected artifacts: {sum(1 for interval in self.examination.RR_intervals if (interval.artifact is not None))}\n")
                
                for key in self.examination.RR_intervals[0].correction_methods.keys():
                    sum_pre_mean_artifact_true = sum(interval.correction_methods[key] for interval in self.examination.RR_intervals if interval.artifact)
                    f.write("Count for %s: %s\n" % (key, sum_pre_mean_artifact_true))

                unique_artifacts = {interval.artifact for interval in self.examination.RR_intervals if interval.artifact}

                sums_by_artifact = {value: sum(1 for interval in self.examination.RR_intervals if interval.artifact == value) for value in unique_artifacts}
                for artifact, total_sum in sums_by_artifact.items():
                    f.write(f"Count for {artifact}: {total_sum}\n")
    
                
                f.write("\nHRV parameters:\n")
                f.write(self.hrv_label.text())

    def auto_detect(self):
        """
        funkcja znajdujaca artefakty automatycznie i wykreslajaca je na wykresie
        """
        # warunek wczytania badania
        if len(self.examination.RR_intervals) > 0:
            self.examination.artifacts["T1"] = find_art1(self)
            self.examination.artifacts["T2"] = find_art2(self)
            self.examination.artifacts["T3"] = find_art3(self)
            self.plot_artifacts()

    def auto_tarvainen(self):
        if len(self.examination.RR_intervals) > 0:
            self.examination.artifacts["Tarvainen"] = find_art_tarvainen(self)
            self.plot_artifacts()

    def auto_poincare(self):
        if len(self.examination.RR_intervals) > 0:
            self.examination.artifacts["Quotient"] = find_art_quotient(self)
            self.plot_artifacts()
    
    def clear_artifacts(self):
        if len(self.examination.RR_intervals) > 0:
            for key in (self.examination.artifacts.keys()):
                self.examination.artifacts[key] = []
            self.plot_artifacts()

            
    def delete_chosen_artifacts(self):
        """
        funkcja odpowiedzialna za usuwanie wybranych artefaktow
        """
        self.chosen_artifacts = [chbx.text() for chbx in self.checkbox_list if chbx.isChecked()]
        if len(self.chosen_artifacts) > 0:
            to_del = remove_artifacts(self)
            self.update_plot()
            self.del_artifact(to_del)
            self.update_hrv_params()

    def create_poincare(self):
        self.poincareWidget = pg.PlotWidget()
        self.poincareWidget.setBackground('w')
        self.poincareWidget.setWindowTitle('Poincare plot')

        self.poincare_label = self.poincareWidget.plotItem
        self.poincare_label.setLabels(left='RRi+1 [ms]', bottom='RRi [ms]')

        """obj.plot_label = obj.graphWidget.plotItem
        obj.plot_label.setYRange(-100, 1000, padding=0)
        obj.plot_label.setXRange(-100, 30000, padding=0)
        obj.plot_label.setLabels(left = 'RR [ms]', bottom = 'Interval number')"""

        self.plot_poincare = pg.ViewBox()
        self.points_poin_art = pg.ViewBox()

        for p in [self.plot_poincare, self.points_poin_art]:
            self.poincare_label.scene().addItem(p)
            p.setXLink(self.poincare_label)
            p.setYLink(self.poincare_label)
        
        def updateViews():
            for p in [self.plot_poincare, self.points_poin_art]:
                p.setGeometry(self.poincare_label.vb.sceneBoundingRect())
                p.linkedViewChanged(self.poincare_label.vb, p.XAxis)

        updateViews()
        self.poincare_label.vb.sigResized.connect(updateViews)

        # Define scatter plot for Poincaré plot
        self.points_poincare = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush('b'), 
                                                 pxMode=True)

        self.plot_poincare.addItem(self.points_poincare)
        
    

    def update_plot(self):
        """
        funkcja aktualizująca wykres po zmianie jego parametrow
        """
        for p in [self.plot_art, self.p3, self.plot_cursor, self.legend, self.plot_poincare]:
            p.clear()
        
        self.plot_label.setXRange(-100, len(self.examination.RR_intervals)+150, padding=0)
        self.plot_label.setYRange(-100, max(self.examination.RR_intervals, key=lambda interval: interval.value).value+150, padding=0)
        self.RRs = pg.PlotCurveItem([interval.value for interval in self.examination.RR_intervals], pen='b')
        self.plot_art.addItem(self.RRs)
        self.update_hrv_params() 

        # Set x and y limits for the Poincaré plot
        xy_min = min(self.examination.RR_intervals, key=lambda interval: interval.value).value - 5
        xy_max = max(self.examination.RR_intervals, key=lambda interval: interval.value).value + 5
        self.plot_poincare.setXRange(xy_min, xy_max)
        self.plot_poincare.setYRange(xy_min, xy_max)
        
        x_values = [interval.value for interval in self.examination.RR_intervals[:-1]]
        y_values = [interval.value for interval in self.examination.RR_intervals[1:]]
        self.points_poincare.setData(x_values, y_values) 
        self.plot_poincare.addItem(self.points_poincare)
        self.plot_poincare.addItem(self.points_poin_art)
        
    def plot_artifacts(self):
        """
        funkcja odpowiedzialna za wykreslanie artefaktów na wykresie
        """
        #self.exam_start
        #self.exam_stop
        # okreslenie miejsc występowania artefaktów

        self.brush_colors = {'Tarvainen': pg.mkBrush(255, 196, 61, 255), 
                            'Quotient': pg.mkBrush(6, 214, 160, 255),
                            'T1': pg.mkBrush(192, 214, 223, 255),
                            'T2': pg.mkBrush(192, 50, 33, 255),
                            'T3': pg.mkBrush(157, 68, 181, 255),
                            'Manual': pg.mkBrush(68, 43, 72, 255)}
        self.scatter_points = {'Tarvainen': pg.ScatterPlotItem(), 
                                'Quotient': pg.ScatterPlotItem(),
                                'T1': pg.ScatterPlotItem(),
                                'T2': pg.ScatterPlotItem(),
                                'T3': pg.ScatterPlotItem(),
                                'Manual': pg.ScatterPlotItem()}
        self.scatter_poincare = {'Tarvainen': pg.ScatterPlotItem(), 
                                'Quotient': pg.ScatterPlotItem(),
                                'T1': pg.ScatterPlotItem(),
                                'T2': pg.ScatterPlotItem(),
                                'T3': pg.ScatterPlotItem(),
                                'Manual': pg.ScatterPlotItem()}

        # clear previously found artifacts
        self.p3.clear()
        self.plot_poincare.clear()
        self.update_plot()

        # adding new scatterpoints
        for key in self.scatter_points.keys():
            # add artifacts on examination plot
            self.scatter_points[key] = pg.ScatterPlotItem(self.examination.artifacts[key], 
                                       list(map(lambda idx: self.examination.RR_intervals[idx].value, self.examination.artifacts[key])),            
                                       brush=self.brush_colors[key], hoverable=True)
            self.p3.addItem(self.scatter_points[key])

            # add artifacts on pioncare plot
            RRi1_list = np.array([x - 1 for x in self.examination.artifacts[key]])
            if len(RRi1_list) > 0:
                self.scatter_poincare[key] = pg.ScatterPlotItem(list(map(lambda idx: self.examination.RR_intervals[idx].value, RRi1_list.tolist())),
                                                                list(map(lambda idx: self.examination.RR_intervals[idx].value, self.examination.artifacts[key])), 
                                                                brush=self.brush_colors[key],
                                                                hoverable=True)
            #self.scatter_poincare[key].setData() 
            self.plot_poincare.addItem(self.scatter_poincare[key])

        """for points in [self.points_T1_auto, self.points_T2_auto, self.points_T3_auto,
                   self.points_T1_manual, self.points_T2_manual, self.points_T3_manual,
                   self.points_diff]:
            points = list(filter(lambda x: x > self.exam_start ))"""        
        
        """"""

        # ustawienia legendy 
        self.legend.clear()
        for key in self.scatter_points.keys():
            self.legend.addItem(self.scatter_points[key], key)
        self.legend.setPos(self.legend.mapFromItem(self.legend, QtCore.QPointF(0, max(self.examination.RR_intervals, key=lambda interval: interval.value).value)))
