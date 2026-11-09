import re

INDEX_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/public/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert User Profile button in Header right before Quick Entry
target_header = '        <!-- Quick Entry Trigger (High-contrast Dark Pill) -->'
user_pill = '''        <!-- User Profile Pill -->
        <button onclick="openProfileModal()" id="btnUserProfile" title="Configurações da Conta e Perfil" class="flex items-center gap-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 text-xs font-bold px-2.5 py-1.5 md:px-3 md:py-2 rounded-2xl shadow-xs transition active:scale-95 cursor-pointer">
          <div id="userAvatarPill" class="w-6 h-6 rounded-full bg-[#18191D] text-white flex items-center justify-center text-[10px] font-black uppercase">
            D
          </div>
          <span id="userNamePill" class="hidden sm:inline max-w-[110px] truncate">Davi & Nathalie</span>
          <i data-lucide="settings" class="w-3.5 h-3.5 text-slate-400"></i>
        </button>

        <!-- Quick Entry Trigger (High-contrast Dark Pill) -->'''

assert target_header in content, "target_header not found in index.html"
content = content.replace(target_header, user_pill, 1)

# 2. Insert Profile Modal before the JS core logic
target_modal_end = '  <!-- 5. RECORD PAYMENT MODAL -->'
profile_modal_html = '''  <!-- 8. USER PROFILE & SETTINGS MODAL -->
  <div id="profileModal" class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 hidden">
    <div class="bg-white border border-slate-200 rounded-3xl shadow-2xl p-6 sm:p-7 max-w-sm w-full space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 pb-3">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-2xl bg-[#F0EDFF] text-[#5B21B6] flex items-center justify-center text-lg">
            ⚙️
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-900">Configurações da Conta</h3>
            <p class="text-[11px] text-slate-500">Seus dados e segurança no Organize Aí</p>
          </div>
        </div>
        <button onclick="closeProfileModal()" class="w-7 h-7 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition cursor-pointer">
          <i data-lucide="x" class="w-3.5 h-3.5"></i>
        </button>
      </div>

      <div id="profileMsg" class="hidden p-2.5 rounded-xl text-xs font-semibold text-center"></div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">Nome / Identificação</label>
          <input type="text" id="formProfileName" placeholder="Ex: Davi & Nathalie" class="w-full bg-slate-50 border border-slate-200 focus:bg-white rounded-xl px-3 py-2 text-slate-800 font-semibold focus:outline-none">
        </div>
        <div>
          <label class="font-bold text-slate-700 block mb-1">E-mail</label>
          <input type="email" id="formProfileEmail" placeholder="seu@email.com" class="w-full bg-slate-50 border border-slate-200 focus:bg-white rounded-xl px-3 py-2 text-slate-800 focus:outline-none">
        </div>
        <div>
          <label class="font-bold text-slate-700 block mb-1">Alterar Senha</label>
          <div class="relative">
            <input type="password" id="formProfilePassword" placeholder="Deixe em branco para manter" class="w-full bg-slate-50 border border-slate-200 focus:bg-white rounded-xl px-3 py-2 pr-9 text-slate-800 focus:outline-none">
            <button type="button" onclick="togglePasswordVisibility('formProfilePassword', 'profileEyeIcon')" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 text-xs p-1">
              <span id="profileEyeIcon">👁️</span>
            </button>
          </div>
        </div>
      </div>

      <div class="pt-3 border-t border-slate-100 flex flex-col gap-2">
        <button type="button" onclick="saveProfileSettings()" id="btnSaveProfile" class="w-full py-2.5 rounded-xl font-bold text-xs bg-[#18191D] hover:bg-slate-800 text-white shadow-xs transition cursor-pointer">
          Salvar Alterações
        </button>
        <button type="button" onclick="logoutUser()" class="w-full py-2 rounded-xl font-bold text-xs text-rose-600 hover:bg-rose-50 border border-rose-200 transition cursor-pointer flex items-center justify-center gap-1.5">
          <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
          <span>Desconectar / Sair da Conta</span>
        </button>
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT APPLICATION CORE LOGIC -->'''

assert target_modal_end in content, "target_modal_end not found"
content = content.replace(target_modal_end, profile_modal_html, 1)

