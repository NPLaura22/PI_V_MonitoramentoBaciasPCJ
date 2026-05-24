"""
embedding_classifier.py

Motor central de classificação semântica por embeddings.
Zero-shot por similaridade de cosseno com âncoras calibradas.

Modelo: paraphrase-multilingual-mpnet-base-v2
"""

from sentence_transformers import SentenceTransformer, util

_modelo = None

# Limiar mínimo para considerar uma notícia relevante para PCJ
LIMIAR_RELEVANCIA = 0.40


def carregar_modelo():
    global _modelo
    if _modelo is None:
        print("[embeddings] Carregando modelo de linguagem...")
        _modelo = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        print("[embeddings] Modelo carregado.")
    return _modelo


# ---------------------------------------------------------------------------
# Âncoras de relevância PCJ
# Foco exclusivo em eventos hídricos nas bacias PCJ
# Âncoras de irrelevante reforçadas para cobrir falsos positivos observados
# ---------------------------------------------------------------------------

ANCORAS_RELEVANCIA = {
    "relevante": [
        # --- Linguagem jornalística ---
        "nível do rio Piracicaba, Capivari ou Jundiaí subiu ou caiu de forma crítica",
        "reservatório das bacias PCJ está abaixo da capacidade por estiagem",
        "enchente ou alagamento causado por chuva intensa na região de Campinas",
        "seca ou estiagem afeta o abastecimento de água em municípios da bacia PCJ",
        "comitê PCJ ou Agência PCJ divulga boletim de monitoramento hídrico",
        "defesa civil emite alerta de chuva forte ou risco de enchente para a bacia PCJ",
        "qualidade da água dos rios da bacia PCJ está comprometida por poluição",
        "racionamento ou falta de água afeta moradores de municípios da região PCJ",
        "temporal ou chuva forte causa alagamento em cidade da bacia hidrográfica PCJ",
        "rio transbordou e causou inundação em município monitorado pelas bacias PCJ",
        "contaminação ou despejo ilegal detectado em manancial que abastece a bacia PCJ",
        "alerta meteorológico de chuva intensa com risco de alagamento em município PCJ",
        "monitoramento hídrico indica queda no nível dos rios da bacia Piracicaba Capivari Jundiaí",

        # --- Linguagem técnica PCJ ---
        "cota de inundação ultrapassada no rio Piracicaba ou afluente das bacias PCJ",
        "volume útil do Sistema Cantareira ou reservatórios PCJ abaixo do limite crítico",
        "pluviometria acima da média histórica provoca alerta hidrológico nas bacias PCJ",
        "vazão do Rio Piracicaba registra queda significativa por período de estiagem",
        "estação fluviométrica das bacias PCJ registra nível crítico de alerta",
        "índice de qualidade da água IQA dos rios PCJ apresenta piora significativa",
        "afluente do Rio Capivari ou Jundiaí com contaminação detectada por análise",
        "Agência PCJ emite nota técnica sobre situação hídrica crítica das bacias",
        "Comitê das Bacias PCJ convoca reunião de emergência por evento hídrico",
        "SABESP ou concessionária reduz captação por baixo nível dos mananciais PCJ",
        "operação emergencial no Sistema Cantareira por risco de colapso hídrico",
        "DBO ou DQO acima do limite em trecho monitorado dos rios das bacias PCJ",
        "CETESB interdita captação por contaminação detectada em manancial PCJ",
        "boletim de acompanhamento do Sistema Cantareira indica volume em zona de atenção",
    ],
    "irrelevante": [
        "festival de gastronomia, show musical ou evento cultural em Campinas",
        "política nacional, declaração de político ou resultado de eleição",
        "operação policial, tráfico de drogas ou crime violento sem relação com água",
        "acidente de trânsito, queda de poste ou problema de infraestrutura elétrica",
        "petróleo, combustível, mercado financeiro ou inflação econômica",
        "saúde pública, vacina, hospital ou tratamento médico sem relação com água",
        "esporte, futebol, campeonato, Copa do Mundo ou resultado de jogo",
        "educação, universidade, vestibular, concurso público ou escola",
        "tecnologia, startup, inteligência artificial ou lançamento de produto digital",
        "obra urbana, reforma de praça ou inauguração de equipamento público",
        "notícia sobre empresa, negócios locais ou empreendedorismo",
        "receita culinária, gastronomia, restaurante ou alimento",
        "qualidade de vida no ranking de cidades, premiação ou homenagem municipal",
        "morte, homicídio, assassinato ou crime sem envolvimento de recurso hídrico",
        "produto de limpeza, detergente, sabão ou cosmético doméstico",
        "bancário, financeiro, IPTU, imposto ou tributo municipal",
        "sequestro, roubo, furto ou golpe financeiro sem relação com meio ambiente",
        "INSS, aposentadoria, benefício social ou previdência",
        "imóvel, construção civil, incorporadora ou mercado imobiliário",
        "vagas de emprego, concurso ou contratação de funcionários",
        "animais domésticos, pets ou fauna silvestre sem relação com mananciais",
        "evento esportivo, campeonato regional ou competição atlética",
        "show, festa, festival ou evento de entretenimento sem relação ambiental",
    ],
}


