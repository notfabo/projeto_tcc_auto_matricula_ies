import os
import json
import mysql.connector
from typing import TypedDict, List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# --- 1. Configuração ---
load_dotenv()
llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco: {err}")
        return None

# --- 2. Definição do Estado ---
class ValidationState(TypedDict):
    matricula_id: int
    candidate_data: Optional[Dict[str, Any]]
    documents_data: Optional[List[Dict[str, Any]]]
    
    facts_dossier: Optional[Dict[str, Any]]
    
    prereq_met: bool
    prereq_message: str
    
    final_status: str
    final_observation: str

# --- 3. Definição dos Nós ---

def fetch_data(state: ValidationState):
    print(f"--- [Nó: fetch_data] Processando Matrícula ID: {state['matricula_id']} ---")
    matricula_id = state['matricula_id']
    conn = get_db_connection()
    if not conn:
        return {**state, "prereq_met": False, "prereq_message": "Falha na conexão com o DB"}

    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        c.id_candidato, c.nome as candidato_nome, c.cpf as candidato_cpf, 
        d.dados_extraidos, dt.nome as tipo_documento, d.fk_documento_tipo
    FROM 
        matricula m
    JOIN 
        candidato c ON m.fk_candidato = c.id_candidato
    JOIN 
        documento d ON c.id_candidato = d.fk_candidato
    JOIN 
        documento_tipo dt ON d.fk_documento_tipo = dt.id_documento_tipo
    WHERE 
        m.id = %s AND d.status_documento = 'aprovado'
    """
    cursor.execute(query, (matricula_id,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return {**state, "prereq_met": False, "prereq_message": "Candidato sem documentos aprovados."}

    candidate_data = {
        "id_candidato": results[0]["id_candidato"],
        "nome": results[0]["candidato_nome"],
        "cpf": results[0]["candidato_cpf"].replace(".", "").replace("-", "")
    }
    
    documents_data = []
    for row in results:
        try:
            dados_json = json.loads(row["dados_extraidos"]) if isinstance(row["dados_extraidos"], str) else row["dados_extraidos"]
        except json.JSONDecodeError:
            dados_json = {"erro": "Formato JSON inválido"}
        documents_data.append({
            "tipo_id": row["fk_documento_tipo"],
            "tipo_nome": row["tipo_documento"],
            "dados": dados_json
        })
        
    return {**state, "candidate_data": candidate_data, "documents_data": documents_data}


# Nó 2: check_prerequisites (Exatamente igual ao anterior)
def check_prerequisites(state: ValidationState):
    print("--- [Nó: check_prerequisites] Verificando documentos mínimos ---")
    documents = state["documents_data"]
    if not documents:
        return {**state, "prereq_met": False, "prereq_message": "Nenhum documento aprovado."}

    has_rg = any(doc['tipo_id'] == 1 for doc in documents) # ID 1 = RG
    has_historico_concluido = any(
        doc['tipo_id'] == 3 and doc["dados"].get("certificacao_conclusao") == True 
        for doc in documents
    ) 

    if has_rg and has_historico_concluido:
        print("Pré-requisitos atendidos (RG e Histórico Concluído).")
        return {**state, "prereq_met": True}
    
    msg = "Documentos obrigatórios pendentes: "
    if not has_rg: msg += "RG não encontrado ou não aprovado. "
    if not has_historico_concluido: msg += "Histórico Escolar com conclusão não encontrado. "
    print(f"Falha nos pré-requisitos: {msg}")
    return {**state, "prereq_met": False, "prereq_message": msg}


# Nó 3: (NOVO) Prepara o "Dossiê de Fatos" para a IA
def prepare_facts_for_ai(state: ValidationState):
    """
    Nó 3: Coleta, HARMONIZA e pré-calcula dados para a IA.
    """
    print("--- [Nó: prepare_facts_for_ai] Montando dossiê de fatos harmonizado ---")
    
    candidate = state['candidate_data']
    documents = state['documents_data']
    
    hoje = datetime.now().date()
    data_limite_curso_dt = hoje + relativedelta(years=4)
    data_limite_comprovante_dt = hoje - relativedelta(months=3)

    nomes_encontrados = []
    cpfs_encontrados = []
    dobs_encontrados = []
    filiacao_encontradas = []
    rgs_normalizados = []
    nomes_validos_titularidade = [candidate['nome'].upper()]
    
    fatos_rg = {}
    fatos_comprovante = {}
    fatos_historico = {}
    fatos_enem = {}
    fatos_reservista = {}
    fatos_certidao = {}
    documentos_enviados = [] 

    # --- Início da Harmonização ---
    for doc in documents:
        print(f"[DEBUG] Processando documento tipo_id={doc.get('tipo_id')}, tipo_nome={doc.get('tipo_nome')}")
        print(f"[DEBUG] dados = {doc.get('dados')}")
        
        if not isinstance(doc.get('dados'), dict):
            print(f"[DEBUG] Pulando documento {doc.get('tipo_nome')} - dados inválidos")
            continue
            
        dados = doc['dados']
        doc_tipo_nome = doc['tipo_nome']
        documentos_enviados.append(doc_tipo_nome)

        nome = None
        if 'nome' in dados: nome = dados['nome']
        elif 'nome_aluno' in dados: nome = dados['nome_aluno']
        elif 'nome_participante' in dados: nome = dados['nome_participante']
        elif 'nome_registrado' in dados: nome = dados['nome_registrado']
        if nome:
            nomes_encontrados.append({"nome": nome, "documento": doc_tipo_nome})

        cpf = None
        if 'cpf' in dados: cpf = dados['cpf']
        elif 'cpf_vinculado' in dados: cpf = dados['cpf_vinculado'] 
        if cpf:
            cpfs_encontrados.append({"cpf": cpf.replace(".", "").replace("-", ""), "documento": doc_tipo_nome})

        if 'data_nascimento' in dados and dados['data_nascimento']:
            dobs_encontrados.append({"data": dados['data_nascimento'], "documento": doc_tipo_nome})
            
        if 'filiacao' in dados and dados['filiacao']:
            mae = dados['filiacao'].get('mae')
            pai = dados['filiacao'].get('pai')
            if mae:
                filiacao_encontradas.append({"tipo": "mae", "nome": mae, "documento": doc_tipo_nome})
                if mae.upper() not in nomes_validos_titularidade:
                    nomes_validos_titularidade.append(mae.upper())
            if pai:
                filiacao_encontradas.append({"tipo": "pai", "nome": pai, "documento": doc_tipo_nome})
                if pai.upper() not in nomes_validos_titularidade:
                    nomes_validos_titularidade.append(pai.upper())

        
        # ID 1: RG
        if doc['tipo_id'] == 1:
            try:
                exp_str = dados.get('data_expedicao')
                exp_dt = datetime.strptime(exp_str, '%d/%m/%Y').date()
                venc_dt = exp_dt + relativedelta(years=10)
                fatos_rg['calculado_data_vencimento'] = venc_dt.isoformat()
            except Exception:
                fatos_rg['calculado_data_vencimento'] = None
            rg_num = None
            for k in ('registro_geral', 'registro', 'numero_rg', 'rg'):
                if k in dados and dados.get(k):
                    rg_num = dados.get(k)
                    break
            if rg_num:
                rg_norm = str(rg_num).replace('.', '').replace('-', '').replace(' ', '').upper()
                rgs_normalizados.append({
                    'original': rg_num,
                    'normalizado': rg_norm,
                    'documento': doc_tipo_nome
                })

        # ID 3: Histórico Escolar
        elif doc['tipo_id'] == 3:
            fatos_historico['certificacao_conclusao'] = dados.get('certificacao_conclusao', False)
        
        # ID 4: Comprovante de Residência
        elif doc['tipo_id'] == 4:
            fatos_comprovante['titular'] = dados.get('nome_titular')
            fatos_comprovante['titular_upper'] = dados.get('nome_titular', '').upper()
            fatos_comprovante['cpf_vinculado'] = dados.get('cpf_vinculado')
            try:
                emissao_str = dados.get('data_emissao')
                emissao_dt = datetime.strptime(emissao_str, '%d/%m/%Y').date()
                fatos_comprovante['calculado_data_emissao'] = emissao_dt.isoformat()
            except Exception:
                fatos_comprovante['calculado_data_emissao'] = None
        
        # ID 6: Certificado de Reservista
        elif doc['tipo_id'] == 6:
            fatos_reservista['presente'] = True
            # Dados já capturados no loop genérico (nome, cpf, filiacao)
        
        # ID 7: Certidão de Nascimento
        elif doc['tipo_id'] == 7:
            fatos_certidao['presente'] = True
            # Dados já capturados no loop genérico (nome_registrado, data_nascimento, filiacao)
        
        # ID 8: Boletim do ENEM
        elif doc['tipo_id'] == 8:
            fatos_enem['presente'] = True
            fatos_enem['ano_enem'] = dados.get('ano_enem')
            # Dados já capturados no loop genérico (nome_participante, cpf)

    nomes_encontrados_lower = [
        {"nome": n["nome"].lower() if isinstance(n.get("nome"), str) else n.get("nome"), "documento": n["documento"].lower()}
        for n in nomes_encontrados
    ]
    cpfs_encontrados_lower = [
        {"cpf": p["cpf"], "documento": p["documento"].lower()} for p in cpfs_encontrados
    ]
    rgs_encontrados_lower = [
        {
            'original': r['original'].lower() if isinstance(r.get('original'), str) else r.get('original'),
            'normalizado': r['normalizado'].lower() if isinstance(r.get('normalizado'), str) else r.get('normalizado'),
            'documento': r['documento'].lower()
        }
        for r in rgs_normalizados
    ]
    dobs_encontrados_lower = [
        {"data": d["data"], "documento": d["documento"].lower()} for d in dobs_encontrados
    ]
    filiacao_encontradas_lower = [
        {"tipo": f["tipo"], "nome": f["nome"].lower() if isinstance(f.get("nome"), str) else f.get("nome"), "documento": f["documento"].lower()} 
        for f in filiacao_encontradas
    ]
    nomes_validos_titularidade_lower = [n.lower() for n in nomes_validos_titularidade]
    documentos_enviados_lower = [d.lower() for d in documentos_enviados]

    candidate_for_ai = {**candidate, 'nome': candidate['nome'].lower(), 'cpf': candidate['cpf']}

    fatos = {
        "referencias_calculadas": {
            "data_hoje": hoje.isoformat(),
            "data_limite_curso_4_anos": data_limite_curso_dt.isoformat(),
            "data_limite_comprovante_3_meses": data_limite_comprovante_dt.isoformat()
        },
        "dados_cadastro": candidate_for_ai,
        "harmonizacao_consistencia": {
            "nomes_encontrados": nomes_encontrados_lower,
            "cpfs_encontrados": cpfs_encontrados_lower,
            "rgs_encontrados": rgs_encontrados_lower,
            "datas_nascimento_encontradas": dobs_encontrados_lower,
            "filiacao_encontradas": filiacao_encontradas_lower
        },
        "fatos_especificos": {
            "rg": fatos_rg,
            "historico_escolar": fatos_historico,
            "comprovante_residencia": fatos_comprovante,
            "enem": fatos_enem,
            "reservista": fatos_reservista,
            "certidao_nascimento": fatos_certidao,
            "nomes_validos_titularidade": list(set(nomes_validos_titularidade_lower)), 
            "documentos_enviados": list(set(documentos_enviados_lower))
        }
    }
    
    print("Dossiê harmonizado montado com sucesso.")
    return {**state, "facts_dossier": fatos}


# Nó 4: (NOVO) A IA Auditora
def run_ai_auditor(state: ValidationState):
    """
    Nó 4: A IA Generativa aplica as Regras de Negócio ao Dossiê de Fatos HARMONIZADO.
    """
    print("--- [Nó: run_ai_auditor] IA está auditando o dossiê harmonizado ---")
    
    dossie_json = json.dumps(state['facts_dossier'], indent=2, ensure_ascii=False)
    
    prompt_regras = """### REGRAS DE AUDITORIA DE MATRÍCULA

