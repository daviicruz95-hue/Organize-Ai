import os
import re

SERVER_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/server.py"

with open(SERVER_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Let's inspect where DATA_FILE is defined
old_data_def = '''DATA_FILE = os.path.join(BASE_DIR, "data.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")'''

new_data_def = '''DATA_FILE = os.path.join(BASE_DIR, "data.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
USERS_DIR = os.path.join(BASE_DIR, "users_data")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
os.makedirs(USERS_DIR, exist_ok=True)

MASTER_USER_ID = "user-davi"

def get_users():
    if not os.path.exists(USERS_FILE):
        initial = {
            "users": [
                {
                    "id": MASTER_USER_ID,
                    "name": "Davi & Nathalie",
                    "email": "davi@organizeai.com",
                    "password": "123",
                    "role": "master",
                    "avatar": ""
                }
            ]
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial, f, ensure_ascii=False, indent=2)
        return initial.get("users", [])
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("users", [])
    except Exception:
        return []

def save_users(users_list):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users_list}, f, ensure_ascii=False, indent=2)

def get_user_file_path(user_id):
    if not user_id or user_id == MASTER_USER_ID:
        return DATA_FILE
    return os.path.join(USERS_DIR, f"data_{user_id}.json")

def create_blank_user_data(user_name):
    return {
        "activeMonth": "2026-11",
        "savingsGoal": {
            "targetAmount": 1000.0,
            "description": "Minha Meta de Poupança",
            "boxes": [
                {"id": "box-1", "name": "Reserva de Emergência", "amount": 0.0, "target": 5000.0, "icon": "🛡️"},
                {"id": "box-2", "name": "Cofrinho / Sonhos", "amount": 0.0, "target": 2000.0, "icon": "🐷"}
            ]
        },
        "futureInstallments": [],
        "months": [
            {
                "id": "2026-11",
                "name": "Novembro",
                "year": 2026,
                "reserve": 0.0,
                "incomes": [],
                "expenses": []
            }
        ]
    }'''

assert old_data_def in content, "old_data_def not found"
content = content.replace(old_data_def, new_data_def, 1)

# Now update load_data and save_data to accept user_id
old_load_save = '''def load_data():
    if not os.path.exists(DATA_FILE):
        return {"activeMonth": "2026-11", "months": [], "futureInstallments": [], "savingsGoal": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)'''

new_load_save = '''def load_data(user_id=MASTER_USER_ID):
    file_path = get_user_file_path(user_id)
    if not os.path.exists(file_path):
        blank = create_blank_user_data("Usuário")
        save_data(blank, user_id)
        return blank
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"activeMonth": "2026-11", "months": [], "futureInstallments": [], "savingsGoal": {}}

def save_data(data, user_id=MASTER_USER_ID):
    file_path = get_user_file_path(user_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)'''

assert old_load_save in content, "old_load_save not found"
content = content.replace(old_load_save, new_load_save, 1)

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Step 1 of server upgrade completed.")
