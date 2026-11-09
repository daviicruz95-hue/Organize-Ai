import json
import os

USERS_FILE = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/users.json"

with open(USERS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

users = data.get("users", [])

# Ensure both variations of Nathalie's email exist or link to the same family
family_id = "fam-davi-nathalie"

for u in users:
    email = u.get("email", "").lower()
    if email in [
        "davi@organizeai.com",
        "daviicruz95@gmail.com",
        "costacf@icloud.com",
        "nathaliea.pezzarico@gmail.com",
        "nathalie.a.pezarico@gmail.com"
    ]:
        u["familyId"] = family_id
        u["role"] = "family"

# Also add the dot variation if Nathalie used it
if not any(u.get("email") == "nathalie.a.pezarico@gmail.com" for u in users):
    users.append({
        "id": "usr-nathalie-dot",
        "name": "Nathalie Cruz",
        "email": "nathalie.a.pezarico@gmail.com",
        "password": "Tomate149",
        "familyId": family_id,
        "role": "family",
        "avatar": ""
    })

with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump({"users": users}, f, ensure_ascii=False, indent=2)

print("Linked users in users.json to family:", family_id)
