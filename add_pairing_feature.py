import re

SERVER_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/server.py"

with open(SERVER_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update get_user_file_path to respect familyId
old_func = '''def get_user_file_path(user_id):
    if not user_id or user_id == MASTER_USER_ID:
        return DATA_FILE
    return os.path.join(USERS_DIR, f"data_{user_id}.json")'''

new_func = '''def get_user_file_path(user_id):
    if not user_id or user_id == MASTER_USER_ID or user_id == "fam-davi-nathalie":
        return DATA_FILE
    users = get_users()
    u = next((x for x in users if x.get("id") == user_id), None)
    if u and u.get("familyId") == "fam-davi-nathalie":
        return DATA_FILE
    elif u and u.get("familyId"):
        return os.path.join(USERS_DIR, f"data_family_{u['familyId']}.json")
    return os.path.join(USERS_DIR, f"data_{user_id}.json")'''

assert old_func in code, "old_func not found"
code = code.replace(old_func, new_func, 1)

# 2. Add /api/auth/pair endpoint inside do_POST
pair_endpoint_code = '''        elif self.path == "/api/auth/pair":
            user_id = self.get_user_id(req)
            partner_email = req.get("partnerEmail", "").strip().lower()

            if not partner_email:
                return self.send_json_response({"error": "Informe o e-mail do parceiro(a)."}, 400)

            users = get_users()
            current_u = next((u for u in users if u.get("id") == user_id), None)
            partner_u = next((u for u in users if u.get("email", "").lower() == partner_email), None)

            if not partner_u:
                return self.send_json_response({"error": f"Nenhuma conta encontrada com o e-mail {partner_email}."}, 404)

            # Assign common familyId
            common_fam_id = current_u.get("familyId") or partner_u.get("familyId") or f"fam-{int(datetime.now().timestamp()*1000)}"
            current_u["familyId"] = common_fam_id
            partner_u["familyId"] = common_fam_id

            # If either was Davi/Nathalie family, ensure it uses fam-davi-nathalie
            if any(email in ["davi@organizeai.com", "daviicruz95@gmail.com", "nathaliea.pezzarico@gmail.com", "nathalie.a.pezarico@gmail.com", "costacf@icloud.com"] for email in [current_u.get("email"), partner_u.get("email")]):
                common_fam_id = "fam-davi-nathalie"
                current_u["familyId"] = common_fam_id
                partner_u["familyId"] = common_fam_id

            save_users(users)
            return self.send_json_response({
                "success": True,
                "message": f"Contas vinculadas com sucesso! Agora você e {partner_u.get('name')} compartilham o mesmo painel.",
                "familyId": common_fam_id,
                "partner": {"name": partner_u.get("name"), "email": partner_u.get("email")}
            })
'''

target_post_marker = '        elif self.path == "/api/auth/profile":'
assert target_post_marker in code, "target_post_marker not found"
code = code.replace(target_post_marker, pair_endpoint_code + "\n" + target_post_marker, 1)

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("Server pairing logic successfully written to server.py!")
