import flet as ft
import threading
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from arduino_serial import ArduinoSerial
from ml_models.ml_algorithms.linear_regression import LinearRegressionModel
from ml_models.ml_algorithms.random_forest import RandomForestModel
from ml_models.ml_algorithms.bayes_theorem import BayesTheoremModel
from ml_models.ml_algorithms.mlp import MLPModel
from ml_models.model_manager import ModelManager

# Import UI panels
from ui_components.left_panel import LeftPanel
from ui_components.center_panel import CenterPanel
from ui_components.right_panel import RightPanel

# --- Configuration ---
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
USE_REAL_ARDUINO = True

class SmartHomeAIFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # Initialize data
        self.current_temp = 0.0
        self.current_humidity = 0.0
        self.has_sensor_error = False
        self.error_message = ""
        
        # Track last states to avoid duplicate logging
        self.last_prediction = None
        self.last_action = None
        
        # Initialize machine learning model manager
        self.model_manager = ModelManager()
        self.model_manager.set_callbacks(
            training_complete_callback=self.on_model_training_complete,
            training_progress_callback=self.on_model_training_progress
        )
        
        # Model prediction results
        self.ml_predictions = {
            'linear_regression': 'N/A',
            'random_forest': 'N/A', 
            'bayes_theorem': 'N/A',
            'mlp': 'N/A'
        }
        
        # Initialize UI panels
        self.left_panel = LeftPanel()
        self.center_panel = CenterPanel()
        self.right_panel = RightPanel()
        
        # Set references for cross-panel communication
        self.left_panel.set_main_app(self)
        self.center_panel.set_main_app(self)
        self.right_panel.set_main_app(self)
        
        # Arduino connection
        self.arduino = ArduinoSerial(SERIAL_PORT, BAUD_RATE)
        self.arduino.set_callbacks(
            data_callback=self.handle_arduino_data,
            error_callback=self.handle_arduino_error,
            status_callback=self.handle_arduino_status,
            feedback_callback=self.handle_user_feedback
        )
        
        self.setup_ui()
        
        # Add initial log message
        self.add_log_message("🚀 Starting SmartHome AI Control System...", "#4CAF50")
        
        # Initialize feedback display
        self.right_panel.update_feedback_display()
        
        # Start Arduino communication
        self.start_real_arduino()
        
        # Initialize default models
        self.model_manager.initialize_default_models()
    
    def setup_page(self):
        """Configure page properties"""
        self.page.title = "SmartHome AI Control System"
        self.page.theme_mode = "dark"
        self.page.window.icon = str(Path(__file__).parent / "assets" / "icon.png")
        
        # Set window properties
        self.page.window.width = 1440   
        self.page.window.height = 900
        self.page.window.min_width = 1440
        self.page.window.min_height = 900
        self.page.window.resizable = True
        self.page.window.maximizable = True
        
        # Update page
        self.page.update()
        
        # Disable scrolling
        self.page.scroll = ft.ScrollMode.HIDDEN
        self.page.auto_scroll = False
        self.page.padding = ft.padding.all(5)
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Title
        title = ft.Text(
            "🏠 SmartHome AI Control System",
            size=20,
            weight=ft.FontWeight.BOLD,
            color="#64B5F6"
        )
        
        # Create main layout
        main_layout = ft.Container(
            content=ft.Column([
                # Title row
                ft.Container(
                    content=title,
                    alignment=ft.alignment.center,
                    height=35,
                    margin=ft.margin.only(bottom=5)
                ),
                
                # Three-column layout
                ft.Row([
                    self.left_panel.create_panel(),
                    ft.VerticalDivider(width=1, color="#444444"),
                    self.center_panel.create_panel(),
                    ft.VerticalDivider(width=1, color="#444444"),
                    self.right_panel.create_panel()
                ], spacing=0, expand=True, alignment=ft.CrossAxisAlignment.START)
            ], expand=True),
            padding=ft.padding.all(8),
            expand=True
        )
        
        self.page.add(main_layout)
    
    def reconnect_arduino(self, e):
        """Reconnect Arduino"""
        threading.Thread(target=self._reconnect_arduino_thread, daemon=True).start()
    
    def disconnect_arduino(self, e):
        """Disconnect Arduino"""
        threading.Thread(target=self._disconnect_arduino_thread, daemon=True).start()
    
    def _disconnect_arduino_thread(self):
        """Thread function for Arduino disconnection"""
        self.add_log_message("🔌 Manually disconnecting from Arduino...", "#FF9800")
        self.arduino.disconnect()
        
        # Set error state similar to connection failure
        self.has_sensor_error = True
        self.error_message = "Arduino manually disconnected"
        
        # Reset sensor data and clear displays
        self.current_temp = 0.0
        self.current_humidity = 0.0
        
        # Update left panel with error state
        self.left_panel.update_sensor_data(
            self.current_temp, 
            self.current_humidity, 
            has_error=True, 
            error_msg="Arduino disconnected"
        )
        
        # Update UI to reflect disconnection
        self.left_panel.update_arduino_status("Manually Disconnected", "#888888")
        
        # Reset ML predictions to error state
        for model_name in self.ml_predictions:
            self.ml_predictions[model_name] = "-"
        
        # Update center panel with error state
        self.center_panel.update_ml_predictions(self.ml_predictions)
        self.center_panel.update_final_decision("STANDBY", "⏸️ System on standby (disconnected)")
        
        # Turn off all devices
        self.center_panel.fan_status = False
        self.center_panel.heater_status = False
        self.center_panel.update_device_animations()
        
        try:
            self.page.update()
        except Exception as ui_error:
            print(f"UI update error in disconnect thread (non-critical): {ui_error}")
    
    def _reconnect_arduino_thread(self):
        """Thread function for Arduino reconnection"""
        self.arduino.disconnect()
        time.sleep(1)
        if self.arduino.connect():
            self.arduino.start_communication()
        else:
            self.add_log_message("❌ ERROR: Failed to reconnect to Arduino", "#F44336")
            self.left_panel.update_arduino_status("Connection Failed", "#F44336")
            try:
                self.page.update()
            except Exception as ui_error:
                print(f"UI update error in reconnect thread (non-critical): {ui_error}")
    
    def celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return celsius * 9.0 / 5.0 + 32.0
    
    def handle_arduino_data(self, data: Dict[str, Any]):
        """Handle Arduino data"""
        # Convert temperature from Celsius to Fahrenheit
        temp_celsius = data['temperature']
        self.current_temp = self.celsius_to_fahrenheit(temp_celsius)
        self.current_humidity = data['humidity']
        
        # Validate sensor data
        has_error, error_msg = self.validate_sensor_data()
        
        # Update left panel
        self.left_panel.update_sensor_data(
            self.current_temp, 
            self.current_humidity, 
            has_error, 
            error_msg
        )
        
        # Only run ML predictions if no sensor error
        if not has_error:
            # Get predictions from all models
            self.update_ml_predictions()
            
            # Calculate final decision
            final_decision = self.calculate_final_decision()
            
            # Get system action
            current_action = self.get_system_status(final_decision)
            
            # Update center panel
            self.center_panel.update_ml_predictions(self.ml_predictions)
            self.center_panel.update_final_decision(final_decision, current_action)
            self.center_panel.update_device_status(final_decision)
            
            # Update tracking variables
            if final_decision != self.last_prediction and final_decision != "N/A":
                self.last_prediction = final_decision
            
            if current_action != self.last_action and current_action != "⏳ Waiting for data...":
                self.last_action = current_action
            
            # Send decision back to Arduino
            if final_decision != "N/A":
                self.arduino.send_prediction(final_decision)
        else:
            # Reset predictions to error state
            for model_name in self.ml_predictions:
                self.ml_predictions[model_name] = "-"
            
            # Update center panel with error state
            self.center_panel.update_ml_predictions(self.ml_predictions)
            self.center_panel.update_final_decision("STANDBY", "⏸️ System on standby (sensor error)")
            
            # Turn off all devices during error
            self.center_panel.fan_status = False
            self.center_panel.heater_status = False
            self.center_panel.update_device_animations()
        
        # Update page
        try:
            self.page.update()
        except Exception as ui_error:
            # UI update failed, likely due to threading issues during model switching
            # This is non-critical, the UI will be updated on the next successful cycle
            print(f"UI update error (non-critical): {ui_error}")
    
    def validate_sensor_data(self):
        """Validate sensor data and return error status"""
        # Temperature range for Fahrenheit: -58°F to 212°F (equivalent to -50°C to 100°C)
        if self.current_temp <=0 or self.current_humidity <= 0:
            error_msg = "Invalid sensor data"
            self.add_log_message(f"❌ ERROR: {error_msg} - Temp: {self.current_temp}°F, Humidity: {self.current_humidity}%", "#F44336")
            return True, error_msg
        elif self.current_temp > 212 or self.current_humidity > 100:
            error_msg = "Sensor data out of range"
            self.add_log_message(f"❌ ERROR: {error_msg} - Temp: {self.current_temp}°F, Humidity: {self.current_humidity}%", "#F44336")
            return True, error_msg
        else:
            # Clear error state if data is valid
            if self.has_sensor_error:
                self.has_sensor_error = False
                self.error_message = ""
                self.add_log_message("✅ Sensor data restored to normal", "#4CAF50")
            return False, ""
    
    def handle_arduino_error(self, error_msg: str):
        """Handle Arduino error"""
        self.add_log_message(f"❌ ERROR: {error_msg}", "#F44336")
        self.left_panel.update_arduino_status("Connection Error", "#F44336")
        
        # Set sensor error state
        self.has_sensor_error = True
        self.error_message = f"Arduino error: {error_msg}"
        
        # Reset predictions to error state
        for model_name in self.ml_predictions:
            self.ml_predictions[model_name] = "-"
        
        self.center_panel.update_ml_predictions(self.ml_predictions)
        try:
            self.page.update()
        except Exception as ui_error:
            print(f"UI update error in handle_arduino_error (non-critical): {ui_error}")
    
    def handle_arduino_status(self, status_msg: str):
        """Handle Arduino status"""
        self.add_log_message(f"ℹ️ INFO: {status_msg}", "#4CAF50")
        if "Connected" in status_msg:
            # Clear error state when successfully connected
            if self.has_sensor_error and "manually disconnected" in self.error_message:
                self.has_sensor_error = False
                self.error_message = ""
                self.add_log_message("✅ Connection restored, resuming normal operation", "#4CAF50")
            
            self.left_panel.update_arduino_status("Connected", "#4CAF50")
        elif "Disconnected" in status_msg:
            self.left_panel.update_arduino_status("Disconnected", "#F44336")
        try:
            self.page.update()
        except Exception as ui_error:
            print(f"UI update error in handle_arduino_status (non-critical): {ui_error}")
    
    def handle_user_feedback(self, temperature: float, humidity: float, feeling: str):
        """Handle user feedback from Arduino"""
        # Convert temperature from Celsius to Fahrenheit
        temp_fahrenheit = self.celsius_to_fahrenheit(temperature)
        self.right_panel.add_user_feedback(temp_fahrenheit, humidity, feeling)
    
    def update_ml_predictions(self):
        """Update predictions from all machine learning models"""
        if self.model_manager.is_model_ready():
            # Use model manager to get predictions
            self.ml_predictions = self.model_manager.predict(self.current_temp, self.current_humidity)
        else:
            # Models not ready yet
            for model_name in self.ml_predictions:
                self.ml_predictions[model_name] = "Training..."
    
    def calculate_final_decision(self) -> str:
        """Calculate final decision using our custom model"""
        # return self.model_manager.get_voting_decision(self.ml_predictions)
        return self.model_manager.get_our_model_prediction(self.current_temp, self.current_humidity)
    
    def get_system_status(self, decision: str) -> str:
        """Get system status based on decision"""
        if decision == "hot":
            return "🌀 Start cooling fan"
        elif decision == "cold":
            return "🔥 Start heating lamp"
        elif decision == "comfortable":
            return "😌 System idle"
        else:
            return "⏳ Waiting for data..."
    
    def start_real_arduino(self):
        """Start real Arduino communication"""
        def arduino_thread():
            if self.arduino.connect():
                self.arduino.start_communication()
            else:
                self.add_log_message("❌ ERROR: Unable to connect to Arduino", "#F44336")
                self.has_sensor_error = True
                self.error_message = "Arduino connection failed"
                self.left_panel.update_arduino_status("Connection Failed", "#F44336")
                try:
                    self.page.update()
                except Exception as ui_error:
                    print(f"UI update error in arduino thread (non-critical): {ui_error}")
        
        threading.Thread(target=arduino_thread, daemon=True).start()

    def add_log_message(self, message: str, color: str = "#E0E0E0"):
        """Add a message to the system log"""
        self.right_panel.add_log_message(message, color)

    def on_model_training_complete(self, person_type: str, models_count: int):
        """Called when model training is complete"""
        self.add_log_message(f"🧠 Model training complete for {person_type} ({models_count} models)", "#4CAF50")
        try:
            self.page.update()
        except Exception as ui_error:
            print(f"UI update error in training complete callback (non-critical): {ui_error}")
    
    def on_model_training_progress(self, progress_message: str):
        """Called during model training progress"""
        self.add_log_message(f"🔄 {progress_message}", "#FF9800")


def main(page: ft.Page):
    app = SmartHomeAIFlet(page)


if __name__ == "__main__":
    ft.app(target=main) 