Você deve auditar o "Dossiê de Fatos" de um candidato.
O dossiê contém dados de referência, dados do cadastro e dados HARMONIZADOS de todos os documentos aprovados.

IMPORTANTE: Este processo só é acionado quando o RG (ID 1) e o Histórico Escolar (ID 3) estão com status 'aprovado'.
Todos os outros documentos são opcionais, mas se enviados e aprovados, devem ser validados.

Siga as regras abaixo e para CADA REGRA aplicável, gere um "finding" (descoberta).

#### REGRAS DE CONSISTÊNCIA ENTRE DOCUMENTOS (Erros Bloqueantes)

1. **Consistência de Nome entre Documentos:**
   - Compare o nome do cadastro (dados_cadastro.nome) com TODOS os nomes encontrados em harmonizacao_consistencia.nomes_encontrados.
   - Nomes são considerados iguais mesmo com diferenças de maiúsculas/minúsculas, acentos, espaços extras ou abreviações comuns (ex: "José" = "Jose", "Maria Silva" = "Maria da Silva", "João P." = "João Pedro").
   - ATENÇÃO: Variações significativas de nome (ex: "João Silva" vs "Pedro Santos") são ERRO.
   - Se houver discrepância significativa entre o nome do cadastro e qualquer documento (RG, Histórico Escolar, ENEM, Reservista, Certidão), é um ERRO.
   - Documentos que devem ter nome: RG, Histórico Escolar, ENEM (se presente), Reservista (se presente), Certidão (se presente).

