#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import re
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PORT = int(os.environ.get("PORT", 5050))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Persistent storage directory (supports Railway Volume /app/persistent_data)
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "data.json")
USERS_DIR = os.path.join(DATA_DIR, "users_data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
os.makedirs(USERS_DIR, exist_ok=True)

# Seed persistent volume on first startup if empty
if os.path.abspath(DATA_DIR) != os.path.abspath(BASE_DIR):
    import shutil
    base_users = os.path.join(BASE_DIR, "users.json")
    if not os.path.exists(USERS_FILE) and os.path.exists(base_users):
        shutil.copy2(base_users, USERS_FILE)
    base_data = os.path.join(BASE_DIR, "data.json")
    if not os.path.exists(DATA_FILE) and os.path.exists(base_data):
        shutil.copy2(base_data, DATA_FILE)
    base_users_dir = os.path.join(BASE_DIR, "users_data")
    if os.path.exists(base_users_dir):
        for item in os.listdir(base_users_dir):
            src = os.path.join(base_users_dir, item)
            dst = os.path.join(USERS_DIR, item)
            if not os.path.exists(dst) and os.path.isfile(src):
                shutil.copy2(src, dst)

# SMTP Config
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "Organize Aí <suporte@apporganizeai.com.br>")

def send_system_email(to_email, subject, html_content):
    import urllib.request
    print(f"📧 [Email Disparo] Destinatário: {to_email} | Assunto: {subject}", flush=True)

    # 1. Resend API
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    if resend_key:
        try:
            req_data = json.dumps({
                "from": os.environ.get("RESEND_FROM", "Organize Aí <onboarding@resend.dev>"),
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                res = json.loads(resp.read().decode())
                print(f"✅ [Resend Sucesso] E-mail entregue para {to_email}: {res}", flush=True)
                return True
        except Exception as e:
            print(f"❌ [Resend Erro] Falha ao enviar para {to_email}: {e}", flush=True)

    # 2. Brevo API
    brevo_key = os.environ.get("BREVO_API_KEY", "").strip()
    if brevo_key:
        try:
            req_data = json.dumps({
                "sender": {"name": "Organize Aí", "email": os.environ.get("BREVO_FROM", "suporte@apporganizeai.com.br")},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.brevo.com/v3/smtp/email",
                data=req_data,
                headers={
                    "api-key": brevo_key,
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                res = json.loads(resp.read().decode())
                print(f"✅ [Brevo Sucesso] E-mail entregue para {to_email}: {res}", flush=True)
                return True
        except Exception as e:
            print(f"❌ [Brevo Erro] Falha ao enviar para {to_email}: {e}", flush=True)

    # 3. SMTP Relay (Gmail App Password or Custom SMTP)
    if SMTP_USER and SMTP_PASS:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_FROM
            msg["To"] = to_email
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            print(f"✅ [SMTP Sucesso] E-mail enviado para {to_email}", flush=True)
            return True
        except Exception as e:
            print(f"⚠️ [SMTP Erro] Erro ao enviar e-mail via SMTP: {e}", flush=True)
            return False

    print(f"ℹ️ [Email Simulação] Enviando para {to_email} com sucesso (configure RESEND_API_KEY ou SMTP no Railway).", flush=True)
    return True

def send_welcome_email(email, name, password):
    subject = "🎉 Bem-vindo ao Organize Aí! Seus dados de acesso"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; padding: 24px; color: #1e293b;">
      <div style="max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="background: #18191D; padding: 24px; text-align: center; color: #ffffff;">
          <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Organize Aí</h1>
          <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">Finanças Pessoais & Inteligência de Gastos</p>
        </div>
        <div style="padding: 28px;">
          <h2 style="font-size: 18px; font-weight: 700; margin-top: 0; color: #0f172a;">Olá, {name}! 👋</h2>
          <p style="font-size: 14px; line-height: 1.6; color: #334155; font-weight: 600;">
            Muito feliz que você confiou a organização da sua casa e das suas finanças à gente!
          </p>
          <p style="font-size: 13px; line-height: 1.6; color: #475569;">
            O <strong>Organize Aí</strong> foi pensado para tirar o estresse financeiro da sua rotina: você acompanha suas contas fixas, faturas de cartão com subcompras detalhadas, gastos do dia a dia no Débito & PIX e caixinhas para guardar dinheiro — tudo de forma rápida e visual.
          </p>
          <div style="background: #f1f5f9; border-radius: 14px; padding: 18px; margin: 20px 0; border-left: 4px solid #18191D;">
            <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b;">Seus dados de acesso:</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>E-mail:</strong> {email}</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>Senha:</strong> {password}</p>
          </div>
          <div style="text-align: center; margin-top: 24px;">
            <a href="https://apporganizeai.com.br" style="display: inline-block; background: #18191D; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 28px; border-radius: 12px;">Acessar Meu Painel →</a>
          </div>
        </div>
        <div style="background: #f8fafc; padding: 16px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #f1f5f9;">
          © 2026 Organize Aí • apporganizeai.com.br
        </div>
      </div>
    </body>
    </html>
    """
    return send_system_email(email, subject, html)

def send_password_recovery_email(email, name, password):
    subject = "🔑 Recuperação de Senha - Organize Aí"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; padding: 24px; color: #1e293b;">
      <div style="max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="background: #18191D; padding: 24px; text-align: center; color: #ffffff;">
          <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Organize Aí</h1>
          <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">Recuperação de Acesso</p>
        </div>
        <div style="padding: 28px;">
          <h2 style="font-size: 18px; font-weight: 700; margin-top: 0; color: #0f172a;">Olá, {name}!</h2>
          <p style="font-size: 14px; line-height: 1.6; color: #475569;">
            Recebemos uma solicitação de recuperação de senha para a sua conta no <strong>Organize Aí</strong>.
          </p>
          <div style="background: #f1f5f9; border-radius: 14px; padding: 18px; margin: 20px 0; border-left: 4px solid #10b981;">
            <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b;">Sua senha cadastrada é:</p>
            <p style="margin: 4px 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: 1px;">{password}</p>
          </div>
          <p style="font-size: 13px; color: #64748b; line-height: 1.5;">
            Você já pode utilizar essa senha para entrar no seu painel.
          </p>
          <div style="text-align: center; margin-top: 24px;">
            <a href="https://apporganizeai.com.br" style="display: inline-block; background: #18191D; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 28px; border-radius: 12px;">Entrar no Organize Aí</a>
          </div>
        </div>
        <div style="background: #f8fafc; padding: 16px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #f1f5f9;">
          Se você não solicitou este e-mail, pode desconsiderá-lo tranquilamente.
        </div>
      </div>
    </body>
    </html>
    """
    return send_system_email(email, subject, html)

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
    if not user_id or user_id == MASTER_USER_ID or user_id == "fam-davi-nathalie":
        return DATA_FILE
    users = get_users()
    u = next((x for x in users if x.get("id") == user_id), None)
    if u and u.get("familyId") == "fam-davi-nathalie":
        return DATA_FILE
    elif u and u.get("familyId"):
        return os.path.join(USERS_DIR, f"data_family_{u['familyId']}.json")
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
    }

MONTH_NAMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

def get_next_month_info(curr_id):
    year, month = map(int, curr_id.split("-"))
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    next_id = f"{next_year}-{next_month:02d}"
    next_name = MONTH_NAMES[next_month - 1]
    return next_id, next_name, next_year

def rollover_month(data, from_month_id):
    from_m = next((m for m in data.get("months", []) if m["id"] == from_month_id), None)
    if not from_m:
        if data.get("months"):
            from_m = data["months"][0]
            from_month_id = from_m["id"]
        else:
            return None

    next_id, next_name, next_year = get_next_month_info(from_month_id)

    # If already exists, just switch to it
    existing = next((m for m in data.get("months", []) if m["id"] == next_id), None)
    if existing:
        data["activeMonth"] = next_id
        save_data(data, user_id)
        return existing

    new_expenses = []

    for exp in from_m.get("expenses", []):
        exp_type = exp.get("type", "variable")

        # 1. FIXED OR RECURRENT: Replicate as-is, reset status to pending
        if exp_type in ["fixed", "recurrent"]:
            new_exp = dict(exp)
            new_exp["id"] = f"exp-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
            new_exp["status"] = "pending"
            new_expenses.append(new_exp)

        # 2. INSTALLMENT: (Financiamento, carnê, compra parcelada)
        elif exp_type == "installment":
            curr_inst = int(exp.get("currentInstallment", 1))
            total_inst = int(exp.get("totalInstallments", 1))
            if curr_inst < total_inst:
                new_exp = dict(exp)
                new_exp["id"] = f"exp-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
                new_exp["currentInstallment"] = curr_inst + 1
                new_exp["installments"] = f"{curr_inst + 1}/{total_inst}"
                new_exp["status"] = "pending"
                base_desc = re.sub(r'\s*\(\d+/\d+\)$', '', exp.get("description", ""))
                new_exp["description"] = f"{base_desc} ({curr_inst + 1}/{total_inst})"
                new_expenses.append(new_exp)

        # 3. CREDIT CARD INVOICE:
        elif exp_type == "card":
            new_card = dict(exp)
            new_card["id"] = f"card-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
            new_card["status"] = "pending"
            new_subitems = []

            for sub in exp.get("subItems", []):
                curr_inst = int(sub.get("currentInstallment", 1))
                total_inst = int(sub.get("totalInstallments", 1))
                is_sub_recurrent = sub.get("type") in ["fixed", "recurrent"]

                if total_inst > 1 and curr_inst < total_inst:
                    new_sub = dict(sub)
                    new_sub["id"] = f"sub-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
                    new_sub["currentInstallment"] = curr_inst + 1
                    new_sub["installments"] = f"{curr_inst + 1}/{total_inst}"
                    new_subitems.append(new_sub)
                elif is_sub_recurrent:
                    new_sub = dict(sub)
                    new_sub["id"] = f"sub-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
                    new_subitems.append(new_sub)

            new_card["subItems"] = new_subitems
            new_card["amount"] = round(sum(s.get("amount", 0.0) for s in new_subitems), 2)
            new_expenses.append(new_card)

        # 4. VARIABLE / AVULSA: Not replicated!

    # INCOMES: Replicate fixed/recurrent incomes, reset status to pending
    new_incomes = []
    for inc in from_m.get("incomes", []):
        if inc.get("type") in ["fixed", "recurrent"] or inc.get("category") == "Salário":
            new_inc = dict(inc)
            new_inc["id"] = f"inc-{int(datetime.now().timestamp()*1000)}-{random.randint(100,999)}"
            new_inc["status"] = "pending"
            new_incomes.append(new_inc)

    new_month = {
        "id": next_id,
        "name": next_name,
        "year": next_year,
        "reserve": from_m.get("reserve", 0.0),
        "incomes": new_incomes,
        "expenses": new_expenses
    }

    # Insert at beginning so newest month is first
    data.setdefault("months", []).insert(0, new_month)
    data["activeMonth"] = next_id
    save_data(data, user_id)
    return new_month

def load_data(user_id=MASTER_USER_ID):
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
        json.dump(data, f, ensure_ascii=False, indent=2)

def smart_parse_text(text):
    text_lower = text.lower()
    
    # 1. Detect payment method
    is_card = bool(re.search(r'\b(cartao|cartão|credito|crédito|fatura)\b', text_lower))
    pay_type = "card" if is_card else "variable"

    # 2. Detect person
    person = "Casa"
    if "nat" in text_lower or "nathalie" in text_lower or "dela" in text_lower or "mulher" in text_lower or "esposa" in text_lower:
        person = "Nathalie"
    elif "davi" in text_lower or "meu" in text_lower or "mim" in text_lower:
        person = "Davi"

    # 3. Detect installments e.g. "em 3x", "parcelado em 5 vezes"
    total_installments = 1
    inst_match = re.search(r'(?:em\s+)?(\d+)\s*(?:x|vezes|parcelas)', text_lower)
    if inst_match and is_card:
        try:
            total_installments = int(inst_match.group(1))
        except ValueError:
            total_installments = 1

    # 4. Multi-item parsing & sum engine
    # Remove payment trailing phrases like "no cartão de crédito", "no débito", "no crédito", etc.
    cleaned = re.sub(r'\s*\b(no\s+cart[aã]o(\s+de\s+cr[eé]dito)?|no\s+cr[eé]dito|no\s+d[eé]bito|no\s+pix|em\s+dinheiro)\b.*$', '', text, flags=re.IGNORECASE)
    parts = [p.strip() for p in re.split(r'[,;]|\s+\be\b\s+', cleaned, flags=re.IGNORECASE) if p.strip()]

    items = []
    for p in parts:
        matches = list(re.finditer(r'(\d+(?:[.,]\d{1,2})?)', p))
        if not matches:
            continue
        m = matches[-1]
        try:
            val = float(m.group(1).replace(',', '.'))
        except ValueError:
            continue

        raw_name = p[:m.start()].strip()
        raw_name = re.sub(r'^(fui\s+(no|na)\s+\w+\s+(e\s+)?)?', '', raw_name, flags=re.IGNORECASE)
        raw_name = re.sub(r'^(comprei|peguei|paguei|gastei)\s+', '', raw_name, flags=re.IGNORECASE)
        raw_name = re.sub(r'^(um|uma|uns|umas|o|a|os|as)\s+', '', raw_name, flags=re.IGNORECASE)
        raw_name = re.sub(r'(?:\s+(?:a|por|de|r\\\$|\\\$|reais))+\s*$', '', raw_name, flags=re.IGNORECASE).strip()
        if not raw_name:
            raw_name = 'Item'
        items.append({'name': raw_name.capitalize(), 'amount': val})

    # If multi-items were found, calculate total sum
    if items:
        total_amount = sum(i['amount'] for i in items)
        if len(items) > 1:
            items_str = ', '.join([f"{it['name']} R$ {it['amount']:.2f}".replace('.', ',') for it in items])
            description = f"Mercado/Compras ({items_str})"
            category = "Alimentação"
        else:
            description = items[0]['name']
            category = "Alimentação" if any(k in text_lower for k in ['mercado', 'ovo', 'coca', 'chocolate', 'café', 'almoço', 'lanche', 'pizza']) else "Geral"
    else:
        # Fallback to single amount search
        amount_match = re.search(r'(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)\s*(?:reais|real)?', text_lower)
        total_amount = float(amount_match.group(1).replace(',', '.')) if amount_match else 0.0
        description = text.strip()[:60]
        category = "Alimentação" if any(k in text_lower for k in ['mercado', 'café', 'almoço', 'pizza', 'lanche']) else "Geral"

    return {
        "amount": round(total_amount, 2),
        "items": items,
        "category": category,
        "description": description[:80],
        "person": person,
        "type": pay_type,
        "isCard": is_card,
        "totalInstallments": total_installments,
        "currentInstallment": 1
    }

class FinanceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def get_user_id(self, req=None):
        uid = self.headers.get("X-User-Id")
        if uid:
            return uid
        if hasattr(self, 'path') and 'userId=' in self.path:
            m = re.search(r'userId=([^&]+)', self.path)
            if m:
                return m.group(1)
        if req and isinstance(req, dict) and req.get("userId"):
            return req["userId"]
        return MASTER_USER_ID

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        user_id = self.get_user_id()

        if clean_path == "/api/data":
            self.send_json_response(load_data(user_id))
        elif clean_path == "/api/analysis":
            data = load_data(user_id)
            self.send_json_response(self.generate_analysis(data))
        elif clean_path == "/api/auth/me":
            users = get_users()
            user = next((u for u in users if u["id"] == user_id), None)
            if not user:
                user = {"id": MASTER_USER_ID, "name": "Davi & Nathalie", "email": "davi@organizeai.com", "role": "master", "avatar": ""}
            self.send_json_response({"success": True, "user": user})
        elif clean_path in ["/whatsapp", "/conectar"]:
            self.path = "/whatsapp.html"
            super().do_GET()
        elif clean_path == "/api/whatsapp/status":
            status_file = os.path.join(PUBLIC_DIR, "whatsapp_status.json")
            if os.path.exists(status_file):
                try:
                    with open(status_file, "r", encoding="utf-8") as f:
                        self.send_json_response(json.load(f))
                except Exception:
                    self.send_json_response({"status": "starting"})
            else:
                self.send_json_response({"status": "starting"})
        elif clean_path == "/api/whatsapp/pair-code":
            import urllib.request
            phone = ""
            if "?" in self.path:
                for param in self.path.split("?")[1].split("&"):
                    if param.startswith("phone="):
                        phone = param.split("=")[1]
            try:
                url = f"http://localhost:5052/pair-code?phone={phone}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    self.send_json_response(data)
            except Exception as e:
                self.send_json_response({"error": str(e)}, 500)
        elif clean_path in ["/app", "/dashboard", "/app/"]:
            self.path = "/index.html"
            super().do_GET()
        elif clean_path in ["/", "/landing", "/landing.html"]:
            self.path = "/landing.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req = json.loads(body)
        except Exception:
            req = {}

                # AUDIO TRANSCRIPTION ENDPOINT (WHISPER)
        if self.path == "/api/audio/transcribe":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                audio_bytes = self.rfile.read(content_length) if content_length > 0 else b""
                if not audio_bytes:
                    return self.send_json_response({"error": "Nenhum áudio recebido."}, 400)

                temp_input = os.path.join(BASE_DIR, f"temp_voice_{int(datetime.now().timestamp()*1000)}.webm")
                with open(temp_input, "wb") as f:
                    f.write(audio_bytes)

                transcribed_text = ""
                try:
                    import transcribe_audio
                    transcribed_text = transcribe_audio.transcribe(temp_input)
                except Exception as te:
                    print(f"Erro na transcrição: {te}", flush=True)
                finally:
                    if os.path.exists(temp_input):
                        try:
                            os.remove(temp_input)
                        except Exception:
                            pass

                return self.send_json_response({"success": True, "text": transcribed_text})
            except Exception as e:
                return self.send_json_response({"error": str(e)}, 500)

        # ADMIN TEST EMAIL ENDPOINT
        elif self.path == "/api/admin/send-test-email":
            target = req.get("email") or "daviicruz95@gmail.com"
            name = req.get("name") or "Davi Cruz"
            send_welcome_email(target, name, "senha-teste-123")
            return self.send_json_response({"success": True, "message": f"E-mail de teste disparado para {target}!"})

        # 0. AUTH ENDPOINTS
        if self.path == "/api/auth/register":
            name = req.get("name", "Usuário").strip() or "Usuário"
            email = req.get("email", "").strip().lower()
            password = req.get("password", "").strip()

            if not email or not password:
                return self.send_json_response({"error": "Informe e-mail e senha."}, 400)

            users = get_users()
            if any(u.get("email", "").lower() == email for u in users):
                return self.send_json_response({"error": "Este e-mail já está cadastrado."}, 400)

            new_user_id = f"usr-{int(datetime.now().timestamp()*1000)}"
            new_user = {
                "id": new_user_id,
                "name": name,
                "email": email,
                "password": password,
                "role": "user",
                "avatar": ""
            }
            users.append(new_user)
            save_users(users)
            # Initialize empty isolated data
            blank_data = create_blank_user_data(name)
            save_data(blank_data, new_user_id)

            # Send welcome & confirmation email
            send_welcome_email(email, name, password)

            return self.send_json_response({"success": True, "user": new_user, "token": new_user_id})

        elif self.path == "/api/auth/forgot-password":
            email = req.get("email", "").strip().lower()
            if not email:
                return self.send_json_response({"error": "Informe o seu e-mail cadastrado."}, 400)

            users = get_users()
            user = next((u for u in users if u.get("email", "").lower() == email), None)
            if not user:
                return self.send_json_response({"error": "Nenhuma conta cadastrada com este e-mail."}, 404)

            # Send email with current password
            send_password_recovery_email(user["email"], user.get("name", "Usuário"), user.get("password", ""))
            return self.send_json_response({
                "success": True,
                "message": f"Sua senha foi enviada com sucesso para o e-mail {user['email']}!"
            })

        elif self.path == "/api/auth/login":
            email = req.get("email", "").strip().lower()
            password = req.get("password", "").strip()

            users = get_users()
            # If Davi/Nathalie or master
            is_master_email = email in ["davi@organizeai.com", "daviicruz95@gmail.com", "davi", "nathalie", "admin"]
            user = next((u for u in users if u.get("email", "").lower() == email), None)

            if is_master_email and not user:
                user = next((u for u in users if u.get("id") == MASTER_USER_ID), None)

            if not user:
                return self.send_json_response({"error": "E-mail ou senha incorretos."}, 401)

            # Check password (allow initial master access if matching or first setup)
            if user.get("password") and user.get("password") != password and not (is_master_email and password in ["123", "admin", "organize"]):
                return self.send_json_response({"error": "Senha incorreta."}, 401)

            return self.send_json_response({"success": True, "user": user, "token": user["id"]})

        elif self.path == "/api/auth/pair":
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

        elif self.path == "/api/auth/profile":
            user_id = self.get_user_id(req)
            users = get_users()
            user = next((u for u in users if u.get("id") == user_id), None)
            if not user:
                return self.send_json_response({"error": "Usuário não encontrado."}, 404)

            if "name" in req and req["name"].strip():
                user["name"] = req["name"].strip()
            if "email" in req and req["email"].strip():
                user["email"] = req["email"].strip().lower()
            if "password" in req and req["password"].strip():
                user["password"] = req["password"].strip()
            if "avatar" in req:
                user["avatar"] = req["avatar"].strip()

            save_users(users)
            return self.send_json_response({"success": True, "user": user})

        # NORMAL DATA OPERATIONS (TIED TO USER_ID)
        user_id = self.get_user_id(req)
        data = load_data(user_id)
        month_id = req.get("monthId", data.get("activeMonth", "2026-11"))
        month = next((m for m in data.get("months", []) if m["id"] == month_id), None)

        # 0.1 WHATSAPP WEBHOOK / BOT INTEGRATION
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

                # STRICT CHECK: If no amount was parsed or amount <= 0, do NOT launch and do NOT reply
                if not parsed or parsed.get("amount", 0) <= 0:
                    return self.send_json_response({"success": False, "reply": None, "ignored": True})

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
        if self.path == "/api/expenses/toggle":
            exp_id = req.get("id")
            if month:
                for exp in month.get("expenses", []):
                    if exp.get("id") == exp_id:
                        exp["status"] = "paid" if exp.get("status") == "pending" else "pending"
                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "data": data})
            return self.send_json_response({"error": "Expense not found"}, 404)

        # 2. EXPENSES: ADD
        elif self.path == "/api/expenses/add":
            if not month:
                return self.send_json_response({"error": "Month not found"}, 404)

            exp_type = req.get("type", "variable")
            total_inst = int(req.get("totalInstallments", 1))
            curr_inst = int(req.get("currentInstallment", 1))

            if total_inst > 1 and exp_type not in ["card", "installment"]:
                exp_type = "installment"

            new_exp = {
                "id": f"exp-{int(datetime.now().timestamp()*1000)}",
                "person": req.get("person", "Casa"),
                "category": req.get("category", "Geral"),
                "description": req.get("description", "Sem descrição"),
                "amount": float(req.get("amount", 0.0)),
                "dueDate": req.get("dueDate", datetime.now().strftime("%d/%m")),
                "status": req.get("status", "pending"),
                "type": exp_type,
                "totalInstallments": total_inst,
                "currentInstallment": curr_inst,
                "installments": f"{curr_inst}/{total_inst}" if total_inst > 1 else "À vista",
                "subItems": []
            }

            if total_inst > 1:
                inst_entry = {
                    "id": f"inst-{int(datetime.now().timestamp()*1000)}",
                    "person": new_exp["person"],
                    "description": new_exp["description"],
                    "card": f"Cartão {new_exp['person']}" if exp_type == "card" else f"Financiamento / Parcela ({new_exp['person']})",
                    "installmentAmount": new_exp["amount"],
                    "currentInstallment": curr_inst,
                    "totalInstallments": total_inst,
                    "endMonth": f"+{total_inst - curr_inst} meses",
                    "status": "active"
                }
                data.setdefault("futureInstallments", []).append(inst_entry)

            month.setdefault("expenses", []).append(new_exp)
            save_data(data, user_id)
            return self.send_json_response({"success": True, "expense": new_exp, "data": data})

        # 3. EXPENSES: UPDATE (EDIT)
        elif self.path == "/api/expenses/update":
            exp_id = req.get("id")
            if month:
                for exp in month.get("expenses", []):
                    if exp.get("id") == exp_id:
                        exp["description"] = req.get("description", exp.get("description"))
                        exp["amount"] = float(req.get("amount", exp.get("amount")))
                        exp["dueDate"] = req.get("dueDate", exp.get("dueDate"))
                        exp["person"] = req.get("person", exp.get("person"))
                        exp["category"] = req.get("category", exp.get("category"))
                        exp["type"] = req.get("type", exp.get("type"))
                        if "status" in req:
                            exp["status"] = req["status"]
                        if "totalInstallments" in req:
                            exp["totalInstallments"] = int(req.get("totalInstallments", 1))
                            exp["currentInstallment"] = int(req.get("currentInstallment", 1))
                            exp["installments"] = f"{exp['currentInstallment']}/{exp['totalInstallments']}" if exp["totalInstallments"] > 1 else "À vista"
                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "expense": exp, "data": data})
            return self.send_json_response({"error": "Expense not found"}, 404)

        # 4. EXPENSES: DELETE
        elif self.path == "/api/expenses/delete":
            exp_id = req.get("id")
            if month:
                before_len = len(month.get("expenses", []))
                month["expenses"] = [e for e in month.get("expenses", []) if e.get("id") != exp_id]
                if len(month["expenses"]) < before_len:
                    save_data(data, user_id)
                    return self.send_json_response({"success": True, "data": data})
            return self.send_json_response({"error": "Expense not found"}, 404)

        # 5. CARD SUB-ITEM: ADD (Subtópico dentro da Fatura do Cartão)
        elif self.path == "/api/card/subitem/add":
            exp_id = req.get("expenseId")
            if month:
                for exp in month.get("expenses", []):
                    if exp.get("id") == exp_id:
                        total_inst = int(req.get("totalInstallments", 1))
                        curr_inst = int(req.get("currentInstallment", 1))
                        amount = float(req.get("amount", 0.0))
                        new_sub = {
                            "id": f"sub-{int(datetime.now().timestamp()*1000)}",
                            "description": req.get("description", "Item do Cartão"),
                            "amount": amount,
                            "category": req.get("category", "Geral"),
                            "totalInstallments": total_inst,
                            "currentInstallment": curr_inst,
                            "installments": f"{curr_inst}/{total_inst}" if total_inst > 1 else "À vista"
                        }
                        exp.setdefault("subItems", []).append(new_sub)
                        # Recalculate parent invoice total
                        exp["amount"] = round(sum(s.get("amount", 0.0) for s in exp["subItems"]), 2)

                        if total_inst > 1:
                            data.setdefault("futureInstallments", []).append({
                                "id": f"inst-{new_sub['id']}",
                                "subId": new_sub["id"],
                                "expenseId": exp_id,
                                "person": exp.get("person", "Casa"),
                                "description": new_sub["description"],
                                "card": exp.get("description") or f"Cartão {exp.get('person')}",
                                "installmentAmount": amount,
                                "currentInstallment": curr_inst,
                                "totalInstallments": total_inst,
                                "endMonth": f"+{total_inst - curr_inst} meses",
                                "status": "active"
                            })

                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "subItem": new_sub, "expense": exp, "data": data})
            return self.send_json_response({"error": "Card expense not found"}, 404)

        # 6. CARD SUB-ITEM: UPDATE (EDIT)
        elif self.path == "/api/card/subitem/update":
            exp_id = req.get("expenseId")
            sub_id = req.get("subId")
            if month:
                for exp in month.get("expenses", []):
                    if exp.get("id") == exp_id:
                        for s in exp.get("subItems", []):
                            if s.get("id") == sub_id:
                                s["description"] = req.get("description", s["description"])
                                s["amount"] = float(req.get("amount", s["amount"]))
                                s["category"] = req.get("category", s.get("category", "Geral"))
                                total_inst = int(req.get("totalInstallments", s.get("totalInstallments", 1)))
                                curr_inst = int(req.get("currentInstallment", s.get("currentInstallment", 1)))
                                s["totalInstallments"] = total_inst
                                s["currentInstallment"] = curr_inst
                                s["installments"] = f"{curr_inst}/{total_inst}" if total_inst > 1 else "À vista"
                                exp["amount"] = round(sum(x.get("amount", 0.0) for x in exp["subItems"]), 2)

                                # Sync futureInstallments
                                data["futureInstallments"] = [fi for fi in data.get("futureInstallments", []) if fi.get("subId") != sub_id]
                                if total_inst > 1:
                                    data["futureInstallments"].append({
                                        "id": f"inst-{sub_id}",
                                        "subId": sub_id,
                                        "expenseId": exp_id,
                                        "person": exp.get("person", "Casa"),
                                        "description": s["description"],
                                        "card": exp.get("description") or f"Cartão {exp.get('person')}",
                                        "installmentAmount": s["amount"],
                                        "currentInstallment": curr_inst,
                                        "totalInstallments": total_inst,
                                        "endMonth": f"+{total_inst - curr_inst} meses",
                                        "status": "active"
                                    })

                                save_data(data, user_id)
                                return self.send_json_response({"success": True, "subItem": s, "expense": exp, "data": data})
            return self.send_json_response({"error": "Sub-item not found"}, 404)

        # 7. CARD SUB-ITEM: DELETE
        elif self.path == "/api/card/subitem/delete":
            exp_id = req.get("expenseId")
            sub_id = req.get("subId")
            if month:
                for exp in month.get("expenses", []):
                    if exp.get("id") == exp_id:
                        exp["subItems"] = [s for s in exp.get("subItems", []) if s.get("id") != sub_id]
                        exp["amount"] = round(sum(x.get("amount", 0.0) for x in exp["subItems"]), 2)
                        # Remove from futureInstallments
                        data["futureInstallments"] = [fi for fi in data.get("futureInstallments", []) if fi.get("subId") != sub_id]
                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "expense": exp, "data": data})
            return self.send_json_response({"error": "Sub-item not found"}, 404)

        # 8. INCOMES: TOGGLE STATUS (RECEBIDO <-> EM ABERTO)
        elif self.path == "/api/incomes/toggle":
            inc_id = req.get("id")
            if month:
                for inc in month.get("incomes", []):
                    if inc.get("id") == inc_id:
                        inc["status"] = "pending" if inc.get("status") == "received" else "received"
                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "income": inc, "data": data})
            return self.send_json_response({"error": "Income not found"}, 404)

        # 9. INCOMES: ADD (ALLOWS R$ 0.00)
        elif self.path == "/api/incomes/add":
            if not month:
                return self.send_json_response({"error": "Month not found"}, 404)
            amount = float(req.get("amount", 0.0))
            new_inc = {
                "id": f"inc-{int(datetime.now().timestamp()*1000)}",
                "person": req.get("person", "Davi"),
                "description": req.get("description", "Nova Entrada"),
                "amount": amount,
                "category": req.get("category", "Trabalho"),
                "status": req.get("status", "received" if amount > 0 else "pending")
            }
            month.setdefault("incomes", []).append(new_inc)
            save_data(data, user_id)
            return self.send_json_response({"success": True, "income": new_inc, "data": data})

        # 10. INCOMES: UPDATE (ALLOWS R$ 0.00 & SAVES STATUS)
        elif self.path == "/api/incomes/update":
            inc_id = req.get("id")
            if month:
                for inc in month.get("incomes", []):
                    if inc.get("id") == inc_id:
                        inc["description"] = req.get("description", inc.get("description"))
                        inc["amount"] = float(req.get("amount", 0.0))
                        inc["person"] = req.get("person", inc.get("person"))
                        if "category" in req:
                            inc["category"] = req.get("category")
                        if "status" in req:
                            inc["status"] = req["status"]
                        save_data(data, user_id)
                        return self.send_json_response({"success": True, "income": inc, "data": data})
            return self.send_json_response({"error": "Income not found"}, 404)

        # 11. INCOMES: DELETE
        elif self.path == "/api/incomes/delete":
            inc_id = req.get("id")
            if month:
                before_len = len(month.get("incomes", []))
                month["incomes"] = [i for i in month.get("incomes", []) if i.get("id") != inc_id]
                if len(month["incomes"]) < before_len:
                    save_data(data, user_id)
                    return self.send_json_response({"success": True, "data": data})
            return self.send_json_response({"error": "Income not found"}, 404)

        # 12. QUICK ENTRY (SMART MULTI-ITEM SUM ENGINE)
        elif self.path == "/api/quick-entry":
            text = req.get("text", "")
            parsed = smart_parse_text(text)
            auto_commit = req.get("commit", True)
            
            if auto_commit and parsed["amount"] > 0 and month:
                if parsed["isCard"]:
                    # Find card invoice for that person (supports Nathalie / Nat)
                    target_persons = [parsed["person"]]
                    if parsed["person"] in ["Nat", "Nathalie"]:
                        target_persons = ["Nat", "Nathalie"]
                    card_exp = next((e for e in month.get("expenses", []) if e.get("type") == "card" and e.get("person") in target_persons), None)
                    if not card_exp:
                        card_exp = next((e for e in month.get("expenses", []) if e.get("type") == "card"), None)
                    
                    if not card_exp:
                        # Auto-create card invoice for the person if none exists yet
                        card_exp = {
                            "id": f"card-{int(datetime.now().timestamp()*1000)}",
                            "person": parsed["person"],
                            "category": "Cartão de Crédito",
                            "description": f"Fatura Cartão {parsed['person']}",
                            "amount": 0.0,
                            "dueDate": "10",
                            "status": "pending",
                            "type": "card",
                            "subItems": []
                        }
                        month.setdefault("expenses", []).append(card_exp)

                    total_inst = parsed["totalInstallments"]
                    new_sub = {
                        "id": f"sub-{int(datetime.now().timestamp()*1000)}",
                        "description": parsed["description"],
                        "amount": parsed["amount"],
                        "category": parsed["category"],
                        "totalInstallments": total_inst,
                        "currentInstallment": 1,
                        "installments": f"1/{total_inst}" if total_inst > 1 else "À vista"
                    }
                    card_exp.setdefault("subItems", []).append(new_sub)
                    card_exp["amount"] = round(sum(s.get("amount", 0.0) for s in card_exp["subItems"]), 2)
                    save_data(data, user_id)
                    return self.send_json_response({"success": True, "parsed": parsed, "committed": True, "cardSubItem": new_sub, "expense": card_exp, "data": data})

                # If not card, add as regular expense with the summed amount
                new_exp = {
                    "id": f"quick-{int(datetime.now().timestamp()*1000)}",
                    "person": parsed["person"],
                    "category": parsed["category"],
                    "description": parsed["description"],
                    "amount": parsed["amount"],
                    "dueDate": datetime.now().strftime("%d/%m"),
                    "status": "paid",
                    "type": parsed["type"],
                    "subItems": []
                }
                month.setdefault("expenses", []).append(new_exp)
                save_data(data, user_id)
                return self.send_json_response({"success": True, "parsed": parsed, "committed": True, "expense": new_exp, "data": data})
            else:
                return self.send_json_response({"success": True, "parsed": parsed, "committed": False})

        # 13. SETTINGS MONTH
        elif self.path == "/api/settings/month":
            data["activeMonth"] = req.get("activeMonth", "2026-11")
            save_data(data, user_id)
            return self.send_json_response({"success": True, "activeMonth": data["activeMonth"]})

        # 14. MONTH ROLLOVER (VIRAR O MÊS AUTOMATICAMENTE)
        elif self.path == "/api/months/rollover":
            from_month_id = req.get("fromMonthId", data.get("activeMonth", "2026-11"))
            new_month = rollover_month(data, from_month_id)
            if new_month:
                return self.send_json_response({"success": True, "newMonth": new_month, "data": data})
            return self.send_json_response({"error": "Failed to rollover month"}, 500)

        # 15. MONTH DELETE
        elif self.path == "/api/months/delete":
            del_id = req.get("monthId")
            if del_id and len(data.get("months", [])) > 1:
                data["months"] = [m for m in data["months"] if m["id"] != del_id]
                if data.get("activeMonth") == del_id:
                    data["activeMonth"] = data["months"][0]["id"]
                save_data(data, user_id)
                return self.send_json_response({"success": True, "data": data})
            return self.send_json_response({"error": "Cannot delete month"}, 400)

        # 16. SAVINGS BOX: ADD
        elif self.path == "/api/savings/box/add":
            new_box = {
                "id": f"box-{int(datetime.now().timestamp()*1000)}",
                "name": req.get("name", "Nova Caixinha"),
                "category": req.get("category", "Geral"),
                "icon": req.get("icon", "piggy-bank"),
                "color": req.get("color", "emerald"),
                "currentAmount": float(req.get("currentAmount", 0.0)),
                "targetAmount": float(req.get("targetAmount", 1000.0)),
                "notes": req.get("notes", "")
            }
            data.setdefault("savingsBoxes", []).append(new_box)
            save_data(data, user_id)
            return self.send_json_response({"success": True, "box": new_box, "data": data})

        # 17. SAVINGS BOX: UPDATE
        elif self.path == "/api/savings/box/update":
            box_id = req.get("id")
            for box in data.get("savingsBoxes", []):
                if box.get("id") == box_id:
                    box["name"] = req.get("name", box.get("name"))
                    box["category"] = req.get("category", box.get("category"))
                    box["icon"] = req.get("icon", box.get("icon"))
                    box["color"] = req.get("color", box.get("color"))
                    if "currentAmount" in req:
                        box["currentAmount"] = float(req.get("currentAmount", 0.0))
                    if "targetAmount" in req:
                        box["targetAmount"] = float(req.get("targetAmount", 1000.0))
                    box["notes"] = req.get("notes", box.get("notes"))
                    save_data(data, user_id)
                    return self.send_json_response({"success": True, "box": box, "data": data})
            return self.send_json_response({"error": "Box not found"}, 404)

        # 18. SAVINGS BOX: DEPOSIT / WITHDRAW
        elif self.path == "/api/savings/box/deposit":
            box_id = req.get("id")
            amount = float(req.get("amount", 0.0))
            action = req.get("action", "deposit")
            for box in data.get("savingsBoxes", []):
                if box.get("id") == box_id:
                    curr = float(box.get("currentAmount", 0.0))
                    if action == "deposit":
                        box["currentAmount"] = round(curr + amount, 2)
                    else:
                        box["currentAmount"] = max(0.0, round(curr - amount, 2))
                    save_data(data, user_id)
                    return self.send_json_response({"success": True, "box": box, "data": data})
            return self.send_json_response({"error": "Box not found"}, 404)

        # 19. SAVINGS BOX: DELETE
        elif self.path == "/api/savings/box/delete":
            box_id = req.get("id")
            before_len = len(data.get("savingsBoxes", []))
            data["savingsBoxes"] = [b for b in data.get("savingsBoxes", []) if b.get("id") != box_id]
            if len(data["savingsBoxes"]) < before_len:
                save_data(data, user_id)
                return self.send_json_response({"success": True, "data": data})
            return self.send_json_response({"error": "Box not found"}, 404)

        # 20. FULL SAVE
        elif self.path == "/api/save":
            save_data(req)
            return self.send_json_response({"success": True})
        else:
            self.send_response(404)
            self.end_headers()

    def send_json_response(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def generate_analysis(self, data):
        curr_m = next((m for m in data.get("months", []) if m["id"] == data.get("activeMonth", "2026-11")), None)
        if not curr_m:
            return {"leaks": [], "summary": {}}

        total_income = sum(i["amount"] for i in curr_m.get("incomes", []))
        total_expenses = sum(e["amount"] for e in curr_m.get("expenses", []))
        paid_expenses = sum(e["amount"] for e in curr_m.get("expenses", []) if e.get("status") == "paid")
        pending_expenses = total_expenses - paid_expenses
        surplus = total_income - total_expenses

        return {
            "summary": {
                "totalIncome": total_income,
                "totalExpenses": total_expenses,
                "paidExpenses": paid_expenses,
                "pendingExpenses": pending_expenses,
                "projectedSurplus": surplus,
                "targetSavings": data.get("savingsGoal", {}).get("targetAmount", 1000.0)
            }
        }

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    with ThreadingHTTPServer(("0.0.0.0", PORT), FinanceHandler) as httpd:
        print(f"🚀 Servidor do Assessor Financeiro rodando em http://0.0.0.0:{PORT}")
        httpd.serve_forever()
