import os
import json
from typing import TypedDict, List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# --- 1. Configuração ---
load_dotenv()
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

# --- 2. Definição do Estado (Necessário para as funções) ---
class ValidationState(TypedDict):
    matricula_id: int
    candidate_data: Optional[Dict[str, Any]]
    documents_data: Optional[List[Dict[str, Any]]]
    facts_dossier: Optional[Dict[str, Any]]
    prereq_met: bool
    prereq_message: str
    final_status: str
    final_observation: str

# --- 3. Cenário de Teste (Mude aqui para testar) ---
# Copie e cole qualquer cenário do 'test_scenarios.json' aqui dentro.
# Este é o 'scenario_4_pendente_cpf_data_nasc'
CENARIO_PARA_TESTAR = {
        "candidate_data": {
            "id_candidato": 10,
            "nome": "BRUNO GOMES DA SILVA",
            "cpf": "12345678900"
        },
        "documents_data": [
            {
                "tipo_id": 1,
                "tipo_nome": "rg",
                "dados": {
                    "nome": "BRUNO GOMES DA SILVA",
                    "cpf": "123.456.789-00",
                    "data_nascimento": "20/04/2003",
                    "registro_geral": "11.222.333-4",
                    "data_expedicao": "15/01/2022",
                    "filiacao": { "mae": "MARIA APARECIDA GOMES", "pai": "JOÃO CARLOS DA SILVA" }
                }
            },
            {
                "tipo_id": 3,
                "tipo_nome": "historico escolar",
                "dados": {
                    "nome_aluno": "BRUNO GOMES DA SILVA",
                    "nivel_ensino": "Ensino Médio",
                    "instituicao_ensino": "ESCOLA ESTADUAL PADRE ANCHIETA",
                    "tempo_letivo": "2020 - 2022",
                    "cidade": "RIO DE JANEIRO",
                    "estado": "RJ",
                    "certificacao_conclusao": True
                }
            },
            {
                "tipo_id": 4,
                "tipo_nome": "comprovante de residencia",
                "dados": {
                    "nome_titular": "MARIA APARECIDA GOMES",
                    "rua_avenida": "RUA DAS FLORES",
                    "numero_endereco": "100",
                    "bairro": "CENTRO",
                    "cidade": "RIO DE JANEIRO",
                    "estado_uf": "RJ",
                    "cep": "20000100",
                    "data_emissao": "25/10/2025",
                    "empresa_emissora": "COMPANHIA DE LUZ",
                    "cpf_vinculado": "null",
                    "tipo_documento": "conta de luz"
                }
            },
            {
                "tipo_id": 7,
                "tipo_nome": "certidao de nascimento",
                "dados": {
                    "nome_registrado": "BRUNO GOMES DA SILVA",
                    "data_nascimento": "20/04/2003",
                    "local_nascimento": "RIO DE JANEIRO - RJ",
                    "filiacao": { "mae": "MARIA APARECIDA GOMES", "pai": "JOÃO CARLOS DA SILVA" }
                }
            },
            {
                "tipo_id": 8,
                "tipo_nome": "enem",
                "dados": {
                    "nome_participante": "BRUNO GOMES DA SILVA",
                    "cpf": "12345678900",
                    "ano_enem": 2022
                }
            },
            {
                "tipo_id": 6,
                "tipo_nome": "reservista",
                "dados": {
                    "nome": "BRUNO GOMES DA SILVA",
                    "cpf": "123.456.789-00",
                    "filiacao": { "mae": "MARIA APARECIDA GOMES", "pai": "JOÃO CARLOS DA SILVA" }
                }
            }
        ]
    }

# --- 4. Funções Essenciais (Copiadas do ia_auditor_graph.py) ---

def prepare_facts_for_ai(state: ValidationState):
    """
    Nó 3: Coleta, HARMONIZA e pré-calcula dados para a IA.
    """
    print("--- [ETAPA 1: prepare_facts_for_ai] Montando dossiê de fatos harmonizado ---")
    
    candidate = state['candidate_data']
    documents = state['documents_data']
    
    # Simula as datas para consistência nos testes
    hoje_str = "2025-11-13" 
    hoje = datetime.strptime(hoje_str, '%Y-%m-%d').date()
    
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
        if not isinstance(doc.get('dados'), dict):
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
        # ID 7: Certidão de Nascimento
        elif doc['tipo_id'] == 7:
            fatos_certidao['presente'] = True
        # ID 8: Boletim do ENEM
        elif doc['tipo_id'] == 8:
            fatos_enem['presente'] = True
            fatos_enem['ano_enem'] = dados.get('ano_enem')
    
    # Padroniza para lower case para a IA (como definido no prompt)
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

def run_ai_auditor(state: ValidationState):
    """
    Nó 4: A IA Generativa aplica as Regras de Negócio ao Dossiê de Fatos HARMONIZADO.
    """
    print("--- [ETAPA 2: run_ai_auditor] IA está auditando o dossiê harmonizado ---")
    
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

    print("\n[DEBUG] Dossiê de Fatos (JSON) que será enviado para a IA:")
    print(dossie_json)
    print("-"*60)
    
    try:
        result = chain.invoke({"dossie": dossie_json})
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

# --- 5. Execução do Teste ---

if __name__ == "__main__":
    print("="*50)
    print("INICIANDO TESTE DE PROMPT ISOLADO")
    print("="*50)
    
    # 1. Monta o estado inicial (simulando a saída do 'fetch_data')
    initial_state: ValidationState = {
        "matricula_id": CENARIO_PARA_TESTAR['candidate_data'].get('id_candidato', 0),
        "candidate_data": CENARIO_PARA_TESTAR['candidate_data'],
        "documents_data": CENARIO_PARA_TESTAR['documents_data'],
        "facts_dossier": None,
        "prereq_met": False,
        "prereq_message": "",
        "final_status": "",
        "final_observation": ""
    }

    try:
        # 2. Executa o Nó de Preparação de Fatos (Pura lógica Python)
        state_after_prepare = prepare_facts_for_ai(initial_state)

        # 3. Executa o Nó de Auditoria da IA (Chamada LLM)
        final_state = run_ai_auditor(state_after_prepare)
        
        # 4. Imprime o Resultado Final
        print("\n" + "!"*20 + " RESULTADO FINAL " + "!"*20)
        print(f"Decisão Final:    {final_state.get('final_status')}")
        print(f"Observação da IA: {final_state.get('final_observation')}")
        print("!"* (40 + len(" RESULTADO FINAL ")) )

    except Exception as e:
        print(f"\n!!! ERRO DURANTE A EXECUÇÃO DO TESTE !!!")
        print(e)
    
    print("="*50)
    print("TESTE CONCLUÍDO")
    print("="*50)