import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox, QToolTip)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer, QEvent
from Cocoa import NSApplication, NSObject, NSApp
from PyObjCTools import AppHelper
import objc
import os
import platform
from converter import make_readwise_format

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
            print("Application did finish launching")
            NSApp.activateIgnoringOtherApps_(True)
        
    def application_openFiles_(self, app, filenames):
        print("Opening files from Finder:", filenames)
        global window
        if window:
            for filename in filenames:
                # Ignore .py files or specifically gui.py to prevent processing during development
                if not filename.endswith('.py'):
                    window.processFilePath(filename)
        
class CSVConverterApp(QWidget):
    def __init__(self, filePath=None):
        super().__init__()
        self.filePath = filePath
        self.currentTooltip = None
        self.infoButtons = []
        self.setFocusPolicy(Qt.StrongFocus)
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
        #self.mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Checkboxes for options
        # Checkboxes with info buttons
        self.splitQuotesCheckbox = self.addCheckboxWithInfo("Split quotes to \"Highlights\" column and non quotes to \"Notes\" column", 'Quotes are indicated by anytime your libby bookmark has anything between quotation marks \nAnything that is not is moved to the Notes section', self.mainLayout)
        self.estimatePageNumberCheckbox = self.addCheckboxWithInfo("Estimate page number from percent of audiobook (Rough Estimate)", "Estimates the page number based on the percentage of the audiobook the \nbookmark was marked at and the total page count of the book. \nRequires internet connection to connect to Google Books API to find page count", self.mainLayout)
        self.notePrefixCheckbox = self.addCheckboxWithInfo("Add \"N:\" as a prefix for any highlight that is not a direct quote", 'Prefixes non-quote highlights with "N:" to differentiate them. \nex. "N: Romeo really does care about Juliet it seems"', self.mainLayout)        
        # Convert button
        self.convertButton = QPushButton('Convert')
        self.convertButton.clicked.connect(self.processFile)
        self.mainLayout.addWidget(self.convertButton)
        
        #self.setFixedSize(self.sizeHint())
        
        if self.infoButtons:  # Check if there are any info buttons
            self.infoButtons[0].setFocus()  # Set focus to the first info button
        # Enable drag and drop
        
        self.setAcceptDrops(True)
        
        self.setLayout(self.mainLayout)
        
        self.adjustSize()
        self.setMinimumSize(self.width(), self.height())
        
    def activateApplication(self):
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        
    def showEvent(self, event):
        # Ensure that the window has the initial focus when shown
        super().showEvent(event)
        self.activateApplication()
        
    def addCheckboxWithInfo(self, label, tooltipText, layout):
        checkboxLayout = QHBoxLayout()
        checkbox = QCheckBox(label)
        checkboxLayout.addWidget(checkbox)
    
        infoButton = QPushButton()
        infoButton.setFocusPolicy(Qt.StrongFocus)
        infoButton.setIcon(QIcon('info-16.png'))  # Ensure the icon path is correct
        infoButton.setIconSize(QSize(12, 12))
        infoButton.setFixedSize(16, 16)
        infoButton.setStyleSheet("QPushButton {border: none; background-color: transparent;}")
    
        # Associate tooltip text with the button using properties
        infoButton.setProperty("tooltipText", tooltipText)
    
        # Connect the custom event handlers
        infoButton.installEventFilter(self)
    
        checkboxLayout.addWidget(infoButton)
        layout.addLayout(checkboxLayout)
        if self.infoButtons:  # Check if there are any info buttons
            self.infoButtons[0].setFocus()
        return checkbox
    
    def processFilePath(self, filePath):
        if os.path.isfile(filePath) and filePath.lower().endswith('.json'):
            self.filePath = filePath
            self.showSelectedFile()  # Update the UI to reflect the selected file
        else:
            QMessageBox.critical(self, "Invalid File", "Please select a valid JSON file.")
                
    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and obj.property("tooltipText"):
            if event.type() == QEvent.Enter:
                self.infoButtonEnter(obj)
                return True
            elif event.type() == QEvent.Leave:
                self.infoButtonLeave(obj)
                return True
        return super().eventFilter(obj, event)
    
    def infoButtonEnter(self, button):
        tooltipText = button.property("tooltipText")
        if tooltipText:
            self.showTooltip(button, tooltipText)
            
    def infoButtonLeave(self, button):
        self.hideTooltip()
        
    def showTooltip(self, parent, text):
        if self.currentTooltip:
            self.currentTooltip.close()
        self.currentTooltip = QLabel(text, self, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.currentTooltip.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #f0f0f0;
                padding: 4px;
                border-radius: 5px;
                font: 12px;
            }
        """)
        self.currentTooltip.adjustSize()
        self.currentTooltip.move(parent.mapToGlobal(QPoint(20, -self.currentTooltip.height() - 10)))
        self.currentTooltip.show()
        
    def hideTooltip(self):
        if self.currentTooltip:
            self.currentTooltip.close()
            self.currentTooltip = None

            
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
        
        
        splitQuotes = self.splitQuotesCheckbox.isChecked()
        estimatePageNumber = self.estimatePageNumberCheckbox.isChecked()
        notePrefix = self.notePrefixCheckbox.isChecked()
        try:
            df= make_readwise_format(self.filePath, splitQuotes, estimatePageNumber, notePrefix)
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
    delegate = AppDelegate.alloc().init()
    NSApplication.sharedApplication().setDelegate_(delegate)
    window = CSVConverterApp()
    window.show()
    sys.exit(app.exec_())
    