# ════════════════════════════════════════════════════════════════════════
# DOA INTELIGENTE — sua generosidade merece inteligência (arquivo único)
# MeusAgentesIA.com.br
#
# Antes de doar, verifique. Depois de doar, acompanhe. Sinta o seu impacto.
#
# COMO PUBLICAR
#   Coloque SÓ este arquivo num repositório do GitHub e publique no
#   Streamlit Cloud (share.streamlit.io). Não precisa de requirements.txt:
#   usa só o que já vem com o Streamlit (requests, pandas, altair).
#   Cada pessoa entra com o próprio nome e a própria chave Groq (grátis).
#
# PRINCÍPIOS
#   • O app é ESCLARECEDOR: não recebe, não repassa e não intermedeia
#     dinheiro, e não indica onde doar. Ele mostra o que foi verificado,
#     o que NÃO foi comprovado e os sinais de alerta.
#   • CNPJ ativo NÃO é sinônimo de confiável. Cada critério do Índice de
#     Confiança aparece como comprovado, informado por você, não
#     comprovado ou alerta.
#   • Dados públicos: Receita Federal (via BrasilAPI / CNPJ.ws) e, com
#     chave gratuita opcional, Portal da Transparência (CEIS, CNEP, CEPIM).
# ════════════════════════════════════════════════════════════════════════
import json
import os
import re
import unicodedata
import uuid
from datetime import date, datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Doa Inteligente", page_icon="💚", layout="wide")

SITE = "https://meusagentesia.com.br"
GROQ_URL = os.environ.get("DI_GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")
BRASILAPI = os.environ.get("DI_BRASILAPI", "https://brasilapi.com.br/api/cnpj/v1/")
CNPJWS = os.environ.get("DI_CNPJWS", "https://publica.cnpj.ws/cnpj/")
TRANSP = os.environ.get("DI_TRANSP", "https://api.portaldatransparencia.gov.br/api-de-dados/")
MODELOS = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
HOJE = date.today()
S = st.session_state
UA = {"User-Agent": "Mozilla/5.0 (DoaInteligente; +https://meusagentesia.com.br)", "Accept": "application/json"}

