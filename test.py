import requests

def test_api():
    print("Testing API endpoints...")
    
    # Test simulation creation
    try:
        response = requests.post("http://127.0.0.1:8000/simulation", 
                               json={"num_robots": 1})
        print("\nCreate simulation response:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            simulation_id = data["id"]
            print("Simulation ID:", simulation_id)
            
            # Test simulation update
            update_response = requests.post(f"http://127.0.0.1:8000/simulation/{simulation_id}", 
                                         json={"velocidad": 1.0, "tiempo": 0.1})
            print("\nUpdate simulation response:", update_response.status_code)
            if update_response.status_code == 200:
                print("Update data:", update_response.json())
                
    except requests.RequestException as e:
        print("Error testing API:", e)

if __name__ == "__main__":
    test_api()