# 🏗️ NOVA ESTRUTURA DO PROJETO — Guia de Navegação

## ✨ Projeto Reorganizado Profissionalmente

Tudo está agora em seu lugar certo, fácil de encontrar e profissional para apresentar.

---

## 📂 Mapa Visual da Estrutura

```
PI_V_MonitoramentoBaciasPCJ/
│
├─ 📄 README.md                        ← COMECE AQUI (overview)
├─ 📄 requirements.txt                 ← Dependências
├─ 📄 .env.example                     ← Template configuração
│
├─ 📁 docs/                            ⭐ DOCUMENTAÇÃO TÉCNICA
│  ├─ ARCHITECTURE.md                  (Arquitetura completa)
│  ├─ QUICK_SETUP.md                   (Setup em 5 passos)
│  ├─ GUIA_PROJETO_MONITORAMENTO_PCJ.md
│  └─ GUIA_INTEGRANTES.md
│
├─ 📁 presentation/                    ⭐ APRESENTAÇÃO BANCA
│  ├─ PRESENTATION_20MIN.md            (🎯 COMECE AQUI - roteiro)
│  ├─ PRESENTATION_SLIDES.md           (12 slides)
│  ├─ PRESENTATION_README.md           (Índice + como usar)
│  └─ PRESENTATION_SCRIPT.md           (Versão anterior - backup)
│
├─ 📁 scripts/                         ⭐ UTILITÁRIOS
│  ├─ demos/
│  │  ├─ demo_pipeline_summary.py      (10s - resumo do pipeline)
│  │  └─ demo_bertopic_quick.py        (1-2 min - BERTopic ao vivo)
│  ├─ tests/
│  │  ├─ teste_ambiente.py             (Verifica bibliotecas)
│  │  ├─ teste_fontes.py               (Testa config YAML)
│  │  ├─ teste_coleta.py               (Testa coleta G1)
│  │  ├─ teste_classificacao_amostras.py
│  │  ├─ teste_bigquery_conexao.py     (Testa BigQuery)
│  │  ├─ teste_bigquery_envio_csv.py
│  │  ├─ teste_bigquery_criar_views.py
│  │  └─ teste_filtro_pcj.py
│  └─ utils/
│     └─ enviar_amostras_bigquery.py
│
├─ 📁 src/                             🔧 CÓDIGO PRINCIPAL
│  ├─ main.py                          (Pipeline orquestrador)
│  ├─ collectors/                      (Web scraping)
│  ├─ processing/                      (NLP - limpeza, filtros)
│  ├─ nlp/                             (IA - embeddings, risco, BERTopic)
│  ├─ database/                        (BigQuery)
│  ├─ config/                          (Configurações)
│  └─ utils/
│
├─ 📁 data/                            📊 DADOS
│  ├─ raw/                             (Dados brutos do pipeline)
│  ├─ processed/                       (Dados processados)
│  └─ samples/                         (Dados de teste)
│
├─ 📁 notebooks/                       📓 EXPLORAÇÃO
│  └─ (Jupyter notebooks opcionais)
│
└─ 📁 credentials/ (GITIGNORE)         🔐 CREDENCIAIS (não subir)
```

---

## 🎯 Onde Encontrar Cada Coisa

### Para Apresentação (SEGUNDA-FEIRA)

```bash
# 1. Ler o roteiro
cat presentation/PRESENTATION_20MIN.md

# 2. Ver os slides
cat presentation/PRESENTATION_SLIDES.md

# 3. Entender como usar tudo
cat presentation/PRESENTATION_README.md

# 4. Rodar as demos
PYTHONPATH=. python3 scripts/demos/demo_pipeline_summary.py
PYTHONPATH=. python3 scripts/demos/demo_bertopic_quick.py
```

### Para Entender Técnica

```bash
# Arquitetura completa
cat docs/ARCHITECTURE.md

# Setup para replicar
cat docs/QUICK_SETUP.md
```

### Para Testar Localmente

```bash
# Verificar ambiente
python scripts/tests/teste_ambiente.py

# Testar coleta
python scripts/tests/teste_coleta.py

# Testar BigQuery
python scripts/tests/teste_bigquery_conexao.py
```

### Para Rodar Pipeline

```bash
# Modo local
export ENVIAR_PARA_BIGQUERY=false
python -m src.main

# Com BigQuery
export ENVIAR_PARA_BIGQUERY=true
python -m src.main
```

---

## 📊 Comparação: Antes vs Depois

