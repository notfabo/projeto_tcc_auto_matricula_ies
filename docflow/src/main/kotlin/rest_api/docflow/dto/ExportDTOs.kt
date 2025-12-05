package rest_api.docflow.dto

import com.fasterxml.jackson.annotation.JsonProperty
import java.time.LocalDate
import java.time.LocalDateTime

data class FiliacaoDTO(
    @JsonProperty("mae")
    val mae: String?,

    @JsonProperty("pai")
    val pai: String?
)

data class DadosRgDTO(
    @JsonProperty("nome")
    val nome: String?,

    @JsonProperty("cpf")
    val cpf: String?,

    @JsonProperty("data_nascimento")
    val dataNascimento: String?,

    @JsonProperty("registro_geral")
    val registroGeral: String?,

    @JsonProperty("data_expedicao")
    val dataExpedicao: String?,

    @JsonProperty("filiacao")
    val filiacao: FiliacaoDTO?,

    @JsonProperty("naturalidade")
    val naturalidade: String?
)

data class DadosHistoricoDTO(
    @JsonProperty("nome_aluno")
    val nomeAluno: String?,

    @JsonProperty("nivel_ensino")
    val nivelEnsino: String?,

    @JsonProperty("instituicao_ensino")
    val instituicaoEnsino: String?,

    @JsonProperty("tempo_letivo")
    val tempoLetivo: String?,

    @JsonProperty("cidade")
    val cidade: String?,

    @JsonProperty("estado")
    val estado: String?,

    @JsonProperty("certificacao_conclusao")
    val certificacaoConclusao: Boolean?
)

data class DadosComprovanteResidenciaDTO(
    @JsonProperty("rua_avenida")
    val ruaAvenida: String?,

    @JsonProperty("numero_endereco")
    val numeroEndereco: String?,

    @JsonProperty("bairro")
    val bairro: String?,

    @JsonProperty("cidade")
    val cidade: String?,

    @JsonProperty("estado_uf")
    val estadoUf: String?,

    @JsonProperty("cep")
    val cep: String?,

    @JsonProperty("data_emissao")
    val dataEmissao: String?,

    @JsonProperty("cpf_vinculado")
    val cpfVinculado: String?
)

data class CandidatoAprovadoExportDTO(
    val idCandidato: Int,
    val nomeCompleto: String?,
    val cpf: String?,
    val email: String?,
    val telefone: String?,
    val dataNascimentoCandidato: LocalDate?,
    val nomeSocial: String?,
    val estadoCivil: String?,
    val racaCandidato: String?,
    val orientacaoSexual: String?,
    val identidadeGenero: String?,
    val possuiDeficiencia: String?,
    val numeroCid: String?,
    val dataInscricao: LocalDateTime?,
    val statusMatricula: String?
) {
    var nomeMae: String? = null
    var nomePai: String? = null
    var rg: String? = null
    var dataEmissaoRg: String? = null
    var naturalidade: String? = null
    var escolaEnsinoMedio: String? = null
    var anoConclusaoEnsinoMedio: String? = null
    var cidadeEscola: String? = null
    var estadoEscola: String? = null
    var enderecoRua: String? = null
    var enderecoNumero: String? = null
    var enderecoBairro: String? = null
    var enderecoCidade: String? = null
    var enderecoEstado: String? = null
    var enderecoCep: String? = null
}