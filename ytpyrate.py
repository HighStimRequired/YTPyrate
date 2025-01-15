import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, 
    QVBoxLayout, QWidget, QMessageBox, QComboBox, QProgressBar, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pytube import YouTube

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url, save_path, itag):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.itag = itag

    def run(self):
        yt = YouTube(self.url, on_progress_callback=self.report_progress)
        stream = yt.streams.get_by_itag(self.itag)
        stream.download(output_path=self.save_path)
        self.finished.emit()

    def report_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        progress_percent = int((1 - bytes_remaining / total_size) * 100)
        self.progress.emit(progress_percent)

class YTPyrate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YTPyrate - YouTube Downloader")
        self.setFixedSize(520, 480)
        self.setStyleSheet("background-color: #09000f; color: white;")

        self.font = QFont("Roboto", 12)
        self.button_font = QFont("Roboto", 12, QFont.Weight.Bold)

        self.input_url = ""
        self.output_folder = ""
        self.output_filename = ""
        self.sizes = []

        self.init_ui()

    def init_ui(self):
        """Creates the modern UI layout"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("YouTube Video Downloader")
        title.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Divider
        layout.addWidget(self.create_divider())

        # YouTube URL Input
        self.url_input = QLineEdit()
        self.url_input.setFont(self.font)
        self.url_input.setPlaceholderText("Enter YouTube URL")
        self.url_input.setStyleSheet("background-color: #6b4a5e; color: white; padding: 6px;")
        layout.addWidget(self.url_input)

        # Load Video Qualities
        self.load_quality_button = QPushButton("Load Video Qualities")
        self.load_quality_button.setFont(self.button_font)
        self.load_quality_button.setStyleSheet(self.button_style())
        self.load_quality_button.clicked.connect(self.load_video_qualities)
        layout.addWidget(self.load_quality_button)

        # Quality Selector
        self.quality_selector = QComboBox()
        self.quality_selector.setFont(self.font)
        self.quality_selector.setStyleSheet("background-color: #6b4a5e; color: white; padding: 6px;")
        layout.addWidget(self.quality_selector)

        # Divider
        layout.addWidget(self.create_divider())

        # Output Folder Selection
        self.output_label = QLabel("Save Location: Not selected")
        self.output_label.setFont(self.font)
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.output_label)

        self.browse_button = QPushButton("Choose Output Folder")
        self.browse_button.setFont(self.button_font)
        self.browse_button.setStyleSheet(self.button_style())
        self.browse_button.clicked.connect(self.browse_location)
        layout.addWidget(self.browse_button)

        # Divider
        layout.addWidget(self.create_divider())

        # Download Button
        self.download_button = QPushButton("Download Video")
        self.download_button.setFont(self.button_font)
        self.download_button.setStyleSheet(self.button_style())
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("background-color: #6b4a5e; color: white;")
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setFont(self.font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_divider(self):
        """Creates a modern divider"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #6b4a5e;")
        return line

    def button_style(self):
        """Returns a consistent button style"""
        return """
        QPushButton {
            background-color: #6b4a5e;
            color: white;
            border-radius: 5px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #8c6278;
        }
        QPushButton:pressed {
            background-color: #5a3a4c;
        }
        """

    def browse_location(self):
        """Opens folder dialog to select output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.output_folder = folder
            self.output_label.setText(f"Save Location: {folder}")

    def load_video_qualities(self):
        """Loads available video and audio qualities"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL.")
            return

        try:
            yt = YouTube(url)
            self.quality_selector.clear()
            for stream in yt.streams.filter(progressive=True):
                self.quality_selector.addItem(f"{stream.resolution} - {stream.mime_type}", stream.itag)
            for stream in yt.streams.filter(only_audio=True):
                self.quality_selector.addItem(f"Audio Only - {stream.mime_type}", stream.itag)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load video qualities: {str(e)}")

    def download_video(self):
        """Starts the video download"""
        url = self.url_input.text().strip()
        save_path = self.output_folder
        itag = self.quality_selector.currentData()

        if not url or not save_path or itag is None:
            QMessageBox.warning(self, "Error", "Please enter all details correctly.")
            return

        self.status_label.setText("Downloading...")
        self.download_thread = DownloadThread(url, save_path, itag)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.start()

    def download_complete(self):
        """Handles completion of download"""
        self.status_label.setText("Download Complete!")
        QMessageBox.information(self, "Success", "Download complete!")
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YTPyrate()
    window.show()
    sys.exit(app.exec())