2. **Consistência de CPF entre Documentos:**
   - O CPF do cadastro (dados_cadastro.cpf) deve ser idêntico a TODOS os CPFs encontrados em harmonizacao_consistencia.cpfs_encontrados.
   - IGNORE CPFs de comprovante de residência nesta regra (eles podem ser de terceiros).
   - CPFs são considerados iguais mesmo com pontuação diferente (ex: '123.456.789-00' = '12345678900').
   - Documentos que devem ter CPF: RG, ENEM (se presente), Reservista (se presente).
   - Se houver discrepância entre CPFs de documentos oficiais (RG, ENEM, Reservista), é um ERRO.

3. **Consistência de RG entre Documentos:**
   - Se houver múltiplos documentos com RG, compare todos entre si.
   - RGs são considerados iguais mesmo com pontuação diferente (ex: '12.345.678-9' = '123456789').
   - Se houver discrepância entre RGs de diferentes documentos, é um ERRO.
   - Normalmente apenas o RG (ID 1) contém número de RG, mas verifique se outros documentos também contêm.

4. **Consistência de Data de Nascimento entre Documentos:**
   - Todas as datas de nascimento em harmonizacao_consistencia.datas_nascimento_encontradas devem ser idênticas.
   - Datas são consideradas iguais mesmo em formatos diferentes (ex: '01/01/2000' = '2000-01-01' = '01-01-2000').
   - Documentos que devem ter data de nascimento: RG, Certidão de Nascimento (se presente).
   - Se houver discrepância entre datas de nascimento de documentos oficiais, é um ERRO.

