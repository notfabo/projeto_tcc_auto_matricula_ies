package rest_api.docflow.dto

import org.springframework.web.multipart.MultipartFile

data class DocumentoUploadRequestDTO(
    val fkCandidato: Int,
    val fkDocumentoTipo: Int,
    val subtipo: String?,
    val file: MultipartFile
)