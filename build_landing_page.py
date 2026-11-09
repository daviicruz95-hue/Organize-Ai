import os

landing_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Organize Aí | Finanças Leves para Casais e Famílias</title>
  
  <!-- Fonts & Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
          },
          colors: {
            canvas: '#FBFBFD',
            surface: '#FFFFFF',
            ink: '#18191D',
            'ink-muted': '#6B7280',
            line: '#F0F1F3',
            'line-dark': '#E5E7EB',
            primary: '#18191D',
            accent: '#3B82F6',
            mint: '#E8F8F0',
            'mint-ink': '#0F693E',
            lilac: '#F0EDFF',
            'lilac-ink': '#5B21B6',
            peach: '#FFF1F2',
            'peach-ink': '#9F1239',
            amber: '#FEF7E6',
            'amber-ink': '#92400E',
            ice: '#EDF5FF',
            'ice-ink': '#1E40AF',
          },
          animation: {
            'marquee-infinite': 'marquee 35s linear infinite',
          },
          keyframes: {
            marquee: {
              '0%': { transform: 'translateX(0%)' },
              '100%': { transform: 'translateX(-50%)' },
            }
          }
        }
      }
    }
  </script>

  <style>
    body {
      background-color: #FBFBFD;
      color: #18191D;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }
    
    /* Pause marquee on hover */
    .marquee-container:hover .marquee-track {
      animation-play-state: paused;
    }

    .glass-nav {
      background: rgba(251, 251, 253, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
    }
    
    .gradient-hero {
      background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(240, 237, 255, 0.6), transparent 70%);
    }

    .modal-backdrop {
      background: rgba(24, 25, 29, 0.4);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }
  </style>
</head>

<body class="flex flex-col min-h-screen">

  <!-- ========================================== -->
  <!-- 1. NAVIGATION BAR                          -->
  <!-- ========================================== -->
  <header class="sticky top-0 z-40 glass-nav border-b border-line">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      
      <!-- Brand Logo -->
      <a href="/" class="flex items-center gap-2.5 group">
        <div class="w-9 h-9 rounded-xl bg-ink text-white flex items-center justify-center font-bold text-lg shadow-sm group-hover:scale-105 transition-transform">
          ✦
        </div>
        <div>
          <span class="text-lg font-extrabold tracking-tight text-ink">Organize Aí</span>
          <span class="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-mint text-mint-ink border border-mint-ink/10">Simples & Prático</span>
        </div>
      </a>

      <!-- Desktop Links -->
      <nav class="hidden md:flex items-center gap-7 text-sm font-medium text-ink-muted">
        <a href="#funcionalidades" class="hover:text-ink transition-colors">O que faz</a>
        <a href="#conceito" class="hover:text-ink transition-colors">O Conceito</a>
        <a href="#objetivos" class="hover:text-ink transition-colors">Objetivos Reais</a>
      </nav>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2.5">
        <button onclick="openModal('login')" class="text-sm font-semibold px-4 py-2 rounded-xl text-ink hover:bg-line transition-colors">
          Entrar
        </button>
        <button onclick="openModal('register')" class="text-sm font-semibold px-4 py-2 rounded-xl bg-ink text-white hover:bg-neutral-800 transition-all shadow-sm active:scale-95">
          Começar Grátis
        </button>
      </div>
    </div>
  </header>

  <!-- ========================================== -->
  <!-- 2. HERO SECTION                            -->
  <!-- ========================================== -->
  <section class="gradient-hero pt-14 pb-12 sm:pt-20 sm:pb-16 px-4">
    <div class="max-w-4xl mx-auto text-center">
      
      <!-- Pill Badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-line-dark shadow-xs mb-6">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="text-xs font-semibold text-ink">Feito para casais e pessoas reais que odeiam planilhas</span>
      </div>

      <!-- Main Headline -->
      <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-ink tracking-tight leading-[1.15] mb-5">
        Cuidar do dinheiro da sua casa não deveria dar <span class="underline decoration-indigo-300 decoration-wavy decoration-2">dor de cabeça</span>.
      </h1>

      <!-- Subtitle -->
      <p class="text-base sm:text-lg text-ink-muted max-w-2xl mx-auto font-normal leading-relaxed mb-8">
        Chega de planilhas complexas com 50 fórmulas e aplicativos cheios de menus que você abandona na segunda semana. O <strong class="text-ink font-semibold">Organize Aí</strong> foi desenhado para você bater o olho e dominar as finanças em menos de um minuto.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-3 mb-10">
        <button onclick="openModal('register')" class="w-full sm:w-auto px-7 py-3.5 rounded-2xl bg-ink text-white font-bold text-base hover:bg-neutral-800 shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center justify-center gap-2">
          <span>Começar Agora Grátis</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
        <a href="/app" class="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-white border border-line-dark text-ink font-semibold text-base hover:bg-neutral-50 shadow-xs transition-all flex items-center justify-center gap-2">
          <span>👀 Ver Demonstração Direta</span>
        </a>
      </div>

      <!-- Quick Trust Indicators -->
      <div class="flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs font-medium text-ink-muted">
        <div class="flex items-center gap-1.5">
          <span class="text-emerald-500 font-bold">✓</span> Cadernos separados para o casal
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-emerald-500 font-bold">✓</span> Faturas de cartão sem susto
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-emerald-500 font-bold">✓</span> 100% no celular sem baixar nada
        </div>
      </div>
    </div>
  </section>

  <!-- ========================================== -->
  <!-- 3. INFINITE HORIZONTAL MARQUEE CAROUSEL   -->
  <!-- ========================================== -->
  <section id="funcionalidades" class="py-6 border-y border-line bg-surface/70 overflow-hidden marquee-container">
    <div class="max-w-6xl mx-auto px-4 mb-3 flex items-center justify-between">
      <span class="text-xs font-bold uppercase tracking-wider text-ink-muted">Recursos essenciais que funcionam no dia a dia</span>
      <span class="text-xs text-ink-muted hidden sm:inline">Passe o mouse para pausar ⏸</span>
    </div>

    <div class="relative w-full overflow-hidden">
      <!-- Gradient Fade Edges -->
      <div class="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-surface to-transparent z-10 pointer-events-none"></div>
      <div class="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-surface to-transparent z-10 pointer-events-none"></div>

      <!-- Marquee Track (Repeated twice for seamless loop) -->
      <div class="flex gap-3 w-max marquee-track animate-marquee-infinite py-2">
        
        <!-- Item 1 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-mint border border-mint-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">👫</span>
          <div>
            <div class="text-xs font-bold text-mint-ink">Cadernos do Casal</div>
            <div class="text-[11px] text-mint-ink/80">Espaço Davi & Nathalie sem misturar</div>
          </div>
        </div>

        <!-- Item 2 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-lilac border border-lilac-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">💳</span>
          <div>
            <div class="text-xs font-bold text-lilac-ink">Fatura com Subcompras</div>
            <div class="text-[11px] text-lilac-ink/80">Organize Uber, iFood e compras por cartão</div>
          </div>
        </div>

        <!-- Item 3 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-amber border border-amber-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📦</span>
          <div>
            <div class="text-xs font-bold text-amber-ink">Caixinhas & Cofrinhos</div>
            <div class="text-[11px] text-amber-ink/80">Metas visuais com barra de progresso</div>
          </div>
        </div>

        <!-- Item 4 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-ice border border-ice-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">🔄</span>
          <div>
            <div class="text-xs font-bold text-ice-ink">Virada de Mês com 1 Clique</div>
            <div class="text-[11px] text-ice-ink/80">Replica contas fixas e soma parcelas</div>
          </div>
        </div>

        <!-- Item 5 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-peach border border-peach-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📑</span>
          <div>
            <div class="text-xs font-bold text-peach-ink">Exportar em PDF Limpo</div>
            <div class="text-[11px] text-peach-ink/80">Relatório executivo para arquivar</div>
          </div>
        </div>

        <!-- Item 6 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-surface border border-line-dark shadow-xs whitespace-nowrap">
          <span class="text-lg">⚡</span>
          <div>
            <div class="text-xs font-bold text-ink">Entrada Rápida no Celular</div>
            <div class="text-[11px] text-ink-muted">Lance um gasto em menos de 5 segundos</div>
          </div>
        </div>

        <!-- Item 7 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-mint border border-mint-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">🎯</span>
          <div>
            <div class="text-xs font-bold text-mint-ink">Contagem de Parcelas</div>
            <div class="text-[11px] text-mint-ink/80">Saiba quando a última parcela vai acabar</div>
          </div>
        </div>

        <!-- Item 8 -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-lilac border border-lilac-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📊</span>
          <div>
            <div class="text-xs font-bold text-lilac-ink">Gráficos Minimalistas</div>
            <div class="text-[11px] text-lilac-ink/80">Visual Coinview neutro, sem poluição neon</div>
          </div>
        </div>

        <!-- DUPLICATE SET FOR SMOOTH INFINITE LOOP -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-mint border border-mint-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">👫</span>
          <div>
            <div class="text-xs font-bold text-mint-ink">Cadernos do Casal</div>
            <div class="text-[11px] text-mint-ink/80">Espaço Davi & Nathalie sem misturar</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-lilac border border-lilac-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">💳</span>
          <div>
            <div class="text-xs font-bold text-lilac-ink">Fatura com Subcompras</div>
            <div class="text-[11px] text-lilac-ink/80">Organize Uber, iFood e compras por cartão</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-amber border border-amber-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📦</span>
          <div>
            <div class="text-xs font-bold text-amber-ink">Caixinhas & Cofrinhos</div>
            <div class="text-[11px] text-amber-ink/80">Metas visuais com barra de progresso</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-ice border border-ice-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">🔄</span>
          <div>
            <div class="text-xs font-bold text-ice-ink">Virada de Mês com 1 Clique</div>
            <div class="text-[11px] text-ice-ink/80">Replica contas fixas e soma parcelas</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-peach border border-peach-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📑</span>
          <div>
            <div class="text-xs font-bold text-peach-ink">Exportar em PDF Limpo</div>
            <div class="text-[11px] text-peach-ink/80">Relatório executivo para arquivar</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-surface border border-line-dark shadow-xs whitespace-nowrap">
          <span class="text-lg">⚡</span>
          <div>
            <div class="text-xs font-bold text-ink">Entrada Rápida no Celular</div>
            <div class="text-[11px] text-ink-muted">Lance um gasto em menos de 5 segundos</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-mint border border-mint-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">🎯</span>
          <div>
            <div class="text-xs font-bold text-mint-ink">Contagem de Parcelas</div>
            <div class="text-[11px] text-mint-ink/80">Saiba quando a última parcela vai acabar</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-lilac border border-lilac-ink/15 shadow-xs whitespace-nowrap">
          <span class="text-lg">📊</span>
          <div>
            <div class="text-xs font-bold text-lilac-ink">Gráficos Minimalistas</div>
            <div class="text-[11px] text-lilac-ink/80">Visual Coinview neutro, sem poluição neon</div>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- ========================================== -->
  <!-- 4. O QUE DE FATO É O ORGANIZE AÍ (CONCEITO)-->
  <!-- ========================================== -->
  <section id="conceito" class="py-16 sm:py-24 px-4 max-w-5xl mx-auto">
    
    <div class="text-center max-w-2xl mx-auto mb-14">
      <span class="text-xs font-bold uppercase tracking-wider text-accent">Nossa Filosofia</span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-ink mt-2 mb-4 tracking-tight">
        Feito para a vida real, não para contadores de empresa.
      </h2>
      <p class="text-ink-muted text-base">
        A maioria dos aplicativos financeiros falha pelo mesmo motivo: exige esforço demais. O Organize Aí foi construído sobre uma única premissa: <strong class="text-ink">atrito zero</strong>.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Card 1 -->
      <div class="p-6 rounded-3xl bg-surface border border-line-dark shadow-xs hover:border-neutral-300 transition-all flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-2xl bg-mint text-mint-ink flex items-center justify-center text-2xl mb-5">
            📝
          </div>
          <h3 class="text-lg font-bold text-ink mb-2">A leveza de um caderno</h3>
          <p class="text-sm text-ink-muted leading-relaxed">
            Lembra da facilidade de anotar o que gastou num caderninho? Trouxemos essa mesma simplicidade, com a vantagem de fazer todos os cálculos e somas automaticamente.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-line text-xs font-semibold text-mint-ink">
          Sem categorias complexas ou menus chatos
        </div>
      </div>

      <!-- Card 2 -->
      <div class="p-6 rounded-3xl bg-surface border border-line-dark shadow-xs hover:border-neutral-300 transition-all flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-2xl bg-lilac text-lilac-ink flex items-center justify-center text-2xl mb-5">
            🤝
          </div>
          <h3 class="text-lg font-bold text-ink mb-2">Finanças a dois sem brigas</h3>
          <p class="text-sm text-ink-muted leading-relaxed">
            Nem tudo precisa ser jogado no mesmo bolo. Cada um tem seu próprio caderno para suas despesas pessoais, e os gastos em comum da casa ficam claros para os dois.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-line text-xs font-semibold text-lilac-ink">
          Transparência e privacidade no equilíbrio certo
        </div>
      </div>

      <!-- Card 3 -->
      <div class="p-6 rounded-3xl bg-surface border border-line-dark shadow-xs hover:border-neutral-300 transition-all flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-2xl bg-amber text-amber-ink flex items-center justify-center text-2xl mb-5">
            👁️
          </div>
          <h3 class="text-lg font-bold text-ink mb-2">Visão de sobra real</h3>
          <p class="text-sm text-ink-muted leading-relaxed">
            O mais importante não é ver quanto já passou, mas saber quanto sobra até o fim do mês para investir, poupar na caixinha ou curtir um final de semana em paz.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-line text-xs font-semibold text-amber-ink">
          Previsão automática de sobra mensal
        </div>
      </div>

    </div>
  </section>

  <!-- ========================================== -->
  <!-- 5. CASOS REAIS: O QUE VOCÊ QUER CONQUISTAR?-->
  <!-- ========================================== -->
  <section id="objetivos" class="py-16 px-4 bg-line/40 border-y border-line">
    <div class="max-w-5xl mx-auto">
      
      <div class="text-center max-w-2xl mx-auto mb-12">
        <span class="text-xs font-bold uppercase tracking-wider text-emerald-600">Aplicações na Vida Real</span>
        <h2 class="text-2xl sm:text-4xl font-extrabold text-ink mt-2 mb-4 tracking-tight">
          O dinheiro é só um meio. O que você quer realizar?
        </h2>
        <p class="text-ink-muted text-base">
          O Organize Aí não existe para você ficar olhando números, mas para dar a tranquilidade necessária para tirar seus maiores projetos do papel.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Caso 1: Casamento -->
        <div class="p-5 rounded-2xl bg-surface border border-line-dark shadow-xs flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-3">💍</div>
            <h4 class="text-base font-bold text-ink mb-1.5">Vai Casar?</h4>
            <p class="text-xs text-ink-muted leading-relaxed">
              Acompanhe os custos de buffet, decoração e foto sem estourar o limite do casal antes mesmo de subir no altar.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-line text-[11px] font-semibold text-accent">
            Controle de contratos & parcelas
          </div>
        </div>

        <!-- Caso 2: Viagem -->
        <div class="p-5 rounded-2xl bg-surface border border-line-dark shadow-xs flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-3">✈️</div>
            <h4 class="text-base font-bold text-ink mb-1.5">Sonha em Viajar?</h4>
            <p class="text-xs text-ink-muted leading-relaxed">
              Crie a caixinha da viagem, junte mês a mês e viaje com a certeza de não voltar com a fatura do cartão atolada de dívida.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-line text-[11px] font-semibold text-accent">
            Caixinha com barra de progresso
          </div>
        </div>

        <!-- Caso 3: Carro ou Casa -->
        <div class="p-5 rounded-2xl bg-surface border border-line-dark shadow-xs flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-3">🚗</div>
            <h4 class="text-base font-bold text-ink mb-1.5">Carro ou Casa Própria</h4>
            <p class="text-xs text-ink-muted leading-relaxed">
              Identifique vazamentos pequenos no dia a dia para acelerar o valor da entrada do seu veículo ou imóvel.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-line text-[11px] font-semibold text-accent">
            Caça aos vazamentos invisíveis
          </div>
        </div>

        <!-- Caso 4: Reserva de Emergência -->
        <div class="p-5 rounded-2xl bg-surface border border-line-dark shadow-xs flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-3">🛡️</div>
            <h4 class="text-base font-bold text-ink mb-1.5">Dormir em Paz</h4>
            <p class="text-xs text-ink-muted leading-relaxed">
              Monte seu colchão de segurança de 3 a 6 meses para que imprevistos com saúde ou carro nunca mais tirem o seu sono.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-line text-[11px] font-semibold text-accent">
            Reserva protegida e visível
          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- ========================================== -->
  <!-- 6. FINAL CALL TO ACTION                    -->
  <!-- ========================================== -->
  <section class="py-16 sm:py-20 px-4 text-center">
    <div class="max-w-2xl mx-auto bg-ink text-white rounded-3xl p-8 sm:p-12 shadow-xl relative overflow-hidden">
      <div class="relative z-10">
        <h3 class="text-2xl sm:text-3xl font-extrabold mb-3 tracking-tight">
          Pronto para ter paz com as contas do mês?
        </h3>
        <p class="text-sm sm:text-base text-neutral-300 max-w-md mx-auto mb-7">
          Você não precisa de um curso de finanças. Só precisa de uma ferramenta simples que você realmente use.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button onclick="openModal('register')" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white text-ink font-bold text-sm hover:bg-neutral-100 transition-all shadow-sm active:scale-95">
            Criar Minha Conta Grátis
          </button>
          <a href="/app" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-neutral-800 text-white font-semibold text-sm hover:bg-neutral-700 transition-all">
            Entrar como Convidado
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- ========================================== -->
  <!-- 7. FOOTER                                  -->
  <!-- ========================================== -->
  <footer class="mt-auto border-t border-line py-8 px-4 text-center text-xs text-ink-muted">
    <div class="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="font-bold text-ink">Organize Aí</span> — Finanças descomplicadas para casais e famílias
      </div>
      <div>
        © 2026 Organize Aí. Todos os direitos reservados.
      </div>
    </div>
  </footer>

  <!-- ========================================== -->
  <!-- 8. MODAL DE LOGIN & CADASTRO               -->
  <!-- ========================================== -->
  <div id="authModal" class="fixed inset-0 z-50 modal-backdrop hidden items-center justify-center p-4">
    <div class="bg-surface border border-line-dark rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl relative">
      
      <!-- Close Button -->
      <button onclick="closeModal()" class="absolute top-5 right-5 text-ink-muted hover:text-ink w-8 h-8 rounded-full flex items-center justify-center hover:bg-line transition-colors">
        ✕
      </button>

      <!-- Modal Tabs -->
      <div class="flex gap-2 p-1 bg-line rounded-2xl mb-6">
        <button id="tabLogin" onclick="switchAuthTab('login')" class="flex-1 py-2 text-xs font-bold rounded-xl bg-surface text-ink shadow-xs transition-all">
          Entrar
        </button>
        <button id="tabRegister" onclick="switchAuthTab('register')" class="flex-1 py-2 text-xs font-bold rounded-xl text-ink-muted hover:text-ink transition-all">
          Criar Conta
        </button>
      </div>

      <!-- Quick Family Shortcut -->
      <div class="mb-5 p-3.5 rounded-2xl bg-mint border border-mint-ink/15">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-xs font-bold text-mint-ink flex items-center gap-1.5">
            <span>✨</span> Espaço Davi & Nathalie
          </span>
          <span class="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-white text-mint-ink">Pronto</span>
        </div>
        <p class="text-[11px] text-mint-ink/80 mb-2.5">
          Seus dados e cadernos já estão salvos e configurados neste aparelho.
        </p>
        <a href="/app" class="block w-full text-center py-2 rounded-xl bg-ink text-white font-bold text-xs hover:bg-neutral-800 transition-all shadow-xs">
          Acessar Meu Painel Agora →
        </a>
      </div>

      <div class="relative flex py-2 items-center mb-4">
        <div class="flex-grow border-t border-line"></div>
        <span class="flex-shrink mx-3 text-[11px] text-ink-muted uppercase font-medium">Ou entre com e-mail</span>
        <div class="flex-grow border-t border-line"></div>
      </div>

      <!-- Auth Form -->
      <form onsubmit="handleAuthSubmit(event)" class="space-y-3.5">
        <div id="nameField" class="hidden">
          <label class="block text-xs font-bold text-ink mb-1">Seu Nome</label>
          <input type="text" placeholder="Ex: Davi Cruz" class="w-full px-3.5 py-2.5 rounded-xl border border-line-dark text-sm focus:outline-none focus:border-ink">
        </div>

        <div>
          <label class="block text-xs font-bold text-ink mb-1">E-mail</label>
          <input type="email" required placeholder="seu@email.com" class="w-full px-3.5 py-2.5 rounded-xl border border-line-dark text-sm focus:outline-none focus:border-ink">
        </div>

        <div>
          <label class="block text-xs font-bold text-ink mb-1">Senha</label>
          <input type="password" required placeholder="••••••••" class="w-full px-3.5 py-2.5 rounded-xl border border-line-dark text-sm focus:outline-none focus:border-ink">
        </div>

        <button type="submit" id="btnAuthSubmit" class="w-full py-3 rounded-xl bg-ink text-white font-bold text-sm hover:bg-neutral-800 transition-all mt-2">
          Entrar no Organize Aí
        </button>
      </form>

      <p class="text-center text-[11px] text-ink-muted mt-4">
        🔒 Seus dados financeiros são privados e criptografados.
      </p>

    </div>
  </div>

  <!-- Client-side Logic -->
  <script>
    function openModal(mode = 'login') {
      const modal = document.getElementById('authModal');
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      switchAuthTab(mode);
    }

    function closeModal() {
      const modal = document.getElementById('authModal');
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }

    function switchAuthTab(tab) {
      const isLogin = tab === 'login';
      document.getElementById('tabLogin').className = isLogin 
        ? 'flex-1 py-2 text-xs font-bold rounded-xl bg-surface text-ink shadow-xs transition-all'
        : 'flex-1 py-2 text-xs font-bold rounded-xl text-ink-muted hover:text-ink transition-all';
        
      document.getElementById('tabRegister').className = !isLogin 
        ? 'flex-1 py-2 text-xs font-bold rounded-xl bg-surface text-ink shadow-xs transition-all'
        : 'flex-1 py-2 text-xs font-bold rounded-xl text-ink-muted hover:text-ink transition-all';

      document.getElementById('nameField').classList.toggle('hidden', isLogin);
      document.getElementById('btnAuthSubmit').innerText = isLogin ? 'Entrar no Organize Aí' : 'Criar Conta Gratuita';
    }

    function handleAuthSubmit(e) {
      e.preventDefault();
      // Directly transition to the app
      window.location.href = '/app';
    }

    // Close modal on click outside
    document.getElementById('authModal').addEventListener('click', (e) => {
      if (e.target.id === 'authModal') closeModal();
    });
  </script>

</body>
</html>
"""

dest_path = "/Users/davicruz/.gemini/antigravity/scratch/assessor-financeiro/public/landing.html"
with open(dest_path, "w", encoding="utf-8") as f:
    f.write(landing_html)

print("Landing page created successfully at:", dest_path)
