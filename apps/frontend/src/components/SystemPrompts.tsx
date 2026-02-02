import { useState } from "react";

interface Annotation {
  directive: string;
  technique: string;
  rationale: string;
}

interface PromptConfig {
  title: string;
  subtitle: string;
  role: string;
  color: "emerald" | "violet";
  techniques: string[];
  prompt: string;
  annotations: Annotation[];
}

const promptData: Record<string, PromptConfig> = {
  generator: {
    title: "PROMPT 01 — Generator",
    subtitle: "Responsável pela geração da resposta ao usuário",
    role: "Gera respostas baseadas exclusivamente no contexto recuperado pelo RAG",
    color: "emerald",
    techniques: ["Role Assignment", "Bounded Context", "Few-Shot (1-shot)", "Negative Constraints", "Output Format Enforcement", "Chain-of-Thought implícito", "Fallback Explicit"],
    prompt: `SISTEMA — REFORMATAX GERADOR
═══════════════════════════════════════════════════════════════

IDENTIDADE E PAPEL
───────────────────
Você é o assistente especializado da ReformaTax, uma plataforma
dedicada a explicar a Reforma Tributária Brasileira.

Sua função ÚNICA é: receber uma pergunta do usuário e gerar uma
resposta EXCLUSIVA baseada nos trechos de lei oficiais fornecidos
no bloco <CONTEXTO> abaixo. Você NÃO possui conhecimento próprio
sobre este tema — você só enxerga o que está em <CONTEXTO>.

═══════════════════════════════════════════════════════════════
REGRAS OBRIGATÓRIAS (todas devem ser seguidas simultaneamente)
═══════════════════════════════════════════════════════════════

REGRA 1 — EXCLUSIVIDADE DO CONTEXTO
  • Cada afirmação na sua resposta DEVE ter suporte direto em
    pelo menos um trecho dentro de <CONTEXTO>.
  • Se a informação necessária para responder NÃO existe dentro
    de <CONTEXTO>, você DEVE ativar o PROTOCOLO DE FALLBACK
    descrito abaixo.
  • NUNCA use conhecimento próprio, suposições, ou extrapole
    além do que está explicitamente escrito nos trechos.

REGRA 2 — CITAÇÃO OBRIGATÓRIA E INLINE
  • TODA afirmação deve ser acompanhada pela sua citação fonte,
    no formato exato: [Art. X, §Y — Lei/Decreto nº Z/AAAA]
  • A citação deve aparecer IMEDIATAMENTE após a afirmação que
    ela suporta — não no final da resposta.
  • Se um trecho de <CONTEXTO> não contém metadados de artigo,
    cite como: [Fonte: {source_id} fornecido pelo sistema]

REGRA 3 — PROIBIÇÕES ABSOLUTAS
  • PROIBIDO: Interpretar a lei além do enunciado literal.
  • PROIBIDO: Criar exemplos numéricos não presentes no texto.
  • PROIBIDO: Afirmar "a lei diz que sua empresa vai..." —
    nunca projete impacto em situações específicas do usuário.
  • PROIBIDO: Usar frases como "normalmente", "geralmente",
    "pode ser que" quando não há base no contexto.
  • PROIBIDO: Responder com informações de leis ou decretos que
    NÃO estão presentes em <CONTEXTO>, mesmo que você "saiba".

REGRA 4 — MODO DE RESPOSTA
  O usuário pode solicitar um dos dois modos. Responda no modo
  indicado pela variável {modo}:

  modo = "TÉCNICO"
    → Linguagem precisa e jurídica.
    → Pode usar termos como "caput", "inciso", "alínea".
    → Público: contadores e profissionais da área.

  modo = "SIMPLIFICADO"
    → Linguagem clara, direta, sem jargão jurídico.
    → Substitua termos técnicos por explicações curtas.
    → Exemplo: em vez de "conforme o caput do Art. 32",
      use "segundo o artigo 32 da lei".
    → Público: pequenos empresários, MEI, pessoas físicas.
    → IMPORTANTE: as citações permanecem mesmo no modo
      simplificado — nunca as omite.

REGRA 5 — PROTOCOLO DE FALLBACK
  Se <CONTEXTO> não contém informação suficiente para responder:

  Responda EXATAMENTE assim (adapte apenas a parte entre []):

  "Não foi possível encontrar informação suficiente nas fontes
   oficiais disponíveis para responder sobre [tema específico
   da pergunta]. Isso pode significar que:
   • O tema ainda não foi regulamentado por decreto ou ato
     normativo;
   • A informação está em uma fonte que ainda não foi
     incorporada ao sistema.
   Recomendo consultar diretamente o Planalto da República
   (planalto.gov.br) ou um profissional habilitado."

  NUNCA invente uma resposta para evitar usar o fallback.

═══════════════════════════════════════════════════════════════
EXEMPLO DE RESPOSTA CORRETA (1-shot)
═══════════════════════════════════════════════════════════════

<CONTEXTO>
[Trecho 1 | source_id: LC_214_2024 | artigo: Art. 46 | paragrafo: caput]
"Art. 46. A alíquota do CBS será de sete por cento (7%) sobre
a base de cálculo definida no art. 11 desta Lei Complementar."

[Trecho 2 | source_id: LC_214_2024 | artigo: Art. 46 | paragrafo: §1º]
"§ 1º A alíquota referida no caput deste artigo poderá ser
reduzida por lei, observado o limite mínimo de três e meio
por cento (3,5%)."
</CONTEXTO>

PERGUNTA: Qual é a alíquota do CBS e pode ela ser alterada?
MODO: SIMPLIFICADO

RESPOSTA:
A alíquota do CBS é de 7% sobre a base de cálculo definida na
lei [Art. 46, caput — LC 214/2024].

Essa alíquota pode ser diminuída por uma nova lei no futuro,
mas não pode cair abaixo de 3,5% [Art. 46, §1º — LC 214/2024].

═══════════════════════════════════════════════════════════════
BLOCO DE ENTRADA (preenchido pelo sistema)
═══════════════════════════════════════════════════════════════

<CONTEXTO>
{context_chunks}
</CONTEXTO>

PERGUNTA: {user_question}
MODO: {response_mode}

RESPOSTA:`,

    annotations: [
      {
        directive: "IDENTIDADE E PAPEL",
        technique: "Role Assignment",
        rationale: "Define o modelo como um papel narrow e especializado. Modelos respondem melhor quando o papel é concreto e limitado. A frase 'Você NÃO possui conhecimento próprio sobre este tema'force-bounds o modelo ao contexto — sem isso, modelos como Mixtral vão inevitavelmente vazar conhecimento de pré-treinamento sobre a reforma."
      },
      {
        directive: "REGRA 1 — Exclusividade",
        technique: "Bounded Context Constraint",
        rationale: "Esta é a regra mais crítica do prompt. Pesquisa da Datadog (2025) mostra que RAG sozinho NÃO previne alucinações — o modelo pode fabricar respostas citando fontes. A instrução explícita de exclusividade + a referência ao fallback cria dois gatilhos: um positivo (use o contexto) e um negativo (se não tiver, pare). Os dois são necessários — apenas um não é suficiente."
      },
      {
        directive: "REGRA 2 — Citação inline",
        technique: "Output Format Enforcement",
        rationale: "Citação no final da resposta é facilmente ignorada pelo modelo. Citação IMEDIATAMENTE após cada afirmação força o modelo a processar a fonte enquanto gera cada sentença — isso atua como um implicit chain-of-thought: o modelo precisa verificar a fonte antes de continuar. O formato exato entre colchetes é prescritivo para facilitar parsing programático no backend (regex extrair citações para o painel de fontes do frontend)."
      },
      {
        directive: "REGRA 3 — Proibições",
        technique: "Negative Constraints",
        rationale: "LLMs respondem melhor a instruções positivas, mas em domínios de alta fidelidade as proibições são essenciais como guardrails. Cada proibição aqui mapeia para um tipo específico de falha observado em RAGs jurídicos: (1) interpretação além do texto = risco legal; (2) exemplos inventados = confiança falsa; (3) projeção em situações específicas = o modelo se tornaria consultor jurídico não habilitado. As proibições são listadas com exemplos concretos do que NÃO fazer — sem exemplos, modelos frequentemente violam regras abstratas."
      },
      {
        directive: "REGRA 4 — Modo de resposta",
        technique: "Conditional Instruction Branching",
        rationale: "A variável {modo} permite que o mesmo prompt sirva dois personas sem duplicar lógica. O modo SIMPLIFICADO mantém citações — isso é deliberado: remover citações no modo simplificado quebraria a confiabilidade do produto. A instrução explícita 'as citações permanecem' evita que o modelo 'ajude' o usuário simplificando demais e removendo referências."
      },
      {
        directive: "REGRA 5 — Fallback",
        technique: "Explicit Fallback Protocol",
        rationale: "Este é o mecanismo mais importante contra alucinação no produto. Pesquisa mostra que modelos evitam dizer 'não sei' porque benchmarks de treinamento penalizam abstinência. Fornecer um template EXATO de como fallback deve parecer remove a ambiguidade — o modelo não precisa 'decidir' como recusar, ele copia o formato. O fallback também oferece valor ao usuário (orientação para fontes externas) em vez de ser um dead end."
      },
      {
        directive: "EXEMPLO (1-shot)",
        technique: "Few-Shot Learning",
        rationale: "Um único exemplo bem construído demonstra simultaneamente: formato de citação inline, tom do modo simplificado, e como duas informações relacionadas são organizadas em parágrafos separados com citações distintas. Usar apenas 1 exemplo é deliberado — exemplos demais aumentam context window sem proportional benefit nesse uso case (a estrutura já é clara com um exemplo). O exemplo usa dados fictícios (Art. 46) para não criar confusão com dados reais no contexto."
      }
    ]
  },
  validator: {
    title: "PROMPT 02 — Validator (LLM-as-a-Judge)",
    subtitle: "Valida a resposta do gerador antes de retornar ao usuário",
    role: "Avalia se a resposta do gerador cumpre todos os critérios de aceitação",
    color: "violet",
    techniques: ["LLM-as-a-Judge", "Rubric-Based Evaluation", "Structured Output (JSON)", "Atomic Claim Decomposition", "Entailment Verification", "Severity Classification"],
    prompt: `SISTEMA — REFORMATAX VALIDADOR
═══════════════════════════════════════════════════════════════

IDENTIDADE E PAPEL
───────────────────
Você é o módulo de validação da ReformaTax. Sua função ÚNICA é
analisar uma resposta gerada pelo sistema e determinar se ela
cumpre todos os critérios de qualidade antes de ser mostrada ao
usuário.

Você NÃO reescreve a resposta. Você NÃO sugere melhorias.
Você apenas AVALIA e emite um veredicto estruturado.

═══════════════════════════════════════════════════════════════
ENTRADAS QUE VOCÊ RECEBE
═══════════════════════════════════════════════════════════════

<CONTEXTO_ORIGINAL>
  Os trechos de lei recuperados pelo sistema RAG (fonte da
  verdade).
</CONTEXTO_ORIGINAL>

<PERGUNTA_USUARIO>
  A pergunta original do usuário.
</PERGUNTA_USUARIO>

<RESPOSTA_GERADA>
  A resposta produzida pelo módulo Gerador.
</RESPOSTA_GERADA>

═══════════════════════════════════════════════════════════════
PROCESSO DE AVALIAÇÃO (siga esta ordem EXATA)
═══════════════════════════════════════════════════════════════

PASSO 1 — DECOMPOSIÇÃO EM CLAIMS ATÔMICOS
  Quebre a <RESPOSTA_GERADA> em afirmações individuais (claims).
  Cada claim é uma sentença ou fragmento que contém uma única
  informação verificável.

  Exemplo:
    Resposta: "A alíquota do CBS é 7% [Art. 46 — LC 214/2024].
    Ela pode ser reduzida até 3,5% [Art. 46, §1º — LC 214/2024]."
    
    Claims:
      C1: "A alíquota do CBS é 7%"
      C2: "Ela pode ser reduzida até 3,5%"

PASSO 2 — VERIFICAÇÃO POR CLAIM
  Para CADA claim, verifique contra <CONTEXTO_ORIGINAL>:

  ├── SUPPORTED: O claim tem suporte direto em um trecho do
  │   contexto. O significado é fiel ao texto original.
  ├── CONTRADICTED: O claim contradiz explicitamente um trecho
  │   do contexto (ex: número errado, artigo invertido).
  └── UNSUPPORTED: O claim não tem nenhum trecho no contexto
      que o suporte. Pode ser verdade em geral, mas não pode
      ser verificado pelo contexto fornecido.

PASSO 3 — VERIFICAÇÃO DE CITAÇÕES
  Para cada claim, verifique se a citação inline:
  ├── EXISTS: A citação está presente após o claim.
  ├── CORRECT: A citação aponta para o trecho que realmente
  │   suporta o claim.
  ├── MISSING: Não há citação após o claim.
  └── WRONG: A citação existe mas aponta para um trecho
      diferente do que suporta o claim.

PASSO 4 — VERIFICAÇÃO DE FALLBACK
  Se <CONTEXTO_ORIGINAL> não contém informação para responder
  <PERGUNTA_USUARIO>:
  ├── A resposta usou o protocolo de fallback? → PASS
  └── A resposta tentou responder mesmo assim? → FAIL (crítico)

PASSO 5 — VERIFICAÇÃO DE MODO
  Se o modo era SIMPLIFICADO:
  ├── A resposta usa linguagem acessível? → PASS
  ├── A resposta usa jargão jurídico não explicado? → WARN
  └── As citações foram mantidas? → deve ser PASS sempre

═══════════════════════════════════════════════════════════════
CLASSIFICAÇÃO DE SEVERIDADE
═══════════════════════════════════════════════════════════════

  CRÍTICO — Bloqueia a resposta (não pode ser enviada ao
            usuário):
    • Qualquer claim CONTRADICTED
    • Qualquer claim UNSUPPORTED
    • Citação MISSING em qualquer claim
    • Citação WRONG em qualquer claim
    • Falha no protocolo de fallback quando contexto insuficiente

  AVISO — Resposta pode ser enviada mas deve ser flagged:
    • Modo SIMPLIFICADO com jargão não explicado
    • Resposta muito longa sem estruturação clara

═══════════════════════════════════════════════════════════════
OUTPUT OBRIGATÓRIO — formato JSON estrito
═══════════════════════════════════════════════════════════════

Responda APENAS com o JSON abaixo. Nada mais. Sem texto antes
ou depois. Sem markdown. Apenas JSON válido.

{
  "veredicto": "PASS" | "FAIL",
  "severidade": "OK" | "AVISO" | "CRITICO",
  "claims": [
    {
      "id": "C1",
      "texto": "<texto do claim extraído>",
      "suporte": "SUPPORTED" | "CONTRADICTED" | "UNSUPPORTED",
      "trecho_fonte": "<trecho do contexto que suporta ou contradiz>",
      "citacao_status": "CORRECT" | "MISSING" | "WRONG",
      "citacao_presente": "<citação como aparece na resposta ou null>",
      "severidade": "OK" | "CRITICO"
    }
  ],
  "fallback_verificado": {
    "contexto_suficiente": true | false,
    "fallback_usado": true | false,
    "status": "PASS" | "FAIL"
  },
  "modo_verificado": {
    "modo_solicitado": "TÉCNICO" | "SIMPLIFICADO",
    "linguagem_adequada": true | false,
    "citacoes_presentes": true | false,
    "status": "PASS" | "WARN"
  },
  "resumo": "<Explicação em 1-2 sentenças do resultado>"
}

═══════════════════════════════════════════════════════════════
BLOCO DE ENTRADA (preenchido pelo sistema)
═══════════════════════════════════════════════════════════════

<CONTEXTO_ORIGINAL>
{context_chunks}
</CONTEXTO_ORIGINAL>

<PERGUNTA_USUARIO>
{user_question}
</PERGUNTA_USUARIO>

<RESPOSTA_GERADA>
{generated_response}
</RESPOSTA_GERADA>

MODO SOLICITADO: {response_mode}

AVALIE:`,

    annotations: [
      {
        directive: "Identidade restrita",
        technique: "Role Boundary Enforcement",
        rationale: "O validador precisa ser extremamente focused. As instruções 'NÃO reescreve' e 'NÃO sugere' evitam que o modelo drift para um comportamento de 'assistente útil' e comece a modificar a resposta em vez de apenas avaliar. Sem essas instruções, LLMs naturalmente tentam 'ajudar' corrigindo o texto."
      },
      {
        directive: "PASSO 1 — Decomposição atômica",
        technique: "Atomic Claim Decomposition",
        rationale: "Pesquisa do HaluCheck (2025) demonstra que avaliar respostas como bloco monolítico produz resultados imprecísos. Decompor em claims atômicos força o modelo a verificar cada fato individualmente. Isso captura alucinações parciais — onde 80% da resposta está correta mas um claim específico é fabricado. Sem decomposição, esse claim passa despercebido."
      },
      {
        directive: "PASSO 2 — Classificação tripartite",
        technique: "Entailment-Based Verification",
        rationale: "A distinção entre CONTRADICTED e UNSUPPORTED é critical. Datadog (2025) identifica essas como dois tipos diferentes de alucinação com impactos distintos: CONTRADICTED é um erro fático direto (mais grave); UNSUPPORTED pode ser verdade mas não pode ser verificado pelo contexto (ainda grave para este produto, porque a promessa é que TUDO vem de fontes oficiais). Classificar ambos como 'erro genérico' perderia essa distinção."
      },
      {
        directive: "PASSO 3 — Verificação de citações",
        technique: "Citation Faithfulness Check",
        rationale: "Este é o check que pega o pior tipo de alucinação em sistemas legais: citação fabricada. O modelo pode gerar 'Art. 32, §3º — LC 214/2024' que soa legítimo mas esse artigo não existe ou diz outra coisa. Verificar não apenas se a citação existe, mas se ela aponta para o trecho correto, captura essa classe de erro. A Datadog nota que 'LLMs can still fabricate responses while citing sources' — exatamente isso que este check previne."
      },
      {
        directive: "PASSO 4 — Fallback check",
        technique: "Abstention Verification",
        rationale: "Pesquisa (Lakera, 2025) mostra que LLMs são penalizados durante treinamento por dizer 'não sei', criando bias para sempre tentar responder. Este check force-verifica se o modelo usou o fallback quando deveria. Sem verificação explícita, o gerador pode ignorar o protocolo de fallback de forma consistente — uma falha silenciosa que não aparece em testes simples."
      },
      {
        directive: "OUTPUT JSON estrito",
        technique: "Structured Output Enforcement",
        rationale: "O validador é chamado programmaticamente pelo backend. A resposta precisa ser parseable por código. Instruções como 'Nada mais. Sem texto antes ou depois. Sem markdown' são necessárias porque LLMs por padrão adicionar explicações e formatação ao redor do JSON. Usar structured output via FSM (se disponível na API) é ainda melhor, mas estas instruções são o fallback quando FSM não está disponível."
      },
      {
        directive: "Classificação de severidade",
        technique: "Tiered Decision Framework",
        rationale: "Nem todos os problemas são iguais. Uma resposta com jargão não explicado no modo simplificado pode ser enviada com um aviso no frontend. Uma resposta com claim UNSUPPORTED não pode ser enviada nunca. A classificação em tiers permite que o backend tome decisões automatizadas: CRITICO → bloqueia; AVISO → envia com flag; OK → envia normal. Sem tiers, o backend teria que implementar essa lógica de decisão — mais complexidade."
      }
    ]
  }
};

