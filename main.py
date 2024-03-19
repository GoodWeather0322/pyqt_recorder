from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtMultimedia import QMediaDevices

import threading
import multiprocessing
import sys
from pathlib import Path
import pyaudio
import wave
import random


class Recorder(QMainWindow):
    def __init__(self):
        """
        初始化Recorder類的實例。
        """
        super().__init__()
        self.setWindowTitle("Audio Device Selector")
        self.initUI()

    def initUI(self):
        """
        初始化用戶界面，設置主窗口的中央小部件，並添加三個下拉選單和一個刷新按鈕。
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        mainLayout = QVBoxLayout(central_widget)

        # 創建刷新按鈕
        self.setupRefreshButton(mainLayout)

        # 創建包含下拉選單和標籤的布局
        self.setupDeviceSelectors(mainLayout)

        # 新增audio folder下拉選單
        self.setupAudioFolderSelector(mainLayout)

        # 新增用於顯示行數的標籤
        self.labelLineCount = QLabel("Total Lines: ")
        mainLayout.addWidget(self.labelLineCount)

        # 設置下拉選單的選中事件
        self.comboAudioFolder.currentTextChanged.connect(self.updateLineCount)

        # 新增用於顯示選中音頻數據的標籤
        self.selectedAudioDataLabel = QLabel("Selected Audio Data: ")
        mainLayout.addWidget(self.selectedAudioDataLabel)

        # 新增一個按鈕來選擇隨機音頻數據
        self.selectRandomButton = QPushButton("Select Random Audio Data")
        self.selectRandomButton.clicked.connect(self.selectRandomAudioData)
        mainLayout.addWidget(self.selectRandomButton)

        # 新增一個按鈕來播放隨機音頻數據
        self.playButton = QPushButton("Play Selected WAV")
        mainLayout.addWidget(self.playButton)
        self.playButton.clicked.connect(self.playSelectedWav)

        self.setupPlaybackControls(mainLayout)

        self.updateLineCount()

    def setupPlaybackControls(self, layout):
        """
        设置播放控制按钮。
        """
        # 播放控制布局
        playbackControlLayout = QHBoxLayout()

        # PLAY ALL 按钮
        self.playAllButton = QPushButton("PLAY ALL")
        self.playAllButton.clicked.connect(self.playAllAudio)
        playbackControlLayout.addWidget(self.playAllButton)

        # EVERYDAY START TIME 按钮
        self.everydayStartTimeButton = QPushButton("EVERYDAY START TIME")
        # 这里需要定义 onEverydayStartTime 方法
        self.everydayStartTimeButton.clicked.connect(self.onEverydayStartTime)
        playbackControlLayout.addWidget(self.everydayStartTimeButton)

        # EVERYDAY END TIME 按钮
        self.everydayEndTimeButton = QPushButton("EVERYDAY END TIME")
        # 这里需要定义 onEverydayEndTime 方法
        self.everydayEndTimeButton.clicked.connect(self.onEverydayEndTime)
        playbackControlLayout.addWidget(self.everydayEndTimeButton)

        # 将播放控制布局添加到主布局
        layout.addLayout(playbackControlLayout)

    def setupDeviceSelectors(self, layout):
        layout.addWidget(QLabel("Input Device 1:"))
        self.comboInputDevices1 = QComboBox()
        layout.addWidget(self.comboInputDevices1)

        layout.addWidget(QLabel("Input Device 2:"))
        self.comboInputDevices2 = QComboBox()
        layout.addWidget(self.comboInputDevices2)

        layout.addWidget(QLabel("Output Device:"))
        self.comboOutputDevices = QComboBox()
        layout.addWidget(self.comboOutputDevices)

        self.refreshDeviceList()

    def setupRefreshButton(self, layout):
        # 創建一個水平佈局來右對齊按鈕
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        refreshButton = QPushButton("Refresh")
        refreshButton.clicked.connect(self.refreshDeviceList)
        buttonLayout.addWidget(refreshButton)

        # 將按鈕佈局添加到主佈局
        layout.addLayout(buttonLayout)

    def setupAudioFolderSelector(self, layout):
        """
        新增audio folder下拉選單，從prepare_record資料夾讀取目錄作為選項。
        """
        layout.addWidget(QLabel("Audio Folder:"))
        self.comboAudioFolder = QComboBox()
        self.updateAudioFolderList()
        layout.addWidget(self.comboAudioFolder)

    def refreshDeviceList(self):
        """
        重新讀取音頻裝置列表並更新下拉選單。
        """
        inputDevices, outputDevices = self.get_audio_devices()
        self.updateComboBox(self.comboInputDevices1, inputDevices)
        self.updateComboBox(self.comboInputDevices2, inputDevices)
        self.updateComboBox(self.comboOutputDevices, outputDevices)

    def updateComboBox(self, comboBox, deviceList):
        """
        更新下拉選單項目。
        """
        comboBox.clear()
        for device in deviceList:
            comboBox.addItem(device)

    def get_audio_devices(self):
        """
        獲取系統上的音頻輸入和輸出裝置列表。

        Returns:
            tuple: 返回兩個列表，第一個是輸入裝置的列表，第二個是輸出裝置的列表。
        """

        QT_inputDevices = []
        QT_outputDevices = []
        devices = QMediaDevices.audioInputs()
        for device in devices:
            QT_inputDevices.append(device.description())
        devices = QMediaDevices.audioOutputs()
        for device in devices:
            QT_outputDevices.append(device.description())

        p = pyaudio.PyAudio()
        inputDevices = []
        outputDevices = []
        self.deviceName2index = {}
        for i in range(p.get_device_count()):
            deviceInfo = p.get_device_info_by_index(i)
            if deviceInfo.get("maxInputChannels") > 0:
                deviceName = deviceInfo.get("name")
                deviceIndex = deviceInfo.get("index")
                if (
                    deviceName in QT_inputDevices
                    and deviceName not in self.deviceName2index
                ):
                    print(deviceInfo)
                    inputDevices.append(deviceName)
                    self.deviceName2index[deviceName] = deviceIndex
            if deviceInfo.get("maxOutputChannels") > 0:
                deviceName = deviceInfo.get("name")
                deviceIndex = deviceInfo.get("index")
                if (
                    deviceName in QT_outputDevices
                    and deviceName not in self.deviceName2index
                ):
                    outputDevices.append(deviceName)
                    self.deviceName2index[deviceName] = deviceIndex
        p.terminate()
        print(self.deviceName2index)
        return inputDevices, outputDevices

    def updateAudioFolderList(self):
        """
        使用pathlib從prepare_record資料夾讀取目錄並更新audio folder下拉選單。
        """
        folderPath = Path("prepare_record")
        folders = [folder.name for folder in folderPath.iterdir() if folder.is_dir()]
        self.comboAudioFolder.clear()
        for folder in folders:
            self.comboAudioFolder.addItem(folder)

    def updateLineCount(self):
        """
        根據選中的audio folder讀取resource/text文件，計算行數並顯示。
        """
        selectedFolder = self.comboAudioFolder.currentText()
        if selectedFolder:
            folderPath = Path("prepare_record") / selectedFolder / "resource"
            try:
                self.audio_datas = []
                with open(folderPath / "text") as f1, open(
                    folderPath / "wav.scp"
                ) as f2, open(folderPath / "utt2dur") as f3:
                    for l1, l2, l3 in zip(f1, f2, f3):
                        n1, t = l1.strip().split()
                        n2, w = l2.strip().split()
                        n3, d = l3.strip().split()
                        assert n1 == n2 == n3
                        w = folderPath.parent / "wav" / f"{n1}.wav"
                        self.audio_datas.append([n1, t, d, w])
                    self.labelLineCount.setText(f"Total Lines: {len(self.audio_datas)}")
            except FileNotFoundError:
                self.labelLineCount.setText("Total Lines: File not found")

    def selectRandomAudioData(self):
        """
        從self.audio_datas中隨機選擇一個項目並顯示在QLabel上。
        """
        if self.audio_datas:
            selectedData = random.choice(self.audio_datas)
            # 假設selectedData是一個列表，其中包含了你想要顯示的信息
            self.selectedAudioDataLabel.setText(
                f"Selected Audio Data: WAV: {selectedData[3]} , Duration: {selectedData[2]}"
            )
        else:
            self.selectedAudioDataLabel.setText("No data available or not loaded.")
    
    def create_input_stream(self, inputIndex, deviceIndex):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        # p = pyaudio.PyAudio()
        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=deviceIndex,
            frames_per_buffer=CHUNK,
        )

        frames = []
        while True:
            data = stream.read(1024 * 8)
            frames.append(data)
            print(len(frames))
            if self.STOP:
                print("detect STOP")
                break

        wave_file = wave.open(f"prepare_record\\clean\\test{inputIndex}.wav", "wb")
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.p.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b"".join(frames))
        wave_file.close()

        # 錄音完成後關閉所有輸入流
        stream.stop_stream()
        stream.close()
        # p.terminate()
        return f'record success {inputIndex}'

    def create_output_stream(self, outputIndex, deviceIndex, wavPath):
        # p = pyaudio.PyAudio()
        print(outputIndex)
        wf = wave.open(wavPath, "rb")
        audio_data = wf.readframes(wf.getnframes())

        stream = self.p.open(
            format=self.p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=deviceIndex,
        )

        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

        return f'plat audio success {outputIndex}'

    def start_record_and_playback(self, inputDevices, outputDevices, wavPath):

        self.STOP = False
        self.p = pyaudio.PyAudio()

        record_tasks = []
        # for i, inputDevice in enumerate(inputDevices):
        #     recording_thread = threading.Thread(target=self.create_input_stream, args=(i, inputDevice,))
        #     record_tasks.append(recording_thread)
        # for task in record_tasks:
        #     task.start()

        
        playaudio_tasks = []
        for i, outputDevice in enumerate(outputDevices):
            playaudio_thread = threading.Thread(target=self.create_output_stream, args=(i, outputDevice, wavPath))
            playaudio_tasks.append(playaudio_thread)

        for task in playaudio_tasks:
            task.start()
        for task in playaudio_tasks:
            task.join()

        ##-------------------------
        self.p.terminate()

    def playSelectedWav(self):
        """
        播放selectedAudioDataLabel選中的WAV文件。
        """

        inputDevices = []
        deviceName = self.comboInputDevices1.currentText()
        inputDevices.append(self.deviceName2index[deviceName])
        deviceName = self.comboInputDevices2.currentText()
        inputDevices.append(self.deviceName2index[deviceName])

        outputDevices = []
        deviceName = self.comboOutputDevices.currentText()
        outputDevices.append(self.deviceName2index[deviceName])
        outputDevices.append(5)
        outputDevices.append(5)
        outputDevices.append(5)

        text = self.selectedAudioDataLabel.text()
        wavPath = text.split(" ")[4]  # 擷取WAV路徑
        self.start_record_and_playback(inputDevices, outputDevices, wavPath)

    def playAllAudio(self):
        """
        播放所有音频文件。
        """
        pass  # 这里需要实现播放所有音频文件的逻辑

    def onEverydayStartTime(self):
        """
        设置每日开始时间。
        """
        pass  # 这里需要实现设置每日开始时间的逻辑

    def onEverydayEndTime(self):
        """
        设置每日结束时间。
        """
        pass  # 这里需要实现设置每日结束时间的逻辑


if __name__ == "__main__":
    app = QApplication(sys.argv)
    recorder = Recorder()
    recorder.show()

    sys.exit(app.exec())
