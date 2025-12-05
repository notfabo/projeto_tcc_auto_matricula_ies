package rest_api.docflow.controllers

import org.springframework.core.io.ByteArrayResource
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import rest_api.docflow.dto.AprovarMatriculaRequest
import rest_api.docflow.dto.MatriculaDetalhesDTO
import rest_api.docflow.dto.MatriculaResumoDTO
import rest_api.docflow.dto.ReprovarMatriculaRequest
import rest_api.docflow.services.MatriculaService
import rest_api.docflow.services.PreMatriculaService
import rest_api.docflow.services.DocumentoService
import rest_api.docflow.services.S3Service

@RestController
@RequestMapping("/api/admin/matriculas")
class MatriculaController(
    private val matriculaService: MatriculaService,
    private val preMatriculaService: PreMatriculaService,
    private val documentoService: DocumentoService,
    private val s3Service: S3Service
) {

    @GetMapping("/revisao")
    fun getMatriculasParaRevisao(
        @RequestParam(required = false) status: String?
    ): ResponseEntity<List<MatriculaResumoDTO>> {
        val matriculas = matriculaService.listarMatriculasParaRevisao(status)
        return ResponseEntity.ok(matriculas)
    }

    @GetMapping("/{id}")
    fun getMatriculaDetalhes(@PathVariable id: Int): ResponseEntity<MatriculaDetalhesDTO> {
        return ResponseEntity.ok(matriculaService.buscarDetalhesMatricula(id))
    }

    @PostMapping("/{id}/aprovar")
    fun aprovarMatricula(
        @PathVariable id: Int,
        @RequestBody request: AprovarMatriculaRequest
    ): ResponseEntity<Void> {
        matriculaService.aprovarMatricula(id, request)
        return ResponseEntity.ok().build()
    }

    @PostMapping("/{id}/reprovar")
    fun reprovarMatricula(
        @PathVariable id: Int,
        @RequestBody request: ReprovarMatriculaRequest
    ): ResponseEntity<Void> {
        matriculaService.reprovarMatricula(id, request)
        return ResponseEntity.ok().build()
    }

    @PostMapping("/{id}/verificar-documentos")
    fun verificarDocumentos(@PathVariable id: Int): ResponseEntity<Void> {
        preMatriculaService.verificarEAtualizarPreMatricula(id)
        return ResponseEntity.ok().build()
    }

    @PostMapping("/processar-pendentes")
    fun processarMatriculasPendentes(): ResponseEntity<Map<String, Int>> {
        val processadas = matriculaService.processarMatriculasPendentes()
        return ResponseEntity.ok(mapOf("matriculasProcessadas" to processadas))
    }

    @GetMapping("/documentos/{documentoId}/download")
    fun downloadDocumento(@PathVariable documentoId: Int): ResponseEntity<Any> {
        try {
            val documento = documentoService.buscarDocumentoPorId(documentoId)
            
            if (documento.caminhoArquivo.isBlank()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(mapOf("erro" to "Documento não possui arquivo associado"))
            }

            val fileBytes = s3Service.downloadFile(documento.caminhoArquivo)
            
            if (fileBytes == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(mapOf("erro" to "Arquivo não encontrado no S3"))
            }

            val extension = documento.caminhoArquivo.substringAfterLast('.', "pdf")
            val contentType = when (extension.lowercase()) {
                "pdf" -> MediaType.APPLICATION_PDF
                "jpg", "jpeg" -> MediaType.IMAGE_JPEG
                "png" -> MediaType.IMAGE_PNG
                else -> MediaType.APPLICATION_OCTET_STREAM
            }

            val resource = ByteArrayResource(fileBytes)
            val fileName = "documento_${documentoId}.$extension"

            return ResponseEntity.ok()
                .contentType(contentType)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"$fileName\"")
                .body(resource)
        } catch (e: Exception) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("erro" to "Erro ao baixar documento: ${e.message}"))
        }
    }
}