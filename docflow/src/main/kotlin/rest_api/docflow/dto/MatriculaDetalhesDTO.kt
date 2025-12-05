package rest_api.docflow.dto

import rest_api.docflow.models.Turma
import java.time.LocalDateTime

data class MatriculaDetalhesDTO(
    val idMatricula: Int,
    val statusMatricula: String,
    val statusPreMatricula: String?,
    val motivoPreMatricula: String?,
    val candidato: CandidatoResponse,
    val turma: Turma?,
    val documentos: List<DocumentoResponseDTO>,
    val observacoes: String?,
    val dataAtualizacao: LocalDateTime?

)