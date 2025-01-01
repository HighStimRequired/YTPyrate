import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QWidget, QMessageBox, QComboBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pytube import YouTube

class DownloadThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, url, save_path, itag):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.itag = itag

    def run(self):
        yt = YouTube(self.url, on_progress_callback=self.report_progress)
        stream = yt.streams.get_by_itag(self.itag)
        stream.download(output_path=self.save_path)

    def report_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        progress_percent = int((1 - bytes_remaining / total_size) * 100)
        self.progress.emit(progress_percent)

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YTPyrate")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-family: Arial;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.url_label = QLabel("Enter YouTube URL:")
        self.url_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setStyleSheet("font-size: 14px; padding: 5px; background-color: #444444; color: white;")
        self.layout.addWidget(self.url_input)

        self.save_label = QLabel("Choose Save Location:")
        self.save_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.save_label)

        self.save_button = QPushButton("Browse")
        self.save_button.setStyleSheet("background-color: #444444; color: white; padding: 5px;")
        self.save_button.clicked.connect(self.browse_location)
        self.layout.addWidget(self.save_button)

        self.save_location = QLabel("Not selected")
        self.save_location.setStyleSheet("font-size: 12px; color: gray;")
        self.layout.addWidget(self.save_location)

        self.quality_label = QLabel("Select Quality:")
        self.quality_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.quality_label)

        self.quality_selector = QComboBox()
        self.quality_selector.setStyleSheet("background-color: #444444; color: white; padding: 5px;")
        self.layout.addWidget(self.quality_selector)

        self.load_quality_button = QPushButton("Load Qualities")
        self.load_quality_button.setStyleSheet("background-color: #444444; color: white; padding: 5px;")
        self.load_quality_button.clicked.connect(self.load_video_qualities)
        self.layout.addWidget(self.load_quality_button)

        self.download_button = QPushButton("Download")
        self.download_button.setStyleSheet("background-color: #444444; color: white; padding: 10px; font-size: 14px;")
        self.download_button.clicked.connect(self.download_video)
        self.layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("background-color: #444444; color: white;")
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_location.setText(folder)

    def load_video_qualities(self):
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
        url = self.url_input.text().strip()
        save_path = self.save_location.text()
        itag = self.quality_selector.currentData()

        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL.")
            return

        if save_path == "Not selected":
            QMessageBox.warning(self, "Error", "Please select a save location.")
            return

        if itag is None:
            QMessageBox.warning(self, "Error", "Please select a quality.")
            return

        self.download_thread = DownloadThread(url, save_path, itag)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_complete(self):
        QMessageBox.information(self, "Success", "Download complete!")
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
