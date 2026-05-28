# 📋 APRESENTAÇÃO BANCA — Índice de Materiais Preparados

## 🎯 Seu Material Completo para Apresentação (20 min + 15 min perguntas)

Tudo foi preparado para a apresentação de segunda-feira (31/05/2026) seguindo as dicas do professor.

---

## 📁 Arquivos Criados

### 1️⃣ Roteiro Principal (COMECE AQUI)
**Arquivo:** `PRESENTATION_20MIN.md`

- ✅ **20 minutos** estruturados
- ✅ Segue sequência exata do professor:
  1. Problema (3 min)
  2. Solução + Pitch (3 min)
  3. Parceria Extensão (1 min)
  4. IA/ML Técnico (6 min)
  5. Demo ao vivo (4 min)
  6. Qualidade/Métricas (3 min)
- ✅ Timings por slide
- ✅ O que falar (script completo)
- ✅ Respostas para perguntas técnicas
- ✅ Checklist pré-apresentação

**Como usar:** Leia na ordem, pratique com cronômetro, responda as perguntas prováveis.

---

### 2️⃣ Slides para PowerPoint/Apresentação
**Arquivo:** `PRESENTATION_SLIDES.md`

- ✅ 12 slides em Markdown
- ✅ Estrutura:
  - Slide 1: Capa
  - Slide 2-3: Problema + Contexto
  - Slide 4-7: IA/ML Técnico (embeddings, BERTopic, risco)
  - Slide 8: Dashboard Looker
  - Slide 9: Implementação/Resultados
  - Slide 10: Próximos Passos
  - Slide 11: Benefícios/Impacto
  - Slide 12: Conclusão

**Como usar:**
- Copiar conteúdo para PowerPoint/Google Slides
- Adicionar logos e cores do projeto
- Ou apresentar em Markdown (via Reveal.js, etc)

---

### 3️⃣ Documentação Técnica Completa
**Arquivo:** `ARCHITECTURE.md`

- ✅ Visão geral do projeto
- ✅ 5 camadas de arquitetura explicadas
- ✅ Pipeline de dados passo a passo
- ✅ Modelos de IA (embeddings + BERTopic)
- ✅ BigQuery e views SQL
- ✅ Como estender o projeto
- ✅ Troubleshooting

**Como usar:** Consultar quando banca fizer pergunta técnica profunda. Leitura prévia recomendada.

---

### 4️⃣ Scripts de Demonstração ao Vivo

#### A. `demo_pipeline_summary.py`
```bash
PYTHONPATH=. python3 demo_pipeline_summary.py
```
- Mostra resumo em 1 tela
- 📊 Total de notícias
- ✓ Relevantes vs Irrelevantes (%)
- 📈 Categorias e Riscos (distribuição)
- ⭐ Últimas 5 notícias

**Tempo:** ~10 segundos

#### B. `demo_bertopic_quick.py`
```bash
PYTHONPATH=. python3 demo_bertopic_quick.py
```
- Roda BERTopic em dados reais
- 🧠 Descobre tópicos automaticamente
- 📌 Mostra palavras-chave por tópico
- 📝 Exemplos de notícias

**Tempo:** ~1-2 minutos

**Como usar na demo:**
1. Terminal pronto antes da apresentação
2. Na Slide 7 (BERTopic), rodar Demo B
3. Mostrar os tópicos descobertos
4. Explicar: "Sem configuração prévia, algoritmo encontrou X tópicos coherentes"

---

### 5️⃣ Guia Rápido de Setup
**Arquivo:** `QUICK_SETUP.md`

- ✅ 5 passos para replicar tudo
- ✅ Pré-requisitos
- ✅ Instalação de dependências
- ✅ Configuração de credenciais
- ✅ Testes do ambiente
- ✅ Troubleshooting rápido

**Como usar:** Se someone da banca quiser replicar depois, compartilhe este arquivo.

---

## 🎬 Como Usar Durante a Apresentação

### Antes (dia anterior)
- [ ] Ler `PRESENTATION_20MIN.md` completo
- [ ] Praticar falando em voz alta com cronômetro
- [ ] Fazer os testes: `teste_ambiente.py`, `teste_fontes.py`
- [ ] Rodar `python -m src.main` para gerar dados frescos
- [ ] Preparar terminal com scripts de demo
- [ ] Testar link do Dashboard Looker (se houver)
- [ ] Revisar `ARCHITECTURE.md` (perguntas técnicas)

### Durante apresentação (20 min)
1. **Slides 1-3 (6 min):** Problema + Solução
   - Leia o script em `PRESENTATION_20MIN.md`
   - Use slides como guia, não leia

2. **Slides 4-7 (6 min):** IA/ML Técnico
   - Seções: Arquitetura, Embeddings, Classificação, BERTopic
   - **DEMO de BERTopic aqui:** `python3 demo_bertopic_quick.py`
   - Deixar rodando enquanto explica o resto

3. **Slides 8-9 (2 min):** Dashboard + Resultados
   - Mostrar link Looker (se disponível)
   - Ou mostrar `demo_pipeline_summary.py`

4. **Slides 10-12 (3 min):** Próximos passos + Conclusão

### Depois (15 min de perguntas)
- Responda usando `ARCHITECTURE.md` como referência
- Respostas pré-prontas estão em `PRESENTATION_20MIN.md` seção "Respostas para Perguntas"
- Se não souber: "Ótima pergunta, vou verificar e envio por email"

