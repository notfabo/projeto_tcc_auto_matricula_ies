package rest_api.docflow.dto

import java.time.LocalDateTime

data class DocumentoResponseDTO(
    val id: Int,
    val tipo: String,
    val status: String,
    val dadosExtraidos: String?,
    val motivoErro: String?,
    val dataUpload: String,
    val caminhoArquivo: String? = null
)