5. **Consistência de Filiação entre Documentos:**
   - Compare todos os nomes de mãe em harmonizacao_consistencia.filiacao_encontradas onde tipo='mae'.
   - Compare todos os nomes de pai em harmonizacao_consistencia.filiacao_encontradas onde tipo='pai'.
   - Nomes são considerados iguais mesmo com diferenças de maiúsculas/minúsculas, acentos ou espaços extras.
   - Documentos que devem ter filiação: RG, Certidão de Nascimento (se presente), Reservista (se presente).
   - Se houver discrepância significativa entre filiações de documentos oficiais (ex: RG e Certidão com nomes de mãe diferentes), é um ERRO.

#### REGRAS DE VALIDAÇÃO DE DOCUMENTOS ESPECÍFICOS (Erros Bloqueantes)

6. **RG Vencido:**
   - Se fatos_especificos.rg.calculado_data_vencimento existir e for ANTERIOR à referencias_calculadas.data_hoje, é um ERRO.
   - RG vencido não pode ser aceito para matrícula.

7. **Comprovante de Residência Vencido:**
   - PRIMEIRO, verifique se 'comprovante de residencia' está na lista fatos_especificos.documentos_enviados.
   - Se NÃO estiver, ignore esta regra (OK/Não Aplicável).
   - Se ESTIVER, verifique se fatos_especificos.comprovante_residencia.calculado_data_emissao existe e é ANTERIOR à referencias_calculadas.data_limite_comprovante_3_meses.
   - Se o comprovante estiver vencido (mais de 3 meses), é um ERRO.

8. **Titularidade do Comprovante de Residência:**
   - PRIMEIRO, verifique se 'comprovante de residencia' está na lista fatos_especificos.documentos_enviados.
   - Se NÃO estiver, ignore esta regra (OK/Não Aplicável - comprovante não é obrigatório para pré-matrícula).
   - Se ESTIVER, verifique se fatos_especificos.comprovante_residencia.titular_upper está na lista fatos_especificos.nomes_validos_titularidade.
   - Nomes válidos incluem: candidato, mãe e pai (se presentes nos documentos).
   - Se o titular NÃO estiver na lista de nomes válidos:
     - Verifique se "documento do responsável" está na lista fatos_especificos.documentos_enviados.
     - Se o documento do responsável NÃO estiver presente, é um ERRO.
     - Se o documento do responsável ESTIVER presente, é um AVISO (requer análise humana para validar o vínculo).

