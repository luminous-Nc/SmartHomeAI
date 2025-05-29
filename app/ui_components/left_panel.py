import flet as ft

class LeftPanel:
    def __init__(self):
        # Initialize sensor data
        self.current_temp = 0.0
        self.current_humidity = 0.0
        self.has_sensor_error = False
        self.error_message = ""
        
        # Connection state tracking
        self.is_connected = False
        
        # UI elements
        self.temp_text = ft.Text("--°F", size=28, weight=ft.FontWeight.BOLD, color="#FF6B6B")
        self.humidity_text = ft.Text("--%", size=28, weight=ft.FontWeight.BOLD, color="#4ECDC4")
        self.arduino_status_text = ft.Text("Not Connected", size=14, color="#FF9800")
        
        self.temp_progress = ft.ProgressBar(width=160, color="#FF6B6B")
        self.humidity_progress = ft.ProgressBar(width=160, color="#4ECDC4")
        
        # Connection button - will be updated dynamically
        self.connection_button = ft.ElevatedButton(
            "🔄 Reconnect", 
            on_click=self.handle_connection_button, 
            height=30
        )
        
        # Store reference to main app for callbacks
        self.main_app = None
    
    def set_main_app(self, main_app):
        """Set reference to main application for callbacks"""
        self.main_app = main_app
    
    def create_panel(self) -> ft.Container:
        """Create and return the left panel container"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("📊 Current Status", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=8)
                ),
                
                # Temperature card
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🌡️ Temperature", size=14, color="#FF6B6B"),
                            self.temp_text,
                            self.temp_progress
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=12,
                        expand=True,
                        alignment=ft.alignment.top_center
                    ),
                    elevation=3
                ),
                
                # Humidity card
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("💧 Humidity", size=14, color="#4ECDC4"),
                            self.humidity_text,
                            self.humidity_progress
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=12,
                        expand=True,
                        alignment=ft.alignment.top_center
                    ),
                    elevation=3
                ),
                
                # Arduino status card
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("📡 Arduino Status", size=14, color="#FF9800"),
                            self.arduino_status_text,
                            self.connection_button
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=12,
                        expand=True,
                        alignment=ft.alignment.top_center
                    ),
                    elevation=3
                )
            ], spacing=40, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(8),
            expand=1,
            alignment=ft.alignment.top_center
        )
    
    def update_sensor_data(self, temperature: float, humidity: float, has_error: bool = False, error_msg: str = ""):
        """Update sensor data and UI"""
        self.current_temp = temperature
        self.current_humidity = humidity
        self.has_sensor_error = has_error
        self.error_message = error_msg
        
        # Update UI elements
        if self.has_sensor_error:
            self.temp_text.value = "ERROR"
            self.temp_text.color = "#F44336"
            self.humidity_text.value = "ERROR"
            self.humidity_text.color = "#F44336"
            self.temp_progress.value = 0
            self.humidity_progress.value = 0
        else:
            self.temp_text.value = f"{self.current_temp:.1f}°F"
            self.temp_text.color = "#FF6B6B"
            self.humidity_text.value = f"{self.current_humidity:.1f}%"
            self.humidity_text.color = "#4ECDC4"
            # Temperature progress bar: 32°F to 104°F range (0°C to 40°C equivalent)
            self.temp_progress.value = min(max((self.current_temp - 32.0) / 72.0, 0.0), 1.0)
            self.humidity_progress.value = self.current_humidity / 100.0
    
    def update_arduino_status(self, status: str, color: str):
        """Update Arduino connection status"""
        self.arduino_status_text.value = status
        self.arduino_status_text.color = color
        
        # Update connection state and button
        if "Connected" in status:
            self.is_connected = True
            self.connection_button.text = "🔌 Disconnect"
            self.connection_button.color = "#F44336"  # Red color for disconnect
        else:
            self.is_connected = False
            self.connection_button.text = "🔄 Reconnect"
            self.connection_button.color = None  # Default color for reconnect
    
    def handle_connection_button(self, e):
        """Handle connection button click"""
        if self.main_app:
            if self.is_connected:
                self.main_app.disconnect_arduino(e)
            else:
                self.main_app.reconnect_arduino(e) 