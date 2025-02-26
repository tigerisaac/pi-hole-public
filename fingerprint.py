import pandas as pd
from collections import defaultdict
from log import log_file_path
# website weights
website_weights = {
    "tiktok.com": 2.5,  
    "youtube.com": 1.0,  
    "instagram.com": 1.5,
    # add further based on child
}

# Function to get weight for a domain
def get_weight(domain):
    for site, weight in website_weights.items():
        if site in domain:
            return weight
    return 0  # Default weight to prevent a greater number of accesses overrepresenting actual websites
# i.e. if a device accesses google 300 times but tiktok 0 times it will not be considered in the calculation

# Read raw log file
def read_logs(log_file):
    device_activity = defaultdict(float)  # Store weighted scores per device

    with open(log_file, "r") as file:
        for line in file:
            parts = line.strip().split("|")
            if len(parts) < 3:
                continue 
            
            _, ip, domain = parts  # Extract timestamp, IP, and domain
            weight = get_weight(domain)  # Get domain weight

            device_activity[ip] += weight  # Accumulate weighted score

    return device_activity

def predict_child_device(log_file):
    device_scores = read_logs(log_file)

    # Sort devices by highest weighted score
    sorted_devices = sorted(device_scores.items(), key=lambda x: x[1], reverse=True)

    # Print device scores
    print("\nDevice Scores:")
    for ip, score in sorted_devices:
        print(f"{ip}: {score:.2f}")

    # Get top-scoring device
    predicted_child_ip = sorted_devices[0][0]
    return predicted_child_ip


# Predict the child's device
predicted_ip = predict_child_device(log_file_path)
actual_child_ip = "192.168.0.137"

# Print final result
print(f"\nPredicted Child's Device: {predicted_ip}")
if predicted_ip == actual_child_ip:
    print("✅ Correct")
else:
    print("❌ Incorrect")
