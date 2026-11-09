import re

INDEX_PATH = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/public/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the grid of buttons in expenseModal
old_type_grid = '''          <div class="grid grid-cols-2 gap-2">
            <button type="button" onclick="onExpenseTypeChange('fixed')" id="btnExpenseTypeFixa" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-[#18191D] text-white text-left transition cursor-pointer">
              <span class="block text-xs">📌 Conta Fixa</span>
              <span class="text-[10px] font-normal opacity-80 block">Luz, condomínio, internet</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('recurrent')" id="btnExpenseTypeRecorrente" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">🔄 Recorrente</span>
              <span class="text-[10px] font-normal text-slate-500 block">Assinatura, academia, MEI</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('installment')" id="btnExpenseTypeParcela" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">🔢 Parcela</span>
              <span class="text-[10px] font-normal text-slate-500 block">Financiamento (ex: 18/36)</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('variable')" id="btnExpenseTypeAvulsa" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">⚡ Gasto Avulso</span>
              <span class="text-[10px] font-normal text-slate-500 block">Gasto único deste mês</span>
            </button>
          </div>'''

new_type_grid = '''          <div class="grid grid-cols-2 gap-2">
            <button type="button" onclick="onExpenseTypeChange('pix')" id="btnExpenseTypePix" class="p-2.5 rounded-xl font-bold border border-emerald-300 bg-emerald-50 text-emerald-950 text-left transition cursor-pointer">
              <span class="block text-xs">⚡ PIX (À Vista)</span>
              <span class="text-[10px] font-medium text-emerald-700 block">Almoço, padaria, saída</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('debit')" id="btnExpenseTypeDebito" class="p-2.5 rounded-xl font-bold border border-sky-300 bg-sky-50 text-sky-950 text-left transition cursor-pointer">
              <span class="block text-xs">💳 Débito (À Vista)</span>
              <span class="text-[10px] font-medium text-sky-700 block">Direto da conta no ato</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('fixed')" id="btnExpenseTypeFixa" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">📌 Conta Fixa</span>
              <span class="text-[10px] font-normal opacity-80 block">Luz, condomínio, aluguel</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('recurrent')" id="btnExpenseTypeRecorrente" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">🔄 Recorrente</span>
              <span class="text-[10px] font-normal text-slate-500 block">Assinatura, academia, MEI</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('installment')" id="btnExpenseTypeParcela" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">🔢 Parcela</span>
              <span class="text-[10px] font-normal text-slate-500 block">Financiamento (ex: 18/36)</span>
            </button>
            <button type="button" onclick="onExpenseTypeChange('variable')" id="btnExpenseTypeAvulsa" class="p-2.5 rounded-xl font-bold border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 text-left transition cursor-pointer">
              <span class="block text-xs">🏷️ Outro / Avulso</span>
              <span class="text-[10px] font-normal text-slate-500 block">Gasto eventual</span>
            </button>
          </div>'''

assert old_type_grid in content, "old_type_grid not found"
content = content.replace(old_type_grid, new_type_grid, 1)

# 2. Update onExpenseTypeChange function in JS
target_on_change = '''      const regularBtns = [
        { id: 'fixed', el: btnFixa },
        { id: 'recurrent', el: btnRecorrente },
        { id: 'installment', el: btnParcela },
        { id: 'variable', el: btnAvulsa }
      ];'''

new_on_change = '''      const btnPix = document.getElementById('btnExpenseTypePix');
      const btnDebito = document.getElementById('btnExpenseTypeDebito');

      const regularBtns = [
        { id: 'pix', el: btnPix },
        { id: 'debit', el: btnDebito },
        { id: 'fixed', el: btnFixa },
        { id: 'recurrent', el: btnRecorrente },
        { id: 'installment', el: btnParcela },
        { id: 'variable', el: btnAvulsa }
      ];'''

assert target_on_change in content, "target_on_change not found"
content = content.replace(target_on_change, new_on_change, 1)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated expense modal with PIX and Débito options!")
