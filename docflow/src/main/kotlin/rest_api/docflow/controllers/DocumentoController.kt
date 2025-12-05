package rest_api.docflow.controllers

import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.boot.autoconfigure.security.SecurityProperties
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.core.userdetails.User
import org.springframework.web.bind.annotation.*
import rest_api.docflow.services.S3Service
import rest_api.docflow.services.SqsService
import rest_api.docflow.services.DocumentoService
import org.springframework.web.multipart.MultipartFile
import rest_api.docflow.dto.DocumentoResponseDTO
import rest_api.docflow.models.DocumentoTipo
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.repositories.DocumentoTipoRepository
import rest_api.docflow.services.DocumentoTipoService
import java.security.Principal

@RestController
@RequestMapping("/api/documentos")
class DocumentoController(
    private val s3Service: S3Service,
    private val documentoService: DocumentoService,
    private val sqsService: SqsService,
    private val documentoTipoRepository: DocumentoTipoRepository,
    private val candidatoRepository: CandidatoRepository,
    private val documentoTipoService: DocumentoTipoService
) {
    @PostMapping("/upload", consumes = [MediaType.MULTIPART_FORM_DATA_VALUE])
    fun uploadDocumento(
        @RequestParam("file") file: MultipartFile,
        @RequestParam("tipoDocumento") tipoDocumentoId: Int,
        @RequestParam("subtipo", required = false) subtipo: String?,
        principal: Principal
    ): ResponseEntity<Any> {
        val cpf = principal.name
        val candidato = candidatoRepository.findByCpf(cpf)
            ?: return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Candidato não encontrado")

        val tipo = documentoTipoRepository.findById(tipoDocumentoId)
            .orElseThrow { IllegalArgumentException("Tipo de documento inválido") }

        val tipoExigeSubtipo = tipo.nome.contains("Identidade", ignoreCase = true)
        if (tipoExigeSubtipo && subtipo.isNullOrBlank()) {
            return ResponseEntity.badRequest().body("Subtipo obrigatório para documentos de identidade (RG ou CIN).")
        }

        val caminhoArquivo = s3Service.uploadFile(file, folder = "documentos/${candidato.idCandidato}")

        val documento = documentoService.salvarOuAtualizarDocumento(
            fkCandidato = candidato.idCandidato,
            fkDocumentoTipo = tipoDocumentoId,
            novoCaminhoArquivo = caminhoArquivo,
            subtipo = if (tipoExigeSubtipo) subtipo else null
        )

        val payload = mapOf(
            "documentoId" to documento.id,
            "caminhoArquivo" to caminhoArquivo,
            "tipoDocumento" to tipo.nome,
            "cpf" to candidato.cpf,
            "subtipo" to (if (tipoExigeSubtipo) subtipo else null)
        )
        val payloadJson = ObjectMapper().writeValueAsString(payload)
        sqsService.sendMessage(payloadJson)

        val response = mapOf(
            "id" to documento.id,
            "status" to documento.statusDocumento,
            "dataUpload" to documento.dataUpload.toString(),
            "mensagem" to "Upload realizado com sucesso. O documento está em revisão."
        )
        return ResponseEntity.ok(response)
    }

    @PostMapping("/reupload", consumes = [MediaType.MULTIPART_FORM_DATA_VALUE])
    fun reuploadDocumento(
        @RequestParam("file") file: MultipartFile,
        @RequestParam("documentoId") documentoId: Int,
        @RequestParam("subtipo", required = false) subtipo: String?,
        principal: Principal
    ): ResponseEntity<Any> {
        val cpf = principal.name
        val candidato = candidatoRepository.findByCpf(cpf)
            ?: return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Candidato não encontrado")

        // verificar que o documento existe e pertence ao candidato
        val documentoExistente = documentoService.buscarDocumentoPorId(documentoId)
        if (documentoExistente.fkCandidato != candidato.idCandidato) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Documento não pertence ao candidato autenticado")
        }

        val caminhoArquivo = s3Service.uploadFile(file, folder = "documentos/${candidato.idCandidato}")

        val documento = documentoService.reuploadDocumento(
            documentoId = documentoId,
            novoCaminhoArquivo = caminhoArquivo,
            subtipo = subtipo
        )

        val tipo = documentoTipoRepository.findById(documento.fkDocumentoTipo).orElse(null)

        val payload = mapOf(
            "documentoId" to documento.id,
            "caminhoArquivo" to caminhoArquivo,
            "tipoDocumento" to (tipo?.nome ?: ""),
            "cpf" to candidato.cpf,
            "subtipo" to subtipo
        )
        val payloadJson = ObjectMapper().writeValueAsString(payload)
        sqsService.sendMessage(payloadJson)

        val response = mapOf(
            "id" to documento.id,
            "status" to documento.statusDocumento,
            "dataUpload" to documento.dataUpload.toString(),
            "mensagem" to "Reenvio realizado com sucesso. O documento está em revisão."
        )
        return ResponseEntity.ok(response)
    }

    @GetMapping("/tipos")
    fun listarTiposDeDocumento(): ResponseEntity<List<DocumentoTipo>> {
        val tipos = documentoTipoService.listarTodos()
        return ResponseEntity.ok(tipos)
    }

    @GetMapping("/me")
    fun listarMeusDocumentos(@AuthenticationPrincipal user: User): ResponseEntity<List<DocumentoResponseDTO>> {
        val documentos = documentoService.listarDocumentosDoCandidato(user.username)
        return ResponseEntity.ok(documentos)
    }

    @PostMapping("/atualizar-status")
    fun atualizarStatusDocumento(
        @RequestBody request: Map<String, Any>
    ): ResponseEntity<Any> {
        try {
            val documentoId = (request["documentoId"] as Number).toInt()
            val status = request["status"] as String
            val dadosExtraidos = request["dadosExtraidos"] as? String
            val motivoErro = request["motivoErro"] as? String

            val documento = documentoService.atualizarStatusDocumento(
                documentoId = documentoId,
                status = status,
                dadosExtraidos = dadosExtraidos,
                motivoErro = motivoErro
            )

            val response = mapOf(
                "documentoId" to documento.id,
                "status" to documento.statusDocumento,
                "mensagem" to "Status atualizado com sucesso"
            )
            return ResponseEntity.ok(response)
        } catch (e: Exception) {
            return ResponseEntity.badRequest().body(mapOf("erro" to e.message))
        }
    }
}