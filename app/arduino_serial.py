"""
Arduino Serial Communication Module
Handles real-time data exchange with Arduino
"""

import serial
import threading
import time
from typing import Callable, Optional, Dict, Any
from datetime import datetime

class ArduinoSerial:
    """Arduino serial communication class"""
    
    def __init__(self, port: str = 'COM3', baud_rate: int = 9600, timeout: int = 1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_running = False
        
        # Callback functions
        self.data_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.feedback_callback: Optional[Callable] = None
        
        # Data cache
        self.last_data = {
            'temperature': 0.0,
            'humidity': 0.0
        }
        
        # Track last sent prediction to avoid duplicate logging
        self.last_sent_prediction = None
        
        # Track last received status/action to avoid duplicate logging
        self.last_received_status = None
        self.last_received_action = None
        
        # Statistics
        self.packets_received = 0
        self.packets_sent = 0
        self.connection_time = None
        
        # Threading
        self.serial_thread: Optional[threading.Thread] = None
    
    def set_callbacks(self, 
                     data_callback: Callable = None,
                     error_callback: Callable = None, 
                     status_callback: Callable = None,
                     feedback_callback: Callable = None):
        """Set callback functions"""
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.status_callback = status_callback
        self.feedback_callback = feedback_callback
    
    def connect(self) -> bool:
        """Connect to Arduino"""
        try:
            self.serial_connection = serial.Serial(
                self.port, 
                self.baud_rate, 
                timeout=self.timeout
            )
            
            # Wait for Arduino reset
            time.sleep(2)
            
            self.is_connected = True
            self.connection_time = datetime.now()
            
            if self.status_callback:
                self.status_callback(f"Connected to Arduino: {self.port}")
            
            return True
            
        except serial.SerialException as e:
            self.is_connected = False
            if self.error_callback:
                self.error_callback(f"Connection failed: {e}")
            return False
        except Exception as e:
            self.is_connected = False
            if self.error_callback:
                self.error_callback(f"Unknown error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect Arduino connection"""
        self.is_running = False
        
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=2)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            
        self.is_connected = False
        
        if self.status_callback:
            self.status_callback("Arduino connection disconnected")
    
    def start_communication(self):
        """Start serial communication thread"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        self.is_running = True
        self.serial_thread = threading.Thread(target=self._communication_loop, daemon=True)
        self.serial_thread.start()
        
        if self.status_callback:
            self.status_callback("Starting real-time data reception")
        
        return True
    
    def _communication_loop(self):
        """Serial communication main loop"""
        while self.is_running and self.is_connected:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Read Arduino data
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        self._process_arduino_data(line)
                        
                time.sleep(0.05)  # 50ms interval
                
            except serial.SerialException as e:
                if self.error_callback:
                    self.error_callback(f"Serial communication error: {e}")
                self.is_connected = False
                break
            except Exception as e:
                if self.error_callback:
                    self.error_callback(f"Data processing error: {e}")
    
    def _process_arduino_data(self, data_line: str):
        """Process data received from Arduino"""
        try:
            # Expected data format: "T:25.6,H:45.2" (removed target temperature)
            if data_line.startswith("T:") and ",H:" in data_line:
                parts = data_line.split(',')
                
                # Parse temperature
                temp_str = parts[0].split(':')[1]
                temperature = float(temp_str)
                
                # Parse humidity
                hum_str = parts[1].split(':')[1]
                humidity = float(hum_str)
                
                # Update cache (no target temperature needed)
                self.last_data = {
                    'temperature': temperature,
                    'humidity': humidity,
                    'timestamp': datetime.now()
                }
                
                self.packets_received += 1
                
                # Call data callback
                if self.data_callback:
                    self.data_callback(self.last_data)
            
            elif data_line.startswith("USER_FEEDBACK:"):
                # Handle user feedback data: "USER_FEEDBACK:25.6,45.2,hot"
                feedback_data = data_line.replace("USER_FEEDBACK:", "")
                parts = feedback_data.split(',')
                
                if len(parts) == 3:
                    temperature = float(parts[0])
                    humidity = float(parts[1])
                    feeling = parts[2].strip()
                    
                    # Call feedback callback if available
                    if hasattr(self, 'feedback_callback') and self.feedback_callback:
                        self.feedback_callback(temperature, humidity, feeling)
                        
            elif data_line.startswith("Status:") or data_line.startswith("Action:"):
                # Process status information - only log if changed
                if data_line.startswith("Status:"):
                    if data_line != self.last_received_status:
                        if self.status_callback:
                            self.status_callback(data_line)
                        self.last_received_status = data_line
                elif data_line.startswith("Action:"):
                    if data_line != self.last_received_action:
                        if self.status_callback:
                            self.status_callback(data_line)
                        self.last_received_action = data_line
                    
            else:
                # Other information - filter out redundant messages
                if "Received command from Python" not in data_line:
                    if self.status_callback:
                        self.status_callback(f"Arduino: {data_line}")
                    
        except (ValueError, IndexError) as e:
            if self.error_callback:
                self.error_callback(f"Data parsing error: {e}, Raw data: {data_line}")
    
    def send_prediction(self, prediction: str) -> bool:
        """Send prediction result to Arduino"""
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            # Send prediction result
            message = f"{prediction}\n"
            self.serial_connection.write(message.encode('utf-8'))
            self.serial_connection.flush()
            
            self.packets_sent += 1
            
            # Only log if prediction changed
            if prediction != self.last_sent_prediction:
                if self.status_callback:
                    self.status_callback(f"Sent prediction: {prediction}")
                self.last_sent_prediction = prediction
            
            return True
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Failed to send prediction: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection status information"""
        return {
            "is_connected": self.is_connected,
            "port": self.port,
            "baud_rate": self.baud_rate,
            "packets_received": self.packets_received,
            "packets_sent": self.packets_sent,
            "connection_time": self.connection_time,
            "last_data": self.last_data.copy() if self.last_data else None
        }
    
    def test_connection(self) -> bool:
        """Test Arduino connection"""
        try:
            test_serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            test_serial.close()
            return True
        except serial.SerialException:
            return False
    
    @staticmethod
    def list_available_ports() -> list:
        """List available serial ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] 