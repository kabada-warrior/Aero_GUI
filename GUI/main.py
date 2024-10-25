import os
import sys
import yaml
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, \
                            QWidget, QLabel, QSlider, QProgressBar, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils import DataHelper, ModelInferenceThread





class ContourPlotCanvas(FigureCanvas):

    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(1, 2)
        super().__init__(self.fig)
        self.setParent(parent)

        self.colorbar1 = None
        self.colorbar2 = None
    
    def plot_contour(self, data):
        if self.colorbar1:
            self.colorbar1.remove()
            self.colorbar1 = None  
        if self.colorbar2:
            self.colorbar2.remove()
            self.colorbar2 = None

        self.ax[0].clear()
        self.ax[1].clear()


        contour1 = self.ax[0].contourf(data[0], cmap='viridis')
        contour2 = self.ax[1].contourf(data[1], cmap='plasma')

        self.colorbar1 = self.fig.colorbar(contour1, ax=self.ax[0])
        self.colorbar2 = self.fig.colorbar(contour2, ax=self.ax[1])

        self.draw()


class MainWindow(QMainWindow):

    def __init__(self, cfg_pth):
        super().__init__()
        self.init_cfg(cfg_pth)

        self.data_helper = DataHelper()

        # 模块初始化
        self.init_window()
        self.init_file_path_editor() # 输入文件路径编辑模块
        # self.init_label()
        self.init_canvas()
        self.init_slider()
        self.init_progress_bar()
        self.init_modelThread()

        self.init_show()


    def init_cfg(self, cfg_pth):
        with open(cfg_pth, 'r') as file:
            self.cfg = yaml.safe_load(file)

    
    def init_file_path_editor(self):
        '''
        增加文件路径选择器
        '''
        # 标签显示当前文件路径
        self.file_path_label = QLabel(f"当前数据文件路径: {self.cfg['data']['output_pth']}", self)
        self.file_path_label.setFixedSize(1000, 20)
        self.layout.addWidget(self.file_path_label)

        # 按钮来打开文件选择对话框
        self.select_file_button = QPushButton('选择新的数据文件路径', self)
        self.select_file_button.clicked.connect(self.select_new_file_path)
        self.layout.addWidget(self.select_file_button)


    def select_new_file_path(self):
        '''
        弹出文件选择框，让用户选择新的文件路径，并更新到配置中
        '''
        new_file_path, _ = QFileDialog.getOpenFileName(self, '选择数据文件', '', 'Text Files (*.txt);;All Files (*)')

        if new_file_path:  # 如果用户选择了文件
            # 更新配置中的路径
            self.cfg['data']['output_pth'] = new_file_path
            self.file_path_label.setText(f"当前数据文件路径: {new_file_path}")

            # 保存修改后的配置到 YAML 文件
            with open(self.cfg_pth, 'w') as file:
                yaml.safe_dump(self.cfg, file)

            print(f"配置文件已更新: {new_file_path}")


    def init_show(self):
        data = (np.zeros((15, 15)), np.zeros((15, 15)))
        self.canvas.plot_contour(data)


    def init_progress_bar(self):
        '''
        进度条
        '''
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.cfg['time_steps'])
        self.progress_bar.setValue(0)  # 初始值

        self.layout.addWidget(self.progress_bar)

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)


    def init_modelThread(self):
        cfg = self.cfg['model']
        self.thread = ModelInferenceThread(self.cfg['time_steps'], self.data_helper, self.cfg['data']['output_pth'])
        self.thread.result_ready.connect(self.update_plot)  # 连接推理完成的信号
        self.thread.progress_signal.connect(self.update_progress)  # 连接进度信号
        self.thread.start()  # 开始推理


    def update_plot(self, result, time_index):
        '''
        更新绘图
        '''
        if result:
            # 初始化缓存列表
            if not hasattr(self, 'cached_results'):
                self.cached_results = [None] * self.cfg['time_steps']
            
            # 缓存当前结果
            self.cached_results[time_index] = result

             # 动态更新滑动条的最大值
            if time_index > self.slider.maximum():
                self.slider.setMaximum(time_index)  # 增加滑动条的最大值

            # 更新滑块位置，避免触发 slider_changed 信号
            # self.slider.blockSignals(True)
            # self.slider.setValue(time_index)
            # self.slider.blockSignals(False)

            # 更新绘图
            self.canvas.plot_contour(result)
        else:
            print(f"时间点 {time_index} 的数据无效。")


    def init_canvas(self):
        self.canvas = ContourPlotCanvas(self)
        self.layout.addWidget(self.canvas)


    def init_window(self):
        cfg = self.cfg['window']
        self.setWindowTitle(cfg['name'])
        self.setGeometry(*cfg['size'])

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget) # 垂直布局
    

    def init_label(self):
        '''
        标签,比如校徽logo
        '''
        cfg = self.cfg['label']
        label = QLabel(self)

        pixmap = QPixmap(cfg['pic1']['path'])  
        pixmap = pixmap.scaled(*cfg['pic1']['size'], Qt.KeepAspectRatio)
        label.setPixmap(pixmap)

        label.setGeometry(*cfg['pic1']['pos'], *cfg['pic1']['size'])  # (x, y, width, height)
        self.layout.addWidget(label)


    def init_slider(self):
        '''
        滑动条
        '''
        cfg = self.cfg['slider']

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(cfg['range'][0])  # 滑块最小值
        self.slider.setMaximum(cfg['range'][1])  
        self.slider.setValue(0)    # 初始值

        self.slider.setTickPosition(QSlider.TicksBelow) # 刻度线
        self.slider.setTickInterval(1)

        self.layout.addWidget(self.slider)
        self.slider.valueChanged.connect(self.slider_changed)


    def slider_changed(self):
        # 当滑块值改变时，获取当前的时间点，并更新图表
        time_index = self.slider.value()  # 获取滑块的当前值
        # self.canvas.plot_contour(self.data[time_index])  # 使用当前时间点数据更新图表

        # 测试用 
        data = self.get_data(self.cfg['data']['output_pth'])
        self.canvas.plot_contour(data)
    

    def get_data(self, file_pth):
        return self.data_helper.read_txt_demo(file_pth)



def main(cfg_pth):

    app = QApplication(sys.argv)

    window = MainWindow(cfg_pth)
    window.show()

    sys.exit(app.exec_())




if __name__ == '__main__':
    proj_pth = "/Users/xuehao/Desktop/code_proj/aero_1_GUI"
    cfg_pth = os.path.join(proj_pth, "config/cfg_demo.yml")
    # with open(cfg_pth, 'r') as file:
    #     cfg = yaml.safe_load(file)

    main(cfg_pth)


    