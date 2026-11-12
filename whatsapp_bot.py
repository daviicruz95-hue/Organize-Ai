import json
import re
import os
from datetime import datetime

TEXT_NUMBERS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3, "quatro": 4,
    "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    "quinze": 15, "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50,
    "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100
}

MONTHS_PT = {
    "janeiro": 1, "jan": 1,
    "fevereiro": 2, "fev": 2,
    "marco": 3, "março": 3, "mar": 3,
    "abril": 4, "abr": 4,
    "maio": 5, "mai": 5,
    "junho": 6, "jun": 6,
    "julho": 7, "jul": 7,
    "agosto": 8, "ago": 8,
    "setembro": 9, "set": 9,
    "outubro": 10, "out": 10,
    "novembro": 11, "nov": 11,
    "dezembro": 12, "dez": 12
}

MONTH_NAMES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

class WhatsAppFinancialBot:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def parse_message(self, text, sender_phone="", sender_name="", ref_month_id="2026-11"):
        text_lower = text.lower()

        # Parse reference year and month (default to active month 2026-11)
        try:
            ref_parts = ref_month_id.split("-")
            ref_year = int(ref_parts[0])
            ref_month = int(ref_parts[1])
        except Exception:
            ref_year = datetime.now().year
            ref_month = datetime.now().month

        # 1. Detect person based on phone, sender or content
        person = "Davi"
        if any(k in text_lower for k in ["nat", "nati", "nathalie", "esposa", "mulher"]):
            person = "Nathalie"
        elif "davi" in text_lower or "meu" in text_lower:
            person = "Davi"
        elif sender_name:
            if "nat" in sender_name.lower():
                person = "Nathalie"
            elif "davi" in sender_name.lower():
                person = "Davi"

        # 2. Extract numeric amount
        amount = 0.0

        # Spoken format like "16 e 40", "16 reais e 50 centavos"
        spoken_match = re.search(r'\b(\d+)\s*(?:reais)?\s+e\s+(\d{1,2})\b', text_lower)
        if spoken_match:
            try:
                r = int(spoken_match.group(1))
                c_str = spoken_match.group(2)
                c = int(c_str) if len(c_str) == 2 else int(c_str) * 10
                amount = float(f"{r}.{c:02d}")
            except Exception:
                pass

        # Installment format like "3x de 50", "3x de 50,00", "2 vezes de 45"
        if amount == 0.0:
            inst_amount_match = re.search(r'\b\d{1,2}\s*(?:x|vezes)\s+de\s+(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)', text_lower)
            if inst_amount_match:
                try:
                    candidate = float(inst_amount_match.group(1).replace(',', '.'))
                    if candidate > 0:
                        amount = candidate
                except ValueError:
                    pass

        if amount == 0.0:
            # Check text numbers (e.g. "quatro reais")
            for word, val in TEXT_NUMBERS.items():
                if re.search(rf'\b{word}\s*(?:reais|real)?\b', text_lower):
                    amount = float(val)
                    break

        if amount == 0.0:
            # Check numeric digits (e.g. "4 reais", "R$ 4,50", "68,79", "45.00")
            amount_match = re.search(r'(?:r\$\s*|reais\s*|\b)?(\d+(?:[.,]\d{1,2})?)\s*(?:reais|real|\b)?', text_lower)
            if amount_match:
                try:
                    candidate = float(amount_match.group(1).replace(',', '.'))
                    if candidate > 0:
                        amount = candidate
                except ValueError:
                    pass

        # 3. Detect payment method (Pix, Débito, Crédito, Fixa)
        is_pix = bool(re.search(r'\b(pix|chave|qr|qrcode)\b', text_lower))
        is_debit = bool(re.search(r'\b(debito|débito|devido|deb|maquininha)\b', text_lower))
        is_card = bool(re.search(r'\b(credito|crédito|cartao|cartão|fatura|parcela|parcelado)\b', text_lower))
        is_fixed = bool(re.search(r'\b(fixa|fixo|recorrente|mensal|aluguel|condominio|condomínio|internet|copasa|enel|conta\s+de\s+luz|conta\s+de\s+agua|plano)\b', text_lower))

        if is_pix:
            pay_type = "pix"
        elif is_debit:
            pay_type = "debit"
        elif is_card:
            pay_type = "card"
        elif is_fixed:
            pay_type = "fixed"
        else:
            pay_type = "debit"

        # 4. Detect Installments (e.g. "em 3x", "3 parcelas", "2x")
        total_installments = 1
        inst_match = re.search(r'\b(?:em\s+)?(\d{1,2})\s*x\b|\b(?:em\s+)?(\d{1,2})\s+parcelas?\b', text_lower)
        if inst_match:
            try:
                g = inst_match.group(1) or inst_match.group(2)
                if g and int(g) > 1:
                    total_installments = int(g)
                    pay_type = "card" # Installments imply credit card
            except Exception:
                pass

        # 5. Detect Target Month / Invoice Month
        # If user specifies: "para a fatura de dezembro", "fatura de dezembro", "para dezembro", "mês que vem", etc.
        target_month_id = None
        target_month_name = None
        target_year = ref_year

        is_next_month = bool(re.search(r'\b(?:fatura\s+(?:do\s+)?m[eê]s\s+que\s+vem|m[eê]s\s+que\s+vem|pr[oó]ximo\s+m[eê]s|pr[oó]xima\s+fatura)\b', text_lower))
        if is_next_month:
            if ref_month == 12:
                t_m = 1
                t_y = ref_year + 1
            else:
                t_m = ref_month + 1
                t_y = ref_year
            target_month_id = f"{t_y}-{t_m:02d}"
            target_month_name = MONTH_NAMES_PT[t_m]
            target_year = t_y
        else:
            # Check explicit month names
            for m_key, m_num in MONTHS_PT.items():
                pattern = rf'\b(?:para\s+(?:a\s+)?fatura\s+(?:de\s+)?|pra\s+fatura\s+(?:de\s+)?|fatura\s+(?:de\s+)?|pro\s+m[eê]s\s+(?:de\s+)?|no\s+m[eê]s\s+(?:de\s+)?|para\s+|pra\s+|em\s+)?{m_key}\b'
                if re.search(pattern, text_lower):
                    # Make sure it is tied to financial context or invoice
                    if any(k in text_lower for k in ['fatura', 'para', 'pra', 'mês', 'mes', 'em', 'crédito', 'credito', 'cartão', 'cartao', 'fatura']):
                        y_match = re.search(rf'\b{m_key}\s+(?:de\s+)?(\d{{4}})\b', text_lower)
                        if y_match:
                            t_y = int(y_match.group(1))
                        else:
                            t_y = ref_year + 1 if m_num < ref_month else ref_year
                        target_month_id = f"{t_y}-{m_num:02d}"
                        target_month_name = MONTH_NAMES_PT[m_num]
                        target_year = t_y
                        break

        # 6. Detect Category
        if any(w in text_lower for w in ["igreja", "churrasco da igreja", "dizimo", "dízimo", "oferta", "doacao", "doação"]):
            category = "Dízimo / Doações"
        elif any(w in text_lower for w in ["uber", "99", "corrida", "gasolina", "combustivel", "combustível", "estacionamento", "estapar", "moto", "posto", "pedagio", "pedágio"]):
            category = "Transporte"
        elif any(w in text_lower for w in ["agua", "água", "almoco", "almoço", "jantar", "comida", "mercado", "lanche", "padaria", "cafe", "café", "cerveja", "ifood", "pizza", "restaurante", "chocolate", "doce", "bombom", "sorvete", "açai", "açaí", "sushi", "hamburguer", "hambúrguer", "supermercado", "hortifruti", "açougue", "acougue"]):
            category = "Alimentação"
        elif any(w in text_lower for w in ["farmacia", "farmácia", "remedio", "remédio", "dentista", "medico", "médico", "academia", "psicologo", "psicólogo", "exame", "consulta", "hospital", "otica", "ótica"]):
            category = "Saúde & Bem-Estar"
        elif any(w in text_lower for w in ["luz", "agua copasa", "copasa", "condominio", "condomínio", "aluguel", "internet", "claro", "vivo", "tim", "iptu", "lixo"]):
            category = "Habitação"
        elif any(w in text_lower for w in ["cinema", "praia", "passeio", "futebol", "jogo", "show", "viagem", "hotel", "lazer"]):
            category = "Lazer"
        else:
            category = "Variável"

        # 7. Clean description (Extract exact item/place without fillers)
        cleaned = text
        patterns = [
            r'\b(?:fala\s+)?(?:z[eé]ca|zeck|zac|jack)\b',
            r'\b(?:caderno\s+(?:do\s+|da\s+)?(?:davi|nati|nathalie)|caderno)\b',
            r'\b(?:comprei|paguei|gastei|mandei|peguei|compra|compras|despesa|gasto|lan[cç]a|registra|anota|coloca|botei|bota|anote)\s*(?:um|uma|o|a|os|as)?\b',
            r'\b(?:para\s+(?:a\s+)?fatura\s+(?:de\s+)?|pra\s+fatura\s+(?:de\s+)?|fatura\s+(?:de\s+)?|fatura\s+(?:do\s+)?m[eê]s\s+que\s+vem|m[eê]s\s+que\s+vem|pr[oó]ximo\s+m[eê]s|pr[oó]xima\s+fatura|fatura)\b',
            r'\b(?:pro\s+m[eê]s\s+(?:de\s+)?|no\s+m[eê]s\s+(?:de\s+)?)\b',
            r'\b(?:janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)(?:\s+(?:de\s+)?\d{4})?\b',
            r'\b(?:foi\s+)?(?:no|na|de|em|pelo|pela|via)\s+(?:d[eé]bito|devido|pix|cr[eé]dito|cart[aã]o)\b',
            r'\b(?:no\s+)?(?:d[eé]bito|devido|pix|cr[eé]dito|cart[aã]o)\b',
            r'\b(?:à\s+vista|a\s+vista|parcelado|parcela|parcelas)\b',
            r'\b(?:em\s+\d+x|\d+x)\b',
            r'\b(?:foi|deu|custou|por)\b',
            r'\b(?:aqui|a[ií]|tamb[eé]m|por\s+favor|pra\s+mim)\b',
            r'\b(?:reais|real|r\$)\b',
            r'\b\d+(?:[.,]\d+)?\b',
            r'\b\d+\s+e\s+\d+\b'
        ]
        for p in patterns:
            cleaned = re.sub(p, ' ', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'[,.\-–—:;!?]+', ' ', cleaned).strip()
        for _ in range(3):
            cleaned = re.sub(r'^\s*(?:um|uma|o|a|os|as|de|do|da|dos|das|e|na|no|em|pra|para)\s+', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s+(?:um|uma|o|a|os|as|de|do|da|dos|das|e|na|no|em|pra|para)\s*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Format and capitalize nicely
        if cleaned and len(cleaned) >= 2:
            words = cleaned.split()
            cap_words = []
            for i, w in enumerate(words):
                if i > 0 and w.lower() in ['de', 'do', 'da', 'dos', 'das', 'e', 'em', 'no', 'na', 'nos', 'nas']:
                    cap_words.append(w.lower())
                else:
                    cap_words.append(w.capitalize())
            cleaned = ' '.join(cap_words)
        else:
            cleaned = f"Gasto {category}"

        return {
            "valid": amount > 0.0,
            "description": cleaned,
            "amount": round(amount, 2),
            "category": category,
            "type": pay_type,
            "person": person,
            "status": "paid" if pay_type in ["pix", "debit", "variable"] else "pending",
            "dueDate": datetime.now().strftime("%d/%m"),
            "target_month_id": target_month_id,
            "target_month_name": target_month_name,
            "target_year": target_year,
            "totalInstallments": total_installments,
            "currentInstallment": 1,
            "installments": f"1/{total_installments}" if total_installments > 1 else "À vista"
        }

    def generate_reply(self, parsed, active_month_name="Novembro", current_balance=None):
        if not parsed or parsed.get("amount", 0) <= 0 or not parsed.get("valid", True):
            return None

        person_name = "Nati" if "nat" in parsed['person'].lower() else "Davi"

        def fmt_brl(val):
            if val is None:
                return "0,00"
            try:
                return f"{float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(val)

        amt_str = fmt_brl(parsed['amount'])

        if parsed["type"] == "pix":
            type_icon = "⚡ PIX (No Caderno)"
            status_text = f"Pago no ato ({parsed['dueDate']})"
            reply = (
                f"✅ *Lançado com sucesso no Organize Aí!*\n\n"
                f"👤 *Caderno:* {person_name}\n"
                f"📝 *Item:* {parsed['description']}\n"
                f"💰 *Valor:* R$ {amt_str}\n"
                f"🏷️ *Forma:* {type_icon}\n"
                f"📁 *Categoria:* {parsed['category']}\n"
                f"📅 *Status:* {status_text}"
            )
            if current_balance is not None:
                reply += f"\n🏦 *Saldo em Conta:* R$ {fmt_brl(current_balance)}"
            return reply
        elif parsed["type"] == "debit":
            type_icon = "💳 Débito (No Caderno)"
            status_text = f"Pago no ato ({parsed['dueDate']})"
            reply = (
                f"✅ *Lançado com sucesso no Organize Aí!*\n\n"
                f"👤 *Caderno:* {person_name}\n"
                f"📝 *Item:* {parsed['description']}\n"
                f"💰 *Valor:* R$ {amt_str}\n"
                f"🏷️ *Forma:* {type_icon}\n"
                f"📁 *Categoria:* {parsed['category']}\n"
                f"📅 *Status:* {status_text}"
            )
            if current_balance is not None:
                reply += f"\n🏦 *Saldo em Conta:* R$ {fmt_brl(current_balance)}"
            return reply
        elif parsed["type"] == "fixed":
            type_icon = "📌 Conta Fixa (No Caderno)"
            status_text = f"A vencer ({parsed['dueDate']})"
            reply = (
                f"✅ *Lançado com sucesso no Organize Aí!*\n\n"
                f"👤 *Caderno:* {person_name}\n"
                f"📝 *Item:* {parsed['description']}\n"
                f"💰 *Valor:* R$ {amt_str}\n"
                f"🏷️ *Forma:* {type_icon}\n"
                f"📁 *Categoria:* {parsed['category']}\n"
                f"📅 *Status:* {status_text}"
            )
            if current_balance is not None:
                reply += f"\n🏦 *Saldo em Conta Atual:* R$ {fmt_brl(current_balance)}"
            return reply
        else:
            # Credit Card purchase
            inv_name = parsed.get("target_month_name") or active_month_name
            inv_year = parsed.get("target_year") or 2026
            inv_label = f"{inv_name}/{inv_year}"
            inst_label = parsed.get("installments", "À vista")

            reply = (
                f"✅ *Lançado com sucesso no Organize Aí!*\n\n"
                f"👤 *Caderno:* {person_name}\n"
                f"📝 *Item:* {parsed['description']}\n"
                f"💰 *Valor:* R$ {amt_str}\n"
                f"🏷️ *Forma:* 💳 Cartão de Crédito\n"
                f"📅 *Fatura:* {inv_label}\n"
                f"📁 *Categoria:* {parsed['category']}\n"
                f"📊 *Parcelamento:* {inst_label}"
            )
            return reply

if __name__ == "__main__":
    bot = WhatsAppFinancialBot()
    test_cases = [
        "Zeca, quatro reais na água no Pix",
        "Mandei 50 no Pix pro churrasco da igreja",
        "Almoço na rua 45 no débito",
        "Farmácia 38.90 no cartão",
        "compra no crédito para a fatura de dezembro 68,79 na farmácia",
        "farmácia 68,79 no crédito para dezembro",
        "compra no crédito em 3x de 50 no mercado para a fatura de janeiro"
    ]
    print("--- TESTES DE PROCESSAMENTO DO ROBÔ ---")
    for tc in test_cases:
        res = bot.parse_message(tc, sender_name="Davi")
        print("\nInput:", tc)
        print("Reply:\n" + bot.generate_reply(res))
