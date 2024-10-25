import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal




class DataHelper():
    def __init__(self):
        pass

    def read_txt_demo(self, file_pth):
        '''
        用于demo示例文件的读取
        '''
        with open(file_pth, 'r') as file:
            lines = file.readlines()
    
        data = [list(map(float, line.split())) for line in lines]
        matrix = np.array(data).reshape(30, 15)

        temp = matrix[0:15] #温度
        conc = matrix[15:] #浓度

        return temp, conc
    

class ModelInferenceThread(QThread):
    progress_signal = pyqtSignal(int)  # 进度信号，用于更新进度条
    result_ready = pyqtSignal(object, int)  # 推理完成信号，传递推理结果和时间点

    def __init__(self, num_points, data_helper, file_path):
        super().__init__()
        self.num_points = num_points  # 总推理的时间点数
        self.data_helper = data_helper  # 数据读取工具
        self.file_path = file_path  # 文件路径

    def run(self):
        for time_index in range(self.num_points):
            # 模拟推理过程（可以替换为实际模型推理逻辑）
            result = self.data_helper.read_txt_demo(self.file_path)  # 模拟推理结果
            time.sleep(2)  # 模拟推理耗时

            # 发出推理完成信号，传递数据和当前时间点
            self.result_ready.emit(result, time_index)

            # 更新进度条
            progress = int((time_index + 1) / self.num_points * 100)
            self.progress_signal.emit(progress)
    

if __name__ == '__main__':
    datahelper = DataHelper()
    temp, conc = datahelper.read_txt_demo('/Users/xuehao/Desktop/code_proj/aero_1_GUI/data/demo_output.txt')
    # a =1