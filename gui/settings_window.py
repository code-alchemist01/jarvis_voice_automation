"""
Settings window for JARVIS
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QLineEdit, QPushButton, QSlider, QSpinBox,
                             QComboBox, QCheckBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.config import config


class SettingsWindow(QDialog):
    """Settings dialog window"""
    
    settings_changed = pyqtSignal()  # Signal emitted when settings are saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS Ayarları")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "Genel")
        
        # TTS tab
        tts_tab = self.create_tts_tab()
        tabs.addTab(tts_tab, "Ses")
        
        # LLM tab
        llm_tab = self.create_llm_tab()
        tabs.addTab(llm_tab, "AI")
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "Görünüm")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QVBoxLayout()
        
        # User name
        name_group = QGroupBox("Kullanıcı Bilgileri")
        name_layout = QVBoxLayout()
        name_label = QLabel("Kullanıcı Adı:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_group.setLayout(name_layout)
        widget.addWidget(name_group)
        
        # Language
        lang_group = QGroupBox("Dil Ayarları")
        lang_layout = QVBoxLayout()
        lang_label = QLabel("Varsayılan Dil:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Türkçe", "İngilizce", "Her İkisi"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        widget.addWidget(lang_group)
        
        # Auto start
        auto_group = QGroupBox("Başlangıç")
        auto_layout = QVBoxLayout()
        self.auto_listen_check = QCheckBox("Başlangıçta otomatik dinlemeyi başlat")
        auto_layout.addWidget(self.auto_listen_check)
        auto_group.setLayout(auto_layout)
        widget.addWidget(auto_group)
        
        widget.addStretch()
        
        container = QVBoxLayout()
        container.addLayout(widget)
        container_widget = QVBoxLayout()
        container_widget.addLayout(container)
        tab_widget = QVBoxLayout()
        tab_widget.addLayout(container_widget)
        
        from PyQt5.QtWidgets import QWidget
        tab = QWidget()
        tab.setLayout(tab_widget)
        return tab
    
    def create_tts_tab(self):
        """Create TTS settings tab"""
        widget = QVBoxLayout()
        
        # Provider selection
        provider_group = QGroupBox("TTS Sağlayıcı")
        provider_layout = QVBoxLayout()
        provider_label = QLabel("Ses Sağlayıcı:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["ElevenLabs (Yüksek Kalite)", "pyttsx3 (Yerel)"])
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_group.setLayout(provider_layout)
        widget.addWidget(provider_group)
        
        # ElevenLabs settings
        self.elevenlabs_group = QGroupBox("ElevenLabs Ayarları")
        elevenlabs_layout = QVBoxLayout()
        
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        elevenlabs_layout.addWidget(api_key_label)
        elevenlabs_layout.addWidget(self.api_key_input)
        
        voice_label = QLabel("Ses ID:")
        self.voice_id_input = QLineEdit()
        elevenlabs_layout.addWidget(voice_label)
        elevenlabs_layout.addWidget(self.voice_id_input)
        
        stability_label = QLabel("Kararlılık:")
        self.stability_slider = QSlider(Qt.Horizontal)
        self.stability_slider.setRange(0, 100)
        self.stability_value = QLabel("0.5")
        stability_layout = QHBoxLayout()
        stability_layout.addWidget(stability_label)
        stability_layout.addWidget(self.stability_slider)
        stability_layout.addWidget(self.stability_value)
        self.stability_slider.valueChanged.connect(
            lambda v: self.stability_value.setText(f"{v/100:.2f}")
        )
        elevenlabs_layout.addLayout(stability_layout)
        
        self.elevenlabs_group.setLayout(elevenlabs_layout)
        widget.addWidget(self.elevenlabs_group)
        
        # pyttsx3 settings
        self.pyttsx3_group = QGroupBox("pyttsx3 Ayarları")
        pyttsx3_layout = QVBoxLayout()
        
        rate_label = QLabel("Konuşma Hızı:")
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(50, 300)
        self.rate_value = QLabel("150")
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_slider)
        rate_layout.addWidget(self.rate_value)
        self.rate_slider.valueChanged.connect(
            lambda v: self.rate_value.setText(str(v))
        )
        pyttsx3_layout.addLayout(rate_layout)
        
        volume_label = QLabel("Ses Seviyesi:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_value = QLabel("90")
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_value.setText(str(v))
        )
        pyttsx3_layout.addLayout(volume_layout)
        
        self.pyttsx3_group.setLayout(pyttsx3_layout)
        widget.addWidget(self.pyttsx3_group)
        
        widget.addStretch()
        
        from PyQt5.QtWidgets import QWidget
        tab = QWidget()
        tab.setLayout(widget)
        return tab
    
    def create_llm_tab(self):
        """Create LLM settings tab"""
        widget = QVBoxLayout()
        
        # LLM enabled
        enabled_group = QGroupBox("LLM Ayarları")
        enabled_layout = QVBoxLayout()
        self.llm_enabled_check = QCheckBox("LLM kullan (Akıllı mod)")
        enabled_layout.addWidget(self.llm_enabled_check)
        enabled_group.setLayout(enabled_layout)
        widget.addWidget(enabled_group)
        
        # API settings
        api_group = QGroupBox("API Ayarları")
        api_layout = QVBoxLayout()
        
        url_label = QLabel("API URL:")
        self.api_url_input = QLineEdit()
        api_layout.addWidget(url_label)
        api_layout.addWidget(self.api_url_input)
        
        model_label = QLabel("Model:")
        self.model_input = QLineEdit()
        api_layout.addWidget(model_label)
        api_layout.addWidget(self.model_input)
        
        temp_label = QLabel("Temperature:")
        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(0, 200)
        self.temp_spin.setSuffix("%")
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_spin)
        api_layout.addLayout(temp_layout)
        
        max_tokens_label = QLabel("Max Tokens:")
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(50, 1000)
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(max_tokens_label)
        tokens_layout.addWidget(self.max_tokens_spin)
        api_layout.addLayout(tokens_layout)
        
        api_group.setLayout(api_layout)
        widget.addWidget(api_group)
        
        widget.addStretch()
        
        from PyQt5.QtWidgets import QWidget
        tab = QWidget()
        tab.setLayout(widget)
        return tab
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        widget = QVBoxLayout()
        
        # Theme
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu", "Sistem"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        widget.addWidget(theme_group)
        
        # Font
        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout()
        font_size_label = QLabel("Font Boyutu:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        font_layout.addWidget(font_size_label)
        font_layout.addWidget(self.font_size_spin)
        font_group.setLayout(font_layout)
        widget.addWidget(font_group)
        
        widget.addStretch()
        
        from PyQt5.QtWidgets import QWidget
        tab = QWidget()
        tab.setLayout(widget)
        return tab
    
    def on_provider_changed(self, index):
        """Handle provider change"""
        self.elevenlabs_group.setVisible(index == 0)
        self.pyttsx3_group.setVisible(index == 1)
    
    def load_settings(self):
        """Load settings from config"""
        # General
        self.name_input.setText(config.get('user.name', 'Kutay'))
        lang = config.get('language', 'tr')
        if lang == 'tr':
            self.lang_combo.setCurrentIndex(0)
        elif lang == 'en':
            self.lang_combo.setCurrentIndex(1)
        else:
            self.lang_combo.setCurrentIndex(2)
        
        # TTS
        provider = config.get('tts.provider', 'pyttsx3')
        self.provider_combo.setCurrentIndex(0 if provider == 'elevenlabs' else 1)
        self.on_provider_changed(self.provider_combo.currentIndex())
        
        # ElevenLabs
        self.api_key_input.setText(config.get('tts.elevenlabs.api_key', ''))
        self.voice_id_input.setText(config.get('tts.elevenlabs.voice_id', '21m00Tcm4TlvDq8ikWAM'))
        stability = int(config.get('tts.elevenlabs.stability', 0.5) * 100)
        self.stability_slider.setValue(stability)
        
        # pyttsx3
        self.rate_slider.setValue(config.get('tts.rate', 150))
        self.volume_slider.setValue(int(config.get('tts.volume', 0.9) * 100))
        
        # LLM
        self.llm_enabled_check.setChecked(config.get('llm.enabled', True))
        self.api_url_input.setText(config.get('llm.api_url', 'http://localhost:1234/v1/chat/completions'))
        self.model_input.setText(config.get('llm.model', 'qwen3-4b-2507'))
        self.temp_spin.setValue(int(config.get('llm.temperature', 0.7) * 100))
        self.max_tokens_spin.setValue(config.get('llm.max_tokens', 200))
    
    def save_settings(self):
        """Save settings to config"""
        try:
            # General
            config.set('user.name', self.name_input.text())
            lang_index = self.lang_combo.currentIndex()
            lang_map = {0: 'tr', 1: 'en', 2: 'both'}
            config.set('language', lang_map[lang_index])
            
            # TTS
            provider = 'elevenlabs' if self.provider_combo.currentIndex() == 0 else 'pyttsx3'
            config.set('tts.provider', provider)
            
            # ElevenLabs
            config.set('tts.elevenlabs.api_key', self.api_key_input.text())
            config.set('tts.elevenlabs.voice_id', self.voice_id_input.text())
            config.set('tts.elevenlabs.stability', self.stability_slider.value() / 100)
            
            # pyttsx3
            config.set('tts.rate', self.rate_slider.value())
            config.set('tts.volume', self.volume_slider.value() / 100)
            
            # LLM
            config.set('llm.enabled', self.llm_enabled_check.isChecked())
            config.set('llm.api_url', self.api_url_input.text())
            config.set('llm.model', self.model_input.text())
            config.set('llm.temperature', self.temp_spin.value() / 100)
            config.set('llm.max_tokens', self.max_tokens_spin.value())
            
            QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!")
            self.settings_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilirken hata oluştu: {str(e)}")