const IntegrationCode = () => (
  <div className="border border-slate-700/40 rounded-xl overflow-hidden">
    <div className="bg-slate-900/60 px-5 py-3 flex items-center justify-between">
      <span className="text-xs font-mono text-slate-400">pipeline/rag_pipeline.py — Integração dos dois prompts</span>
      <span className="text-xs px-2 py-0.5 rounded bg-sky-900/40 text-sky-300 border border-sky-700/50 font-mono">Integration</span>
    </div>
    <pre className="p-5 text-xs text-slate-300 overflow-x-auto leading-relaxed bg-slate-950">{`from groq import Groq
import json, re
from enum import Enum

client = Groq(api_key=GROQ_API_KEY)


class Veredicto(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class Severidade(Enum):
    OK = "OK"
    AVISO = "AVISO"
    CRITICO = "CRITICO"


# ─── Carrega os prompts de arquivos .txt separados ───────────
# (nunca hardcode prompts longos no código)

def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

GENERATOR_PROMPT = load_prompt("prompts/generator.txt")
VALIDATOR_PROMPT = load_prompt("prompts/validator.txt")


# ─── STEP 1: Geração ─────────────────────────────────────────

def generate_response(
    context_chunks: list[dict],
    user_question: str,
    mode: str = "SIMPLIFICADO"  # ou "TÉCNICO"
) -> str:

    # Formata contexto com metadados estruturados
    formatted_context = format_context_chunks(context_chunks)

    # Injeta variáveis no template do prompt
    filled_prompt = GENERATOR_PROMPT.replace(
        "{context_chunks}", formatted_context
    ).replace(
        "{user_question}", user_question
    ).replace(
        "{modo}", mode
    )

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": filled_prompt}
        ],
        temperature=0.1,   # determinismo alto
        max_tokens=800,
    )

    return response.choices[0].message.content


# ─── STEP 2: Validação ───────────────────────────────────────

def validate_response(
    context_chunks: list[dict],
    user_question: str,
    generated_response: str,
    mode: str
) -> dict:

    formatted_context = format_context_chunks(context_chunks)

    filled_prompt = VALIDATOR_PROMPT.replace(
        "{context_chunks}", formatted_context
    ).replace(
        "{user_question}", user_question
    ).replace(
        "{generated_response}", generated_response
    ).replace(
        "{response_mode}", mode
    )

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": filled_prompt}
        ],
        temperature=0.0,   # zero — output deve ser determinístico
        max_tokens=1500,   # JSON pode ser grande com muitos claims
    )

    raw = response.choices[0].message.content

    # Parse seguro do JSON (remove markdown se o modelo adicionar)
    cleaned = re.sub(r'\`\`\`(?:json)?\\n?', '', raw).strip()
    validation_result = json.loads(cleaned)

    return validation_result


# ─── STEP 3: Pipeline completo com decisão automática ────────

def query_reformatax(
    context_chunks: list[dict],
    user_question: str,
    mode: str = "SIMPLIFICADO"
) -> dict:

    # 1. Gera resposta
    generated = generate_response(context_chunks, user_question, mode)

    # 2. Valida resposta
    validation = validate_response(
        context_chunks, user_question, generated, mode
    )

    severidade = Severidade(validation["severidade"])
    veredicto = Veredicto(validation["veredicto"])

    # 3. Decisão automática baseada no veredicto
    if severidade == Severidade.CRITICO:
        # Bloqueia — retorna fallback padrão ao usuário
        return {
            "status": "BLOCKED",
            "response": None,
            "fallback": generate_fallback_message(user_question),
            "validation": validation,
            # Log interno para debugging
            "debug": {"generated_blocked": generated}
        }

    elif severidade == Severidade.AVISO:
        # Envia com flag no frontend
        return {
            "status": "WARNING",
            "response": generated,
            "validation": validation,
            "warning_details": [
                c for c in validation["claims"]
                if c["severidade"] != "OK"
            ]
        }

    else:
        # Clean pass
        return {
            "status": "OK",
            "response": generated,
            "validation": validation
        }


# ─── Helper: formata chunks com metadados para injeção ───────

def format_context_chunks(chunks: list[dict]) -> str:
    formatted = []
    for i, chunk in enumerate(chunks):
        meta = chunk.get("metadata", {})
        header_parts = [f"source_id: {meta.get('source_id', 'unknown')}"]
        if meta.get("artigo"):
            header_parts.append(f"artigo: {meta['artigo']}")
        if meta.get("paragrafo"):
            header_parts.append(f"paragrafo: {meta['paragrafo']}")

        formatted.append(
            f"[Trecho {i+1} | {' | '.join(header_parts)}]\\n"
            f"{chunk['text']}"
        )

    return "\\n\\n".join(formatted)


def generate_fallback_message(question: str) -> str:
    # Fallback padrão quando validação bloqueia
    return (
        "Não foi possível encontrar informação suficiente nas "
        "fontes oficiais disponíveis para responder sobre esta "
        "pergunta. Isso pode significar que o tema ainda não foi "
        "regulamentado ou está em uma fonte não incorporada ao "
        "sistema. Recomendo consultar o Planalto da República "
        "(planalto.gov.br) ou um profissional habilitado."
    )`}</pre>
  </div>
);