# ══════════════════════════════════════════════════════════════════════════
# VISUAL — claro e acolhedor (verde-água + coral)
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Nunito',sans-serif;}
.stApp {background:#F6FBFA;}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stMarkdown {color:#1E2E2D;}
h1,h2,h3,h4 {color:#0B4F4C !important;}
.stTabs [data-baseweb="tab-list"] {gap:2px; overflow-x:auto;}
.stTabs [data-baseweb="tab"] {background:#E3F3F1; border-radius:10px 10px 0 0; padding:8px 14px; color:#0B4F4C;}
.stTabs [aria-selected="true"] {background:#0E7C7B !important;}
.stTabs [aria-selected="true"] p {color:#fff !important;}
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  background:#0E7C7B; color:#fff !important; border:none; border-radius:12px; font-weight:700; min-height:2.8em;}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {background:#0A5F5E; color:#fff !important;}
.stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {color:#fff !important;}
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {background:#fff !important; color:#1E2E2D !important;}
div[data-baseweb="select"] > div {background:#fff !important; color:#1E2E2D !important;}
.card {background:#fff; border:1px solid #CFE7E4; border-radius:16px; padding:16px 18px; margin-bottom:10px;}
.cab {background:linear-gradient(135deg,#0E7C7B,#14A39E); border-radius:18px; padding:20px 24px; margin-bottom:12px;}
.cab h1, .stApp .cab h1, .stApp .cab h1 span {color:#fff !important; margin:0; font-size:2em;}
.cab p {color:#E2FBF8 !important; margin:4px 0 0 0;}
.cab .lema {color:#FFE3D9 !important; font-weight:700;}
.kpi {background:#fff; border:1px solid #CFE7E4; border-radius:16px; padding:14px; text-align:center;}
.kpi .v {font-size:1.6em; font-weight:800; color:#0B4F4C; font-variant-numeric:tabular-nums;}
.kpi .l {font-size:.8em; color:#4E6765; text-transform:uppercase; letter-spacing:.04em;}
.selo {display:inline-block; background:#FF7A59; color:#fff !important; border-radius:20px; padding:4px 12px; font-weight:700; font-size:.85em;}
.crit {display:flex; gap:10px; align-items:flex-start; background:#fff; border:1px solid #E1EFED; border-radius:12px; padding:10px 14px; margin-bottom:6px;}
.crit .ic {font-size:1.25em; line-height:1.2;}
.crit .st {font-size:.75em; font-weight:800; letter-spacing:.04em; text-transform:uppercase;}
.crit.ok {border-left:6px solid #138A55;} .crit.ok .st {color:#138A55 !important;}
.crit.info {border-left:6px solid #2C6FD1;} .crit.info .st {color:#2C6FD1 !important;}
.crit.nd {border-left:6px solid #9AA9A7;} .crit.nd .st {color:#6B7F7D !important;}
.crit.alerta {border-left:6px solid #D64527;} .crit.alerta .st {color:#D64527 !important;}
.indice {border-radius:20px; padding:20px; text-align:center; color:#fff;}
.indice .n {font-size:3.2em; font-weight:800; line-height:1; color:#fff !important;}
.indice .f {font-size:1.1em; font-weight:800; color:#fff !important;}
.indice p, .indice span {color:#fff !important;}
.explorar {background:#FFF1EC; border:2px solid #FF7A59; border-radius:18px; padding:14px 16px; margin:4px 0 10px 0;}
.explorar .t {font-weight:800; color:#9A3412 !important; letter-spacing:.03em; margin-bottom:10px;}
.passos {display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:8px;}
.passo {display:flex; gap:8px; align-items:flex-start; background:#fff; border:1px solid #FFD2C4; border-radius:12px; padding:8px 10px; font-size:.86em; line-height:1.3;}
.passo .n {flex:0 0 26px; height:26px; border-radius:50%; background:#FF7A59; color:#fff !important; font-weight:800; display:flex; align-items:center; justify-content:center;}
.passo.ok .n {background:#138A55;}
.passo span {color:#4E6765 !important;}
.medalha {background:#fff; border:1px solid #CFE7E4; border-radius:14px; padding:12px; text-align:center; min-height:120px;}
.medalha .e {font-size:2em;} .medalha.off {opacity:.4; filter:grayscale(1);}
.aviso {font-size:.82em; color:#4E6765 !important;}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# CONTEÚDO
# ══════════════════════════════════════════════════════════════════════════
CAUSAS = ["Fome e alimentação", "Saúde", "Crianças e adolescentes", "Idosos", "Pessoas com deficiência", "Animais",
          "Educação", "Emergências e desastres", "Moradia e população de rua", "Meio ambiente", "Cultura e esporte",
          "Mulheres e vítimas de violência", "Outra"]

# Naturezas jurídicas do grupo 3 (IBGE/Receita) = entidades sem fins lucrativos
NATUREZA_SEM_FINS = "3"
NOMES_NATUREZA = {"3999": "Associação privada", "3069": "Fundação privada", "3220": "Organização religiosa",
                  "3301": "Organização social (OS)", "3204": "Fundação ou associação estrangeira no Brasil",
                  "3131": "Entidade sindical"}
# Prefixos de CNAE ligados a atividades sociais, de saúde, educação, defesa de direitos, cultura e religião
CNAE_SOCIAIS = ("87", "88", "9430", "9491", "9493", "9499", "85", "86", "9001", "9102", "9103", "9311", "9312", "9319")

GOLPES_COMUNS = [
    "Pedido de PIX para **CPF de uma pessoa** em nome de uma 'instituição'.",
    "Campanha criada **logo depois de uma tragédia**, por perfil novo ou desconhecido.",
    "**Pressa e culpa**: 'só hoje', 'se você não ajudar, ele morre', 'compartilhe ou...'.",
    "Perfil **clonado** de ONG conhecida, com nome parecido e chave PIX diferente da oficial.",
    "**Falso parente ou amigo** pedindo dinheiro para emergência por mensagem.",
    "Promessa de **prêmio ou sorteio** em troca da doação.",
    "**Sem fotos com data, sem notas e sem prestação de contas** — só histórias emocionantes.",
]

CURSOS = [
    ("d1", "Golpes mais comuns em doações", [
        "Golpistas usam a **emoção**: fotos fortes, pressa ('só hoje') e culpa. Quanto mais pressão, mais calma você precisa ter.",
        "Os golpes mais comuns: PIX para CPF de terceiros em nome de 'ONG', perfil clonado de instituição conhecida, vaquinha falsa depois de tragédias e falso parente pedindo dinheiro.",
        "Desconfie de campanhas **sem nome completo do responsável**, sem endereço, sem prestação de contas e que só aceitam PIX para pessoa física.",
        "Na dúvida, **não doe na hora**: pesquise, ligue para a instituição pelo telefone do site oficial e confira a chave PIX.",
    ], [
        ("Uma 'ONG' pede PIX para o CPF de uma pessoa. Isso é:", ["Normal", "Um sinal de alerta importante", "Obrigatório por lei", "Mais seguro"], 1, "Instituições sérias costumam receber em conta com o CNPJ delas."),
        ("A mensagem diz 'só hoje, ou será tarde demais'. O melhor é:", ["Doar na hora", "Ter calma e verificar antes", "Compartilhar sem ler", "Doar o dobro"], 1, "Pressa é uma ferramenta comum de golpe."),
        ("Como confirmar a chave PIX de uma ONG conhecida?", ["Pelo comentário de um perfil", "Pelo site ou canal oficial da instituição", "Pelo primeiro resultado de anúncio", "Pelo grupo de mensagens"], 1, "Use sempre o canal oficial."),
    ]),
    ("d2", "Como verificar uma instituição", [
        "Peça o **CNPJ** e confira: situação **ativa**, tempo de existência, **natureza jurídica** (associação, fundação, organização religiosa) e **atividade** compatível com a causa.",
        "**CNPJ ativo não quer dizer confiável**: só mostra que a entidade existe no papel. Confiança vem de **transparência** e **comprovação de entregas**.",
        "Procure: site com **estatuto**, nomes da **diretoria**, **relatório anual**, **prestação de contas** e fotos de entregas com data.",
        "Confira se a entidade está impedida de receber dinheiro público (CEPIM) ou sancionada (CEIS, CNEP) no **Portal da Transparência**, e veja o **Mapa das OSCs** do IPEA.",
    ], [
        ("Um CNPJ ativo garante que a instituição é confiável?", ["Sim, sempre", "Não: mostra só que ela existe no papel", "Sim, se tiver site", "Só se for fundação"], 1, "Existência não é o mesmo que boa gestão."),
        ("Qual destes é o sinal MAIS forte de seriedade?", ["Muitos seguidores", "Prestação de contas pública e relatório de atividades", "Fotos tristes", "Logo bonito"], 1, "Transparência é o que mais pesa."),
        ("Uma 'instituição' tem CNPJ de empresa de comércio aberto há 1 mês. Isso:", ["É ótimo", "Merece atenção: não combina com uma entidade social", "Não importa", "É obrigatório"], 1, "Natureza e atividade devem combinar com a causa."),
    ]),
    ("d3", "Vaquinhas de pessoas físicas", [
        "Vaquinhas para uma pessoa ou família são legítimas e muitas vezes salvam vidas — mas **não têm CNPJ** para conferir. A verificação depende de outros sinais.",
        "Procure: **beneficiário identificado**, contato direto com a família, **documentos** (laudo, orçamento do hospital), **atualizações** de como o dinheiro está sendo usado.",
        "Prefira plataformas de vaquinha conhecidas, com regras de saque e denúncia, e confira se o **nome do recebedor do PIX** é o do beneficiário ou de alguém próximo identificado.",
        "Melhor ainda quando **você conhece alguém** que conhece a família, ou quando há notícia em veículo de imprensa conhecido.",
    ], [
        ("O que mais ajuda a confiar numa vaquinha para tratamento?", ["Muitos emojis", "Laudo e orçamento, beneficiário identificado e atualizações", "Pedir sigilo", "Ter pressa"], 1, "Documentos e acompanhamento são a base."),
        ("Ao digitar o PIX, aparece o nome de um desconhecido, diferente do beneficiário. Você:", ["Doa mesmo assim", "Para e pergunta quem é essa pessoa antes de doar", "Doa o dobro", "Ignora"], 1, "O nome do recebedor precisa fazer sentido."),
        ("Vaquinha de pessoa física tem CNPJ para consultar?", ["Sim", "Não, por isso outros sinais pesam mais", "Só às vezes", "Sempre na Receita"], 1, "Sem CNPJ, os outros sinais são essenciais."),
    ]),
    ("d4", "Prestação de contas: o que pedir", [
        "Você tem o direito de perguntar: **quanto foi arrecadado, quanto foi gasto e em quê**.",
        "Boa prestação de contas tem **valores**, **notas ou recibos**, **fotos com data** e **resultados** (quantas famílias, refeições, atendimentos).",
        "Entidades maiores costumam publicar **balanço** e **relatório anual**; algumas têm auditoria independente.",
        "Se a instituição se recusa a explicar ou fica ofendida com a pergunta, isso também é uma informação importante.",
    ], [
        ("O que uma boa prestação de contas mostra?", ["Só frases de agradecimento", "Valores, comprovantes e resultados", "Apenas o logo", "Nada, é sigilosa"], 1, "Números e comprovantes são o essencial."),
        ("Perguntar como o dinheiro foi usado é:", ["Falta de educação", "Um direito de quem doa", "Proibido", "Inútil"], 1, "Instituições sérias gostam de mostrar resultados."),
        ("Uma ONG grande que publica relatório anual auditado está:", ["Escondendo algo", "Mostrando um bom nível de transparência", "Fora da lei", "Pedindo mais dinheiro"], 1, "Auditoria e relatório são bons sinais."),
    ]),
    ("d5", "Doação e imposto de renda", [
        "Para **pessoa física**, doações comuns a ONGs **não abatem** o imposto de renda.",
        "Abatem (até **6% do imposto devido**, só na **declaração completa**): doações a **Fundos dos Direitos da Criança e do Adolescente**, **Fundos do Idoso**, projetos aprovados de **cultura**, **audiovisual**, **esporte** e programas de saúde como **PRONON e PRONAS/PCD**.",
        "Na hora de fazer a declaração, dá para **destinar parte do imposto** diretamente aos Fundos da Criança e do Idoso, pelo próprio programa da Receita.",
        "Guarde sempre o **recibo** com CNPJ, valor e data. As regras podem mudar: confirme no site da Receita Federal.",
    ], [
        ("Uma doação comum a uma ONG pode ser abatida no IR de pessoa física?", ["Sim, integralmente", "Em regra, não", "Sim, até 50%", "Só em dinheiro vivo"], 1, "Só doações a fundos e projetos incentivados abatem."),
        ("Qual o limite de dedução para doações incentivadas de pessoa física?", ["Até 6% do imposto devido", "100% da renda", "R$ 100 por ano", "Não há limite"], 0, "O limite geral é de 6% do imposto devido."),
        ("Para usar essas deduções, a declaração precisa ser:", ["Simplificada", "Completa", "Qualquer uma", "Feita em papel"], 1, "Só a declaração completa permite."),
    ]),
    ("d6", "Outras formas de ajudar", [
        "Ajudar não é só dinheiro: **voluntariado**, doação de **alimentos, roupas e móveis**, **doação de sangue**, ensinar o que você sabe, divulgar uma causa séria.",
        "Pergunte à instituição **do que ela realmente precisa**. Muitas vezes falta algo específico (fraldas geriátricas, ração, material escolar) e sobra outra coisa.",
        "**Doação recorrente** (todo mês, mesmo pequena) ajuda a instituição a planejar e costuma ter mais impacto do que uma doação grande isolada.",
        "Ajudar perto de você, onde você consegue **ver o resultado**, também é uma forma de doar com segurança.",
    ], [
        ("Por que a doação recorrente é valiosa para a instituição?", ["Porque é maior", "Porque permite planejar", "Porque abate IR", "Porque é obrigatória"], 1, "Previsibilidade ajuda a manter os projetos."),
        ("Antes de doar itens, o ideal é:", ["Levar qualquer coisa", "Perguntar o que a instituição precisa", "Doar só roupas", "Não avisar"], 1, "Necessidades mudam; pergunte antes."),
        ("Doar tempo como voluntário é:", ["Uma forma de ajudar", "Proibido", "Só para empresas", "Inútil"], 0, "Tempo e habilidades valem muito."),
    ]),
]
CUR = {c[0]: c for c in CURSOS}

LINKS_CONFERIR = [
    ("Consulta de CNPJ na Receita Federal", "https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpj_solicitacao.asp"),
    ("Mapa das Organizações da Sociedade Civil (IPEA)", "https://mapaosc.ipea.gov.br"),
    ("Portal da Transparência — sanções e entidades impedidas", "https://portaldatransparencia.gov.br/sancoes"),
    ("Chave gratuita da API do Portal da Transparência", "https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email"),
]

MEDALHAS = [
    ("primeira", "🌱", "Primeiro gesto", "Registrou a primeira ajuda"),
    ("consciente", "🛡️", "Doador consciente", "Verificou 3 campanhas ou instituições"),
    ("diversidade", "🌈", "Coração plural", "Ajudou 3 causas diferentes"),
    ("constancia", "🔁", "Constância", "Ajudou em 3 meses diferentes"),
    ("recibo", "🧾", "Recibo na mão", "Guardou recibo de 5 doações"),
    ("fiscal", "🔍", "Fiscal do bem", "Confirmou a entrega de 3 doações"),
    ("voluntario", "🙌", "Mãos que ajudam", "Registrou 10 horas de voluntariado"),
    ("estudante", "🎓", "Sabe doar", "Concluiu os 6 cursos de doação segura"),
    ("alerta", "🚨", "Golpe evitado", "Uma verificação com alto risco que você não doou"),
]

DESAFIOS = [
    ("verificar3", "Verificar 3 campanhas antes de doar", lambda m: m["verif_mes"], 3),
    ("causas2", "Ajudar 2 causas diferentes", lambda m: m["causas_mes"], 2),
    ("recibos", "Guardar o recibo de todas as doações do mês (mín. 2)", lambda m: m["recibos_mes"], 2),
    ("voluntario", "Fazer 4 horas de voluntariado", lambda m: m["horas_mes"], 4),
    ("itens", "Doar itens (alimentos, roupas, ração) 2 vezes", lambda m: m["itens_mes"], 2),
]

REGRA_IA = (
    "Você é o assistente do DOA INTELIGENTE, um app brasileiro e ESCLARECEDOR que ajuda pessoas a doar com segurança. "
    "Escreva em português do Brasil, com acolhimento, clareza e frases curtas. REGRAS: 1) Você não recebe doações e não "
    "indica onde doar; ajuda a pessoa a verificar, entender riscos e fazer boas perguntas. 2) Nunca afirme que uma "
    "instituição é confiável ou que é golpe com certeza: diga o que os dados mostram, o que falta comprovar e como "
    "conferir. 3) Use SOMENTE os dados fornecidos pelo app; não invente CNPJ, nomes, valores ou notícias. 4) Lembre que "
    "CNPJ ativo não é sinônimo de confiável. 5) Imposto de renda: para pessoa física, doações comuns a ONGs não abatem o "
    "IR; abatem, até 6% do imposto devido e só na declaração completa, doações a Fundos da Criança e do Adolescente, "
    "Fundos do Idoso e projetos incentivados (cultura, audiovisual, esporte, PRONON, PRONAS/PCD) — peça para confirmar "
    "na Receita Federal. 6) Se a pessoa já caiu num golpe, oriente: registrar boletim de ocorrência, avisar o banco e "
    "pedir o MED (Mecanismo Especial de Devolução do PIX) o quanto antes, e guardar prints."
)

# ══════════════════════════════════════════════════════════════════════════
# ESTADO
# ══════════════════════════════════════════════════════════════════════════
CHAVES_MEMORIA = ["d_nome", "verificacoes", "doacoes", "cursos", "chat", "desafio", "transp_key"]
PADRAO = {"d_nome": "", "d_chave": "", "verificacoes": [], "doacoes": [], "cursos": {}, "chat": [], "desafio": "",
          "transp_key": "", "ver": 0, "resultado": None, "quiz": None}
for k, v in PADRAO.items():
    if k not in S:
        S[k] = json.loads(json.dumps(v)) if isinstance(v, (dict, list)) else v


# ══════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════════════
def brl(v):
    try:
        s = f"{float(v):,.2f}"
    except Exception:
        return "R$ —"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def br_data(iso):
    try:
        return datetime.fromisoformat(str(iso)[:10]).strftime("%d/%m/%Y")
    except Exception:
        return str(iso or "—")


def so_digitos(t):
    return re.sub(r"\D", "", str(t or ""))


def fmt_cnpj(c):
    c = so_digitos(c)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def cnpj_valido(c):
    c = so_digitos(c)
    if len(c) != 14 or c == c[0] * 14:
        return False
    def dv(base, pesos):
        s = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    d1 = dv(c[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = dv(c[:12] + d1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return c[12:] == d1 + d2


def cpf_valido(c):
    c = so_digitos(c)
    if len(c) != 11 or c == c[0] * 11:
        return False
    for n in (9, 10):
        s = sum(int(c[i]) * (n + 1 - i) for i in range(n)) * 10 % 11
        if s % 10 != int(c[n]):
            return False
    return True


def normalizar(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    vazias = {"de", "da", "do", "das", "dos", "e", "a", "o", "ltda", "me", "eireli", "s", "sa", "instituto", "associacao",
              "fundacao", "ong", "projeto", "casa", "lar", "grupo"}
    return [p for p in t.split() if p and p not in vazias and len(p) > 1]


def nomes_parecidos(a, b):
    """Proporção de palavras importantes em comum entre dois nomes (0 a 1)."""
    pa, pb = set(normalizar(a)), set(normalizar(b))
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / min(len(pa), len(pb))


def tipo_pix(chave):
    k = str(chave or "").strip()
    d = so_digitos(k)
    if not k:
        return "vazia", ""
    if "@" in k:
        return "e-mail", k.lower()
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", k):
        return "aleatória", k
    if len(d) == 14 and cnpj_valido(d):
        return "CNPJ", d
    if len(d) == 11 and cpf_valido(d) and not k.startswith("+"):
        return "CPF", d
    if 10 <= len(d) <= 13:
        return "telefone", d
    return "desconhecida", k


# ══════════════════════════════════════════════════════════════════════════
# IA (GROQ)
# ══════════════════════════════════════════════════════════════════════════
def ia(mensagens, max_tokens=1500, temperatura=0.4, json_mode=False):
    ultimo = "Não consegui falar com a IA."
    for modelo in MODELOS:
        corpo = {"model": modelo, "messages": mensagens, "temperature": temperatura, "max_tokens": max_tokens}
        if json_mode:
            corpo["response_format"] = {"type": "json_object"}
        try:
            r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {S.d_chave}", "Content-Type": "application/json"},
                              json=corpo, timeout=90)
        except requests.RequestException:
            ultimo = "Sem conexão com a IA agora. Tente de novo em instantes."
            continue
        if r.status_code == 200:
            try:
                return r.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                continue
        if r.status_code in (401, 403):
            raise RuntimeError("A Groq recusou a sua chave. Clique em Sair e entre com a chave certa (começa com gsk_).")
        if r.status_code == 429:
            raise RuntimeError("Você atingiu o limite de uso grátis da Groq por agora. Espere alguns minutos e tente de novo.")
        ultimo = f"A IA respondeu com erro ({r.status_code})."
    raise RuntimeError(ultimo)


def analisar_texto(texto):
    """A IA procura sinais de manipulação/golpe no texto da campanha. Devolve dict ou None."""
    if not texto or len(texto.strip()) < 30:
        return None
    pedido = (
        "Analise o texto de um pedido de doação e aponte SINAIS objetivos (não certezas). Procure: pressa extrema, culpa ou "
        "ameaça emocional, promessa de prêmio, pedido de sigilo, falta de identificação do responsável ou do beneficiário, "
        "ausência de prestação de contas, pedido de PIX para pessoa física em nome de instituição, valores ou histórias "
        "incoerentes, erros que sugerem cópia. Aponte também SINAIS POSITIVOS (identificação clara, documentos citados, "
        "prestação de contas, contato oficial). Responda em JSON: "
        '{"alertas":[{"sinal":"...","trecho":"...","por_que":"..."}],"positivos":["..."],"nivel":"baixo|medio|alto",'
        '"perguntas":["perguntas que a pessoa deveria fazer antes de doar"]}\n\nTEXTO:\n' + texto[:4000])
    msgs = [{"role": "system", "content": REGRA_IA + " Responda SOMENTE com JSON válido."}, {"role": "user", "content": pedido}]
    try:
        try:
            txt = ia(msgs, max_tokens=1200, json_mode=True)
        except RuntimeError as e:
            if "chave" in str(e) or "limite" in str(e):
                raise
            txt = ia(msgs, max_tokens=1200)
        m = re.search(r"\{.*\}", txt, re.S)
        d = json.loads(m.group(0)) if m else None
        if d and d.get("nivel") not in ("baixo", "medio", "alto"):
            d["nivel"] = "medio"
        return d
    except RuntimeError as e:
        return {"erro": str(e)}
    except Exception:
        return {"erro": "A IA não conseguiu analisar o texto agora."}


# ══════════════════════════════════════════════════════════════════════════
# CONSULTAS PÚBLICAS
# ══════════════════════════════════════════════════════════════════════════
def consultar_cnpj(cnpj):
    """Dados públicos da Receita. Tenta BrasilAPI e, se falhar, CNPJ.ws. Devolve dict padronizado ou None."""
    c = so_digitos(cnpj)
    try:
        r = requests.get(BRASILAPI + c, headers=UA, timeout=15)
        if r.status_code == 200:
            d = r.json()
            return {
                "fonte": "Receita Federal (via BrasilAPI)",
                "razao": d.get("razao_social") or "", "fantasia": d.get("nome_fantasia") or "",
                "situacao": (d.get("descricao_situacao_cadastral") or "").upper(),
                "data_situacao": d.get("data_situacao_cadastral") or "",
                "abertura": d.get("data_inicio_atividade") or "",
                "natureza_cod": so_digitos(d.get("codigo_natureza_juridica")), "natureza": d.get("natureza_juridica") or "",
                "cnae": so_digitos(d.get("cnae_fiscal")), "cnae_desc": d.get("cnae_fiscal_descricao") or "",
                "socios": [{"nome": s.get("nome_socio", ""), "qualif": s.get("qualificacao_socio", "")} for s in (d.get("qsa") or [])],
                "cidade": d.get("municipio") or "", "uf": d.get("uf") or "",
                "email": d.get("email") or "", "telefone": d.get("ddd_telefone_1") or "",
            }
        if r.status_code == 404:
            return {"inexistente": True}
    except Exception:
        pass
    try:
        r = requests.get(CNPJWS + c, headers=UA, timeout=15)
        if r.status_code == 200:
            d = r.json()
            est = d.get("estabelecimento") or {}
            nat = d.get("natureza_juridica") or {}
            ativ = est.get("atividade_principal") or {}
            return {
                "fonte": "Receita Federal (via CNPJ.ws)",
                "razao": d.get("razao_social") or "", "fantasia": est.get("nome_fantasia") or "",
                "situacao": (est.get("situacao_cadastral") or "").upper(), "data_situacao": est.get("data_situacao_cadastral") or "",
                "abertura": est.get("data_inicio_atividade") or "",
                "natureza_cod": so_digitos(nat.get("id")), "natureza": nat.get("descricao") or "",
                "cnae": so_digitos(ativ.get("id") or ativ.get("subclasse")), "cnae_desc": ativ.get("descricao") or "",
                "socios": [{"nome": s.get("nome", ""), "qualif": (s.get("qualificacao_socio") or {}).get("descricao", "")} for s in (d.get("socios") or [])],
                "cidade": (est.get("cidade") or {}).get("nome", ""), "uf": (est.get("estado") or {}).get("sigla", ""),
                "email": est.get("email") or "", "telefone": (est.get("ddd1") or "") + (est.get("telefone1") or ""),
            }
        if r.status_code == 404:
            return {"inexistente": True}
    except Exception:
        pass
    return None


def consultar_sancoes(cnpj):
    """CEIS, CNEP e CEPIM no Portal da Transparência (precisa de chave gratuita). Devolve dict ou None."""
    if not S.transp_key:
        return None
    c = so_digitos(cnpj)
    achou, consultou = [], []
    consultas = [("CEPIM (entidades impedidas)", "cepim", {"cnpjSancionado": c}),
                 ("CEIS (inidôneas e suspensas)", "ceis", {"codigoSancionado": c}),
                 ("CNEP (punidas)", "cnep", {"codigoSancionado": c})]
    for nome, rota, params in consultas:
        try:
            r = requests.get(TRANSP + rota, params={**params, "pagina": 1},
                             headers={**UA, "chave-api-dados": S.transp_key}, timeout=20)
            if r.status_code == 200:
                consultou.append(nome)
                for item in r.json() or []:
                    # só conta se o registro for mesmo deste CNPJ (evita falso positivo de filtro ignorado)
                    if c in so_digitos(json.dumps(item, ensure_ascii=False)):
                        achou.append(nome)
                        break
            elif r.status_code in (401, 403):
                return {"erro": "O Portal da Transparência recusou a chave. Confira a chave em ⚙️ Configurações."}
        except Exception:
            continue
    if not consultou:
        return {"erro": "Não consegui consultar o Portal da Transparência agora."}
    return {"consultou": consultou, "achou": achou}


# ══════════════════════════════════════════════════════════════════════════
# ÍNDICE DE CONFIANÇA
# ══════════════════════════════════════════════════════════════════════════
ROT_STATUS = {"ok": ("✅", "Comprovado"), "info": ("🔵", "Informado por você"), "nd": ("⚪", "Não comprovado"), "alerta": ("🔴", "Alerta")}
VALOR_STATUS = {"ok": 1.0, "info": 0.5, "nd": 0.0, "alerta": -0.5}


def faixa(n):
    if n < 40:
        return "Alto risco", "#C2410C", "Não doe antes de esclarecer os alertas."
    if n < 60:
        return "Atenção", "#D97706", "Há pontos importantes sem comprovação."
    if n < 80:
        return "Razoável", "#2C6FD1", "Bons sinais, mas confira o que ainda falta."
    return "Bons sinais", "#138A55", "Os principais pontos foram verificados. Continue acompanhando."


def calcular_indice(criterios, teto=100, motivos_teto=None):
    total = sum(c["peso"] for c in criterios) or 1
    pts = sum(c["peso"] * VALOR_STATUS[c["status"]] for c in criterios)
    nota = max(0, min(round(pts / total * 100), teto))
    return nota, motivos_teto or []


def avaliar_instituicao(f):
    """f: campos do formulário. Devolve resultado completo com critérios, nota e explicações."""
    crit, tetos, teto = [], [], 100
    cnpj = so_digitos(f["cnpj"])
    dados = consultar_cnpj(cnpj) if cnpj_valido(cnpj) else None

    def add(nome, peso, status, detalhe):
        crit.append({"nome": nome, "peso": peso, "status": status, "detalhe": detalhe})

    # 1. CNPJ
    if not cnpj_valido(cnpj):
        add("CNPJ válido", 15, "alerta", "O número informado não é um CNPJ válido (dígitos verificadores não conferem).")
        teto = min(teto, 30); tetos.append("CNPJ inválido")
    elif dados is None:
        add("Situação na Receita Federal", 15, "nd", "Não consegui consultar a Receita agora. Confira no site da Receita (link abaixo).")
    elif dados.get("inexistente"):
        add("Situação na Receita Federal", 15, "alerta", "Esse CNPJ não foi encontrado na base da Receita.")
        teto = min(teto, 30); tetos.append("CNPJ não encontrado")
    else:
        if "ATIVA" in dados["situacao"]:
            add("Situação na Receita Federal", 15, "ok", f"CNPJ **ativo** ({dados['fonte']}). Lembre: ativo não quer dizer confiável.")
        else:
            add("Situação na Receita Federal", 15, "alerta", f"Situação: **{dados['situacao'] or 'desconhecida'}**. Entidades baixadas, inaptas ou suspensas não deveriam pedir doações.")
            teto = min(teto, 30); tetos.append("CNPJ não está ativo")
        # 2. tempo de existência
        try:
            ab = datetime.fromisoformat(dados["abertura"][:10]).date()
            anos = (HOJE - ab).days / 365.25
            if anos >= 5:
                add("Tempo de existência", 10, "ok", f"Aberta em {br_data(ab)} ({anos:.0f} anos).")
            elif anos >= 2:
                add("Tempo de existência", 10, "info", f"Aberta em {br_data(ab)} ({anos:.1f} anos). Existe há pouco tempo: peça histórico de atividades.")
            else:
                add("Tempo de existência", 10, "alerta", f"Aberta em {br_data(ab)}, há menos de 2 anos. Muitas fraudes usam CNPJs recém-criados.")
        except Exception:
            add("Tempo de existência", 10, "nd", "Data de abertura não informada pela fonte.")
        # 3. natureza jurídica
        nat = dados["natureza_cod"]
        if nat.startswith(NATUREZA_SEM_FINS):
            add("Tipo de organização", 10, "ok", f"{dados['natureza'] or NOMES_NATUREZA.get(nat, 'Entidade sem fins lucrativos')} — é uma entidade sem fins lucrativos.")
        elif nat:
            add("Tipo de organização", 10, "alerta", f"Natureza jurídica: **{dados['natureza'] or nat}**. Não é uma entidade sem fins lucrativos — pergunte por que uma empresa está pedindo doações.")
        else:
            add("Tipo de organização", 10, "nd", "Natureza jurídica não informada pela fonte.")
        # 4. atividade
        cn = dados["cnae"]
        if cn and cn.startswith(CNAE_SOCIAIS):
            add("Atividade registrada", 10, "ok", f"{cn} — {dados['cnae_desc']}. Compatível com atuação social.")
        elif cn:
            add("Atividade registrada", 10, "alerta" if not nat.startswith(NATUREZA_SEM_FINS) else "info",
                f"{cn} — {dados['cnae_desc']}. Confira se combina com a causa da campanha.")
        else:
            add("Atividade registrada", 10, "nd", "Atividade principal não informada pela fonte.")
        # 5. responsáveis
        if dados["socios"]:
            nomes = ", ".join(f"{s['nome']} ({s['qualif']})" if s['qualif'] else s['nome'] for s in dados["socios"][:5])
            add("Responsáveis identificados", 5, "ok", f"Registro público: {nomes}.")
        else:
            add("Responsáveis identificados", 5, "nd", "A fonte não lista responsáveis. Peça os nomes da diretoria e o estatuto.")
        # 6. nome apresentado x registro
        if f.get("nome_apresentado"):
            sim = max(nomes_parecidos(f["nome_apresentado"], dados["razao"]), nomes_parecidos(f["nome_apresentado"], dados["fantasia"]))
            if sim >= 0.5:
                add("Nome confere com o CNPJ", 10, "ok", f"'{f['nome_apresentado']}' combina com o registro ({dados['fantasia'] or dados['razao']}).")
            else:
                add("Nome confere com o CNPJ", 10, "alerta", f"A campanha se apresenta como '{f['nome_apresentado']}', mas o CNPJ é de **{dados['razao']}**. Pode ser perfil clonado.")
                teto = min(teto, 50); tetos.append("Nome diferente do CNPJ")
    # 7. sanções
    sanc = consultar_sancoes(cnpj) if cnpj_valido(cnpj) else None
    if sanc is None:
        add("Sem sanções e impedimentos (CEPIM, CEIS, CNEP)", 10, "nd",
            "Não consultado: adicione sua chave gratuita do Portal da Transparência em ⚙️ Configurações, ou confira pelo link abaixo.")
    elif sanc.get("erro"):
        add("Sem sanções e impedimentos (CEPIM, CEIS, CNEP)", 10, "nd", sanc["erro"])
    elif sanc["achou"]:
        add("Sem sanções e impedimentos (CEPIM, CEIS, CNEP)", 10, "alerta", "Aparece em: **" + ", ".join(sanc["achou"]) + "**. Veja os detalhes no Portal da Transparência.")
        teto = min(teto, 35); tetos.append("Consta em cadastro de sanções")
    else:
        add("Sem sanções e impedimentos (CEPIM, CEIS, CNEP)", 10, "ok", "Nada encontrado em: " + ", ".join(sanc["consultou"]) + ".")
    # 8. PIX
    tp, val = tipo_pix(f.get("pix"))
    nome_banco = f.get("nome_banco", "").strip()
    if tp == "vazia":
        add("Chave PIX coerente", 15, "nd", "Informe a chave PIX que a campanha divulgou para o app conferir.")
    elif tp == "CNPJ" and val == cnpj:
        add("Chave PIX coerente", 15, "ok", "A chave PIX é o próprio CNPJ da instituição.")
    elif tp == "CNPJ":
        add("Chave PIX coerente", 15, "alerta", f"A chave PIX é **outro CNPJ** ({fmt_cnpj(val)}). Pergunte de quem é essa conta.")
        teto = min(teto, 40); tetos.append("PIX de outro CNPJ")
    elif tp == "CPF":
        add("Chave PIX coerente", 15, "alerta", "A chave PIX é um **CPF (pessoa física)**. Instituições costumam receber na conta do CNPJ. Esse é um dos sinais de golpe mais comuns.")
        teto = min(teto, 40); tetos.append("PIX para pessoa física")
    else:
        if nome_banco and dados and not dados.get("inexistente"):
            sim = max(nomes_parecidos(nome_banco, dados["razao"]), nomes_parecidos(nome_banco, dados["fantasia"]))
            if sim >= 0.5:
                add("Chave PIX coerente", 15, "info", f"Chave do tipo {tp}. O nome que apareceu no seu banco ('{nome_banco}') combina com a instituição.")
            else:
                add("Chave PIX coerente", 15, "alerta", f"Chave do tipo {tp}, e o nome que apareceu no seu banco ('{nome_banco}') **não combina** com {dados['razao']}.")
                teto = min(teto, 40); tetos.append("Recebedor do PIX diferente")
        else:
            add("Chave PIX coerente", 15, "nd", f"Chave do tipo {tp}: o app não consegue ver o dono. Digite a chave no app do seu banco (sem confirmar) e informe o nome que aparece.")
    # 9-10. transparência e entregas (informado pela pessoa)
    if f.get("link_contas"):
        add("Prestação de contas publicada", 15, "info", f"Você informou onde está a prestação de contas: {f['link_contas']}. O app não confere o conteúdo; leia com atenção.")
    elif f.get("viu_contas"):
        add("Prestação de contas publicada", 15, "info", "Você informou que viu a prestação de contas.")
    else:
        add("Prestação de contas publicada", 15, "nd", "Nenhuma prestação de contas informada. Peça: quanto arrecadou, quanto gastou e em quê.")
        teto = min(teto, 75); tetos.append("Sem prestação de contas comprovada")
    if f.get("viu_entregas"):
        add("Comprovação de entregas", 10, "info", "Você informou que viu fotos com data, relatórios ou depoimentos verificáveis de entregas.")
    else:
        add("Comprovação de entregas", 10, "nd", "Sem comprovação de entregas informada.")
    if f.get("contato_ok"):
        add("Contato oficial conferido", 5, "info", "Você confirmou a campanha pelo telefone ou site oficial.")
    else:
        add("Contato oficial conferido", 5, "nd", "Ligue ou escreva pelo canal oficial (site, telefone da Receita) e confirme que a campanha é deles.")
    if f.get("titulos"):
        add("Títulos e certificações", 5, "info", "Você informou: " + ", ".join(f["titulos"]) + ". Confira a validade nos órgãos que emitiram.")
    return montar_resultado("instituicao", f, crit, teto, tetos, dados)


def avaliar_pessoa(f):
    crit, tetos, teto = [], ["Campanha de pessoa física (sem CNPJ): o índice vai no máximo até 70"], 70

    def add(nome, peso, status, detalhe):
        crit.append({"nome": nome, "peso": peso, "status": status, "detalhe": detalhe})

    benef = f.get("beneficiario", "").strip()
    add("Beneficiário identificado", 15, "info" if len(benef.split()) >= 2 else "nd",
        f"Beneficiário: {benef}." if len(benef.split()) >= 2 else "Peça o nome completo de quem será ajudado.")
    tp, val = tipo_pix(f.get("pix"))
    nome_banco = f.get("nome_banco", "").strip()
    if tp == "vazia":
        add("Recebedor do PIX", 20, "nd", "Informe a chave PIX divulgada.")
    elif tp == "CNPJ":
        add("Recebedor do PIX", 20, "info", f"A chave é um CNPJ ({fmt_cnpj(val)}). Confira se é a plataforma de vaquinha, o hospital ou outra empresa — e por quê.")
    elif nome_banco:
        sim = max(nomes_parecidos(nome_banco, benef), nomes_parecidos(nome_banco, f.get("responsavel", "")))
        if sim >= 0.5:
            add("Recebedor do PIX", 20, "info", f"O nome no seu banco ('{nome_banco}') combina com o beneficiário ou responsável informado.")
        else:
            add("Recebedor do PIX", 20, "alerta", f"O nome no seu banco ('{nome_banco}') **não combina** com o beneficiário nem com o responsável. Pergunte quem é antes de doar.")
            teto = min(teto, 35); tetos.append("Recebedor do PIX desconhecido")
    else:
        add("Recebedor do PIX", 20, "nd", "Digite a chave no app do seu banco (sem confirmar) e informe o nome que aparece.")
    add("Documentos (laudo, orçamento, boletim)", 15, "info" if f.get("docs") else "nd",
        "Você informou que viu documentos." if f.get("docs") else "Peça laudo, orçamento ou outro documento que comprove a necessidade.")
    add("Atualizações de uso do dinheiro", 10, "info" if f.get("atualizacoes") else "nd",
        "Há atualizações de como o dinheiro está sendo usado." if f.get("atualizacoes") else "Sem atualizações de uso do dinheiro.")
    add("Conhecido em comum", 15, "info" if f.get("conhece") else "nd",
        "Você conhece a família ou alguém de confiança confirmou a história." if f.get("conhece") else "Ninguém de confiança confirmou a história.")
    add("Plataforma com regras e denúncia", 10, "info" if f.get("plataforma") else "nd",
        "A campanha está numa plataforma de vaquinha com regras de saque e canal de denúncia." if f.get("plataforma") else "Campanha só por mensagem ou rede social, sem plataforma com regras.")
    add("Notícia em veículo conhecido", 5, "info" if f.get("imprensa") else "nd",
        "Há notícia em veículo de imprensa conhecido." if f.get("imprensa") else "Sem notícia em veículo conhecido.")
    return montar_resultado("pessoa", f, crit, teto, tetos, None)


def montar_resultado(tipo, f, crit, teto, tetos, dados):
    analise = analisar_texto(f.get("texto", ""))
    if analise and not analise.get("erro"):
        nv = analise.get("nivel")
        n_al = len(analise.get("alertas") or [])
        status = {"alto": "alerta", "medio": "nd", "baixo": "ok"}[nv]
        crit.append({"nome": "Texto da campanha (análise da IA)", "peso": 10, "status": status,
                     "detalhe": f"Nível de alerta no texto: **{nv}** ({n_al} sinal(is)). Veja os detalhes abaixo."})
        if nv == "alto":
            teto = min(teto, 50); tetos.append("Texto com muitos sinais de manipulação")
    nota, _ = calcular_indice(crit, teto)
    alertas = [c for c in crit if c["status"] == "alerta"]
    return {"id": str(uuid.uuid4())[:8], "data": datetime.now().isoformat(timespec="minutes"), "tipo": tipo,
            "nome": (dados or {}).get("fantasia") or (dados or {}).get("razao") or f.get("nome_apresentado") or f.get("beneficiario") or "Campanha",
            "cnpj": so_digitos(f.get("cnpj", "")), "causa": f.get("causa", ""), "nota": nota, "teto": teto, "tetos": tetos,
            "criterios": crit, "dados": dados, "analise": analise, "n_alertas": len(alertas), "doou": None}


def mostrar_resultado(res):
    nome_f, cor, frase = faixa(res["nota"])
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f'<div class="indice" style="background:{cor}"><span>ÍNDICE DE CONFIANÇA</span>'
                    f'<div class="n">{res["nota"]}</div><div class="f">{nome_f}</div><p>{frase}</p></div>', unsafe_allow_html=True)
        cont = {k: len([c for c in res["criterios"] if c["status"] == k]) for k in ROT_STATUS}
        st.markdown(f'<div class="card">✅ {cont["ok"]} comprovado(s) · 🔵 {cont["info"]} informado(s) por você<br>'
                    f'⚪ {cont["nd"]} não comprovado(s) · 🔴 {cont["alerta"]} alerta(s)</div>', unsafe_allow_html=True)
        if res["tetos"]:
            st.markdown('<div class="card" style="font-size:.88em">🔒 <b>Nota limitada a ' + str(res["teto"]) + '</b> por: ' + "; ".join(res["tetos"]) + '</div>',
                        unsafe_allow_html=True)
    with c2:
        st.markdown(f"#### {res['nome']}" + (f" · {fmt_cnpj(res['cnpj'])}" if res.get("cnpj") else ""))
        ordem = {"alerta": 0, "nd": 1, "info": 2, "ok": 3}
        for c in sorted(res["criterios"], key=lambda x: ordem[x["status"]]):
            ic, rot = ROT_STATUS[c["status"]]
            det = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", c["detalhe"])
            st.markdown(f'<div class="crit {c["status"]}"><div class="ic">{ic}</div><div><span class="st">{rot}</span><br>'
                        f'<b>{c["nome"]}</b><br>{det}</div></div>', unsafe_allow_html=True)
    an = res.get("analise")
    if an:
        if an.get("erro"):
            st.caption(f"Análise do texto pela IA: {an['erro']}")
        else:
            with st.expander("🧠 O que a IA viu no texto da campanha", expanded=an.get("nivel") != "baixo"):
                for a in an.get("alertas") or []:
                    st.markdown(f"🔴 **{a.get('sinal', '')}** — _\"{a.get('trecho', '')}\"_  \n{a.get('por_que', '')}")
                for p in an.get("positivos") or []:
                    st.markdown(f"✅ {p}")
                if an.get("perguntas"):
                    st.markdown("**Perguntas para fazer antes de doar:**")
                    for q in an["perguntas"]:
                        st.markdown(f"- {q}")
    d = res.get("dados")
    if d and not d.get("inexistente"):
        with st.expander("📄 Dados públicos do CNPJ"):
            st.markdown(f"**Razão social:** {d['razao']}  \n**Nome fantasia:** {d['fantasia'] or '—'}  \n"
                        f"**Situação:** {d['situacao'] or '—'} desde {br_data(d['data_situacao'])}  \n**Abertura:** {br_data(d['abertura'])}  \n"
                        f"**Natureza jurídica:** {d['natureza'] or '—'}  \n**Atividade:** {d['cnae']} — {d['cnae_desc']}  \n"
                        f"**Cidade:** {d['cidade']}/{d['uf']}  \n**Contato registrado:** {d['email'] or '—'} {d['telefone'] or ''}  \n"
                        f"_Fonte: {d['fonte']}. Dados cadastrais podem estar desatualizados._")
    with st.expander("🔗 Confira você também (fontes oficiais)"):
        for t, u in LINKS_CONFERIR[:3]:
            st.markdown(f"- [{t}]({u})")
    st.markdown('<p class="aviso">O Índice de Confiança resume o que foi possível verificar com dados públicos e com o que você informou. '
                'Ele não garante que a instituição é honesta nem acusa ninguém de fraude. A decisão é sua.</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# IMPACTO E CONQUISTAS
# ══════════════════════════════════════════════════════════════════════════
def metricas():
    mes = HOJE.isoformat()[:7]
    din = [d for d in S.doacoes if d["tipo"] == "Dinheiro"]
    return {
        "total": sum(float(d.get("valor") or 0) for d in din),
        "n": len(S.doacoes),
        "causas": len({d["causa"] for d in S.doacoes}),
        "meses": len({d["data"][:7] for d in S.doacoes}),
        "recibos": len([d for d in din if d.get("recibo")]),
        "entregas": len([d for d in S.doacoes if d.get("entrega")]),
        "horas": sum(float(d.get("horas") or 0) for d in S.doacoes if d["tipo"] == "Voluntariado"),
        "verif": len(S.verificacoes),
        "evitou": len([v for v in S.verificacoes if v["nota"] < 40 and v.get("doou") is False]),
        "cursos": len([1 for v in S.cursos.values() if v.get("aprovado")]),
        "verif_mes": len([v for v in S.verificacoes if v["data"][:7] == mes]),
        "causas_mes": len({d["causa"] for d in S.doacoes if d["data"][:7] == mes}),
        "recibos_mes": len([d for d in din if d["data"][:7] == mes and d.get("recibo")]),
        "horas_mes": sum(float(d.get("horas") or 0) for d in S.doacoes if d["tipo"] == "Voluntariado" and d["data"][:7] == mes),
        "itens_mes": len([d for d in S.doacoes if d["tipo"] == "Itens" and d["data"][:7] == mes]),
    }


def medalhas_ganhas(m):
    return {
        "primeira": m["n"] >= 1, "consciente": m["verif"] >= 3, "diversidade": m["causas"] >= 3, "constancia": m["meses"] >= 3,
        "recibo": m["recibos"] >= 5, "fiscal": m["entregas"] >= 3, "voluntario": m["horas"] >= 10,
        "estudante": m["cursos"] >= len(CURSOS), "alerta": m["evitou"] >= 1,
    }


def contexto():
    m = metricas()
    ult = S.verificacoes[-3:]
    return (f"Nome: {S.d_nome}. Ajudas registradas: {m['n']} (total em dinheiro {brl(m['total'])}, {m['causas']} causas, "
            f"{m['horas']:.0f} h de voluntariado). Verificações feitas: {m['verif']}. "
            + ("Últimas verificações: " + "; ".join(f"{v['nome']} nota {v['nota']} ({faixa(v['nota'])[0]}), alertas: "
                                                   + ", ".join(c['nome'] for c in v['criterios'] if c['status'] == 'alerta') for v in ult)
               if ult else "Nenhuma verificação ainda."))


def memoria_json():
    d = {k: S[k] for k in CHAVES_MEMORIA}
    d["_app"] = "doa_inteligente"
    d["_salvo_em"] = datetime.now().isoformat(timespec="seconds")
    return json.dumps(d, ensure_ascii=False, indent=2, default=str).encode("utf-8")


TUTORIAL = {
    "1. O que é o Doa Inteligente": """
**Um app que esclarece antes de você doar.** Ele **não recebe dinheiro**, não repassa doações e **não indica onde doar**.

Você encontrou uma campanha, uma ONG ou uma vaquinha e quer ajudar? Traga para cá. O app:
1. **Confere os dados públicos** da instituição (CNPJ na Receita, sanções no Portal da Transparência).
2. **Analisa a chave PIX** e o texto da campanha atrás de sinais de golpe.
3. Mostra um **Índice de Confiança** com tudo separado em: ✅ comprovado · 🔵 informado por você · ⚪ não comprovado · 🔴 alerta.
4. Guarda **o bem que você faz**: doações, itens, horas de voluntariado, medalhas e desafios.

> 💡 **CNPJ ativo não é o mesmo que confiável.** O app mostra o que foi verificado e o que ainda falta comprovar.
""",
    "2. Como verificar uma campanha (passo a passo)": """
1. Vá em **🔎 Verificar**.
2. Escolha: **Instituição (tem CNPJ)** ou **Vaquinha de pessoa física**.
3. Preencha o que você tem: CNPJ, nome como a campanha se apresenta, a **chave PIX** divulgada e cole o **texto da campanha**.
4. **Dica de ouro:** abra o app do seu banco, comece um PIX com a chave divulgada **sem confirmar** e veja o **nome que aparece**. Escreva esse nome no campo "Nome que aparece no seu banco" e cancele o PIX.
5. Marque o que você conseguiu ver (prestação de contas, fotos de entregas, contato oficial).
6. Clique em **🔎 Verificar agora** e leia cada item do resultado.
7. Depois, diga ao app se doou ou não. Se a nota for baixa e você desistir, ganha a medalha **🚨 Golpe evitado**.
""",
    "3. Como ler o Índice de Confiança": """
| Faixa | O que significa |
|---|---|
| **80 a 100 — Bons sinais** | Os principais pontos foram verificados. Continue acompanhando a prestação de contas. |
| **60 a 79 — Razoável** | Bons sinais, mas ainda falta comprovar algo importante. |
| **40 a 59 — Atenção** | Faltam comprovações importantes. Pergunte antes de doar. |
| **0 a 39 — Alto risco** | Há alertas sérios. Não doe sem esclarecer. |

**Por que a nota às vezes fica "travada"?** Alguns problemas limitam a nota máxima (🔒): PIX para CPF numa campanha de instituição, CNPJ inativo, sanções, nome diferente do CNPJ ou falta de prestação de contas. Vaquinhas de pessoa física vão no máximo até 70, porque não há registro público para conferir.

O índice **não acusa ninguém de fraude** e **não garante honestidade**. Ele organiza as evidências para você decidir melhor.
""",
    "4. Registrar o bem que você faz": """
Em **❤️ Meu impacto** você registra:
- **Doações em dinheiro** (com ou sem recibo),
- **Itens** (alimentos, roupas, ração, móveis),
- **Horas de voluntariado**.

O app mostra quanto você já ajudou, quais causas apoiou, suas **medalhas de solidariedade** e o **desafio do mês**.
Quando a instituição mostrar que a ajuda chegou, marque **"entrega comprovada"** — isso vale a medalha **🔍 Fiscal do bem**.

Em **💡 Impacto** você simula o que um valor pode virar (refeições, cestas, atendimentos) usando os custos que a instituição informa.
""",
    "5. A chave Groq (a IA do app)": """
O app usa uma **inteligência artificial grátis** (Groq) para analisar o texto das campanhas e responder suas dúvidas.

**Como pegar a sua (grátis, 2 minutos):**
1. Entre em 👉 **[console.groq.com/keys](https://console.groq.com/keys)**.
2. Clique em **Sign in** e entre com sua conta **Google**.
3. Clique em **Create API Key**, dê um nome (ex.: doa) e clique em **Submit**.
4. **Copie** a chave (começa com **gsk_**) e cole na entrada do app.

🔒 A chave fica só nesta sessão. Não compartilhe.
""",
    "6. Caí num golpe, e agora?": """
Aja rápido:
1. **Avise seu banco imediatamente** e peça a abertura do **MED (Mecanismo Especial de Devolução do PIX)**. Quanto antes, maior a chance de recuperar.
2. **Registre um boletim de ocorrência** (muitos estados aceitam pela internet).
3. **Guarde prints** da campanha, das conversas e do comprovante.
4. **Denuncie o perfil** na rede social ou na plataforma de vaquinha.
5. Avise amigos e família para que não caiam também.
""",
    "7. Dúvidas comuns": """
**O app diz se uma ONG é honesta?** Não. Ele mostra evidências: o que foi comprovado, o que você informou e o que falta.

**Por que preciso informar coisas que eu vi?** Algumas provas (prestação de contas, fotos de entregas) não estão em bases públicas. O app conta essas informações pela metade e deixa claro que foram informadas por você.

**O que é a chave do Portal da Transparência?** Uma chave **gratuita** do governo que libera a consulta de sanções (CEPIM, CEIS, CNEP). É opcional; coloque em ⚙️ Configurações.

**Doação abate imposto de renda?** Para pessoa física, doações comuns não abatem. Só doações a fundos (criança, idoso) e projetos incentivados, até 6% do imposto, na declaração completa. Veja o curso em 🎓 Doar com segurança.

**Perdi meus dados!** Os dados ficam só enquanto a página está aberta. Use **💾 Minha memória** para salvar o arquivo e abrir na próxima vez.
""",
}

# ══════════════════════════════════════════════════════════════════════════
# TELA DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════
if not S.d_chave:
    _, meio, _ = st.columns([1, 2, 1])
    with meio:
        st.markdown("""<div style="text-align:center;padding:18px 0 4px 0;">
          <div style="font-size:3.2em;">💚</div><h1 style="margin:0;">Doa Inteligente</h1>
          <p style="color:#4E6765 !important;font-size:1.05em;">Sua generosidade merece inteligência.<br>
          <b style="color:#E8603C !important;">Doe com consciência. Ajude com segurança. Transforme vidas.</b></p>
        </div>""", unsafe_allow_html=True)
        nome = st.text_input("👤 Seu nome", placeholder="Como quer ser chamado?", key="d_inp_nome")
        chave = st.text_input("🔑 Sua chave Groq API", type="password", placeholder="gsk_...", key="d_inp_chave")
        if st.button("💚 ENTRAR", type="primary", width="stretch"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 letras.")
            elif not chave.strip().startswith("gsk_"):
                st.warning("A chave Groq começa com **gsk_**. Confira e cole novamente.")
            else:
                S.d_nome, S.d_chave = nome.strip(), chave.strip()
                st.rerun()
        with st.expander("🆕 Primeira vez? Veja como entrar em 1 minuto"):
            st.markdown(TUTORIAL["5. A chave Groq (a IA do app)"])
        st.markdown(f"""<div class="card" style="font-size:.92em;line-height:1.7;">
        🛡️ O Doa Inteligente <b>não recebe nem repassa dinheiro</b> e não indica onde doar: ele esclarece.<br>
        🔒 Sua chave fica só nesta sessão do navegador.<br>
        🤖 Mais agentes em <a href="{SITE}" target="_blank">MeusAgentesIA.com.br</a>.</div>""", unsafe_allow_html=True)
        st.markdown('<p class="aviso" style="text-align:center">Ninguém deveria precisar escolher entre ser generoso e ser prudente.</p>',
                    unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# CABEÇALHO, MEMÓRIA, COMO EXPLORAR E TUTORIAL
# ══════════════════════════════════════════════════════════════════════════
m = metricas()
c_cab, c_mem = st.columns([3, 2])
with c_cab:
    st.markdown(f"""<div class="cab"><h1>💚 Doa Inteligente</h1>
    <p>Olá, {S.d_nome}! Você já ajudou <b>{m['n']}</b> vez(es) · {brl(m['total'])} doados · {m['horas']:.0f} h de voluntariado</p>
    <p class="lema">Sua generosidade merece inteligência.</p></div>""", unsafe_allow_html=True)
with c_mem:
    with st.expander("💾 Minha memória: salvar, abrir ou sair"):
        st.caption("Os dados ficam só nesta sessão. Salve o arquivo .json no seu aparelho e abra na próxima visita.")
        st.download_button("💾 Salvar minha memória (.json)", data=memoria_json(),
                           file_name=f"doa_inteligente_{re.sub(r'[^a-z0-9]+', '_', S.d_nome.lower())}_{HOJE.isoformat()}.json",
                           mime="application/json", width="stretch")
        arq = st.file_uploader("📂 Abrir minha memória", type=["json"], key=f"up_mem_{S.ver}")
        if arq is not None and st.button("Carregar esta memória", width="stretch"):
            try:
                dados = json.loads(arq.getvalue().decode("utf-8"))
                if dados.get("_app") != "doa_inteligente":
                    raise ValueError
                for k in CHAVES_MEMORIA:
                    if k in dados:
                        S[k] = dados[k]
                S.ver += 1
                st.rerun()
            except Exception:
                st.error("Esse arquivo não é uma memória do Doa Inteligente.")
        if st.button("🚪 Sair", width="stretch"):
            for k in list(S.keys()):
                del S[k]
            st.rerun()

PASSOS = [
    ("1", "🔎", "Verificar", "Traga a campanha ou ONG e veja o Índice de Confiança", m["verif"] > 0),
    ("2", "💡", "Impacto", "Descubra o que sua doação pode fazer", bool(S.get("_simulou"))),
    ("3", "❤️", "Meu impacto", "Registre doações, itens e voluntariado", m["n"] > 0),
    ("4", "🏅", "Conquistas", "Medalhas e o desafio do mês", bool(S.desafio)),
    ("5", "🎓", "Doar com segurança", "6 cursos rápidos e grátis", m["cursos"] > 0),
    ("6", "💬", "Assistente", "Tire dúvidas com a IA", bool(S.chat)),
]
cards = "".join(f'<div class="passo{" ok" if ok else ""}"><div class="n">{"✓" if ok else n}</div><div><b>{ic} {nm}</b><br><span>{tx}</span></div></div>'
                for n, ic, nm, tx, ok in PASSOS)
st.markdown(f'<div class="explorar"><div class="t">🗺️ COMO EXPLORAR O APP — siga as abas nesta ordem</div><div class="passos">{cards}</div></div>',
            unsafe_allow_html=True)

with st.expander("📘 **Tutorial para iniciantes — clique aqui se é sua primeira vez**", expanded=(m["verif"] == 0 and not S.get("_tut_ok"))):
    abas_t = st.tabs(list(TUTORIAL.keys()))
    for a_t, txt in zip(abas_t, TUTORIAL.values()):
        with a_t:
            st.markdown(txt)
    if m["verif"] == 0 and st.button("✅ Entendi, vamos começar", key="tut_ok"):
        S["_tut_ok"] = True
        st.rerun()

abas = st.tabs(["🔎 Verificar", "🛡️ Minhas verificações", "💡 Impacto", "❤️ Meu impacto", "🏅 Conquistas",
                "🎓 Doar com segurança", "💬 Assistente", "⚙️ Configurações"])

# ══════════════════════════════════════════════════════════════════════════
# 1. VERIFICAR
# ══════════════════════════════════════════════════════════════════════════
with abas[0]:
    st.markdown("### 🔎 Antes de doar, verifique")
    modo = st.radio("O que você quer verificar?", ["🏢 Instituição ou ONG (tem CNPJ)", "🙋 Vaquinha de pessoa física"], horizontal=True, key="modo")
    with st.form(f"f_verif_{S.ver}"):
        if modo.startswith("🏢"):
            a1, a2 = st.columns(2)
            cnpj_in = a1.text_input("CNPJ da instituição *", placeholder="00.000.000/0000-00")
            nome_ap = a2.text_input("Nome como a campanha se apresenta", placeholder="ex.: Lar Esperança")
        else:
            a1, a2 = st.columns(2)
            benef = a1.text_input("Nome completo de quem será ajudado *", placeholder="ex.: Maria da Silva Souza")
            resp = a2.text_input("Responsável pela vaquinha (se for outra pessoa)", placeholder="ex.: João Souza (filho)")
        b1, b2, b3 = st.columns(3)
        pix = b1.text_input("Chave PIX divulgada", placeholder="CNPJ, CPF, e-mail, telefone ou aleatória")
        nome_banco = b2.text_input("Nome que aparece no seu banco", help="Comece um PIX com a chave no app do seu banco, SEM confirmar, e copie o nome do recebedor.")
        causa = b3.selectbox("Causa", CAUSAS)
        texto = st.text_area("Cole o texto da campanha (opcional, a IA procura sinais de golpe)", height=130,
                             placeholder="Cole aqui a mensagem, a legenda do post ou a descrição da vaquinha…")
        st.markdown("**O que você conseguiu ver?** _(marque só o que viu de verdade)_")
        if modo.startswith("🏢"):
            c1, c2 = st.columns(2)
            viu_contas = c1.checkbox("Prestação de contas publicada (quanto entrou e como foi gasto)")
            link_contas = c1.text_input("Link da prestação de contas (se tiver)", label_visibility="visible")
            viu_entregas = c2.checkbox("Fotos com data, relatórios ou depoimentos de entregas")
            contato_ok = c2.checkbox("Confirmei a campanha pelo site ou telefone oficial")
            titulos = st.multiselect("Títulos ou certificados que a instituição diz ter",
                                     ["CEBAS", "OSCIP", "Utilidade pública", "Registro no Conselho Municipal (CMAS/CMDCA)", "Auditoria independente"],
                                     placeholder="Escolha, se houver")
        else:
            c1, c2 = st.columns(2)
            docs = c1.checkbox("Vi documentos (laudo, orçamento, boletim de ocorrência)")
            atualiz = c1.checkbox("Há atualizações de como o dinheiro está sendo usado")
            conhece = c1.checkbox("Conheço a família ou alguém de confiança confirmou")
            plataforma = c2.checkbox("Está numa plataforma de vaquinha com regras e denúncia")
            imprensa = c2.checkbox("Saiu em veículo de imprensa conhecido")
        enviar = st.form_submit_button("🔎 Verificar agora", width="stretch")
    if enviar:
        with st.spinner("Consultando dados públicos e analisando…"):
            if modo.startswith("🏢"):
                if not so_digitos(cnpj_in):
                    st.warning("Informe o CNPJ.")
                    st.stop()
                res = avaliar_instituicao({"cnpj": cnpj_in, "nome_apresentado": nome_ap, "pix": pix, "nome_banco": nome_banco,
                                           "causa": causa, "texto": texto, "viu_contas": viu_contas, "link_contas": link_contas.strip(),
                                           "viu_entregas": viu_entregas, "contato_ok": contato_ok, "titulos": titulos})
            else:
                if not benef.strip():
                    st.warning("Informe o nome de quem será ajudado.")
                    st.stop()
                res = avaliar_pessoa({"beneficiario": benef, "responsavel": resp, "pix": pix, "nome_banco": nome_banco, "causa": causa,
                                      "texto": texto, "docs": docs, "atualizacoes": atualiz, "conhece": conhece,
                                      "plataforma": plataforma, "imprensa": imprensa})
        S.verificacoes.append(res)
        S.resultado = res["id"]
        st.rerun()
    atual = next((v for v in S.verificacoes if v["id"] == S.resultado), None)
    if atual:
        st.divider()
        mostrar_resultado(atual)
        st.markdown("#### E então, você vai doar?")
        d1, d2, d3 = st.columns(3)
        if d1.button("💚 Vou doar / já doei", width="stretch", key=f"doou_{atual['id']}"):
            atual["doou"] = True
            S["_pre_doacao"] = atual["id"]
            st.success("Registre a doação em ❤️ Meu impacto — a instituição já aparece na lista.")
        if d2.button("✋ Não vou doar", width="stretch", key=f"naodoou_{atual['id']}"):
            atual["doou"] = False
            if atual["nota"] < 40:
                st.success("🚨 Prudência também é generosidade: você ganhou a medalha **Golpe evitado**.")
            else:
                st.info("Tudo bem. Sua decisão ficou registrada.")
        if d3.button("🤖 Perguntas para fazer à instituição", width="stretch", key=f"perg_{atual['id']}"):
            with st.spinner("Preparando…"):
                try:
                    faltas = "; ".join(f"{c['nome']}: {c['detalhe']}" for c in atual["criterios"] if c["status"] in ("nd", "alerta"))
                    S["_perguntas"] = ia([{"role": "system", "content": REGRA_IA},
                                          {"role": "user", "content": f"Escreva uma mensagem educada e curta que eu possa mandar para '{atual['nome']}' "
                                           f"pedindo os esclarecimentos que faltam antes de eu doar. Pontos em aberto: {faltas}. "
                                           "Depois da mensagem, liste o que seria uma boa resposta e o que seria um sinal de alerta."}])
                except RuntimeError as e:
                    st.error(f"⚠️ {e}")
        if S.get("_perguntas"):
            st.markdown(f'<div class="card">{S["_perguntas"]}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 2. MINHAS VERIFICAÇÕES
# ══════════════════════════════════════════════════════════════════════════
with abas[1]:
    st.markdown("### 🛡️ Minhas verificações")
    if not S.verificacoes:
        st.info("Nenhuma verificação ainda. Comece em 🔎 Verificar.")
    for v in reversed(S.verificacoes):
        nome_f, cor, _ = faixa(v["nota"])
        decisao = {True: "💚 doou", False: "✋ não doou", None: "decisão não registrada"}[v.get("doou")]
        with st.expander(f"{v['nota']} · {nome_f} — {v['nome']} · {br_data(v['data'])} · {decisao}"):
            mostrar_resultado(v)
            if st.button("🗑️ Apagar esta verificação", key=f"del_v_{v['id']}"):
                S.verificacoes = [x for x in S.verificacoes if x["id"] != v["id"]]
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# 3. IMPACTO
# ══════════════════════════════════════════════════════════════════════════
with abas[2]:
    st.markdown("### 💡 O que a sua doação pode fazer")
    st.caption("Use os custos que a instituição informa. Os valores abaixo são só exemplos para você editar — cada lugar tem custos diferentes.")
    valor = st.number_input("Quanto você pensa em doar (R$)?", min_value=0.0, value=0.0, step=10.0, placeholder="ex.: 100")
    base = pd.DataFrame([
        {"O que a instituição oferece": "Refeição completa", "Custo de 1 unidade (R$)": 12.0},
        {"O que a instituição oferece": "Cesta básica", "Custo de 1 unidade (R$)": 150.0},
        {"O que a instituição oferece": "Kit de higiene", "Custo de 1 unidade (R$)": 35.0},
        {"O que a instituição oferece": "Saco de ração 15 kg", "Custo de 1 unidade (R$)": 120.0},
        {"O que a instituição oferece": "Material escolar de 1 criança", "Custo de 1 unidade (R$)": 80.0},
    ])
    tab = st.data_editor(base if "_impacto_tab" not in S else S["_impacto_tab"], num_rows="dynamic", width="stretch", key=f"ed_imp_{S.ver}")
    S["_impacto_tab"] = tab
    linhas = []
    for _, row in tab.iterrows():
        try:
            custo = float(row["Custo de 1 unidade (R$)"])
            if custo > 0 and str(row["O que a instituição oferece"]).strip():
                linhas.append((str(row["O que a instituição oferece"]), int(valor // custo), custo))
        except Exception:
            continue
    if valor > 0 and linhas:
        S["_simulou"] = True
        cols = st.columns(min(len(linhas), 5))
        for (nm, q, _), col in zip(linhas[:5], cols):
            col.markdown(f'<div class="kpi"><div class="v">{q}</div><div class="l">{nm}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">Com <b>{brl(valor)}</b> por mês durante um ano, são <b>{brl(valor*12)}</b> — '
                    f'por exemplo, {int(valor * 12 // linhas[0][2])} unidades de "{linhas[0][0]}". '
                    'Doações recorrentes ajudam a instituição a planejar.</div>', unsafe_allow_html=True)
    st.caption("Peça à instituição quanto custa cada entrega e, depois, a comprovação de que ela aconteceu.")

# ══════════════════════════════════════════════════════════════════════════
# 4. MEU IMPACTO
# ══════════════════════════════════════════════════════════════════════════
with abas[3]:
    st.markdown("### ❤️ Meu impacto")
    verif_nomes = {v["id"]: f"{v['nome']} (índice {v['nota']})" for v in S.verificacoes}
    with st.form(f"f_doacao_{S.ver}", clear_on_submit=True):
        t1, t2, t3 = st.columns(3)
        tipo = t1.selectbox("Tipo de ajuda", ["Dinheiro", "Itens", "Voluntariado"])
        opcoes = ["(outra, não verificada)"] + list(verif_nomes.values())
        pre = S.get("_pre_doacao")
        idx = (list(verif_nomes.keys()).index(pre) + 1) if pre in verif_nomes else 0
        quem = t2.selectbox("Para quem", opcoes, index=idx)
        outro = t3.text_input("Nome (se não estiver na lista)")
        u1, u2, u3, u4 = st.columns(4)
        causa_d = u1.selectbox("Causa", CAUSAS, key="causa_doacao")
        valor_d = u2.number_input("Valor (R$)", min_value=0.0, step=10.0)
        horas_d = u3.number_input("Horas (voluntariado)", min_value=0.0, step=1.0)
        data_d = u4.date_input("Data", value=HOJE, max_value=HOJE, format="DD/MM/YYYY")
        itens_d = st.text_input("Itens doados (se for o caso)", placeholder="ex.: 10 kg de arroz, 5 cobertores")
        r1, r2 = st.columns(2)
        recibo = r1.checkbox("Tenho recibo ou comprovante")
        entrega = r2.checkbox("A entrega foi comprovada pela instituição")
        ok = st.form_submit_button("💚 Registrar ajuda", width="stretch")
    if ok:
        nome_q = outro.strip() or (quem if quem != opcoes[0] else "")
        if not nome_q:
            st.warning("Informe para quem foi a ajuda.")
        elif tipo == "Dinheiro" and valor_d <= 0:
            st.warning("Informe o valor.")
        elif tipo == "Voluntariado" and horas_d <= 0:
            st.warning("Informe as horas.")
        else:
            vid = next((k for k, v in verif_nomes.items() if v == quem), "")
            S.doacoes.append({"id": str(uuid.uuid4())[:8], "tipo": tipo, "para": nome_q.split(" (índice")[0], "verif_id": vid,
                              "causa": causa_d, "valor": valor_d if tipo == "Dinheiro" else 0, "horas": horas_d if tipo == "Voluntariado" else 0,
                              "itens": itens_d, "data": data_d.isoformat(), "recibo": recibo, "entrega": entrega})
            S["_pre_doacao"] = None
            st.rerun()
    m = metricas()
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi"><div class="l">Doado em dinheiro</div><div class="v">{brl(m["total"])}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi"><div class="l">Vezes que ajudou</div><div class="v">{m["n"]}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi"><div class="l">Causas apoiadas</div><div class="v">{m["causas"]}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi"><div class="l">Horas de voluntariado</div><div class="v">{m["horas"]:.0f}</div></div>', unsafe_allow_html=True)
    if S.doacoes:
        df = pd.DataFrame(S.doacoes)
        g = df.groupby("causa", as_index=False).size().rename(columns={"size": "vezes"})
        st.altair_chart(alt.Chart(g).mark_bar(color="#0E7C7B", cornerRadiusEnd=4).encode(
            y=alt.Y("causa:N", title=None, sort="-x"), x=alt.X("vezes:Q", title="Vezes que ajudou"),
            tooltip=["causa", "vezes"]).properties(height=max(120, 36 * len(g))), width="stretch")
        st.markdown("#### Histórico")
        for d in sorted(S.doacoes, key=lambda x: x["data"], reverse=True):
            c1, c2, c3 = st.columns([6, 2, 1])
            desc = brl(d["valor"]) if d["tipo"] == "Dinheiro" else (f"{d['horas']:.0f} h" if d["tipo"] == "Voluntariado" else (d.get("itens") or "itens"))
            selo = " · ✅ verificada antes" if d.get("verif_id") else ""
            c1.markdown(f"{br_data(d['data'])} · **{d['tipo']}** para **{d['para']}** ({d['causa']}) · {desc}{selo}"
                        + (" · 🧾 recibo" if d.get("recibo") else ""))
            if not d.get("entrega"):
                if c2.button("📦 Entrega comprovada", key=f"ent_{d['id']}"):
                    d["entrega"] = True
                    st.rerun()
            else:
                c2.markdown("📦 entregue")
            if c3.button("🗑️", key=f"del_d_{d['id']}"):
                S.doacoes = [x for x in S.doacoes if x["id"] != d["id"]]
                st.rerun()
    else:
        st.info("Registre a sua primeira ajuda acima. Dinheiro, itens e tempo: tudo conta.")

# ══════════════════════════════════════════════════════════════════════════
# 5. CONQUISTAS
# ══════════════════════════════════════════════════════════════════════════
with abas[4]:
    st.markdown("### 🏅 Medalhas de solidariedade")
    m = metricas()
    ganhas = medalhas_ganhas(m)
    cols = st.columns(3)
    for i, (mid, em, nm, desc) in enumerate(MEDALHAS):
        cols[i % 3].markdown(f'<div class="medalha{"" if ganhas[mid] else " off"}"><div class="e">{em}</div><b>{nm}</b><br>'
                             f'<span style="font-size:.85em">{desc}</span>{"<br>✅" if ganhas[mid] else ""}</div>', unsafe_allow_html=True)
    st.markdown(f"**{sum(ganhas.values())} de {len(MEDALHAS)} medalhas**")
    st.divider()
    st.markdown("### 🎯 Desafio do mês")
    nomes_d = [d[1] for d in DESAFIOS]
    escolha = st.selectbox("Escolha o seu desafio", ["(escolha um)"] + nomes_d,
                           index=(nomes_d.index(S.desafio) + 1) if S.desafio in nomes_d else 0)
    S.desafio = escolha if escolha in nomes_d else ""
    if S.desafio:
        _, nm, f_prog, meta = next(d for d in DESAFIOS if d[1] == S.desafio)
        prog = f_prog(m)
        st.progress(min(prog / meta, 1.0), text=f"{prog:g} de {meta} neste mês")
        if prog >= meta:
            st.success("🎉 Desafio do mês concluído! Você está fazendo a diferença.")

# ══════════════════════════════════════════════════════════════════════════
# 6. CURSOS
# ══════════════════════════════════════════════════════════════════════════
with abas[5]:
    st.markdown("### 🎓 Doar com segurança — 6 cursos rápidos e grátis")
    st.caption("Leia os pontos-chave e faça a provinha de 3 perguntas. Acertando todas, o curso é concluído.")
    with st.expander("🚨 Os golpes mais comuns (leitura de 1 minuto)", expanded=False):
        for g_ in GOLPES_COMUNS:
            st.markdown(f"- {g_}")
    for cid, titulo, pontos, perguntas in CURSOS:
        feito = S.cursos.get(cid, {}).get("aprovado")
        with st.expander(f"{'✅' if feito else '📖'} {titulo}"):
            for p in pontos:
                st.markdown(f"- {p}")
            with st.form(f"f_c_{cid}"):
                esc = [st.radio(f"**{i+1}. {q}**", ops, index=None, key=f"cq_{cid}_{i}") for i, (q, ops, _, _) in enumerate(perguntas)]
                ok_c = st.form_submit_button("✅ Conferir respostas")
            if ok_c:
                if any(e is None for e in esc):
                    st.warning("Responda as 3 perguntas.")
                else:
                    acertos = sum(1 for (q, ops, c, _), e in zip(perguntas, esc) if ops.index(e) == c)
                    S.cursos[cid] = {"aprovado": feito or acertos == len(perguntas), "acertos": acertos, "data": HOJE.isoformat()}
                    for (q, ops, c, ex), e in zip(perguntas, esc):
                        st.markdown(f"{'✅' if ops.index(e) == c else '❌'} {q} — correta: **{ops[c]}**. _{ex}_")
                    if acertos == len(perguntas):
                        st.success("Curso concluído! 🎓")
                    else:
                        st.info(f"Você acertou {acertos} de {len(perguntas)}. Releia os pontos e tente de novo.")
    st.markdown("#### 🔗 Para conferir por conta própria")
    for t, u in LINKS_CONFERIR[:3]:
        st.markdown(f"- [{t}]({u})")

# ══════════════════════════════════════════════════════════════════════════
# 7. ASSISTENTE
# ══════════════════════════════════════════════════════════════════════════
with abas[6]:
    st.markdown("### 💬 Assistente Doa Inteligente")
    st.caption("Pergunte sobre golpes, como verificar uma campanha, prestação de contas, imposto de renda ou o que fazer se caiu num golpe.")
    sug = ["Como saber se uma vaquinha é verdadeira?", "Doação abate imposto de renda?", "Caí num golpe de PIX, e agora?", "O que pedir de prestação de contas?"]
    cs = st.columns(len(sug))
    rapida = None
    for s_, c in zip(sug, cs):
        if c.button(s_, width="stretch"):
            rapida = s_
    caixa = st.container(height=400)
    with caixa:
        if not S.chat:
            st.markdown("👋 Olá! Estou aqui para ajudar você a doar com segurança. O que quer saber?")
        for msg in S.chat:
            with st.chat_message("user" if msg["role"] == "user" else "assistant", avatar="🙂" if msg["role"] == "user" else "💚"):
                st.markdown(msg["content"])
    pergunta = st.chat_input("Escreva sua pergunta…") or rapida
    if pergunta:
        S.chat.append({"role": "user", "content": pergunta})
        try:
            resp = ia([{"role": "system", "content": REGRA_IA}, {"role": "system", "content": "CONTEXTO DO USUÁRIO: " + contexto()}] + S.chat[-12:])
        except RuntimeError as e:
            resp = f"⚠️ {e}"
        S.chat.append({"role": "assistant", "content": resp})
        st.rerun()
    if S.chat and st.button("🧹 Limpar conversa"):
        S.chat = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# 8. CONFIGURAÇÕES
# ══════════════════════════════════════════════════════════════════════════
with abas[7]:
    st.markdown("### ⚙️ Configurações")
    st.markdown("**Chave do Portal da Transparência (opcional e gratuita)**")
    st.caption("Libera a consulta automática de entidades impedidas (CEPIM) e de empresas sancionadas (CEIS e CNEP). "
               "Para pegar: entre no link abaixo, informe seu e-mail, e a chave chega por e-mail.")
    st.markdown(f"👉 [{LINKS_CONFERIR[3][0]}]({LINKS_CONFERIR[3][1]})")
    nova = st.text_input("Chave da API do Portal da Transparência", value=S.transp_key, type="password", key=f"tk_{S.ver}")
    if nova != S.transp_key:
        S.transp_key = nova.strip()
        st.success("Chave salva nesta sessão (e na sua memória, quando você salvar).")
    st.divider()
    st.markdown('<p class="aviso">O Doa Inteligente é uma ferramenta de esclarecimento. Ele não recebe, não repassa e não intermedeia '
                'doações, e não indica instituições. As informações vêm de bases públicas, que podem estar desatualizadas, e do que você informa. '
                f'🤖 Mais agentes em <a href="{SITE}" target="_blank">MeusAgentesIA.com.br</a>.</p>', unsafe_allow_html=True)
