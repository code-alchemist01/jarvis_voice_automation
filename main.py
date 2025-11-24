"""
JARVIS Desktop Voice Assistant
Main entry point
"""
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow


def exception_hook(exctype, value, tb):
    """Global exception handler to prevent crashes"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"Unhandled exception: {error_msg}")
    
    # Try to show error in message box if possible
    try:
        app = QApplication.instance()
        if app:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("JARVIS Hata")
            msg.setText("Beklenmeyen bir hata oluştu.")
            msg.setDetailedText(error_msg)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    except:
        pass  # If we can't show message box, just continue


def main():
    """Main application entry point"""
    # Set global exception handler
    sys.excepthook = exception_hook
    
    try:
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("JARVIS")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("JARVIS")
        
        # Create and show main window
        try:
            window = MainWindow()
            window.show()
        except Exception as e:
            print(f"Error creating window: {e}")
            traceback.print_exc()
            return 1
        
        # Run application
        try:
            return app.exec_()
        except Exception as e:
            print(f"Error in event loop: {e}")
            traceback.print_exc()
            return 1
    
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