# ---------------------------------------------------------------------------
# Âncoras de categoria
# ---------------------------------------------------------------------------

ANCORAS_CATEGORIA = {
    "enchente_alagamento": [
        "rio transbordou e inundou ruas e casas de moradores ribeirinhos",
        "enchente deixou dezenas de famílias desabrigadas após chuva intensa",
        "alagamento interdita vias e causa destruição em bairros da cidade",
        "inundação severa atinge área residencial próxima ao rio",
        "defesa civil evacua moradores de área de risco por risco de alagamento",
        "chuva torrencial causa transbordamento de rio e inunda cidade",
        "nível do rio subiu acima da cota de inundação e afetou residências",
        # Técnico
        "nível d'água ultrapassou a cota de transbordamento nas estações de monitoramento",
        "planície de inundação atingida por enchente com famílias em abrigos temporários",
        "áreas ribeirinhas dos rios Piracicaba ou Capivari alagadas por cheia histórica",
        "defesa civil declara situação de emergência por enchente nos municípios PCJ",
    ],
    "estiagem_seca": [
        "seca severa reduz drasticamente o volume dos reservatórios hídricos",
        "estiagem prolongada ameaça o abastecimento de água da região",
        "baixa vazão dos rios preocupa autoridades e técnicos ambientais",
        "falta de chuva por meses provoca crise hídrica e seca dos rios",
        "reservatório atinge volume mínimo histórico por período sem precipitação",
        "estiagem compromete irrigação agrícola e abastecimento urbano da região",
        "nível dos mananciais cai ao menor patamar em anos por falta de chuva",
        # Técnico
        "vazão mínima de referência Q7,10 comprometida por período de estiagem severa",
        "volume útil dos reservatórios das bacias PCJ abaixo de 30% da capacidade",
        "pluviometria acumulada no trimestre inferior a 40% da média histórica esperada",
        "período de recessão hidrológica prolonga-se além do previsto nos rios PCJ",
        "índice de aridez elevado compromete recarga dos aquíferos que alimentam os rios",
    ],
    "contaminacao_poluicao": [
        "rio contaminado por esgoto doméstico ou efluente industrial lançado ilegalmente",
        "poluição química compromete qualidade da água para consumo humano",
        "mortandade massiva de peixes indica contaminação grave no manancial",
        "mancha de óleo ou produto químico tóxico detectada nas águas do rio",
        "despejo ilegal de resíduos tóxicos contamina córrego e afluentes da bacia",
        "odor forte e coloração alterada da água indicam poluição no rio",
        # Técnico
        "DBO acima do limite estabelecido pela resolução CONAMA 357 em trecho monitorado",
        "coliformes fecais detectados acima do valor máximo permitido para captação",
        "CETESB autuou indústria por lançamento de efluente sem tratamento em rio PCJ",
        "IQA ruim ou péssimo registrado por estação de monitoramento das bacias PCJ",
        "metais pesados acima do limite detectados em análise de sedimento fluvial PCJ",
        "florações de cianobactérias detectadas em reservatório de abastecimento PCJ",
    ],
    "abastecimento": [
        "falta de água deixa moradores de vários bairros sem abastecimento por dias",
        "racionamento de água é implantado em toda a cidade por escassez hídrica",
        "interrupção no fornecimento de água deixa região sem abastecimento",
        "rodízio de água é adotado para economizar reservas dos mananciais",
        "crise hídrica força restrição severa no uso e distribuição de água",
        "sistema de abastecimento colapsa por baixo nível crítico dos reservatórios",
        # Técnico
        "SABESP ou SANASA reduz pressão de distribuição por baixo nível nos mananciais",
        "sistema produtor de água opera abaixo da capacidade nominal por estiagem",
        "concessionária implanta rodízio por impossibilidade de manter fornecimento contínuo",
        "volume operacional dos reservatórios de abastecimento abaixo do volume mínimo",
        "ETA Capivari ou ETA Jaguari reduz produção por baixa disponibilidade hídrica",
        "tarifa de contingência hídrica ativada por acionamento de reserva estratégica",
    ],
    "alerta_defesa_civil": [
        "defesa civil emite alerta máximo de risco de enchente ou deslizamento de terra",
        "cemaden detecta chuvas intensas e emite aviso de risco hidrológico elevado",
        "alerta laranja ou vermelho para chuvas fortes na bacia hidrográfica PCJ",
        "sirenes de emergência são acionadas em área de risco por chuva intensa",
        "meteorologistas preveem temporal severo com risco de inundação nas próximas horas",
        "autoridades recomendam evacuação preventiva de áreas ribeirinhas de risco",
        # Técnico
        "CEMADEN emite aviso de chuva intensa com acumulado previsto acima de 50mm em 24h",
        "alerta hidrológico emitido pelo sistema de monitoramento das bacias PCJ",
        "INMET emite alerta laranja de tempestade com risco de alagamento para municípios PCJ",
        "sala de crise da defesa civil ativada por previsão de evento extremo de precipitação",
        "nível de atenção dos rios PCJ atingido com mobilização das equipes de resposta",
        "protocolo de emergência hidrológica ativado por chuva acumulada crítica",
    ],
    "monitoramento_hidrico": [
        "técnicos medem nível e qualidade da água dos rios da bacia PCJ",
        "comitê PCJ divulga boletim periódico de monitoramento dos mananciais",
        "estações fluviométricas registram variação no volume dos rios da bacia",
        "agência ambiental coleta amostras de água para análise laboratorial de rotina",
        "boletim técnico indica situação hídrica estável sem alertas ativos",
        "medição de vazão dos rios aponta tendência de queda no período de seca",
        # Técnico
        "boletim de acompanhamento do Sistema Cantareira divulgado pela SABESP e ANA",
        "relatório de monitoramento da qualidade da água das bacias PCJ publicado pela CETESB",
        "rede de monitoramento hidrológico das bacias PCJ registra dados de vazão e nível",
        "Agência PCJ publica relatório de situação dos recursos hídricos do trimestre",
        "dados telemétricos das estações fluviométricas indicam tendência de normalização",
        "reunião técnica do Comitê PCJ avalia situação dos recursos hídricos das bacias",
        "SIGRH atualiza sistema de informações sobre disponibilidade hídrica das bacias PCJ",
    ],
    "irrelevante": [
        "festival gastronômico, show cultural ou evento de entretenimento local",
        "acidente de trânsito, crime policial ou operação de segurança pública",
        "política, economia, negócios ou tecnologia sem relação com recursos hídricos",
        "saúde, educação ou esporte sem conexão com água ou meio ambiente",
        "obra urbana, inauguração de praça ou queda de poste sem impacto hídrico",
        "declaração política, notícia sobre empresa ou empreendedorismo local",
        "evento esportivo, campeonato ou competição sem relação ambiental",
    ],
}


