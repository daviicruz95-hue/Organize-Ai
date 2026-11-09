import re

INDEX_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/public/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Navigation tabs to include "⚡ Débito & PIX"
old_tabs_html = '''      <button onclick="switchTab('caderno')" id="tab-btn-caderno" class="px-4 py-2 rounded-2xl text-xs md:text-sm font-bold bg-[#18191D] text-white shadow-xs transition whitespace-nowrap cursor-pointer">
        Caderno da Casa
      </button>'''

new_tabs_html = '''      <button onclick="switchTab('caderno')" id="tab-btn-caderno" class="px-4 py-2 rounded-2xl text-xs md:text-sm font-bold bg-[#18191D] text-white shadow-xs transition whitespace-nowrap cursor-pointer">
        📑 Caderno de Contas & Faturas
      </button>
      <button onclick="switchTab('debit')" id="tab-btn-debit" class="px-4 py-2 rounded-2xl text-xs md:text-sm font-semibold bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 transition whitespace-nowrap cursor-pointer flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>⚡ Débito & PIX (Dia a Dia)</span>
      </button>'''

assert old_tabs_html in content, "old_tabs_html not found"
content = content.replace(old_tabs_html, new_tabs_html, 1)

# 2. Insert TAB CONTENT for Débito & PIX right after tab-content-caderno
old_tab_caderno_end = '    <!-- TAB 2: CONFERÊNCIA RÁPIDA -->'

debit_tab_html = '''    <!-- TAB: DÉBITO & PIX (GASTOS IMEDIATOS DO DIA A DIA) -->
    <div id="tab-content-debit" class="hidden space-y-6">
      <div class="bg-gradient-to-r from-emerald-50/80 via-white to-sky-50/80 border border-emerald-200/80 rounded-3xl p-5 md:p-6 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-black uppercase tracking-wider text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full">Gastos à Vista</span>
            <span class="text-xs text-slate-500">• Dinheiro que já saiu da conta hoje</span>
          </div>
          <h2 class="text-lg md:text-xl font-extrabold text-slate-900">Acompanhamento de Débito & PIX</h2>
          <p class="text-xs text-slate-600">Almoço na rua, padaria, café, mercado e transferências imediatas sem misturar com faturas de cartão.</p>
        </div>
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <button onclick="openQuickDebitPixModal('Davi', 'pix')" class="flex-1 sm:flex-none px-4 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition flex items-center justify-center gap-1.5 cursor-pointer">
            <span>⚡ + Lançar PIX</span>
          </button>
          <button onclick="openQuickDebitPixModal('Davi', 'debit')" class="flex-1 sm:flex-none px-4 py-2.5 rounded-2xl bg-[#18191D] hover:bg-slate-800 text-white font-bold text-xs shadow-xs transition flex items-center justify-center gap-1.5 cursor-pointer">
            <span>💳 + Lançar Débito</span>
          </button>
        </div>
      </div>

      <!-- TWO COLUMNS: NATHALIE & DAVI DEBIT/PIX -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- NATHALIE DEBIT & PIX -->
        <div class="bg-white border border-slate-200/80 rounded-3xl p-5 md:p-6 shadow-xs space-y-4">
          <div class="pb-3 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-2xl bg-[#F0EDFF] text-[#5B21B6] border border-[#DDD5FE] flex items-center justify-center font-black text-sm">
                N
              </div>
              <div>
                <h3 class="text-sm md:text-base font-bold text-slate-900">Débito & PIX Nathalie</h3>
                <p class="text-[11px] text-slate-500 font-medium">Gastos diários à vista</p>
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs md:text-sm font-black bg-emerald-700 text-white px-3 py-1.5 rounded-xl shadow-xs inline-block" id="totalDebitNat">
                R$ 0,00
              </span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="openQuickDebitPixModal('Nathalie', 'pix')" class="text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 py-2 rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs">
              <span>⚡ + PIX Nathalie</span>
            </button>
            <button onclick="openQuickDebitPixModal('Nathalie', 'debit')" class="text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 py-2 rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs">
              <span>💳 + Débito Nathalie</span>
            </button>
          </div>
          <div id="debitListNat" class="space-y-2.5">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- DAVI DEBIT & PIX -->
        <div class="bg-white border border-slate-200/80 rounded-3xl p-5 md:p-6 shadow-xs space-y-4">
          <div class="pb-3 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-2xl bg-[#EDF5FF] text-[#0369A1] border border-[#BAE6FD] flex items-center justify-center font-black text-sm">
                D
              </div>
              <div>
                <h3 class="text-sm md:text-base font-bold text-slate-900">Débito & PIX Davi</h3>
                <p class="text-[11px] text-slate-500 font-medium">Gastos diários à vista</p>
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs md:text-sm font-black bg-emerald-700 text-white px-3 py-1.5 rounded-xl shadow-xs inline-block" id="totalDebitDavi">
                R$ 0,00
              </span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="openQuickDebitPixModal('Davi', 'pix')" class="text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 py-2 rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs">
              <span>⚡ + PIX Davi</span>
            </button>
            <button onclick="openQuickDebitPixModal('Davi', 'debit')" class="text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 py-2 rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs">
              <span>💳 + Débito Davi</span>
            </button>
          </div>
          <div id="debitListDavi" class="space-y-2.5">
            <!-- Dynamically populated -->
          </div>
        </div>

      </div>
    </div>

    <!-- TAB 2: CONFERÊNCIA RÁPIDA -->'''