---

## 📊 Estrutura de Apresentação Recomendada

```
APRESENTAÇÃO (20 MIN)
│
├─ INTRODUÇÃO (3 min)
│  ├─ Slide 1-2: Capa + Contexto
│  └─ Script: PRESENTATION_20MIN.md "PARTE 1: PROBLEMA"
│
├─ SOLUÇÃO (4 min)
│  ├─ Slide 3-4: Solução + Arquitetura
│  ├─ Mencionar: Parceria de Extensão
│  └─ Script: PRESENTATION_20MIN.md "PARTE 2: SOLUÇÃO"
│
├─ TÉCNICO & DEMO (8 min)
│  ├─ Slide 5-8: IA/ML detalhado
│  ├─ DEMO ao vivo: python3 demo_bertopic_quick.py (1 min)
│  ├─ Dashboard (mostrar prints ou link)
│  └─ Script: PRESENTATION_20MIN.md "PARTE 4: IA/ML" + "PARTE 5: DEMO"
│
├─ QUALIDADE (3 min)
│  ├─ Slide 9: Métricas (88% acurácia, etc)
│  ├─ Slide 10-12: Resultados + Conclusão
│  └─ Script: PRESENTATION_20MIN.md "PARTE 6: QUALIDADE"
│
└─ PERGUNTAS (15 min)
   └─ Usar: PRESENTATION_20MIN.md "Respostas para Perguntas"
      + ARCHITECTURE.md para aprofundar

TOTAL: 20 min + 15 min perguntas = 35 min
```

---

## 🎯 Checklist Final

### Preparação Técnica
- [ ] `python -m src.main` rodado (gerar dados novos)
- [ ] Terminal com `demo_*.py` scripts prontos
- [ ] Link Dashboard Looker testado
- [ ] Internet estável na sala
- [ ] Projetor/tela funcionando

### Material
- [ ] PDF slides (backup offline)
- [ ] `PRESENTATION_20MIN.md` impresso ou no notebook
- [ ] `ARCHITECTURE.md` para referência técnica
- [ ] CSV com dados para mostrar

### Pessoal
- [ ] Roupa profissional
- [ ] Chegou 15 min cedo
- [ ] Respirar + calma

---

## 📞 Suporte Rápido

**Se algo der errado:**

| Problema | Solução |
|----------|---------|
| Demos não rodando | Verificar `python -m src.main` foi executado |
| BigQuery erro | Conferir `.env` e credenciais (ARCHITECTURE.md seção Troubleshooting) |
| Slides não aparecem | Testar em PDF converter ou Google Slides |
| Esqueci de algo | Leia `PRESENTATION_20MIN.md` novamente, tem tudo lá |

---

## 📚 Leitura Recomendada (Por Ordem)

1. **Mínimo (1 hora):**
   - [ ] `PRESENTATION_20MIN.md` — Leia todo
   - [ ] Pratique em voz alta

2. **Recomendado (2 horas):**
   - [ ] Leia + 1 acima
   - [ ] `ARCHITECTURE.md` seções 1-4 (visão geral + arquitetura)
   - [ ] Pratique responder perguntas
   - [ ] Rodar demos localmente

3. **Completo (3 horas):**
   - [ ] Tudo acima
   - [ ] `ARCHITECTURE.md` completo
   - [ ] `QUICK_SETUP.md` para entender fluxo
   - [ ] Revisar `GUIA_PROJETO_MONITORAMENTO_PCJ.md` original

---

## 🚀 Dia da Apresentação

**Horário:**
- Chegue 15 min antes
- Teste projetor/som
- Abra terminal com demos
- Respire fundo

**Sequência:**
1. Saudação à banca
2. Apresentação slides (20 min seguindo `PRESENTATION_20MIN.md`)
3. Demo ao vivo (inserida na parte técnica)
4. Perguntas (15 min)

**Lembre:**
- Fale claro, pausas entre ideias
- Contacto visual com avaliadores
- Se não sabe: "Bom ponto, vou verificar"
- Confiança: você domina o projeto!

---

## 📞 Links Úteis

- 📖 GitHub: https://github.com/NPLaura22/PI_V_MonitoramentoBaciasPCJ
- 📊 Dashboard: [Link do Looker Studio]
- 📧 Contato: [seu email]

---

**✅ Você está 100% preparado!**

Todos os materiais estão prontos, testados e estruturados.

**Boa sorte na banca! 🎓🚀**

---

## Índice de Arquivos

```
Raiz do Projeto/
├─ PRESENTATION_20MIN.md          ← COMECE AQUI (roteiro 20 min)
├─ PRESENTATION_SLIDES.md          ← Slides em Markdown
├─ ARCHITECTURE.md                 ← Documentação técnica
├─ QUICK_SETUP.md                  ← Setup rápido
├─ demo_pipeline_summary.py        ← Demo 1 (resumo pipeline)
├─ demo_bertopic_quick.py          ← Demo 2 (BERTopic)
├─ PRESENTATION_SCRIPT.md          ← Roteiro anterior (backup)
└─ [Este arquivo README]           ← Você está aqui
```

**Última atualização:** 2026-05-28
**Pronto para:** 2026-05-31 (segunda banca)
