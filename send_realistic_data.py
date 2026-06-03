import requests
import time
import math
import random

# FastAPI server URL
URL = "http://127.0.0.1:8000/update"
USER_NAME = "RealisticUser"

def send_packet(side, s1, s2, s3, s4):
    data = {
        "name": USER_NAME,
        "side": side,
        "s1": round(s1, 3),
        "s2": round(s2, 3),
        "s3": round(s3, 3),
        "s4": round(s4, 3),
        "timestamp": time.time()
    }
    try:
        response = requests.post(URL, json=data, timeout=1)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending data: {e}")
        return False

def simulate_gait_cycle(side, is_overpronating=False):
    """
    Simulates a single foot's gait cycle.
    A full cycle (stance + swing) takes about 1.0 second.
    Stance phase is roughly 60%, Swing 40%.
    """
    steps = 20  # Number of packets per cycle
    duration = 1.0 
    interval = duration / steps

    for i in range(steps):
        phase = i / steps
        
        s1, s2, s3, s4 = 0.0, 0.0, 0.0, 0.0
        
        # Stance phase (0.0 to 0.6)
        if phase < 0.6:
            stance_phase = phase / 0.6
            
            # 1. Heel Strike (0.0 - 0.2)
            if stance_phase < 0.3:
                s1 = math.sin(stance_phase * (math.pi / 0.3)) * 0.8
            
            # 2. Mid-Stance (0.2 - 0.7)
            if 0.2 < stance_phase < 0.8:
                mid_val = math.sin((stance_phase - 0.2) * (math.pi / 0.6)) * 0.7
                if is_overpronating:
                    s2 = mid_val * 1.2 # High inner pressure
                    s3 = mid_val * 0.3 # Low outer pressure
                else:
                    s2 = mid_val * 0.5
                    s3 = mid_val * 0.5
            
            # 3. Toe-off (0.7 - 1.0)
            if stance_phase > 0.6:
                s4 = math.sin((stance_phase - 0.6) * (math.pi / 0.4)) * 0.9
        
        # Swing phase (0.6 to 1.0) - already 0.0
        
        # Add some noise
        s1 = max(0, s1 + random.uniform(-0.05, 0.05))
        s2 = max(0, s2 + random.uniform(-0.05, 0.05))
        s3 = max(0, s3 + random.uniform(-0.05, 0.05))
        s4 = max(0, s4 + random.uniform(-0.05, 0.05))
        
        # Cap at 1.0
        s1, s2, s3, s4 = min(1.0, s1), min(1.0, s2), min(1.0, s3), min(1.0, s4)
        
        success = send_packet(side, s1, s2, s3, s4)
        if not success:
            print("Failed to send packet, stopping...")
            return False
            
        time.sleep(interval)
    return True

def run_simulation(total_steps=20):
    print(f"🚀 Starting realistic gait simulation for '{USER_NAME}'...")
    print(f"Total steps: {total_steps}")
    
    for step_count in range(total_steps):
        # Occasionally simulate overpronation (every 5th step)
        overpronation = (step_count % 5 == 4)
        
        if overpronation:
            print(f"👣 Step {step_count + 1}: Overpronation detected! (Inner pressure high)")
        else:
            print(f"👣 Step {step_count + 1}: Normal gait")
            
        # Left foot starts
        simulate_gait_cycle("left", is_overpronating=overpronation)
        
        # Right foot starts halfway through left's swing (not perfectly sync'd here for simplicity, 
        # but staggered is better)
        # For a simple simulation, we'll just do them sequentially but closely
        simulate_gait_cycle("right", is_overpronating=overpronation)

    print("✨ Simulation finished!")

if __name__ == "__main__":
    run_simulation(20)
