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

class WhatsAppFinancialBot:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def parse_message(self, text, sender_phone="", sender_name=""):
        text_lower = text.lower()

        # 1. Detect person based on phone, sender or content
        person = "Davi"
        if "nat" in text_lower or "nathalie" in text_lower or "esposa" in text_lower or "mulher" in text_lower:
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

        # Check spoken format like "16 e 40", "16 reais e 50 centavos"
        spoken_match = re.search(r'\b(\d+)\s*(?:reais)?\s+e\s+(\d{1,2})\b', text_lower)
        if spoken_match:
            try:
                r = int(spoken_match.group(1))
                c_str = spoken_match.group(2)
                c = int(c_str) if len(c_str) == 2 else int(c_str) * 10
                amount = float(f"{r}.{c:02d}")
            except Exception:
                pass

        if amount == 0.0:
            # Check text numbers (e.g. "quatro reais")
            for word, val in TEXT_NUMBERS.items():
                if re.search(rf'\b{word}\s*(?:reais|real)?\b', text_lower):
                    amount = float(val)
                    break

        if amount == 0.0:
            # Check numeric digits (e.g. "4 reais", "R$ 4,50", "45.00")
            amount_match = re.search(r'(?:r\$\s*|reais\s*|\b)?(\d+(?:[.,]\d{1,2})?)\s*(?:reais|real|\b)?', text_lower)
            if amount_match:
                try:
                    candidate = float(amount_match.group(1).replace(',', '.'))
                    if candidate > 0:
                        amount = candidate
                except ValueError:
                    pass

        # 3. Detect payment method (Pix, Débito, Crédito, Fixa)
        is_fixed = bool(re.search(r'\b(fixa|fixo|recorrente|mensal|aluguel|condominio|condomínio|internet|copasa|enel|luz|agua|água|plano)\b', text_lower))
        is_pix = bool(re.search(r'\b(pix|chave|qr|qrcode)\b', text_lower))
        is_debit = bool(re.search(r'\b(debito|débito|devido|deb|maquininha)\b', text_lower))
        is_card = bool(re.search(r'\b(credito|crédito|cartao|cartão|fatura|parcela)\b', text_lower))

        if is_fixed:
            pay_type = "fixed"
        elif is_pix:
            pay_type = "pix"
        elif is_debit:
            pay_type = "debit"
        elif is_card:
            pay_type = "card"
        else:
            pay_type = "debit"

        # 4. Detect Category
        if any(w in text_lower for w in ["igreja", "churrasco da igreja", "dizimo", "dízimo", "oferta", "doacao", "doação"]):
            category = "Dízimo / Doações"
        elif any(w in text_lower for w in ["uber", "99", "corrida", "gasolina", "combustivel", "combustível", "estacionamento", "estapar", "moto"]):
            category = "Transporte"
        elif any(w in text_lower for w in ["agua", "água", "almoco", "almoço", "jantar", "comida", "mercado", "lanche", "padaria", "cafe", "café", "cerveja", "ifood", "pizza", "restaurante", "chocolate", "doce", "bombom", "sorvete", "açai", "açaí"]):
            category = "Alimentação"
        elif any(w in text_lower for w in ["farmacia", "farmácia", "remedio", "remédio", "dentista", "medico", "médico", "academia"]):
            category = "Saúde & Bem-Estar"
        elif any(w in text_lower for w in ["luz", "agua copasa", "condominio", "condomínio", "aluguel", "internet"]):
            category = "Habitação"
        else:
            category = "Variável"

        # 5. Clean description (Extract exact item/place without fillers)
        cleaned = text
        patterns = [
            r'\b(?:fala\s+)?(?:z[eé]ca|zeck|zac|jack)\b',
            r'\b(?:comprei|paguei|gastei|mandei|peguei)\s*(?:um|uma|o|a|os|as)?\b',
            r'\b(?:anota|registra|lan[cç]a|coloca)\s*(?:a[ií]|aqui)?\b',
            r'\b(?:foi\s+)?no\s+(?:d[eé]bito|devido|pix|cr[eé]dito|cart[aã]o)\b',
            r'\b(?:no\s+)?(?:d[eé]bito|devido|pix|cr[eé]dito|cart[aã]o)\b',
            r'\b(?:foi|deu|custou|por)\b',
            r'\b(?:aqui|tamb[eé]m|por\s+favor)\b',
            r'\b(?:reais|real|r\$)\b',
            r'\b\d+(?:[.,]\d+)?\b',
            r'\b\d+\s+e\s+\d+\b'
        ]
        for p in patterns:
            cleaned = re.sub(p, ' ', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'[,.\-–—:;!?]+', ' ', cleaned).strip()
        cleaned = re.sub(r'^\s*(?:um|uma|o|a|os|as|de|do|da|e)\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+(?:um|uma|o|a|os|as|de|do|da|e)\s*$', '', cleaned, flags=re.IGNORECASE)
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
            "dueDate": datetime.now().strftime("%d/%m")
        }

    def generate_reply(self, parsed):
        if not parsed or parsed.get("amount", 0) <= 0 or not parsed.get("valid", True):
            return None
        if parsed["type"] == "pix":
            type_icon = "⚡ PIX (No Caderno)"
        elif parsed["type"] == "debit":
            type_icon = "💳 Débito (No Caderno)"
        elif parsed["type"] == "fixed":
            type_icon = "📌 Conta Fixa (No Caderno)"
        else:
            type_icon = "💳 Cartão de Crédito"

        person_name = "Nati" if "nat" in parsed['person'].lower() else "Davi"
        status_text = f"Pago no ato ({parsed['dueDate']})" if parsed['status'] == 'paid' else f"A vencer ({parsed['dueDate']})"
        return (
            f"✅ *Lançado com sucesso no Organize Aí!*\n\n"
            f"👤 *Caderno:* {person_name}\n"
            f"📝 *Item:* {parsed['description']}\n"
            f"💰 *Valor:* R$ {parsed['amount']:.2f}\n"
            f"🏷️ *Forma:* {type_icon}\n"
            f"📁 *Categoria:* {parsed['category']}\n"
            f"📅 *Status:* {status_text}"
        )

if __name__ == "__main__":
    bot = WhatsAppFinancialBot()
    test_cases = [
        "Zeca, quatro reais na água no Pix",
        "Mandei 50 no Pix pro churrasco da igreja",
        "Almoço na rua 45 no débito",
        "Farmácia 38.90 no cartão"
    ]
    print("--- TESTES DE PROCESSAMENTO DO ROBÔ ---")
    for tc in test_cases:
        res = bot.parse_message(tc, sender_name="Davi")
        print("\nInput:", tc)
        print("Reply:\n" + bot.generate_reply(res))