### ❌ Antes (Caótico)
```
Raiz com 20+ arquivos soltos:
├─ teste_ambiente.py
├─ teste_coleta.py
├─ teste_bigquery_conexao.py
├─ teste_bigquery_envio_csv.py
├─ teste_bigquery_criar_views.py
├─ teste_classificacao_amostras.py
├─ teste_filtro_pcj.py
├─ teste_fontes.py
├─ enviar_amostras_bigquery.py
├─ demo_pipeline_summary.py
├─ demo_bertopic_quick.py
├─ ARCHITECTURE.md
├─ PRESENTATION_20MIN.md
├─ PRESENTATION_SLIDES.md
├─ PRESENTATION_SCRIPT.md
├─ QUICK_SETUP.md
├─ GUIA_PROJETO_MONITORAMENTO_PCJ.md
├─ SETUP.md
└─ ... difícil achar nada!
```

### ✅ Depois (Organizado)
```
Raiz limpa:
├─ README.md (overview)
├─ requirements.txt
├─ .env.example
│
├─ docs/                   (4 arquivos doc)
├─ presentation/           (4 arquivos apresentação)
├─ scripts/                (11 scripts organizados)
│  ├─ demos/
│  ├─ tests/
│  └─ utils/
├─ src/                    (código - sem mudanças)
└─ data/                   (dados - sem mudanças)

→ Profissional, fácil navegar, pronto para open-source!
```

---

## 🎓 Workflow para Apresentação

### Domingo (Preparação)
```bash
# 1. Ler roteiro
cat presentation/PRESENTATION_20MIN.md

# 2. Revisar slides
cat presentation/PRESENTATION_SLIDES.md

# 3. Praticar demos
python scripts/tests/teste_ambiente.py
PYTHONPATH=. python3 scripts/demos/demo_pipeline_summary.py
PYTHONPATH=. python3 scripts/demos/demo_bertopic_quick.py

# 4. Revisar arquitetura
cat docs/ARCHITECTURE.md | grep -A 5 "Respostas para Perguntas"
```

### Segunda (Dia da Apresentação)
```bash
# 1. Chegar cedo
# 2. Terminal pronto com demos
cd scripts/demos/
# 3. Seguir PRESENTATION_20MIN.md
# 4. Rodar demos quando chegar na Slide 7
PYTHONPATH=. python3 demo_bertopic_quick.py
```

---

## 📋 Checklist de Uso

### Documentação
- [ ] Li `README.md` (overview geral)
- [ ] Li `presentation/PRESENTATION_20MIN.md` (roteiro)
- [ ] Revisei `docs/ARCHITECTURE.md` (técnica)

### Scripts
- [ ] Testei `scripts/tests/teste_ambiente.py`
- [ ] Testei `scripts/demos/demo_pipeline_summary.py`
- [ ] Testei `scripts/demos/demo_bertopic_quick.py`

### Preparação
- [ ] Slides prontos (PowerPoint ou Markdown)
- [ ] Terminal com demos pronto
- [ ] Link Looker testado
- [ ] Respirei fundo e confiei em mim! 😊

---

## 🔗 Links Rápidos

| O que você quer | Onde ir |
|-----------------|---------|
| Overview geral | `README.md` |
| Apresentação banca | `presentation/PRESENTATION_20MIN.md` |
| Arquitetura técnica | `docs/ARCHITECTURE.md` |
| Setup rápido | `docs/QUICK_SETUP.md` |
| Demo ao vivo | `scripts/demos/demo_*.py` |
| Testes ambiente | `scripts/tests/teste_*.py` |
| Executar pipeline | `python -m src.main` |

---

## 🚀 Dicas Ouro

✨ **Raiz do projeto está limpa** — Abre a pasta e vê tudo organizado

✨ **Documentação centralizada** — Tudo em `docs/` e `presentation/`

✨ **Scripts organizados por tipo** — `demos/` para apresentação, `tests/` para verificação

✨ **Pronto para GitHub** — Estrutura profissional, fácil para outros clonar

✨ **Fácil de estender** — Adicionar nova fonte? Vai em `src/collectors/`

---

## 📞 Suporte Rápido

| Problema | Solução |
|----------|---------|
| "Onde está o script de teste?" | `scripts/tests/` |
| "Qual é o roteiro da apresentação?" | `presentation/PRESENTATION_20MIN.md` |
| "Como faço setup em outro PC?" | `docs/QUICK_SETUP.md` |
| "Qual é a arquitetura?" | `docs/ARCHITECTURE.md` |
| "Preciso rodar uma demo?" | `scripts/demos/demo_*.py` |

---

## ✅ Resumo Final

**Antes:** Projeto funcional mas desorganizado 📁❌  
**Depois:** Projeto profissional e bem estruturado ✨🚀

**Benefícios:**
- ✓ Raiz limpa (fácil navegar)
- ✓ Documentação centralizada
- ✓ Scripts organizados por função
- ✓ Pronto para apresentação
- ✓ Profissional para banca
- ✓ Escalável para futuro

**Próximo passo:** Abra `presentation/PRESENTATION_20MIN.md` e comece a praticar!

---

**Repositório reorganizado com sucesso! 🎉**
