# SmartHome AI Control System

A smart home control system that uses machine learning to predict user comfort preferences and automatically control environmental devices based on temperature and humidity readings.

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (to clone the repository)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd SmartHome
   ```

2. **Create a virtual environment**

   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app/main.py
   ```

## Features

- **Real-time sensor monitoring** - Temperature and humidity readings from Arduino
- **Machine learning predictions** - 4 different ML algorithms predict user comfort
- **Automatic device control** - Smart fan and heater control based on predictions
- **User feedback system** - Collect and learn from user comfort preferences
- **Modern UI** - Clean, responsive interface built with Flet

## Hardware Requirements

- Arduino board (tested with Arduino Uno)
- DHT22 temperature/humidity sensor
- USB connection to computer
- Optional: Fan and heater control relays

## Usage

1. Connect your Arduino with DHT22 sensor to your computer
2. Update the COM port in `app/main.py` (default: COM5)
3. Run the application
4. The system will automatically:
   - Read sensor data
   - Make ML predictions
   - Control connected devices
   - Learn from your feedback

## Project Structure

```
SmartHome/
├── app/                    # Main application
│   ├── main.py            # Application entry point
│   ├── arduino_serial.py  # Arduino communication
│   └── ui_components/     # UI panels
├── ml_models/             # Machine learning models
├── ml_data/               # Training data and datasets
└── requirements.txt       # Python dependencies
```

## Troubleshooting

- **Arduino connection issues**: Check COM port in `app/main.py`
- **Python dependency issues**: Ensure you're using the virtual environment
- **Permission errors**: Run terminal/command prompt as administrator (Windows)
