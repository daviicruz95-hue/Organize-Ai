import re

INDEX_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/public/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert Pairing section in Profile Modal
target_modal_buttons = '      <div class="pt-3 border-t border-slate-100 flex flex-col gap-2">\n        <button type="button" onclick="saveProfileSettings()"'

pairing_ui = '''        <!-- CONTA CONJUNTA (VINCULAR CASAL) -->
        <div class="pt-3 border-t border-slate-100 space-y-2">
          <div class="flex items-center justify-between">
            <label class="font-bold text-slate-800 text-xs flex items-center gap-1.5">
              <span>💍</span>
              <span>Conta Conjunta (Casal)</span>
            </label>
            <span id="pairStatusBadge" class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Conectada</span>
          </div>
          <p class="text-[11px] text-slate-500 leading-snug">
            Compartilhe cadernos, faturas e caixinhas com seu parceiro(a) em tempo real sem precisar usar o mesmo e-mail.
          </p>
          <div class="flex gap-2">
            <input type="email" id="formPartnerEmail" placeholder="E-mail do parceiro(a)" class="flex-1 bg-slate-50 border border-slate-200 focus:bg-white rounded-xl px-3 py-2 text-slate-800 text-xs focus:outline-none font-medium">
            <button type="button" onclick="pairPartnerAccount()" id="btnPairPartner" class="px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-xs transition shrink-0 cursor-pointer">
              Vincular
            </button>
          </div>
          <div id="pairInfo" class="text-[11px] text-purple-900 font-semibold bg-purple-50 p-2.5 rounded-xl border border-purple-100/80">
            ✨ Davi & Nathalie compartilham este mesmo painel familiar.
          </div>
        </div>
      </div>

      <div class="pt-3 border-t border-slate-100 flex flex-col gap-2">
        <button type="button" onclick="saveProfileSettings()"'''

assert target_modal_buttons in content, "target_modal_buttons not found"
content = content.replace(target_modal_buttons, pairing_ui, 1)

# 2. Add pairPartnerAccount function
target_logout = '    function logoutUser() {'
pairing_js = '''    async function pairPartnerAccount() {
      const email = document.getElementById('formPartnerEmail').value.trim();
      if (!email) {
        alert("Por favor, digite o e-mail do seu parceiro(a) para vincular.");
        return;
      }
      const btn = document.getElementById('btnPairPartner');
      const msg = document.getElementById('profileMsg');
      btn.disabled = true;
      btn.innerText = 'Vinculando...';

      try {
        const res = await fetch('/api/auth/pair', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ partnerEmail: email })
        });
        const data = await res.json();
        if (data.success) {
          msg.textContent = `✅ ${data.message}`;
          msg.className = 'p-2.5 rounded-xl text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 block text-center';
          document.getElementById('pairInfo').textContent = `✨ Vinculado com ${data.partner ? data.partner.name : email}! Finanças unificadas.`;
          await fetchAppData();
        } else {
          msg.textContent = data.error || 'Erro ao vincular conta.';
          msg.className = 'p-2.5 rounded-xl text-xs font-bold text-rose-800 bg-rose-50 border border-rose-200 block text-center';
        }
      } catch (err) {
        msg.textContent = 'Erro ao conectar ao servidor.';
        msg.className = 'p-2.5 rounded-xl text-xs font-bold text-rose-800 bg-rose-50 border border-rose-200 block text-center';
      } finally {
        btn.disabled = false;
        btn.innerText = 'Vincular';
      }
    }

    function logoutUser() {'''

assert target_logout in content, "target_logout not found"
content = content.replace(target_logout, pairing_js, 1)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Pairing UI and JS successfully added to index.html!")
