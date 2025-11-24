# JARVIS Voice Automation

An intelligent desktop voice assistant that brings the power of natural language control to your computer. Built with modern Python technologies and AI integration, JARVIS understands your voice commands and executes complex tasks seamlessly across your system.

## 🌟 Overview

JARVIS Voice Automation reimagines how you interact with your computer. Instead of clicking through menus or typing commands, simply speak naturally and watch as your assistant understands context, handles complex requests, and manages your digital environment with precision.

## ✨ Key Features

### 🎤 Natural Voice Control
- Continuous listening mode that captures commands in real-time
- Multi-language support with Turkish and English recognition
- Contextual understanding powered by local LLM integration
- Intelligent error tolerance for natural speech patterns

### 🧠 Intelligent Command Processing
- **AI-Powered Comprehension**: Leverages local language models for nuanced command interpretation
- **Complex Task Orchestration**: Seamlessly handles multi-step instructions with dependency management
- **Automated Workflows**: Define and execute custom scenarios for repetitive tasks
- **Adaptive Learning**: Builds understanding of your preferences and usage patterns over time

### 🎯 System Control
- **Application Management**: Launch any installed application by name
- **Volume Control**: Precise system volume adjustment with multiple fallback methods
- **System Monitoring**: Real-time CPU, memory, disk, and battery status
- **Security Features**: Lock computer, sleep display, and more

### 📁 File Operations
- Quick access to common folders (Documents, Pictures, Downloads, etc.)
- File search across user directories
- File management (copy, move, rename)
- Recent files tracking

### 📅 Productivity Tools
- **Smart Notes**: Voice-activated note taking with persistent storage
- **Reminders & Timers**: Set reminders and timers with voice commands
- **Calendar Integration**: Add events to Google Calendar or Outlook
- **Email Management**: Send emails via Gmail API or SMTP

### 🎵 Media & Entertainment
- **Spotify Control**: Full Spotify integration for music playback
- **Screenshot Capture**: Instant screen capture with multiple fallback methods
- **Media Control**: Play, pause, skip tracks system-wide
- **Entertainment**: Jokes, coin flips, random numbers, and stories

### 🌐 Web & Information
- **Web Search**: Google, Wikipedia, YouTube searches
- **News**: Latest news headlines
- **Weather**: Real-time weather information
- **Calculator**: Voice-activated calculations

### 🏠 Smart Home Integration
- **Home Assistant**: Control smart home devices
- **Device Management**: Lights, thermostats, and more
- **Scenario Automation**: Execute home automation scenarios

### 🎨 Modern Interface
- Dark theme with sleek design
- Real-time waveform visualization
- Command history display
- Status indicators for all systems
- Settings panel for customization

### 🔊 Advanced Text-to-Speech
- **ElevenLabs Integration**: High-quality, natural-sounding voice (primary)
- **Fallback Support**: pyttsx3 as reliable backup
- **Multi-language**: Turkish and English voice support
- **Customizable**: Adjustable rate, volume, and voice selection

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Microphone access
- Internet connection (for speech recognition and APIs)
- LM Studio (optional, for local LLM support)

