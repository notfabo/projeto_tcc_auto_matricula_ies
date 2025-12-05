package rest_api.docflow.dto

import java.time.LocalDate

data class CandidatoResponse(
    val id: Int,
    val nome: String?,
    val cpf: String?,
    val email: String?,
    val telefone: String?,
    val dataNascimento: LocalDate?,
    val nomeSocial: String?,
    val estadoCivil: String?,
    val racaCandidato: String?,
    val orientacaoSexual: String?,
    val identidadeGenero: String?,
    val possuiDeficiencia: String?,
    val numeroCid: String?,
    val nomeCurso: String?,
) {
}