package rest_api.docflow.dto

data class CandidatoAdicionalDTO(
    val nomeSocial: String?,
    val estadoCivil: String?,
    val racaCandidato: String?,
    val orientacaoSexual: String?,
    val identidadeGenero: String?,
    val possuiDeficiencia: String?,
    val numeroCid: String?
)