### Step 1: Clone the Repository
```bash
git clone https://github.com/code-alchemist01/jarvis_voice_automation.git
cd jarvis_voice_automation
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: PyAudio installation may require additional steps:

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

### Step 4: Configure the Application

1. Copy `config.json` and customize settings:
   - Add your ElevenLabs API key (optional, for premium TTS)
   - Configure OpenWeatherMap API key (for weather features)
   - Set up LLM connection (LM Studio URL)
   - Add application paths if needed

2. For Google Calendar/Gmail integration:
   - Place OAuth2 credentials in `tokens/credentials.json`
   - Follow Google Cloud Console setup instructions

3. For Spotify integration:
   - Add Spotify Client ID and Secret to `config.json`
   - Complete OAuth2 flow on first use

## 📖 Usage

### Starting JARVIS
```bash
python main.py
```

### Basic Commands

**System Control:**
- "Microsoft Edge'i aç" - Open Microsoft Edge
- "Sesi kapat" - Mute volume
- "Ses seviyesini artır" - Increase volume
- "Sistem bilgisi" - Get system information

**File Operations:**
- "Belgeler klasörünü aç" - Open Documents folder
- "Resimler klasörünü aç" - Open Pictures folder
- "Masaüstünü aç" - Open Desktop

**Productivity:**
- "Not kaydet: Toplantı yarın saat 3'te" - Save a note
- "Takvime ekle: Toplantı" - Add event to calendar
- "10 dakika sonra hatırlat: İlaç al" - Set reminder

**Media & Entertainment:**
- "Ekran görüntüsü al" - Take screenshot
- "Spotify'da [şarkı adı] çal" - Play song on Spotify
- "Müziği durdur" - Pause music

**Information:**
- "Bugün hava nasıl" - Get weather
- "Wikipedia'da Python ara" - Search Wikipedia
- "2 artı 2 kaç eder" - Calculate

**Multi-Step Tasks:**
- "Önce Notepad'i aç, sonra Calculator'ı aç" - Execute multiple commands
- "Ses seviyesini artır ve ekran görüntüsü al" - Chain commands

**Scenarios:**
- "Çalışma modunu aç" - Run predefined work scenario
- "Uyku modunu aç" - Run sleep scenario

## ⚙️ Configuration

### Main Configuration (`config.json`)

```json
{
  "language": "tr",
  "tts": {
    "provider": "elevenlabs",
    "rate": 150,
    "volume": 0.9,
    "elevenlabs": {
      "api_key": "your_key_here",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "model_id": "eleven_multilingual_v2"
    }
  },
  "llm": {
    "enabled": true,
    "api_url": "http://localhost:1234/v1/chat/completions",
    "model": "qwen3-4b-2507",
    "temperature": 0.7
  },
  "user": {
    "name": "Your Name"
  }
}
```

### LLM Setup (LM Studio)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a compatible model (e.g., qwen3-4b-2507)
3. Start the local server on port 1234
4. JARVIS will automatically connect

### API Keys

**ElevenLabs (Optional):**
- Sign up at [ElevenLabs](https://elevenlabs.io/)
- Get your API key from the dashboard
- Add to `config.json` under `tts.elevenlabs.api_key`

**OpenWeatherMap (Optional):**
- Sign up at [OpenWeatherMap](https://openweathermap.org/api)
- Get your free API key
- Add to `config.json` under `weather.api_key`

**Google APIs (Optional):**
- Create a project in [Google Cloud Console](https://console.cloud.google.com/)
- Enable Calendar API and Gmail API
- Download OAuth2 credentials
- Place in `tokens/credentials.json`

**Spotify (Optional):**
- Create an app in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Get Client ID and Secret
- Add to `config.json` under `spotify`

## 🏗️ Architecture

### Project Structure
```
jarvis_voice_automation/
├── core/                    # Core functionality
│   ├── command_processor.py    # Command routing and execution
│   ├── llm_client.py           # LLM integration (LM Studio)
│   ├── voice_recognition.py    # Speech-to-text
│   ├── text_to_speech.py       # Text-to-speech engine
│   ├── multi_step_processor.py # Multi-step task handling
│   └── prompts.py              # AI prompts and personality
├── features/                 # Feature modules
│   ├── system_control.py       # System operations
│   ├── file_operations.py      # File management
│   ├── calendar.py             # Calendar integration
│   ├── email.py                # Email management
│   ├── spotify_control.py      # Spotify integration
│   ├── smart_home.py           # Smart home control
│   └── ...                     # Additional features
├── gui/                      # User interface
│   ├── main_window.py          # Main application window
│   ├── settings_window.py      # Settings panel
│   └── notification_system.py  # System notifications
├── utils/                    # Utilities
│   ├── config.py              # Configuration management
│   └── oauth2_helper.py        # OAuth2 authentication
├── main.py                   # Application entry point
├── config.json               # User configuration
└── requirements.txt           # Python dependencies
```

### Technology Stack

- **GUI Framework**: PyQt5
- **Speech Recognition**: SpeechRecognition library (Google Speech API)
- **Text-to-Speech**: ElevenLabs API (primary), pyttsx3 (fallback)
- **AI/LLM**: LM Studio (OpenAI-compatible API)
- **System Control**: pycaw (Windows audio), psutil (system monitoring)
- **Media**: pyautogui, Pillow (screenshots)
- **APIs**: Google Calendar, Gmail, Spotify, OpenWeatherMap

## 🎯 Advanced Features

### Multi-Step Task Processing
JARVIS can understand and execute complex multi-step commands:
- "Önce Notepad'i aç, sonra Calculator'ı aç, sonra ses seviyesini artır"
- Tasks are automatically parsed, ordered, and executed sequentially

### Scenario Management
Create reusable task sequences:
- Work mode: Opens productivity apps, adjusts settings
- Sleep mode: Pauses media, dims lights, adjusts volume
- Custom scenarios: Define your own task combinations

### Command Learning
JARVIS learns from your usage:
- Tracks command frequency
- Suggests frequently used commands
- Adapts to your preferences over time

### Smart Home Integration
Control your smart home ecosystem:
- Home Assistant integration
- Device state monitoring
- Automated scenarios
- Voice-controlled lighting and climate

## 🔧 Troubleshooting

### Speech Recognition Not Working
- Check microphone permissions
- Ensure internet connection (for Google Speech API)
- Try adjusting microphone sensitivity in system settings

### LLM Not Responding
- Verify LM Studio is running
- Check API URL in config (default: `http://localhost:1234`)
- Ensure model is loaded in LM Studio
- JARVIS will fall back to regex patterns if LLM unavailable

### Volume Control Issues
- Install `pycaw` for Windows: `pip install pycaw`
- Check Windows audio service is running
- Try alternative methods (PowerShell, pyautogui)

### Application Not Opening
- Add application path to `config.json` under `applications`
- Check application name spelling
- Verify application is installed

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 🙏 Acknowledgments

- Inspired by Iron Man's JARVIS
- Built with PyQt5, SpeechRecognition, and modern AI technologies
- Thanks to all open-source contributors

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ for voice automation enthusiasts**

