import requests

BASE_URL = "http://localhost:8000"

def fetch_states():
    try:
        response = requests.get(f"{BASE_URL}/States")
        # response.raise_for_status()
        return response.json()
    except:
        return

def fetch_categories():
    try:
        response = requests.get(f"{BASE_URL}/Categories")
        # response.raise_for_status()
        return response.json()
    except:
        return 


# def fetch_districts():
#     try:
#         response = requests.get(f"{BASE_URL}/Districts")
#         response.raise_for_status()
#         return response.json()
#     except:
#         return 

# def fetch_indicators():
#     try:
#         response = requests.get(f"{BASE_URL}/Indicators")
#         response.raise_for_status()
#         return response.json()
#     except:
#         return 

# def fetch_nfhs_state_data():
#     try:
#         response = requests.get(f"{BASE_URL}/NFHS_State_Data")
#         response.raise_for_status()
#         return response.json()
#     except:
#         return 

# def fetch_nfhs_district_data():
#     try:
#         response = requests.get(f"{BASE_URL}/NFHS_District_Data")
#         response.raise_for_status()
#         return response.json()
#     except:
#         return 

# def fetch_nfhs_rounds():
#     try:
#         response = requests.get(f"{BASE_URL}/NFHS_Rounds")
#         response.raise_for_status()
#         return response.json()
#     except:
#         return 