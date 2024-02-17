import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from converter import make_readwise_format
import os
import platform

class CSVConverterApp(QWidget):
    def __init__(self, filePath=None):
        super().__init__()
        self.filePath = filePath
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Libby2Readwise')
        self.setGeometry(100, 100, 600, 300)
        
        self.mainLayout = QVBoxLayout()
        
        # Instructions label with a dashed border to indicate drop zone
        self.label = QLabel('Drag and Drop JSON File From Libby Here')
        self.label.setAlignment(Qt.AlignCenter)
        # Set the style sheet for the label to create a dashed border
        self.label.setStyleSheet("border: 2px dashed #aaa;")
        self.label.setMinimumSize(200, 200)  # Set a minimum size for better visibility
        self.label.setWordWrap(True)
        self.mainLayout.addWidget(self.label)
    
        # Horizontal layout for "or" label and Choose File button
        self.fileSelectionLayout = QHBoxLayout()
    
        self.fileSelectionLayout = QHBoxLayout()
        self.fileSelectionLayout.addStretch(1)  # Add stretch to center the elements
    
        self.orLabel = QLabel('or')
        self.fileSelectionLayout.addWidget(self.orLabel)
    
        self.chooseFileButton = QPushButton('Choose File')
        self.chooseFileButton.clicked.connect(self.openFileDialog)
        self.fileSelectionLayout.addWidget(self.chooseFileButton)
    
        self.fileSelectionLayout.addStretch(1)

        self.mainLayout.addLayout(self.fileSelectionLayout)
    
        # Add some space
        self.mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Checkboxes for options
        self.checkbox1 = QCheckBox('Split quotes to "Highlights" column and non quotes to "Notes" column')
        self.mainLayout.addWidget(self.checkbox1)
        
        self.checkbox2 = QCheckBox('Add percent as "Location" for quote. (ie 95% is stored as 95)')
        self.mainLayout.addWidget(self.checkbox2)
        
        # Convert button
        self.convertButton = QPushButton('Convert')
        self.convertButton.clicked.connect(self.processFile)
        self.mainLayout.addWidget(self.convertButton)
        
        self.setFixedSize(self.sizeHint())
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.setLayout(self.mainLayout)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.filePath = files[0]  # Assume only one file is relevant
            filename = os.path.basename(self.filePath)
            self.label.setText(f'File selected: {filename}')
    
    def openFileDialog(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select JSON file", "", "JSON files (*.json);;All files (*.*)")
        if filePath:
            self.filePath = filePath
            filename = os.path.basename(self.filePath)
            self.label.setText(f'File selected: {filename}')
    
    def showSelectedFile(self):
        if self.filePath:
            filename = os.path.basename(self.filePath)
            self.label.setText(f'File selected: {filename}')
    
    def processFile(self):
        if not self.filePath:
            self.label.setText('Please drag and drop a JSON file first.')
            return
        # Assuming the file is a JSON that can be directly converted to a DataFrame
        
        
        splitQuotes = self.checkbox1.isChecked()
        percentLocations = self.checkbox2.isChecked()
        try:
            df = make_readwise_format(self.filePath, splitQuotes, percentLocations)
            # Process DataFrame as per your requirements
            # For example: Convert 'percent' to 'Location', adjust percentages, etc.
            # This step depends on the specifics of your JSON structure and processing needs
            
            # Export to CSV
            savePath = self.filePath.replace('.json', '_readwise.csv')
            df.to_csv(savePath, index=False, encoding='utf-8')
            self.label.setText(f'Success! Saved to: {savePath}')
        except Exception as e:  # Catch any exception during processing or saving
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Check if a file path is passed as an argument
    filePath = sys.argv[1] if len(sys.argv) > 1 else None

    window = CSVConverterApp(filePath=filePath)
    window.showSelectedFile()  # Show selected file on startup if launched with a file argument
    window.show()
    sys.exit(app.exec_())
    