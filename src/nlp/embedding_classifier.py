"""
embedding_classifier.py

Motor central de classificação semântica por embeddings.
Zero-shot por similaridade de cosseno com âncoras calibradas.

Modelo: paraphrase-multilingual-MiniLM-L12-v2
"""

from sentence_transformers import SentenceTransformer, util

_modelo = None

# Limiar mínimo para considerar uma notícia relevante para PCJ.
# A notícia precisa superar esse score para ser marcada como relevante,
# mesmo que vença a categoria "irrelevante". Isso evita falsos positivos.
LIMIAR_RELEVANCIA = 0.38


def carregar_modelo():
    global _modelo
    if _modelo is None:
        print("[embeddings] Carregando modelo de linguagem...")
        _modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("[embeddings] Modelo carregado.")
    return _modelo


# ---------------------------------------------------------------------------
# Âncoras de relevância PCJ
# Foco exclusivo em eventos hídricos nas bacias PCJ — não apenas mencionar Campinas
# ---------------------------------------------------------------------------

ANCORAS_RELEVANCIA = {
    "relevante": [
        "nível do rio Piracicaba, Capivari ou Jundiaí subiu ou caiu de forma crítica",
        "reservatório das bacias PCJ está abaixo da capacidade por estiagem",
        "enchente ou alagamento causado por chuva intensa na região de Campinas",
        "seca ou estiagem afeta o abastecimento de água em Campinas ou municípios da bacia PCJ",
        "comitê PCJ ou Agência PCJ divulga boletim de monitoramento hídrico",
        "defesa civil emite alerta de chuva forte ou risco de enchente para a bacia PCJ",
        "qualidade da água dos rios da bacia PCJ está comprometida por poluição ou contaminação",
        "racionamento ou falta de água afeta moradores de municípios da região PCJ",
        "temporal ou chuva forte causa alagamento em cidade da bacia hidrográfica PCJ",
        "rio transbordou e causou inundação em município monitorado pelas bacias PCJ",
        "contaminação ou despejo ilegal detectado em manancial que abastece a bacia PCJ",
        "análise técnica aponta alteração na qualidade da água dos rios Piracicaba ou Jundiaí",
    ],
    "irrelevante": [
        "festival de gastronomia, show musical ou evento cultural em Campinas",
        "política nacional, declaração de político ou resultado de eleição",
        "operação policial, tráfico de drogas ou crime sem relação com água",
        "acidente de trânsito, queda de poste ou problema de infraestrutura elétrica",
        "petróleo, combustível, mercado financeiro ou inflação econômica",
        "saúde pública, vacina, hospital ou tratamento médico sem relação com água",
        "esporte, futebol, campeonato ou resultado de jogo",
        "educação, universidade, vestibular ou concurso público",
        "tecnologia, startup, inteligência artificial ou lançamento de produto",
        "caminhão cai em córrego ou acidente de carro sem impacto hídrico",
        "obra urbana, reforma de praça ou inauguração de equipamento público",
        "notícia sobre empresa, negócios locais ou empreendedorismo",
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
    ],
    "estiagem_seca": [
        "seca severa reduz drasticamente o volume dos reservatórios hídricos",
        "estiagem prolongada ameaça o abastecimento de água da região",
        "baixa vazão dos rios preocupa autoridades e técnicos ambientais",
        "falta de chuva por meses provoca crise hídrica e seca dos rios",
        "reservatório atinge volume mínimo histórico por período prolongado sem precipitação",
        "estiagem compromete irrigação agrícola e abastecimento urbano da região",
        "nível dos mananciais cai ao menor patamar em anos por falta de chuva",
    ],
    "contaminacao_poluicao": [
        "rio contaminado por esgoto doméstico ou efluente industrial lançado ilegalmente",
        "poluição química compromete qualidade da água para consumo humano",
        "mortandade massiva de peixes indica contaminação grave no manancial",
        "mancha de óleo ou produto químico tóxico detectada nas águas do rio",
        "análise laboratorial aponta poluentes acima do limite legal permitido",
        "despejo ilegal de resíduos tóxicos contamina córrego e afluentes da bacia",
        "odor forte e coloração alterada da água indicam poluição no rio",
    ],
    "abastecimento": [
        "falta de água deixa moradores de vários bairros sem abastecimento por dias",
        "racionamento de água é implantado em toda a cidade por escassez hídrica",
        "interrupção no fornecimento de água deixa região sem abastecimento",
        "rodízio de água é adotado para economizar reservas dos mananciais",
        "companhia de saneamento alerta para possível colapso no abastecimento urbano",
        "crise hídrica força restrição severa no uso e distribuição de água",
        "sistema de abastecimento colapsa por baixo nível crítico dos reservatórios",
    ],
    "alerta_defesa_civil": [
        "defesa civil emite alerta máximo de risco de enchente ou deslizamento de terra",
        "cemaden detecta chuvas intensas e emite aviso de risco hidrológico elevado",
        "alerta laranja ou vermelho para chuvas fortes na bacia hidrográfica PCJ",
        "sirenes de emergência são acionadas em área de risco por chuva intensa",
        "meteorologistas preveem temporal severo com risco de inundação nas próximas horas",
        "autoridades recomendam evacuação preventiva de áreas ribeirinhas de risco",
        "alerta meteorológico emitido por chuvas acumuladas acima da média histórica",
    ],
    "monitoramento_hidrico": [
        "técnicos medem nível e qualidade da água dos rios da bacia PCJ",
        "comitê PCJ divulga boletim periódico de monitoramento dos mananciais",
        "estações fluviométricas registram variação no volume dos rios da bacia",
        "agência ambiental coleta amostras de água para análise laboratorial de rotina",
        "boletim técnico indica situação hídrica estável sem alertas ativos",
        "medição de vazão dos rios aponta tendência de queda no período de seca",
        "relatório técnico apresenta dados de qualidade e quantidade dos recursos hídricos",
    ],
    "irrelevante": [
        "festival gastronômico, show cultural ou evento de entretenimento local",
        "acidente de trânsito, crime policial ou operação de segurança pública",
        "política, economia, negócios ou tecnologia sem relação com recursos hídricos",
        "saúde, educação ou esporte sem conexão com água ou meio ambiente",
        "obra urbana, inauguração de praça ou queda de poste sem impacto hídrico",
        "declaração política, notícia sobre empresa ou empreendedorismo local",
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
    ],
    4: [
        "enchente severa destrói casas e deixa dezenas de famílias desalojadas",
        "contaminação grave em rio de abastecimento exige interdição imediata do manancial",
        "mortandade massiva de peixes por poluição visível e extensa no rio",
        "sirenes acionadas e evacuação de bairro completo por risco alto de alagamento",
        "transbordamento do rio invade bairros residenciais causando danos e vítimas",
        "nível do rio ultrapassa cota de inundação e afeta centenas de moradores",
    ],
    3: [
        "alerta de chuva forte com risco concreto e iminente de alagamento em bairros",
        "reservatórios abaixo de 40% da capacidade por estiagem prolongada severa",
        "racionamento de água implantado afetando parte significativa da população",
        "temporal intenso causa alagamentos localizados com danos materiais relevantes",
        "nível do rio sobe acima da cota de atenção e preocupa autoridades locais",
        "risco hidrológico moderado com previsão de agravamento nas próximas horas",
    ],
    2: [
        "previsão de chuvas acima da média exige monitoramento intensificado pelos órgãos",
        "reservatórios em queda gradual requerem atenção das autoridades hídricas",
        "nível do rio levemente abaixo do normal sem risco imediato à população",
        "defesa civil em estado de observação por previsão de instabilidade climática",
        "boletim aponta situação de atenção para recursos hídricos sem emergência declarada",
    ],
    1: [
        "monitoramento periódico de rotina dos rios e reservatórios sem anomalias",
        "relatório técnico indica situação hídrica dentro da normalidade esperada",
        "coleta preventiva de amostras para análise da qualidade da água",
        "previsão de chuvas dentro da média histórica sem alertas ativos",
        "boletim informativo sobre condições normais dos mananciais da bacia",
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
    acima do limiar mínimo para evitar falsos positivos.
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
