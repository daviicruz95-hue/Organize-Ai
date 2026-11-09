SERVER_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/server.py"

with open(SERVER_PATH, "r", encoding="utf-8") as f:
    content = f.read()

target_marker = '        # 1. EXPENSES: TOGGLE\n        if self.path == "/api/expenses/toggle":'

webhook_code = '''        # 0.1 WHATSAPP WEBHOOK / BOT INTEGRATION
        if self.path == "/api/webhook/whatsapp":
            try:
                from whatsapp_bot import WhatsAppFinancialBot
                bot = WhatsAppFinancialBot()

                message_text = req.get("text") or req.get("body") or req.get("message", "")
                sender_name = req.get("senderName") or req.get("pushName") or "Davi"
                sender_phone = req.get("phone") or req.get("from") or ""

                if "nat" in sender_name.lower():
                    sender_name = "Nathalie"
                else:
                    sender_name = "Davi"

                parsed = bot.parse_message(message_text, sender_phone=sender_phone, sender_name=sender_name)

                # Save directly into family account
                fam_user_id = "fam-davi-nathalie"
                fam_data = load_data(fam_user_id)
                active_m_id = fam_data.get("activeMonth", "2026-11")
                target_month = next((m for m in fam_data.get("months", []) if m["id"] == active_m_id), None)
                if not target_month and fam_data.get("months"):
                    target_month = fam_data["months"][0]

                if target_month:
                    new_exp = {
                        "id": f"exp-{int(datetime.now().timestamp()*1000)}",
                        "person": parsed["person"],
                        "category": parsed["category"],
                        "description": parsed["description"],
                        "amount": parsed["amount"],
                        "dueDate": parsed["dueDate"],
                        "status": parsed["status"],
                        "type": parsed["type"],
                        "totalInstallments": 1,
                        "currentInstallment": 1,
                        "installments": "À vista",
                        "subItems": []
                    }
                    target_month.setdefault("expenses", []).append(new_exp)
                    save_data(fam_data, fam_user_id)
                    reply_text = bot.generate_reply(parsed)
                    return self.send_json_response({"success": True, "reply": reply_text, "expense": new_exp})
                return self.send_json_response({"error": "No active month found"}, 400)
            except Exception as e:
                return self.send_json_response({"error": str(e)}, 500)

        # 1. EXPENSES: TOGGLE
        if self.path == "/api/expenses/toggle":'''

assert target_marker in content, "target_marker not found in server.py"
content = content.replace(target_marker, webhook_code, 1)

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("WhatsApp webhook endpoint added to server.py!")