assert old_tab_caderno_end in content, "old_tab_caderno_end not found"
content = content.replace(old_tab_caderno_end, debit_tab_html, 1)

# 3. Add 'debit' to switchTab tabs list
old_switch_tabs = "const tabs = ['caderno', 'quickcheck', 'incomes', 'installments', 'charts', 'leaks'];"
new_switch_tabs = "const tabs = ['caderno', 'debit', 'quickcheck', 'incomes', 'installments', 'charts', 'leaks'];"
assert old_switch_tabs in content, "old_switch_tabs not found"
content = content.replace(old_switch_tabs, new_switch_tabs, 1)

# 4. Add renderDebitPix call inside renderAll
old_render_all_marker = "renderQuickCheckList(monthData);"
new_render_all_marker = "renderDebitPix(monthData);\n      renderQuickCheckList(monthData);"
assert old_render_all_marker in content, "old_render_all_marker not found"
content = content.replace(old_render_all_marker, new_render_all_marker, 1)

# 5. Add JS functions for renderDebitPix and openQuickDebitPixModal
target_render_func = '    // RENDER CADERNO COLUMNS (NATHALIE & DAVI)'
debit_pix_functions = '''    // RENDER DÉBITO & PIX TAB (GASTOS IMEDIATOS DO DIA A DIA)
    function renderDebitPix(monthData) {
      const listNat = document.getElementById('debitListNat');
      const listDavi = document.getElementById('debitListDavi');
      if (!listNat || !listDavi) return;
      listNat.innerHTML = '';
      listDavi.innerHTML = '';

      let totalNat = 0;
      let totalDavi = 0;

      const isDebitOrPix = (exp) => {
        const t = (exp.type || '').toLowerCase();
        const desc = (exp.description || '').toLowerCase();
        const cat = (exp.category || '').toLowerCase();
        return t === 'pix' || t === 'debit' || t === 'variável' || t === 'variable' ||
               desc.includes('pix') || desc.includes('débito') || desc.includes('debito') ||
               cat.includes('almoço') || cat.includes('café') || cat.includes('lanche');
      };

      (monthData.expenses || []).forEach(exp => {
        if (exp.type === 'card' || exp.isCard || exp.type === 'fixed' || exp.type === 'recurrent' || exp.type === 'installment') {
          // Skip card invoices and fixed bills here
          return;
        }

        const isPix = (exp.type === 'pix' || (exp.description || '').toLowerCase().includes('pix'));
        const typeBadge = isPix 
          ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-200">⚡ PIX</span>'
          : '<span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-sky-100 text-sky-800 border border-sky-200">💳 DÉBITO</span>';

        const itemHtml = `
          <div class="bg-slate-50/80 border border-slate-200/70 hover:border-slate-300 rounded-2xl p-3.5 transition flex items-center justify-between gap-3">
            <div class="min-w-0 space-y-1">
              <div class="flex items-center gap-2">
                ${typeBadge}
                <span class="text-xs font-bold text-slate-900 truncate">${exp.description}</span>
              </div>
              <div class="text-[11px] text-slate-500 font-medium flex items-center gap-2">
                <span>📁 ${exp.category || 'Geral'}</span>
                <span>• Venc/Pago: ${exp.dueDate || 'Hoje'}</span>
                <span class="text-emerald-700 font-bold">• PAGO</span>
              </div>
            </div>
            <div class="flex items-center gap-2.5 shrink-0">
              <span class="text-xs md:text-sm font-black text-slate-900">${formatBRL(exp.amount)}</span>
              <button onclick="deleteExpense('${exp.id}')" title="Excluir" class="text-slate-400 hover:text-rose-600 transition p-1">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;

        if (exp.person === 'Nathalie') {
          totalNat += (exp.amount || 0);
          listNat.insertAdjacentHTML('beforeend', itemHtml);
        } else {
          totalDavi += (exp.amount || 0);
          listDavi.insertAdjacentHTML('beforeend', itemHtml);
        }
      });

      document.getElementById('totalDebitNat').textContent = formatBRL(totalNat);
      document.getElementById('totalDebitDavi').textContent = formatBRL(totalDavi);

      if (listNat.children.length === 0) {
        listNat.innerHTML = '<div class="py-6 text-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-2xl">Nenhum gasto no débito/pix de Nathalie neste mês.</div>';
      }
      if (listDavi.children.length === 0) {
        listDavi.innerHTML = '<div class="py-6 text-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-2xl">Nenhum gasto no débito/pix de Davi neste mês.</div>';
      }
    }

    function openQuickDebitPixModal(person = 'Davi', type = 'pix') {
      openAddExpenseModal(person);
      onExpenseTypeChange(type);
      document.getElementById('formExpenseDesc').placeholder = type === 'pix' ? "Ex: Almoço na rua, Água, Mercado..." : "Ex: Compras no débito, Farmácia...";
      document.getElementById('formExpenseDueDate').value = new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    }

    // RENDER CADERNO COLUMNS (NATHALIE & DAVI)'''

assert target_render_func in content, "target_render_func not found"
content = content.replace(target_render_func, debit_pix_functions, 1)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Débito & PIX menu and tabs successfully added to index.html!")
