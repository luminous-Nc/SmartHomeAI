import os
import csv
import random
import numpy as np
from pathlib import Path

class TrainingDataGenerator:
    def __init__(self):
        # Ensure data directory exists
        self.data_dir = Path(".")  # Current directory (ml_data)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset parameters
        self.num_samples = 500
        
        # Temperature range (Fahrenheit)
        self.temp_min = 32  # 0°C
        self.temp_max = 95  # 35°C
        
        # Humidity range (percentage)
        self.humidity_min = 30
        self.humidity_max = 80
        
        # Comfort labels
        self.comfort_labels = ["cold", "comfortable", "hot"]
    
    def generate_environmental_data(self):
        """Generate temperature and humidity combination data"""
        data_points = []
        
        # Use grid sampling to ensure better coverage
        temp_steps = 25
        humidity_steps = 20
        
        # Create grid points
        temps = np.linspace(self.temp_min, self.temp_max, temp_steps)
        humidities = np.linspace(self.humidity_min, self.humidity_max, humidity_steps)
        
        # Generate grid data points
        for temp in temps:
            for humidity in humidities:
                data_points.append((round(temp, 1), round(humidity, 0)))
        
        # If grid points are not enough, add random points (should not happen with current settings)
        while len(data_points) < self.num_samples:
            temp = random.uniform(self.temp_min, self.temp_max)
            humidity = random.uniform(self.humidity_min, self.humidity_max)
            data_points.append((round(temp, 1), round(humidity, 0)))
        
        # Randomly select 500 points (or shuffle all if exactly 500 grid points)
        random.shuffle(data_points)
        return data_points[:self.num_samples]
    
    def get_hot_person_comfort(self, temperature, humidity):
        """Comfort judgment logic for heat-sensitive people"""
        # Heat-sensitive people are extremely sensitive to temperature, feel hot above 72°F
        # More likely to feel uncomfortable when humidity is high.
        # Increased humidity impact.
        heat_index = temperature + (humidity * 0.5) 
        
        # Thresholds adjusted for higher sensitivity to heat
        if heat_index < 60:  # Still feel cold only when it's significantly cold for them
            return "cold"
        elif heat_index < 78:  # Narrower comfortable range, feel hot sooner
            return "comfortable"
        else:  # Feel hot above a lower effective temperature
            return "hot"
    
    def get_normal_person_comfort(self, temperature, humidity):
        """Normal person comfort judgment logic"""
        # Standard comfort judgment, feel comfortable in 70-76°F range typically.
        heat_index = temperature + (humidity * 0.2) # Original humidity weight
        
        # Adjusted thresholds to ensure 74F/60H is comfortable
        if heat_index < 65:  # Feel cold below 65
            return "cold"
        elif heat_index < 87:  # Comfortable range: 65 <= heat_index < 87
            return "comfortable"
        else:  # Feel hot if heat_index >= 87
            return "hot"
    
    def get_cold_person_comfort(self, temperature, humidity):
        """Comfort judgment logic for cold-sensitive people"""
        # Cold-sensitive people are very sensitive to low temperatures, feel cold below 76°F
        # Need higher temperatures to feel comfortable.
        # Reduced humidity impact on feeling warm.
        heat_index = temperature + (humidity * 0.05) 
        
        # Thresholds significantly adjusted to make them feel cold more easily
        if heat_index < 78:  # Feel cold unless the effective temperature is quite high
            return "cold"
        elif heat_index < 88:  # Comfortable range shifted higher: 78 <= heat_index < 88
            return "comfortable"
        else:  # Feel hot only at very high effective temperatures for them
            return "hot"
    
    def add_noise_to_labels(self, labels, noise_ratio=0.05):
        """Add slight noise to labels to simulate real-world uncertainty"""
        noisy_labels = []
        for label in labels:
            if random.random() < noise_ratio:
                available_labels = [l for l in self.comfort_labels if l != label]
                if available_labels: # Ensure there's a different label to choose
                    noisy_label = random.choice(available_labels)
                    noisy_labels.append(noisy_label)
                else: # Should not happen with 3 labels
                    noisy_labels.append(label) 
            else:
                noisy_labels.append(label)
        return noisy_labels
    
    def generate_dataset(self, person_type):
        """Generate dataset for specific person type"""
        env_data = self.generate_environmental_data()
        
        if person_type == "hot_person":
            comfort_func = self.get_hot_person_comfort
        elif person_type == "normal_person":
            comfort_func = self.get_normal_person_comfort
        elif person_type == "cold_person":
            comfort_func = self.get_cold_person_comfort
        else:
            raise ValueError(f"Unknown person type: {person_type}")
        
        labels = [comfort_func(temp, humidity) for temp, humidity in env_data]
        labels = self.add_noise_to_labels(labels)
        
        dataset = [[temp, humidity, label] for (temp, humidity), label in zip(env_data, labels)]
        return dataset
    
    def save_dataset(self, dataset, filename):
        """Save dataset to CSV file"""
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['temperature', 'humidity', 'comfort_label'])
            writer.writerows(dataset)
        
        print(f"✅ Dataset saved to: {filepath}")
        return filepath
    
    def generate_all_datasets(self):
        """Generate datasets for all three person types"""
        datasets = {
            "hot_person": "hot_person_data.csv",
            "normal_person": "normal_person_data.csv", 
            "cold_person": "cold_person_data.csv"
        }
        
        print("🔄 Starting training dataset generation...")
        print(f"📊 Each dataset contains {self.num_samples} data points")
        print(f"🌡️  Temperature range: {self.temp_min}°F - {self.temp_max}°F")
        print(f"💧 Humidity range: {self.humidity_min}% - {self.humidity_max}%")
        print("-" * 50)
        
        for person_type, filename in datasets.items():
            print(f"🔄 Generating {person_type} dataset...")
            # Important: Reset random seed for each dataset generation if you want
            # the *environmental data points* to be the same for each person type
            # before shuffling and labeling.
            # For this modification, we want the env_data to be the same for direct comparison of labels.
            # However, generate_environmental_data shuffles internally.
            # To ensure identical (temp, humidity) inputs before labeling for each person:
            # Option 1: Generate env_data once outside the loop.
            # Option 2: Re-seed before calling generate_environmental_data IF its internal
            #           randomness needs to be reset for *this specific call only*.
            # Current structure: generate_environmental_data is called for each person_type,
            # so it will generate a *different set* of 500 shuffled (temp, humidity) points
            # for each person type if random seeds are not carefully managed *inside* the loop.
            # For distinct datasets, this is fine. For directly comparable labels on the *same*
            # environmental points, env_data should be generated once.
            # Let's stick to the original structure where each dataset gets its own random sample of points.
            # If you set the global random.seed(42) once at the start, the sequence of
            # random numbers is fixed, so generate_environmental_data() will produce the
            # same sequence of points each time it's called IF it re-initializes its own random state or
            # if the number of random calls before it is consistent.
            # Given random.shuffle(data_points) is called, each person type will get a different set of points.

            dataset = self.generate_dataset(person_type) # This now uses the new comfort logic
            filepath = self.save_dataset(dataset, filename)
            
            label_counts = {}
            for row in dataset:
                label = row[2]
                label_counts[label] = label_counts.get(label, 0) + 1
            
            print(f"📈 Label distribution for {person_type}: {label_counts}")
            print()
        
        print("✅ All datasets generated successfully!")
    
    def display_sample_data(self, dataset, person_type, num_samples=10):
        """Display dataset examples"""
        print(f"\n📋 {person_type} dataset examples (first {num_samples} entries):")
        print("-" * 50)
        print(f"{'Temp(°F)':<10} {'Humidity(%)':<12} {'Comfort':<12}")
        print("-" * 34)
        
        for i, (temp, humidity, label) in enumerate(dataset[:num_samples]):
            print(f"{temp:<10} {humidity:<12} {label:<12}")

    def test_specific_case(self, temp, humidity):
        """Test a specific temperature and humidity against all profiles (without noise)"""
        print(f"\n🧪 Testing specific case: Temperature={temp}°F, Humidity={humidity}%")
        print("-" * 50)
        profiles = {
            "Hot Person": self.get_hot_person_comfort,
            "Normal Person": self.get_normal_person_comfort,
            "Cold Person": self.get_cold_person_comfort
        }
        for person_type, func in profiles.items():
            comfort = func(temp, humidity)
            print(f"{person_type:<15}: {comfort}")
        print("-" * 50)

if __name__ == "__main__":
    # Set random seed for reproducible results for data point generation and noise
    random.seed(42)
    np.random.seed(42) # For numpy operations like linspace (though less critical for this problem)
    
    generator = TrainingDataGenerator()
    
    # Test the specific case 74°F, 60% humidity with the new logic
    generator.test_specific_case(74, 60)
    
    generator.generate_all_datasets()
    
    # Display sample data for each dataset
    # Note: display_sample_data will show data WITH noise.
    # The generate_dataset call here will re-generate the data,
    # potentially with different noise outcomes than what was saved if seeds aren't managed per call.
    # To show samples from the *saved* files, you'd need to read the CSVs.
    # For simplicity, we re-generate and show, keeping in mind noise is present.
    print("\n--- Displaying samples from newly generated (in-memory) datasets ---")
    person_types = ["hot_person", "normal_person", "cold_person"]
    for person_type in person_types:
        # Re-generate with the same seed logic if needed for consistent display
        # However, random.seed(42) is set globally. The sequence of random numbers
        # will continue. If generate_dataset is called multiple times, it will
        # use subsequent random numbers for shuffling and noise.
        dataset = generator.generate_dataset(person_type) 
        generator.display_sample_data(dataset, person_type)