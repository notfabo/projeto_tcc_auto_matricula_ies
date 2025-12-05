package rest_api.docflow.dto

import rest_api.docflow.models.Turma
import java.time.LocalDateTime

data class MatriculaResumoDTO(
    val idMatricula: Int,
    val nomeCandidato: String,
    val turma: Turma,
    val cpfCandidato: String,
    val statusMatricula: String,
    val statusPreMatricula: String?,
    val motivoPreMatricula: String?,
    val dataInscricao: LocalDateTime?
)