# ---------------------------------------------------------------------------
# Âncoras de nível de risco (0 a 5)
# ---------------------------------------------------------------------------

ANCORAS_NIVEL_RISCO = {
    5: [
        "estado de calamidade pública decretado por desastre hídrico com mortes confirmadas",
        "rompimento de barragem causa destruição generalizada e óbitos na região",
        "manancial de abastecimento totalmente contaminado sem alternativa disponível",
        "interrupção completa e prolongada no abastecimento de água de toda a cidade",
        "centenas de famílias desabrigadas e mortes confirmadas por enchente severa",
        # Técnico
        "volume do Sistema Cantareira abaixo de zero no volume morto com colapso iminente",
        "DBO ou concentração de poluente em nível incompatível com qualquer uso da água",
        "enchente ultrapassa recorrência de 100 anos com destruição generalizada da bacia",
    ],
    4: [
        "enchente severa destrói casas e deixa dezenas de famílias desalojadas",
        "contaminação grave em rio de abastecimento exige interdição imediata do manancial",
        "mortandade massiva de peixes por poluição visível e extensa no rio",
        "sirenes acionadas e evacuação de bairro completo por risco alto de alagamento",
        "transbordamento do rio invade bairros residenciais causando danos e vítimas",
        "nível do rio ultrapassa cota de inundação e afeta centenas de moradores",
        # Técnico
        "volume útil dos reservatórios PCJ abaixo de 10% com risco real de colapso hídrico",
        "IQA péssimo em ponto de captação exige interrupção temporária do tratamento",
        "CEMADEN emite alerta vermelho com acumulado previsto superior a 100mm em 24h",
        "nível do rio Piracicaba ultrapassa cota de inundação severa nas estações de medição",
    ],
    3: [
        "alerta de chuva forte com risco concreto e iminente de alagamento em bairros",
        "reservatórios abaixo de 40% da capacidade por estiagem prolongada severa",
        "racionamento de água implantado afetando parte significativa da população",
        "temporal intenso causa alagamentos localizados com danos materiais relevantes",
        "nível do rio sobe acima da cota de atenção e preocupa autoridades locais",
        # Técnico
        "volume útil dos reservatórios PCJ entre 20% e 40% com tendência de queda",
        "INMET emite alerta laranja com acumulado previsto entre 50mm e 100mm em 24h",
        "IQA ruim registrado em ponto de captação com necessidade de tratamento adicional",
        "cota de atenção dos rios PCJ atingida com mobilização preventiva das equipes",
        "estiagem no terceiro mês consecutivo com vazão abaixo da Q7,10 de referência",
    ],
    2: [
        "previsão de chuvas acima da média exige monitoramento intensificado pelos órgãos",
        "reservatórios em queda gradual requerem atenção das autoridades hídricas",
        "nível do rio levemente abaixo do normal sem risco imediato à população",
        "defesa civil em estado de observação por previsão de instabilidade climática",
        "boletim aponta situação de atenção para recursos hídricos sem emergência declarada",
        # Técnico
        "volume útil entre 40% e 60% com tendência de queda exige acompanhamento técnico",
        "IQA regular em trecho monitorado com recomendação de aumento da vigilância",
        "CEMADEN emite alerta amarelo com acumulado previsto entre 20mm e 50mm em 24h",
        "vazão dos rios PCJ 20% abaixo da média histórica para o período sem crise declarada",
    ],
    1: [
        "monitoramento periódico de rotina dos rios e reservatórios sem anomalias",
        "relatório técnico indica situação hídrica dentro da normalidade esperada",
        "coleta preventiva de amostras para análise da qualidade da água",
        "previsão de chuvas dentro da média histórica sem alertas ativos",
        "boletim informativo sobre condições normais dos mananciais da bacia",
        # Técnico
        "boletim de acompanhamento indica volume útil acima de 60% sem tendência negativa",
        "IQA bom ou ótimo registrado em todos os pontos de monitoramento das bacias PCJ",
        "reunião ordinária do Comitê PCJ sem registros de situação crítica",
        "dados fluviométricos dentro da faixa de normalidade histórica para o período",
    ],
    0: [
        "notícia completamente sem relação com recursos hídricos ou meio ambiente",
        "evento social, político, policial ou cultural sem qualquer impacto hídrico",
        "assunto irrelevante para monitoramento ambiental das bacias PCJ",
        "acidente de trânsito, crime ou problema urbano sem conexão com água",
    ],
}


# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------

def calcular_scores(embedding_texto, ancoras_dict):
    modelo = carregar_modelo()
    scores = {}
    for chave, ancoras in ancoras_dict.items():
        embeddings_ancoras = modelo.encode(ancoras, convert_to_tensor=True)
        similaridades = util.cos_sim(embedding_texto, embeddings_ancoras)
        scores[chave] = float(similaridades.max())
    return scores


def classificar_relevancia(titulo: str, texto: str = "") -> dict:
    """
    Decide se uma notícia é relevante para as Bacias PCJ.
    Exige que o score de relevante supere o de irrelevante E esteja
    acima do limiar mínimo (0.42) para evitar falsos positivos.
    """
    modelo = carregar_modelo()
    texto_completo = f"{titulo}. {texto}".strip()
    embedding = modelo.encode(texto_completo, convert_to_tensor=True)
    scores = calcular_scores(embedding, ANCORAS_RELEVANCIA)

    margem = round(scores["relevante"] - scores["irrelevante"], 4)

    relevante = (
        scores["relevante"] > scores["irrelevante"]
        and scores["relevante"] >= LIMIAR_RELEVANCIA
    )

    return {
        "relevante": relevante,
        "confianca_relevante": round(scores["relevante"], 4),
        "confianca_irrelevante": round(scores["irrelevante"], 4),
        "margem": margem,
    }


def classificar_categoria(texto: str) -> dict:
    modelo = carregar_modelo()
    embedding = modelo.encode(texto, convert_to_tensor=True)
    scores = calcular_scores(embedding, ANCORAS_CATEGORIA)
    melhor = max(scores, key=scores.get)

    return {
        "categoria": melhor,
        "confianca": round(scores[melhor], 4),
        "scores": {k: round(v, 4) for k, v in scores.items()},
    }


def classificar_nivel_risco(texto: str, relevante_pcj: bool) -> dict:
    """
    Classifica o nível de risco de 0 a 5.
    Se não for relevante para PCJ, retorna 0 diretamente.
    """
    if not relevante_pcj:
        return {
            "nivel_risco": 0,
            "confianca": 1.0,
            "scores": {},
        }

    modelo = carregar_modelo()
    embedding = modelo.encode(texto, convert_to_tensor=True)
    scores = calcular_scores(embedding, ANCORAS_NIVEL_RISCO)
    melhor_nivel = max(scores, key=scores.get)

    return {
        "nivel_risco": int(melhor_nivel),
        "confianca": round(scores[melhor_nivel], 4),
        "scores": {str(k): round(v, 4) for k, v in scores.items()},
    }
