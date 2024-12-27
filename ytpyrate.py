import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from pytube import YouTube

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window setup
        self.setWindowTitle("YTPyrate")
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-family: Arial;")

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout setup
        self.layout = QVBoxLayout(self.central_widget)

        # YouTube URL label and input
        self.url_label = QLabel("Enter YouTube URL:")
        self.url_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setStyleSheet("font-size: 14px; padding: 5px; background-color: #444444; color: white;")
        self.layout.addWidget(self.url_input)

        # Save location label and button
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

        # Download button
        self.download_button = QPushButton("Download Video")
        self.download_button.setStyleSheet("background-color: #444444; color: white; padding: 10px; font-size: 14px;")
        self.download_button.clicked.connect(self.download_video)
        self.layout.addWidget(self.download_button)

    def browse_location(self):
        """Open a file dialog to select the save location."""
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_location.setText(folder)

    def download_video(self):
        """Download the YouTube video."""
        url = self.url_input.text().strip()
        save_path = self.save_location.text()

        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL.")
            return

        if save_path == "Not selected":
            QMessageBox.warning(self, "Error", "Please select a save location.")
            return

        try:
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            video.download(output_path=save_path)
            QMessageBox.information(self, "Success", f"Video downloaded successfully to {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
