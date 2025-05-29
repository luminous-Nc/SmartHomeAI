import flet as ft
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

class RightPanel:
    def __init__(self):
        # User feedback data storage
        self.user_feedback_data = []
        self.max_feedback_entries = 50
        
        # CSV file path settings
        # Calculate project root directory path
        if hasattr(sys, '_getframe'):
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent  # Go back to root directory from app/ui_components/
        else:
            # Fallback solution
            project_root = Path.cwd()
        
        self.csv_file_path = project_root / "ml_data" / "user_custom.csv"
        
        # Ensure ml_data directory exists
        self.csv_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load historical user feedback data
        self.load_user_feedback_from_csv()
        
        # System log data
        self.log_messages = ["Starting SmartHome AI Control System..."]
        
        # UI components
        self.log_list = ft.ListView(
            expand=True,
            spacing=2,
            padding=ft.padding.all(5),
            auto_scroll=True
        )
        
        self.feedback_list = ft.ListView(
            expand=True,
            spacing=2,
            padding=ft.padding.all(5),
            auto_scroll=True
        )
        
        # Store reference to main app for callbacks
        self.main_app = None
        
        # Initialize UI display (needs to be called again after set_main_app for correct updates)
        self.initial_ui_setup_needed = True
    
    def set_main_app(self, main_app):
        """Set reference to main application for callbacks"""
        self.main_app = main_app
        
        # If there's historical data and this is the initial setup, update UI display
        if self.initial_ui_setup_needed and self.user_feedback_data:
            self.update_feedback_display()
            self.initial_ui_setup_needed = False
    
    def create_panel(self) -> ft.Container:
        """Create and return the right panel container"""
        return ft.Container(
            content=ft.Column([
                # User Feedback Data section
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("👤 User Feedback Data", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=5),
                            height=25
                        ),
                        ft.Container(
                            content=self.feedback_list,
                            bgcolor="#2E3440",
                            border_radius=5,
                            padding=ft.padding.all(8),
                            height=240
                        )
                    ], spacing=0),
                    height=270,
                    expand=False
                ),
                
                # Divider
                ft.Container(
                    content=ft.Divider(height=1, color="#444444"),
                    margin=ft.margin.symmetric(vertical=3),
                    height=10
                ),
                
                # System Log section
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("📝 System Log", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=5),
                            height=25
                        ),
                        ft.Container(
                            content=self.log_list,
                            bgcolor="#2E3440",
                            border_radius=5,
                            padding=ft.padding.all(8),
                            height=300  # Fixed height for internal scrolling
                        )
                    ], spacing=0),
                    height=335,  # Fixed total height (25 + 300 + spacing)
                    expand=False  # Don't expand dynamically
                )
            ], spacing=0),
            bgcolor="#1E1E1E",
            padding=ft.padding.all(10),
            border_radius=8,
            expand=True
        )
    
    def add_log_message(self, message: str, color: str = "#E0E0E0"):
        """Add a message to the system log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = ft.Container(
            content=ft.Text(f"[{timestamp}] {message}", size=12, color=color),
            padding=ft.padding.all(3),
            border_radius=3,
            margin=ft.margin.only(bottom=1)
        )
        
        self.log_list.controls.append(log_entry)
        
        # Keep only the last 100 log entries
        if len(self.log_list.controls) > 100:
            self.log_list.controls.pop(0)
        
        if self.main_app and hasattr(self.main_app, 'page'):
            self.main_app.page.update()
    
    def add_user_feedback(self, temperature: float, humidity: float, feeling: str):
        """Add user feedback data entry"""
        # Use complete timestamp (including date)
        full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create feedback entry
        feedback_entry = {
            'timestamp': full_timestamp,  # Save complete timestamp to CSV
            'temperature': temperature,
            'humidity': humidity,
            'feeling': feeling
        }
        
        # Add to data storage
        self.user_feedback_data.append(feedback_entry)
        
        # Keep only the last max_feedback_entries
        if len(self.user_feedback_data) > self.max_feedback_entries:
            self.user_feedback_data.pop(0)
        
        # Save to CSV file
        self.save_user_feedback_to_csv()
        
        # Update UI
        self.update_feedback_display()
        
        # Log the feedback
        feeling_color = self.get_comfort_color(feeling)
        self.add_log_message(f"👤 User feedback: {feeling.upper()} (T:{temperature:.1f}°F, H:{humidity:.0f}%)", feeling_color)
    
    def update_feedback_display(self):
        """Update the feedback list display"""
        self.feedback_list.controls.clear()
        
        if not self.user_feedback_data:
            # Show placeholder when no data
            placeholder = ft.Text(
                "No user feedback data yet.\nPress buttons on board to add your feedback.",
                size=12,
                color="#888888",
                text_align=ft.TextAlign.CENTER
            )
            self.feedback_list.controls.append(placeholder)
        else:
            # Show recent feedback data (oldest first, newest at bottom)
            for entry in self.user_feedback_data[-20:]:  # Show last 20 entries
                feeling_color = self.get_comfort_color(entry['feeling'])
                
                # Extract display timestamp (show only time part)
                timestamp = entry['timestamp']
                if len(timestamp) > 8:  # If it's a complete timestamp "YYYY-MM-DD HH:MM:SS"
                    display_time = timestamp.split(' ')[1]  # Take only time part
                else:
                    display_time = timestamp  # If it's already in time format
                
                # Create feedback entry display
                feedback_row = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"[{display_time}]", size=10, color="#888888"),
                            ft.Text(entry['feeling'].upper(), size=12, weight=ft.FontWeight.BOLD, color=feeling_color),
                        ], spacing=5),
                        ft.Text(
                            f"T: {entry['temperature']:.1f}°F  |  H: {entry['humidity']:.0f}%",
                            size=11,
                            color="#CCCCCC"
                        )
                    ], spacing=2),
                    padding=ft.padding.all(5),
                    border_radius=3,
                    bgcolor="#3C4043",
                    margin=ft.margin.only(bottom=2)
                )
                self.feedback_list.controls.append(feedback_row)
        
        if self.main_app and hasattr(self.main_app, 'page'):
            self.main_app.page.update()
    
    def get_comfort_color(self, prediction: str) -> str:
        """Get color based on prediction result"""
        if prediction == "hot":
            return "#F44336"  # Red
        elif prediction == "cold":
            return "#2196F3"  # Blue
        elif prediction == "comfortable":
            return "#4CAF50"  # Green
        elif prediction == "-":
            return "#757575"  # Gray for error/inactive state
        else:
            return "#888888"  # Gray 

    def load_user_feedback_from_csv(self):
        """Load user feedback data from CSV file"""
        if self.csv_file_path.exists():
            try:
                with open(self.csv_file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Ensure correct data types
                        feedback_entry = {
                            'timestamp': row['timestamp'],
                            'temperature': float(row['temperature']),
                            'humidity': float(row['humidity']),
                            'feeling': row['feeling']
                        }
                        self.user_feedback_data.append(feedback_entry)
                
                # Limit loaded data amount
                if len(self.user_feedback_data) > self.max_feedback_entries:
                    self.user_feedback_data = self.user_feedback_data[-self.max_feedback_entries:]
                    
            except Exception as e:
                print(f"Error loading user feedback from CSV: {e}")
                self.user_feedback_data = []
        else:
            # If the file doesn't exist, create an empty list
            self.user_feedback_data = []
    
    def save_user_feedback_to_csv(self):
        """Save user feedback data to CSV file"""
        try:
            with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['timestamp', 'temperature', 'humidity', 'feeling']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write all feedback data
                for entry in self.user_feedback_data:
                    writer.writerow(entry)
                    
        except Exception as e:
            print(f"Error saving user feedback to CSV: {e}") 