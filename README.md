# Organize Aí 📊 • Plataforma de Gestão Financeira Familiar & Pessoal

> **Controle financeiro inteligente, sem atrito e em tempo real via WhatsApp e Web.**  
> Aplicação no ar em produção: [https://apporganizeai.com.br](https://apporganizeai.com.br)

---

## 📌 1. Visão Geral do Produto

O **Organize Aí** nasceu para resolver uma dor real e diária de famílias e casais: o cansaço mental e o atrito de anotar gastos em cadernos físicos, planilhas complexas de Excel ou aplicativos burocráticos com dezenas de telas.

A premissa central é a **mordomia e a simplicidade radical**: o perigo financeiro de um casal raramente está nos custos fixos conhecidos (aluguel, condomínio, luz), mas sim nos **ralos invisíveis da rotina** (gastos no débito, cafezinhos, padaria, compras impulsivas no crédito).

Com o **Organize Aí**, o controle financeiro acontece **no fluxo natural da vida**:
1. O usuário ou o casal manda uma mensagem de texto ou áudio no grupo de WhatsApp **"Organize Aí"** (ex: *"Almoço 35 no débito"*, *"Uber 22 no pix"*, *"Farmácia 70 no crédito em 2x"*).
2. O assistente virtual **Zeca** processa a mensagem via NLP/regex, categoriza a despesa, vincula ao caderno correto (ex: *Caderno Davi* ou *Caderno Nathalie*), abate do saldo bancário na hora (se for débito/pix) e confirma no chat.
3. O painel web sincroniza em tempo real, exibindo visão unificada de gastos fixos, variáveis, faturas de cartão, caixinhas de reserva e simulação de metas de poupança com projeção CDI.

---

## 🛠️ 2. Stack Tecnológica & Arquitetura

O projeto foi construído propositalmente com arquitetura enxuta, de alta performance e baixíssima dependência de frameworks pesados:

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                       │
│  - Web App (SPA): Vanilla HTML5 / JS / Tailwind CSS     │
│  - WhatsApp: Mensagens e áudios de grupos autorizados   │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│   WHATSAPP SERVICE        │  │       BACKEND API         │
│   (Node.js / Baileys)     │  │     (Python 3.11)         │
│   - @whiskeysockets/baileys│  │  - http.server nativo     │
│   - QR Code / Pair Code   │  │  - Engine NLP / Regex     │
│   - Multi-device auth     │  │  - JSON Storage Engine    │
└────────────┬──────────────┘  └──────────┬────────────────┘
             │ Webhook POST /api/webhook/whatsapp
             └────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│              INFRAESTRUTURA & PERSISTÊNCIA              │
│  - Railway Container com Volume Persistente (/app/data) │
│  - Cloudflare Proxy & SSL Custom Domain                 │
└─────────────────────────────────────────────────────────┘
```

- **Backend API (Python 3.11):** Servidor HTTP nativo (`http.server`), sem dependências pesadas de frameworks, garantindo inicialização instantânea, baixo consumo de RAM (< 60MB) e portabilidade máxima.
- **WhatsApp Bot Service (Node.js 20+):** Utiliza a biblioteca oficial `@whiskeysockets/baileys` para conexão WebSocket multi-device com o WhatsApp Web, persistindo credenciais de sessão criptografadas.
- **Frontend SPA (Web):** Single Page Application em HTML5 puro, Vanilla JavaScript reativo, Tailwind CSS via CDN, ícones Lucide Icons, gráficos Chart.js e micro-interações táteis (Canvas-Confetti).
- **Armazenamento de Dados:** Motor baseado em documentos JSON com persistência atômica e particionamento por família/usuário (`users_data/data_*.json`).
- **Infraestrutura:** Hospedado no Railway com volume persistente montado em `/app/persistent_data`.

---

## 📁 3. Estrutura do Repositório

```text
assessor-financeiro/
├── server.py                   # Servidor HTTP REST principal (endpoints, auth, rotas e data layer)
├── whatsapp_bot.py             # NLP Engine: parser financeiro e gerador de respostas do Zeca
├── start.sh                    # Script de boot orquestrador (Node Baileys + Python Server)
├── Procfile                    # Declaração de inicialização do processo web
├── requirements.txt            # Dependências Python (requests, etc.)
├── data.json                   # Estrutura base de dados (fallback e template de inicialização)
├── users.json                  # Registro de usuários e famílias autenticadas
│
├── public/                     # Frontend estático servido pelo Python
│   ├── index.html              # Dashboard SPA principal (Cadernos, Cartões, Caixinhas, Metas)
│   ├── index_landing.html      # Landing page de apresentação e conversão
│   ├── login.html              # Tela de autenticação e login
│   ├── register.html           # Cadastro de novo usuário / casal
│   ├── pair.html               # Pareamento via WhatsApp Pair Code
│   ├── faq.html                # Central de Ajuda & Perguntas Frequentes
│   └── whatsapp_status.json    # Estado do socket de conexão do WhatsApp
│
├── whatsapp-service/           # Microserviço Baileys em Node.js
│   ├── bot.js                  # Conexão WhatsApp, listener de mensagens, filtros de grupo
│   ├── package.json            # Dependências do microserviço
│   └── auth_info_baileys/      # Credenciais da sessão do WhatsApp (armazenadas no volume)
│
└── users_data/                 # Diretório de persistência particionada por conta
    └── data_usr-*.json         # Dados isolados de cada usuário/família
```

---

## 🗄️ 4. Modelagem de Dados (`data.json`)

Cada arquivo de dados segue o seguinte esquema principal:

```json
{
  "activeMonth": "2026-11",
  "cadernos": [
    {
      "id": "cad-davi",
      "name": "Caderno Davi",
      "description": "Contas fixas, moto e parcelas",
      "color": "#0284C7",
      "bg": "#EDF5FF",
      "icon": "D"
    },
    {
      "id": "cad-nathalie",
      "name": "Caderno Nathalie",
      "description": "Contas fixas, recorrentes e faturas",
      "color": "#7C3AED",
      "bg": "#F0EDFF",
      "icon": "N"
    }
  ],
  "savingsBoxes": [
    {
      "id": "box-reserva",
      "name": "Reserva de Emergência",
      "currentAmount": 1500.0,
      "targetAmount": 18000.0,
      "color": "#10B981"
    }
  ],
  "months": [
    {
      "id": "2026-11",
      "name": "Novembro",
      "year": 2026,
      "accountBalance": 1197.17,
      "incomes": [
        {
          "id": "inc-1",
          "description": "Salário",
          "amount": 5000.0,
          "status": "received",
          "person": "Davi"
        }
      ],
      "expenses": [
        {
          "id": "exp-1",
          "description": "Condomínio",
          "amount": 730.0,
          "status": "pending",
          "type": "fixed",
          "cadernoId": "cad-davi"
        },
        {
          "id": "exp-2",
          "description": "Presente do Chefe",
          "amount": 20.0,
          "status": "paid",
          "type": "pix",
          "cadernoId": "cad-davi"
        }
      ]
    }
  ]
}
```

### Regra de Negócio Crítica — Saldo em Conta (`accountBalance`):
- Quando definido pelo usuário, representa o saldo líquido real da conta bancária.
- Qualquer lançamento de despesa via **Débito**, **PIX** ou **Variável paga** deduz o `accountBalance` imediatamente.
- Lançamentos em **Cartão de Crédito** não deduzem o saldo bancário no ato, sendo consolidados na fatura do mês correspondente.

---

## 🤖 5. Como Funciona o Robô Zeca (WhatsApp)

1. **Filtro de Segurança e Privacidade:**
   O bot (`whatsapp-service/bot.js`) monitora apenas grupos explicitamente nomeados como **"Organize Aí"** ou **"Organize ai"**. Mensagens em outros grupos ou conversas privadas são sumariamente ignoradas.
2. **Parser Financeiro NLP (`whatsapp_bot.py`):**
   - Identifica quantias monetárias: `50`, `R$ 50,00`, `35 reais`, `4 e 50`.
   - Identifica forma de pagamento: `débito`, `pix`, `crédito`, `no cartão`.
   - Identifica parcelamento: `em 3x`, `3 parcelas`.
   - Identifica o responsável pelo gasto: contextualizado pelo remetente da mensagem ou texto (`Caderno Davi`, `Nati`, `minha conta`).
   - Remove stopwords e formata a descrição do item (ex: transforma *"comprei um café na padaria 6 reais no débito"* em item *"Café Na Padaria"*, categoria *"Alimentação"*, valor `R$ 6,00`).
3. **Comunicação Webhook:**
   O processo Node.js repassa o payload para `POST http://127.0.0.1:8080/api/webhook/whatsapp`. O Python processa, grava os dados, deduz o saldo e devolve a resposta formatada para o Zeca enviar no chat.

---

## 💻 6. Como Rodar o Projeto Localmente

### Pré-requisitos:
- **Python 3.10+**
- **Node.js 18+** e **npm**

### Passo 1: Clonar e instalar dependências do Python
```bash
git clone <URL_DO_REPOSITORIO>
cd assessor-financeiro
pip install -r requirements.txt
```

### Passo 2: Instalar dependências do serviço WhatsApp
```bash
cd whatsapp-service
npm install
cd ..
```

### Passo 3: Inicializar a aplicação
```bash
# Permissão de execução no script de boot
chmod +x start.sh

# Inicia o servidor Python e o worker Baileys
./start.sh
```
Acesse o dashboard no seu navegador em: `http://localhost:8080/app`

---

## 🚀 7. Deploy & Produção no Railway

O projeto está configurado para deploy automático via Railway:

1. **Volume Persistente:** É obrigatório montar um volume no Railway no caminho `/app/persistent_data`. Isso garante que a sessão do WhatsApp (`auth_info_baileys`) e os dados de usuários (`data.json`) não sejam apagados durante novos deploys.
2. **Variáveis de Ambiente:**
   - `PORT`: Porta HTTP (padrão `8080`).
   - `DATA_DIR`: Caminho do volume persistente (`/app/persistent_data`).
3. **Deploy Manual via CLI:**
   ```bash
   npx @railway/cli up -d -y
   ```

---

## 🤝 8. Guia de Contribuição para Desenvolvedores

1. **Padrão de Código:**
   - Mantenha o backend limpo e focado em funções puras para manipulação do JSON de dados.
   - Toda alteração em saldo, despesas ou receitas deve garantir persistência atômica via `save_data()`.
2. **Frontend:**
   - Evite adicionar frameworks pesados (React, Vue, build steps complexos). O Organize Aí preza pela reatividade rápida e renderização direta sem compilação.
   - Utilize as funções globais `formatBRL()`, `fetchAppData()` e `renderAll()`.
3. **Branches:**
   - Crie branches descritivas: `git checkout -b feature/nome-da-funcionalidade` ou `fix/descricao-do-bug`.
   - Abra um Pull Request detalhando as alterações e testes realizados.

---

**Equipe Organize Aí** • Feito com foco em simplicidade, estabilidade e paz financeira.