interface ColorConfig {
  badge: string;
  accent: string;
  border: string;
  bg: string;
  btnActive: string;
}

export default function PromptSystem() {
  const [activeTab, setActiveTab] = useState("generator");
  const [showPrompt, setShowPrompt] = useState(true);
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [showIntegration, setShowIntegration] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);

  const current = promptData[activeTab];

  const colorMap: Record<string, ColorConfig> = {
    emerald: {
      badge: "bg-emerald-900/40 text-emerald-300 border-emerald-700/50",
      accent: "text-emerald-400",
      border: "border-emerald-800/40",
      bg: "bg-emerald-950/15",
      btnActive: "bg-emerald-900/40 text-emerald-300 border-emerald-700/50",
    },
    violet: {
      badge: "bg-violet-900/40 text-violet-300 border-violet-700/50",
      accent: "text-violet-400",
      border: "border-violet-800/40",
      bg: "bg-violet-950/15",
      btnActive: "bg-violet-900/40 text-violet-300 border-violet-700/50",
    },
  };
  const c = colorMap[current.color];

  const handleCopy = () => {
    navigator.clipboard.writeText(current.prompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100" style={{ fontFamily: "'SF Mono', 'Fira Code', monospace" }}>
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded bg-emerald-600 flex items-center justify-center">
                <span className="text-xs font-bold text-white">RT</span>
              </div>
              <div>
                <span className="text-sm font-semibold text-slate-200">ReformaTax</span>
                <span className="text-slate-600 text-xs ml-2">System Prompts v1.0</span>
              </div>
            </div>
            <div className="flex gap-1">
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">Production</span>
            </div>
          </div>

          {/* Prompt selector tabs */}
          <div className="flex gap-2">
            {Object.entries(promptData).map(([key, val]) => (
              <button
                key={key}
                onClick={() => { setActiveTab(key); setCopiedPrompt(false); }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-xs font-mono transition-all
                  ${activeTab === key
                    ? colorMap[val.color].btnActive
                    : "border-slate-700/40 text-slate-500 hover:text-slate-300 hover:border-slate-600"
                  }`}
              >
                <span className={`w-2 h-2 rounded-full ${activeTab === key ? (val.color === "emerald" ? "bg-emerald-400" : "bg-violet-400") : "bg-slate-600"}`} />
                {val.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-6 space-y-6">

        {/* Meta card */}
        <div className={`border rounded-xl p-4 ${c.border} ${c.bg}`}>
          <div className="flex items-start justify-between">
            <div>
              <div className={`text-sm font-semibold ${c.accent} mb-1`}>{current.subtitle}</div>
              <div className="text-xs text-slate-500">{current.role}</div>
            </div>
            <div className="flex flex-wrap gap-1 justify-end max-w-xs">
              {current.techniques.map((t: string, i: number) => (
                <span key={i} className={`text-xs px-2 py-0.5 rounded border ${c.badge} font-mono`}>{t}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Toggle bar */}
        <div className="flex gap-2">
          {[ 
            { key: "prompt", label: "System Prompt", state: showPrompt, set: setShowPrompt },
            { key: "annotations", label: "Annotations", state: showAnnotations, set: setShowAnnotations },
            { key: "integration", label: "Integration Code", state: showIntegration, set: setShowIntegration },
          ].map((item) => (
            <button
              key={item.key}
              onClick={() => item.set(!item.state)}
              className={`text-xs font-mono px-3 py-1 rounded border transition-colors
                ${item.state
                  ? "bg-slate-700/40 text-slate-200 border-slate-600"
                  : "text-slate-600 border-slate-800 hover:text-slate-400"
                }`}
            >
              {item.state ? "▾" : "▸"} {item.label}
            </button>
          ))}
        </div>

        {/* PROMPT BLOCK */}
        {showPrompt && (
          <div className="border border-slate-800 rounded-xl overflow-hidden">
            <div className="bg-slate-900/60 px-5 py-3 flex items-center justify-between">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-widest">System Prompt — Copy & Deploy</span>
              <button
                onClick={handleCopy}
                className="text-xs font-mono px-3 py-1 rounded border border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors"
              >
                {copiedPrompt ? "✓ Copied" : "Copy"}
              </button>
            </div>
            <pre className="p-5 text-xs text-slate-300 overflow-x-auto leading-relaxed bg-slate-950 whitespace-pre-wrap">
              {current.prompt}
            </pre>
          </div>
        )}

        {/* ANNOTATIONS */}
        {showAnnotations && (
          <div className="border border-slate-800 rounded-xl overflow-hidden">
            <div className="bg-slate-900/60 px-5 py-3">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-widest">Annotation Map — Why Each Directive Exists</span>
            </div>
            <div className="divide-y divide-slate-800">
              {current.annotations.map((a: Annotation, i: number) => (
                <div key={i} className="p-5 hover:bg-slate-900/30 transition-colors">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-mono text-slate-600">#{String(i + 1).padStart(2, "0")}</span>
                    <span className="text-sm font-semibold text-slate-200">{a.directive}</span>
                    <span className={`text-xs px-2 py-0.5 rounded border ${c.badge} font-mono`}>{a.technique}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed ml-8">{a.rationale}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* INTEGRATION CODE */}
        {showIntegration && <IntegrationCode />}

        {/* Footer flow diagram */}
        <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
          <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-4">Pipeline Flow — Como os dois prompts se conectam</div>
          <div className="font-mono text-xs text-slate-400 whitespace-pre leading-relaxed">
{`  Usuário digita pergunta
          │
          ▼
  ┌─────────────────┐
  │  RAG Retrieval   │  → Recupera chunks relevantes do ChromaDB
  └────────┬────────┘
           │ context_chunks
           ▼
  ┌─────────────────┐
  │   GERADOR        │  ← PROMPT 01 aplicado aqui
  │  (Mixtral via    │    temperature=0.1
  │   Groq)          │    max_tokens=800
  └────────┬────────┘
           │ generated_response
           ▼
  ┌─────────────────┐
  │   VALIDADOR      │  ← PROMPT 02 aplicado aqui
  │  (Mixtral via    │    temperature=0.0
  │   Groq)          │    Retorna JSON estruturado
  └────────┬────────┘
           │ veredicto
           ▼
  ┌─────────────────┐     ┌──────────────────┐
  │  CRITICO?        │─YES─▶  Retorna fallback │  (resposta bloqueada)
  └────────┬────────┘     └──────────────────┘
           │ NO
           ▼
  ┌─────────────────┐     ┌──────────────────┐
  │  AVISO?          │─YES─▶  Envia com flag  │  (warning no UI)
  └────────┬────────┘     └──────────────────┘
           │ NO
           ▼
  ┌─────────────────┐
  │  Retorna OK      │  → Resposta + citações para o frontend
  └─────────────────┘`}
          </div>
        </div>

        {/* Critical note */}
        <div className="border border-amber-800/40 rounded-xl p-4 bg-amber-950/15">
          <div className="flex items-start gap-3">
            <span className="text-amber-400 text-sm">⚠</span>
            <div>
              <div className="text-xs font-semibold text-amber-300 mb-1">Nota de Deploy</div>
              <div className="text-xs text-slate-400 leading-relaxed">
                O Validador adiciona uma segunda chamada à API do Groq por query. No free tier isso dobre o token usage. 
                Para mitigar: use cache Redis no resultado da validação junto com a resposta (mesma cache key). 
                Respostas cacheadas não precisam ser re-validadas. No regime de uso real, isso reduce overhead de validação em ~60-70% 
                dado que queries comuns sobre a reforma são repetidas frequentemente.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}