9. **Histórico Escolar - Certificação de Conclusão:**
   - Verifique se fatos_especificos.historico_escolar.certificacao_conclusao existe e é True.
   - Se o histórico escolar não tiver certificação de conclusão, é um ERRO.
   - NOTA: Esta regra já foi validada no pré-requisito, mas confirme novamente.

10. **Validação de Documentos Obrigatórios:**
    - RG (ID 1) e Histórico Escolar (ID 3) são obrigatórios e já foram validados no pré-requisito.
    - Se algum deles estiver ausente, é um ERRO (mas isso não deveria acontecer, pois o processo só roda se ambos estiverem aprovados).

#### REGRAS DE AVISO (Não-Bloqueantes, mas importantes)

11. **RG a Vencer:**
    - Se fatos_especificos.rg.calculado_data_vencimento for POSTERIOR à referencias_calculadas.data_hoje, mas ANTERIOR à referencias_calculadas.data_limite_curso_4_anos, é um AVISO.
    - O candidato precisará renovar o RG antes de se formar.

12. **Documentos Opcionais Ausentes:**
    - Se o candidato for do sexo masculino e não tiver Certificado de Reservista na lista fatos_especificos.documentos_enviados, é um AVISO (pode ser obrigatório dependendo da instituição).
    - Se o candidato entrar pelo SISU/ENEM e não tiver Boletim do ENEM na lista fatos_especificos.documentos_enviados, é um AVISO.
    - NOTA: Esta validação é informativa, pois não temos acesso ao sexo do candidato ou forma de ingresso no dossiê atual.

13. **Inconsistências Menores:**
    - Se houver pequenas variações de nome que não sejam erros (ex: abreviações aceitáveis), mas que mereçam atenção, gere um AVISO.

---
### SUA TAREFA

1. Analise cuidadosamente o "Dossiê de Fatos" do candidato.
2. Aplique TODAS as regras acima que sejam aplicáveis aos documentos recebidos.
   - Se um documento não foi enviado, ignore as regras específicas daquele documento.
   - Se um documento foi enviado, valide todas as regras relacionadas a ele.
3. Gere uma lista de findings (descobertas) para cada regra aplicável.
   - Cada finding deve ter: tipo ("OK", "AVISO" ou "ERRO"), regra (número e nome), e detalhe (descrição clara).
4. Tome uma decisao_final:
   - 'pendente': se houver QUALQUER finding do tipo 'ERRO'.
   - 'aprovado': se NÃO houver erros e todos os dados estiverem consistentes e em conformidade.
5. Escreva uma observacao_final em português para o administrador:
   - Se 'pendente': liste APENAS os motivos dos ERROS encontrados, de forma clara e objetiva.
   - Se 'aprovado': liste APENAS os AVISOS (se houver). Se não houver avisos, escreva "Dados consistentes e pré-aprovados pela IA."

### FORMATO DE RESPOSTA

