"""
Main GUI window for JARVIS
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QBrush
from core.voice_recognition import VoiceRecognition
from core.text_to_speech import TextToSpeech
from core.command_processor import CommandProcessor
from core.llm_client import LLMClient
from gui.settings_window import SettingsWindow


class VoiceRecognitionThread(QThread):
    """Thread for voice recognition to avoid blocking UI"""
    command_received = pyqtSignal(str, str)  # text, language
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.voice_recognition = VoiceRecognition()
        self.is_running = False
        self.listen_thread = None
    
    def run(self):
        """Run continuous listening"""
        self.is_running = True
        
        def callback(text, language):
            if self.is_running:
                self.command_received.emit(text, language)
        
        self.listen_thread = self.voice_recognition.listen_continuous(callback)
        if self.listen_thread:
            self.listen_thread.join()
    
    def stop(self):
        """Stop listening"""
        self.is_running = False
        self.voice_recognition.stop_listening()


class WaveformWidget(QWidget):
    """Animated waveform widget for visual feedback"""
    
    def __init__(self):
        super().__init__()
        self.amplitude = 0
        self.is_active = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.setFixedHeight(80)
        self.setMinimumWidth(200)
    
    def start_animation(self):
        """Start waveform animation"""
        self.is_active = True
        self.timer.start(50)  # Update every 50ms
    
    def stop_animation(self):
        """Stop waveform animation"""
        self.is_active = False
        self.timer.stop()
        self.amplitude = 0
        self.update()
    
    def update_animation(self):
        """Update animation frame"""
        if self.is_active:
            import random
            self.amplitude = random.randint(20, 80)
        self.update()
    
    def paintEvent(self, event):
        """Paint waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Draw waveform bars
        bar_count = 20
        bar_width = width // bar_count
        spacing = 2
        
        if self.is_active:
            for i in range(bar_count):
                x = i * (bar_width + spacing)
                bar_height = int(self.amplitude * (0.5 + 0.5 * abs(i - bar_count/2) / (bar_count/2)))
                bar_height = max(5, min(bar_height, height - 10))
                
                # Create gradient color (blue to cyan)
                color = QColor(0, 150 + bar_height, 255)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.NoPen)
                
                y = center_y - bar_height // 2
                painter.drawRect(x, y, bar_width - spacing, bar_height)
        else:
            # Draw idle state (small bars)
            for i in range(bar_count):
                x = i * (bar_width + spacing)
                bar_height = 5
                color = QColor(100, 100, 100)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.NoPen)
                y = center_y - bar_height // 2
                painter.drawRect(x, y, bar_width - spacing, bar_height)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.voice_thread = None
        self.tts = TextToSpeech()
        self.command_processor = CommandProcessor()
        self.llm_client = LLMClient()
        self.is_listening = False
        self.init_ui()
        self.check_llm_status()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("JARVIS - Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 2px solid #00aaff;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00aaff;
                border-color: #00ccff;
            }
            QPushButton:pressed {
                background-color: #0088cc;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                border-color: #555555;
                color: #888888;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #00aaff;
                border-radius: 10px;
                padding: 10px;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #00aaff;
                border-radius: 10px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("JARVIS")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00aaff;")
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        main_layout.addWidget(subtitle)
        
        # Waveform widget
        self.waveform = WaveformWidget()
        main_layout.addWidget(self.waveform, alignment=Qt.AlignCenter)
        
        # LLM Status indicator
        llm_status_layout = QHBoxLayout()
        llm_status_layout.setAlignment(Qt.AlignCenter)
        
        self.llm_status_label = QLabel("LLM: Kontrol ediliyor...")
        self.llm_status_label.setAlignment(Qt.AlignCenter)
        self.llm_status_label.setStyleSheet("color: #888888; font-size: 11px;")
        llm_status_layout.addWidget(self.llm_status_label)
        
        main_layout.addLayout(llm_status_layout)
        
        # Status label
        self.status_label = QLabel("Hazır - Başlatmak için butona tıklayın")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00ff00; font-size: 14px;")
        main_layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.start_button = QPushButton("Başlat")
        self.start_button.clicked.connect(self.start_listening)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Durdur")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.settings_button = QPushButton("Ayarlar")
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(button_layout)
        
        # Command history
        history_label = QLabel("Komut Geçmişi:")
        history_label.setStyleSheet("color: #00aaff; font-size: 16px; font-weight: bold;")
        main_layout.addWidget(history_label)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(200)
        main_layout.addWidget(self.history_text)
        
        # Add initial message
        llm_status = "Akıllı Mod (LLM)" if self.llm_client.is_available() else "Basit Mod (Regex)"
        self.add_to_history(f"JARVIS başlatıldı. Mod: {llm_status}")
        self.add_to_history("Sesli komutlarınızı dinlemeye hazır.")
    
    def start_listening(self):
        """Start voice recognition"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Dinleniyor... Konuşun")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 14px;")
        self.waveform.start_animation()
        
        # Start voice recognition thread
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.command_received.connect(self.on_command_received)
        self.voice_thread.error_occurred.connect(self.on_error)
        self.voice_thread.start()
        
        self.add_to_history("Ses tanıma başlatıldı.")
        try:
            self.tts.speak("Jarvis hazır. Komutlarınızı dinliyorum.")
        except Exception as e:
            print(f"TTS error on start: {e}")
    
    def stop_listening(self):
        """Stop voice recognition"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Durduruldu")
        self.status_label.setStyleSheet("color: #ff8800; font-size: 14px;")
        self.waveform.stop_animation()
        
        # Stop voice recognition thread
        if self.voice_thread:
            try:
                self.voice_thread.stop()
                self.voice_thread.quit()
                # Wait with timeout
                if not self.voice_thread.wait(2000):  # 2 second timeout
                    self.voice_thread.terminate()
                    self.voice_thread.wait(1000)
            except Exception as e:
                print(f"Error stopping thread: {e}")
            finally:
                self.voice_thread = None
        
        self.add_to_history("Ses tanıma durduruldu.")
        try:
            self.tts.speak("Jarvis durduruldu.")
        except Exception as e:
            print(f"TTS error on stop: {e}")
    
    def on_command_received(self, text, language):
        """Handle received command"""
        try:
            self.add_to_history(f"Komut: {text}")
            self.status_label.setText(f"İşleniyor: {text[:30]}...")
            self.status_label.setStyleSheet("color: #ffff00; font-size: 14px;")
            
            # Process command with comprehensive error handling
            try:
                success, message = self.command_processor.process_command(text, language)
            except KeyboardInterrupt:
                # Don't catch keyboard interrupts
                raise
            except SystemExit:
                # Don't catch system exits
                raise
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error processing command: {e}")
                print(f"Traceback: {error_trace}")
                success = False
                # Don't expose internal errors to user
                if "screenshot" in text.lower() or "ekran" in text.lower():
                    message = "Ekran görüntüsü alınırken bir sorun oluştu. Lütfen tekrar deneyin."
                else:
                    message = f"Komut işlenirken hata oluştu. Lütfen tekrar deneyin."
            
            # Update UI safely
            try:
                if success:
                    self.status_label.setText("Başarılı")
                    self.status_label.setStyleSheet("color: #00ff00; font-size: 14px;")
                    self.add_to_history(f"✓ {message}")
                    # Limit TTS message length and handle TTS errors
                    try:
                        tts_message = message[:200] if len(message) > 200 else message
                        self.tts.speak(tts_message)
                    except Exception as tts_error:
                        print(f"TTS error: {tts_error}")
                else:
                    self.status_label.setText("Hata")
                    self.status_label.setStyleSheet("color: #ff0000; font-size: 14px;")
                    self.add_to_history(f"✗ {message}")
                    # Only speak error if it's a user-friendly message
                    try:
                        if "anlaşılamadı" in message.lower() or "anlayamadım" in message.lower():
                            self.tts.speak("Üzgünüm, komutu anlayamadım. Lütfen tekrar deneyin.")
                    except Exception as tts_error:
                        print(f"TTS error: {tts_error}")
                
                # Reset status after a delay
                QTimer.singleShot(2000, lambda: self.status_label.setText("Dinleniyor... Konuşun") 
                                 if self.is_listening else None)
            except Exception as ui_error:
                print(f"UI update error: {ui_error}")
                # At least add to history
                self.add_to_history(f"Hata: UI güncellenemedi")
                
        except (KeyboardInterrupt, SystemExit):
            # Re-raise critical exceptions
            raise
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Critical error in on_command_received: {e}")
            print(f"Traceback: {error_trace}")
            try:
                self.add_to_history(f"Kritik hata: Program çalışmaya devam ediyor...")
                self.status_label.setText("Hata - Devam ediliyor")
            except:
                pass  # If even this fails, just continue
    
    def on_error(self, error_message):
        """Handle error"""
        self.add_to_history(f"Hata: {error_message}")
        self.status_label.setText("Hata oluştu")
        self.status_label.setStyleSheet("color: #ff0000; font-size: 14px;")
    
    def open_settings(self):
        """Open settings window"""
        settings = SettingsWindow(self)
        settings.settings_changed.connect(self.on_settings_changed)
        settings.exec_()
    
    def on_settings_changed(self):
        """Handle settings change"""
        # Reload TTS with new settings
        if hasattr(self, 'tts'):
            self.tts = TextToSpeech()
        
        # Update LLM client
        if hasattr(self, 'llm_client'):
            self.llm_client = LLMClient()
        
        # Update command processor
        if hasattr(self, 'command_processor'):
            self.command_processor = CommandProcessor()
        
        self.add_to_history("Ayarlar güncellendi.")
    
    def check_llm_status(self):
        """Check LLM connection status"""
        if self.llm_client.is_available():
            self.llm_status_label.setText("LLM: ✓ Bağlı (Akıllı Mod)")
            self.llm_status_label.setStyleSheet("color: #00ff00; font-size: 11px;")
        else:
            self.llm_status_label.setText("LLM: ✗ Bağlı Değil (Basit Mod)")
            self.llm_status_label.setStyleSheet("color: #ff8800; font-size: 11px;")
        
        # Check again after 30 seconds
        QTimer.singleShot(30000, self.check_llm_status)
    
    def add_to_history(self, message):
        """Add message to history"""
        self.history_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.history_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            # Stop TTS
            if hasattr(self, 'tts') and self.tts:
                try:
                    self.tts.stop()
                except:
                    pass
            
            # Stop listening
            if self.is_listening:
                try:
                    self.stop_listening()
                except Exception as e:
                    print(f"Error stopping listening on close: {e}")
            
            # Stop voice thread
            if self.voice_thread:
                try:
                    self.voice_thread.stop()
                    self.voice_thread.quit()
                    if not self.voice_thread.wait(1000):
                        self.voice_thread.terminate()
                except:
                    pass
            
            event.accept()
        except Exception as e:
            print(f"Error in closeEvent: {e}")
            # Force accept to allow closing
            event.accept()

