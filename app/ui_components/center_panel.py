import flet as ft
import threading
import time

class CenterPanel:
    def __init__(self):
        # Pretrained model selection
        self.selected_pretrained_model = "Normal Person"
        self.pretrained_model_dropdown = None
        self.pretrained_model_status_text = ft.Text(f"Current selection: Normal Person", size=16, color="#888888")
        
        # Person description display
        self.person_description_text = ft.Text(
            self.get_person_description("Normal Person"), 
            size=14, 
            color="#CCCCCC",
            text_align=ft.TextAlign.CENTER
        )
        
        # Person profile title with name and emoji
        self.person_profile_title = ft.Text(
            f"👤 Person Profile: {self.selected_pretrained_model} {self.get_person_emoji(self.selected_pretrained_model)}", 
            size=14, 
            weight=ft.FontWeight.BOLD, 
            color="#64B5F6"
        )
        
        # ML prediction UI elements
        self.lr_prediction_text = ft.Text("N/A", size=16, weight=ft.FontWeight.BOLD)
        self.rf_prediction_text = ft.Text("N/A", size=16, weight=ft.FontWeight.BOLD)
        self.bayes_prediction_text = ft.Text("N/A", size=16, weight=ft.FontWeight.BOLD)
        self.mlp_prediction_text = ft.Text("N/A", size=16, weight=ft.FontWeight.BOLD)
        
        self.final_decision_text = ft.Text("N/A", size=24, weight=ft.FontWeight.BOLD)
        self.action_text = ft.Text("Initializing...", size=16)
        
        # Device status tracking
        self.fan_status = False
        self.heater_status = False
        self.fan_animation_running = False
        self.heater_animation_running = False
        
        # Device status UI elements
        self.fan_icon = ft.Text("🌀", size=32)
        self.fan_status_text = ft.Text("OFF", size=16, weight=ft.FontWeight.BOLD, color="#888888")
        self.heater_icon = ft.Text("🔥", size=32)
        self.heater_status_text = ft.Text("OFF", size=16, weight=ft.FontWeight.BOLD, color="#888888")
        
        # Animation containers
        self.fan_container = ft.Container(
            content=self.fan_icon,
            width=50,
            height=50,
            alignment=ft.alignment.center
        )
        self.heater_container = ft.Container(
            content=self.heater_icon,
            width=50,
            height=50,
            alignment=ft.alignment.center
        )
        
        # Device cards containers
        self.fan_card = None
        self.heater_card = None
        self.fan_card_container = None
        self.heater_card_container = None
        
        # Store reference to main app for callbacks
        self.main_app = None
    
    def set_main_app(self, main_app):
        """Set reference to main application for callbacks"""
        self.main_app = main_app
    
    def create_panel(self) -> ft.Container:
        """Create and return the center panel container"""
        return ft.Container(
            content=ft.Column([
                # Pretrained Model Select section
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("🎛️ Pretrained Model Select", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=8)
                        ),
                        
                        # Two cards side by side
                        ft.Row([
                            # Model selection card
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        self.pretrained_model_status_text,
                                        self.create_pretrained_model_dropdown(),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=15,
                                    height=120
                                ),
                                elevation=3,
                                expand=1
                            ),
                            
                            # Person description card
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        self.person_profile_title,
                                        self.person_description_text,
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                       alignment=ft.MainAxisAlignment.CENTER),
                                    padding=15,
                                    height=120
                                ),
                                elevation=3,
                                expand=1
                            )
                        ], spacing=12)
                    ], spacing=0),
                    margin=ft.margin.only(bottom=4)
                ),
                
                # Divider
                ft.Container(
                    content=ft.Divider(height=1, color="#444444"),
                    margin=ft.margin.symmetric(vertical=8)
                ),
                
                # ML Predictions section
                ft.Container(
                    content=ft.Text("🧠 Machine Learning Predictions", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=8)
                ),
                
                # ML predictions grid
                ft.Container(
                    content=ft.Column([
                        # First row
                        ft.Row([
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("📈 Linear Regression", size=12, color="#FF6B6B"),
                                        self.lr_prediction_text
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=10,
                                    height=70
                                ),
                                elevation=2,
                                expand=1
                            ),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("🌳 Random Forest", size=12, color="#4CAF50"),
                                        self.rf_prediction_text
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=10,
                                    height=70
                                ),
                                elevation=2,
                                expand=1
                            ),
                        ], spacing=12, expand=True),
                        
                        # Second row
                        ft.Row([
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("🎲 Bayes' Theorem", size=12, color="#2196F3"),
                                        self.bayes_prediction_text
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=10,
                                    height=70
                                ),
                                elevation=2,
                                expand=1
                            ),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("🤖 MLP Neural Net", size=12, color="#FF8C00"),
                                        self.mlp_prediction_text
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=10,
                                    height=70
                                ),
                                elevation=2,
                                expand=1
                            )
                        ], spacing=12, expand=True)
                    ], spacing=12),
                    height=160
                ),
                
                # Divider
                ft.Container(
                    content=ft.Divider(height=1, color="#444444"),
                    margin=ft.margin.symmetric(vertical=8)
                ),
                
                # Final Decision and System Status
                ft.Row([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🎯 Our Model Decision", size=14, color="#FFD700"),
                                self.final_decision_text
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                               alignment=ft.MainAxisAlignment.START),
                            padding=15,
                            height=100
                        ),
                        elevation=4,
                        expand=1
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("⚙️ System Status", size=14, color="#4CAF50"),
                                self.action_text,
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                               alignment=ft.MainAxisAlignment.START),
                            padding=15,
                            height=100
                        ),
                        elevation=4,
                        expand=1
                    )
                ], spacing=12),
                
                # Device Status Cards
                ft.Row([
                    self.create_and_store_fan_card(),
                    self.create_and_store_heater_card()
                ], spacing=12)
            ], spacing=12, alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.all(8),
            expand=2,
            alignment=ft.alignment.top_center
        )
    
    def create_pretrained_model_dropdown(self):
        """Create dropdown for model selection"""
        self.pretrained_model_dropdown = ft.Dropdown(
            width=300,
            options=[
                ft.dropdown.Option("Normal Person"),
                ft.dropdown.Option("Hot Person"),
                ft.dropdown.Option("Cold Person"),
            ],
            value="Normal Person",
            on_change=self.handle_pretrained_model_change,
            bgcolor="#37474F",
            color="#FFFFFF",
            border_color="#64B5F6"
        )
        return self.pretrained_model_dropdown
    
    def handle_pretrained_model_change(self, e):
        """Handle model selection change"""
        self.selected_pretrained_model = e.control.value
        self.pretrained_model_status_text.value = f"Current selection: {self.selected_pretrained_model}"
        
        # Update person description
        self.person_description_text.value = self.get_person_description(self.selected_pretrained_model)
        
        # Update person profile title
        self.person_profile_title.value = f"👤 Person Profile: {self.selected_pretrained_model} {self.get_person_emoji(self.selected_pretrained_model)}"
        
        if self.main_app:
            # Switch model type in the model manager
            self.main_app.model_manager.switch_person_type(self.selected_pretrained_model)
            self.main_app.add_log_message(f"🎛️ Pretrained model switched to: {self.selected_pretrained_model}", "#4CAF50")
            self.main_app.page.update()
    
    def create_and_store_fan_card(self):
        """Create fan status card"""
        self.fan_card_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("💨 Cooling Fan", size=14, color="#2196F3"),
                    self.fan_status_text,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.fan_container,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.START),
            padding=15,
            height=100,
            bgcolor=None,
            border_radius=10
        )
        
        self.fan_card = ft.Card(
            content=self.fan_card_container,
            elevation=3,
            expand=1
        )
        return self.fan_card
    
    def create_and_store_heater_card(self):
        """Create heater status card"""
        self.heater_card_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("🔆 Heating System", size=14, color="#FF6B35"),
                    self.heater_status_text,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.heater_container,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.START),
            padding=15,
            height=100,
            bgcolor=None,
            border_radius=10
        )
        
        self.heater_card = ft.Card(
            content=self.heater_card_container,
            elevation=3,
            expand=1
        )
        return self.heater_card
    
    def update_ml_predictions(self, predictions: dict):
        """Update ML prediction displays"""
        self.lr_prediction_text.value = predictions.get('linear_regression', 'N/A').upper()
        self.lr_prediction_text.color = self.get_comfort_color(predictions.get('linear_regression', 'N/A'))
        
        self.rf_prediction_text.value = predictions.get('random_forest', 'N/A').upper()
        self.rf_prediction_text.color = self.get_comfort_color(predictions.get('random_forest', 'N/A'))
        
        self.bayes_prediction_text.value = predictions.get('bayes_theorem', 'N/A').upper()
        self.bayes_prediction_text.color = self.get_comfort_color(predictions.get('bayes_theorem', 'N/A'))
        
        self.mlp_prediction_text.value = predictions.get('mlp', 'N/A').upper()
        self.mlp_prediction_text.color = self.get_comfort_color(predictions.get('mlp', 'N/A'))
    
    def update_final_decision(self, decision: str, status: str):
        """Update final decision and system status"""
        self.final_decision_text.value = decision.upper()
        self.final_decision_text.color = self.get_comfort_color(decision)
        self.action_text.value = status
    
    def update_device_status(self, final_decision: str):
        """Update device status based on decision"""
        if final_decision == "hot":
            self.fan_status = True
            self.heater_status = False
        elif final_decision == "cold":
            self.fan_status = False
            self.heater_status = True
        elif final_decision == "comfortable":
            self.fan_status = False
            self.heater_status = False
        
        self.update_device_animations()
    
    def update_device_animations(self):
        """Update device animations and colors"""
        # Update fan
        if self.fan_status:
            self.fan_status_text.value = "ON"
            self.fan_status_text.color = "#FFFFFF"
            if self.fan_card_container:
                self.fan_card_container.bgcolor = "#1565C0"
            if not self.fan_animation_running:
                self.fan_animation_running = True
                self.start_fan_rotation()
        else:
            self.fan_status_text.value = "OFF"
            self.fan_status_text.color = "#888888"
            if self.fan_card_container:
                self.fan_card_container.bgcolor = None
            self.fan_animation_running = False
            self.fan_icon.value = "🌀"
        
        # Update heater
        if self.heater_status:
            self.heater_status_text.value = "ON"
            self.heater_status_text.color = "#FFFFFF"
            if self.heater_card_container:
                self.heater_card_container.bgcolor = "#FFB74D"
            if not self.heater_animation_running:
                self.heater_animation_running = True
                self.start_heater_pulse()
        else:
            self.heater_status_text.value = "OFF"
            self.heater_status_text.color = "#888888"
            if self.heater_card_container:
                self.heater_card_container.bgcolor = None
            self.heater_animation_running = False
            self.heater_icon.value = "🔥"
    
    def start_fan_rotation(self):
        """Start fan animation"""
        fan_frames = ["🌀", "💨", "🌪️", "💨"]
        frame_index = [0]
        
        def rotate_fan():
            if self.fan_animation_running and self.fan_status:
                self.fan_icon.value = fan_frames[frame_index[0]]
                frame_index[0] = (frame_index[0] + 1) % len(fan_frames)
                if self.main_app:
                    self.main_app.page.update()
                threading.Timer(0.3, rotate_fan).start()
            else:
                self.fan_animation_running = False
        
        rotate_fan()
    
    def start_heater_pulse(self):
        """Start heater animation"""
        heat_frames = ["🔥", "🔆", "🌡️", "🔆"]
        frame_index = [0]
        
        def pulse_heater():
            if self.heater_animation_running and self.heater_status:
                self.heater_icon.value = heat_frames[frame_index[0]]
                frame_index[0] = (frame_index[0] + 1) % len(heat_frames)
                if self.main_app:
                    self.main_app.page.update()
                threading.Timer(0.6, pulse_heater).start()
            else:
                self.heater_animation_running = False
        
        pulse_heater()
    
    def get_comfort_color(self, prediction: str) -> str:
        """Get color based on prediction"""
        if prediction == "hot":
            return "#F44336"
        elif prediction == "cold":
            return "#2196F3"
        elif prediction == "comfortable":
            return "#4CAF50"
        elif prediction == "-":
            return "#757575"
        else:
            return "#888888"
    
    def get_person_description(self, person_type: str) -> str:
        """Get description for different person types"""
        descriptions = {
            "Normal Person": "Moderate temperature sensitivity.\nBalanced comfort preferences for\nmost environmental conditions.",
            "Hot Person": "High sensitivity to heat.\nPrefers cooler environments and\nfeels hot at lower temperatures.",
            "Cold Person": "High sensitivity to cold.\nPrefers warmer environments and\nfeels cold at higher temperatures."
        }
        return descriptions.get(person_type, "Unknown person type")

    def get_person_emoji(self, person_type: str) -> str:
        """Get emoji based on person type"""
        emojis = {
            "Normal Person": "🌡️",
            "Hot Person": "🔥",
            "Cold Person": "🧊"
        }
        return emojis.get(person_type, "❓") 