Responda APENAS em formato JSON válido com a estrutura:
{{
    "findings": [
        {{"tipo": "OK", "regra": "Regra 1 - Consistência de Nome", "detalhe": "Todos os nomes estão consistentes entre os documentos."}},
        {{"tipo": "ERRO", "regra": "Regra 2 - Consistência de CPF", "detalhe": "CPF do RG (12345678900) difere do CPF do ENEM (98765432100)."}},
        {{"tipo": "AVISO", "regra": "Regra 11 - RG a Vencer", "detalhe": "RG vencerá em 2026, antes da conclusão do curso prevista para 2029."}}
    ],
    "decisao_final": "aprovado" | "pendente",
    "observacao_final": "Texto descritivo em português para o administrador."
}}"""
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", prompt_regras),
        ("user", "Por favor, audite o seguinte Dossiê de Fatos:\n\n{dossie}")
    ])
    
    parser = JsonOutputParser()
    chain = prompt_template | llm | parser

    print("\n" + "="*30 + " [DEBUG] DOSSIÊ DE FATOS ENVIADO PARA A IA " + "="*30)
    print(dossie_json) 
    print("\n" + "="* (60 + len(" [DEBUG] DOSSIÊ DE FATOS ENVIADO PARA A IA ")) + "\n")
    
    try:
        result = chain.invoke({"dossie": dossie_json})
        print(f"Decisão da IA: {result}")
        return {
            **state,
            "final_status": result['decisao_final'],
            "final_observation": result['observacao_final']
        }
    except Exception as e:
        print(f"Erro no nó de auditoria da IA: {e}")
        return {
            **state,
            "final_status": "pendente",
            "final_observation": f"Erro interno da IA ao auditar: {e}"
        }

def update_db_prereq_fail(state: ValidationState):
    print("--- [Nó: update_db_prereq_fail] Atualizando DB (Falha Prereq) ---")
    conn = get_db_connection()
    if not conn: return {**state, "final_status": "erro", "final_observation": "Falha DB"}
    
    cursor = conn.cursor()
    query = "UPDATE matricula SET status_pre_matricula = 'pendente', motivo_pre_matricula = %s, data_atualizacao = NOW() WHERE id = %s"
    try:
        cursor.execute(query, (state['prereq_message'], state['matricula_id']))
        conn.commit()
    except Exception as e:
        print(f"Erro DB: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    return {**state, "final_status": "pendente", "final_observation": state['prereq_message']}


def update_db_final_decision(state: ValidationState):
    print("--- [Nó: update_db_final_decision] Atualizando DB (Decisão Final da IA) ---")
    conn = get_db_connection()
    if not conn: return {**state, "final_status": "erro", "final_observation": "Falha DB"}
    
    cursor = conn.cursor()
    
    query = """
    UPDATE matricula 
    SET 
        status_pre_matricula = %s,
        motivo_pre_matricula = %s,
        data_atualizacao = NOW() 
    WHERE id = %s
    """
    
    try:
        status_pre_matricula = state['final_status']
        # Sempre salva os comentários da IA em motivo_pre_matricula (não em observacoes)
        # observacoes é apenas para quando o admin aprova/reprova a MATRÍCULA final
        motivo_pre_matricula = state['final_observation'] if state['final_observation'] else None
        
        cursor.execute(query, (
            state['final_status'],
            motivo_pre_matricula,
            state['matricula_id']
        ))
        conn.commit()
        print(f"Matrícula {state['matricula_id']} atualizada pela IA para: {state['final_status']}")
        
        if state['final_status'] == 'pendente' and state.get('documents_to_reject'):
            for doc_id in state.get('documents_to_reject', []):
                update_doc_query = """
                UPDATE documento 
                SET status_documento = 'reprovado',
                    motivo_erro = JSON_OBJECT('motivo', %s)
                WHERE id = %s
                """
                cursor.execute(update_doc_query, (state['final_observation'], doc_id))
            conn.commit()
            
    except Exception as e:
        print(f"Erro DB: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    return state


# --- 4. Arestas Condicionais ---

def should_run_audit(state: ValidationState):
    """Decide se vai para a auditoria da IA ou se falha por pré-requisito."""
    print("--- [Aresta: should_run_audit] ---")
    if state["prereq_met"]:
        print("Decisão: Ir para 'prepare_facts_for_ai'")
        return "run_audit"
    else:
        print("Decisão: Ir para 'update_db_prereq_fail'")
        return "fail_prereq"

# --- 5. Montagem do Grafo ---

print("Compilando o grafo da IA Auditora...")
workflow = StateGraph(ValidationState)

workflow.add_node("fetch_data", fetch_data)
workflow.add_node("check_prerequisites", check_prerequisites)
workflow.add_node("prepare_facts_for_ai", prepare_facts_for_ai) 
workflow.add_node("run_ai_auditor", run_ai_auditor)           
workflow.add_node("update_db_prereq_fail", update_db_prereq_fail)
workflow.add_node("update_db_final_decision", update_db_final_decision)

workflow.set_entry_point("fetch_data")

workflow.add_edge("fetch_data", "check_prerequisites")

workflow.add_conditional_edges(
    "check_prerequisites",
    should_run_audit,
    {
        "run_audit": "prepare_facts_for_ai", 
        "fail_prereq": "update_db_prereq_fail" 
    }
)

workflow.add_edge("prepare_facts_for_ai", "run_ai_auditor")
workflow.add_edge("run_ai_auditor", "update_db_final_decision")
workflow.add_edge("update_db_prereq_fail", END)
workflow.add_edge("update_db_final_decision", END)
app = workflow.compile()