# 3. Add window.fetch interceptor and User profile functions at the start of JS
target_js_start = '    let appData = null;'
new_js_auth = '''    // CURRENT LOGGED IN USER & SESSION MANAGEMENT
    let currentUser = null;
    try {
      const stored = localStorage.getItem('organizeai_user');
      if (stored) currentUser = JSON.parse(stored);
    } catch (e) {}

    if (!currentUser) {
      // Default to master Davi & Nathalie account if accessing directly
      currentUser = { id: "user-davi", name: "Davi & Nathalie", email: "davi@organizeai.com" };
      localStorage.setItem('organizeai_user', JSON.stringify(currentUser));
      localStorage.setItem('organizeai_token', currentUser.id);
    }

    // AUTOMATIC FETCH WRAPPER: Attaches X-User-Id to all API requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
      if (typeof url === 'string' && url.startsWith('/api')) {
        options = options || {};
        options.headers = options.headers || {};
        const userId = currentUser ? currentUser.id : 'user-davi';
        if (options.headers instanceof Headers) {
          options.headers.set('X-User-Id', userId);
        } else {
          options.headers['X-User-Id'] = userId;
        }
      }
      return originalFetch(url, options);
    };

    function togglePasswordVisibility(inputId, iconId) {
      const input = document.getElementById(inputId);
      const icon = document.getElementById(iconId);
      if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
      } else {
        input.type = 'password';
        icon.textContent = '👁️';
      }
    }

    function syncUserPill() {
      if (!currentUser) return;
      const namePill = document.getElementById('userNamePill');
      const avatarPill = document.getElementById('userAvatarPill');
      if (namePill) namePill.textContent = currentUser.name || 'Minha Conta';
      if (avatarPill) avatarPill.textContent = (currentUser.name || 'D').charAt(0).toUpperCase();
    }

    function openProfileModal() {
      if (!currentUser) return;
      document.getElementById('formProfileName').value = currentUser.name || '';
      document.getElementById('formProfileEmail').value = currentUser.email || '';
      document.getElementById('formProfilePassword').value = '';
      const msg = document.getElementById('profileMsg');
      msg.className = 'hidden';
      document.getElementById('profileModal').classList.remove('hidden');
    }

    function closeProfileModal() {
      document.getElementById('profileModal').classList.add('hidden');
    }

    async function saveProfileSettings() {
      const name = document.getElementById('formProfileName').value.trim();
      const email = document.getElementById('formProfileEmail').value.trim();
      const password = document.getElementById('formProfilePassword').value.trim();
      const btn = document.getElementById('btnSaveProfile');
      const msg = document.getElementById('profileMsg');

      btn.disabled = true;
      btn.innerText = 'Salvando...';

      try {
        const res = await fetch('/api/auth/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (data.success && data.user) {
          currentUser = data.user;
          localStorage.setItem('organizeai_user', JSON.stringify(currentUser));
          syncUserPill();
          msg.textContent = '✅ Dados atualizados com sucesso!';
          msg.className = 'p-2.5 rounded-xl text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 block text-center';
          setTimeout(() => closeProfileModal(), 1200);
        } else {
          msg.textContent = data.error || 'Erro ao salvar alterações.';
          msg.className = 'p-2.5 rounded-xl text-xs font-bold text-rose-800 bg-rose-50 border border-rose-200 block text-center';
        }
      } catch (e) {
        msg.textContent = 'Erro ao conectar ao servidor.';
        msg.className = 'p-2.5 rounded-xl text-xs font-bold text-rose-800 bg-rose-50 border border-rose-200 block text-center';
      } finally {
        btn.disabled = false;
        btn.innerText = 'Salvar Alterações';
      }
    }

    function logoutUser() {
      if (confirm('Deseja realmente sair da sua conta?')) {
        localStorage.removeItem('organizeai_user');
        localStorage.removeItem('organizeai_token');
        window.location.href = '/';
      }
    }

    let appData = null;'''

assert target_js_start in content, "target_js_start not found"
content = content.replace(target_js_start, new_js_auth, 1)

# Add syncUserPill call in window load
content = content.replace("await fetchAppData();", "syncUserPill();\n      await fetchAppData();", 1)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html upgraded with Profile Modal, User Pill, and automatic X-User-Id header!")
