package rest_api.docflow.services

import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.scheduling.annotation.Async
import org.springframework.web.multipart.MultipartFile
import org.springframework.web.server.ResponseStatusException
import rest_api.docflow.dto.DocumentoResponseDTO
import rest_api.docflow.models.Candidato
import rest_api.docflow.models.Documento
import rest_api.docflow.models.DocumentoTipo
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.repositories.DocumentoRepository
import rest_api.docflow.repositories.DocumentoTipoRepository
import java.time.LocalDateTime

@Service
class DocumentoService(
    private val documentoRepository: DocumentoRepository,
    private val candidatoRepository: CandidatoRepository,
    private val s3Service: S3Service,
    private val matriculaService: MatriculaService
) {
    fun salvarOuAtualizarDocumento(
        fkCandidato: Int,
        fkDocumentoTipo: Int,
        novoCaminhoArquivo: String,
        subtipo: String?
    ): Documento {
        val documentoExistente = documentoRepository.findByFkCandidatoAndFkDocumentoTipo(fkCandidato, fkDocumentoTipo)

        if (documentoExistente != null) {
            val caminhoAntigo = documentoExistente.caminhoArquivo

            documentoExistente.apply {
                caminhoArquivo = novoCaminhoArquivo
                statusDocumento = "revisao"
                dadosExtraidos = null
                motivoErro = null
                dataUpload = LocalDateTime.now()
                dataValidacao = null
                this.subtipo = subtipo
            }

            val documentoAtualizado = documentoRepository.save(documentoExistente)

            if (caminhoAntigo != null && caminhoAntigo != novoCaminhoArquivo) {
                try {
                    s3Service.deleteFile(caminhoAntigo)
                } catch (e: Exception) {
                    println("AVISO: Falha ao deletar arquivo antigo do S3: $caminhoAntigo. Erro: ${e.message}")
                }
            }

            return documentoAtualizado

        } else {
            val novoDocumento = Documento(
                fkCandidato = fkCandidato,
                fkDocumentoTipo = fkDocumentoTipo,
                caminhoArquivo = novoCaminhoArquivo,
                statusDocumento = "revisao",
                dadosExtraidos = null,
                subtipo = subtipo
            )
            return documentoRepository.save(novoDocumento)
        }
    }

    fun reuploadDocumento(documentoId: Int, novoCaminhoArquivo: String, subtipo: String?): Documento {
        val documentoExistente = documentoRepository.findById(documentoId)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Documento não encontrado") }

        val caminhoAntigo = documentoExistente.caminhoArquivo

        documentoExistente.apply {
            caminhoArquivo = novoCaminhoArquivo
            statusDocumento = "revisao"
            dadosExtraidos = null
            motivoErro = null
            dataUpload = LocalDateTime.now()
            dataValidacao = null
            this.subtipo = subtipo
        }

        val documentoAtualizado = documentoRepository.save(documentoExistente)

        if (caminhoAntigo != null && caminhoAntigo != novoCaminhoArquivo) {
            try {
                s3Service.deleteFile(caminhoAntigo)
            } catch (e: Exception) {
                println("AVISO: Falha ao deletar arquivo antigo do S3: $caminhoAntigo. Erro: ${e.message}")
            }
        }

        return documentoAtualizado
    }

    fun atualizarStatusDocumento(
        documentoId: Int,
        status: String,
        dadosExtraidos: String? = null,
        motivoErro: String? = null
    ): Documento {
        val documento = documentoRepository.findById(documentoId)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Documento não encontrado") }
        
        documento.statusDocumento = status
        if (dadosExtraidos != null) {
            documento.dadosExtraidos = dadosExtraidos
        }
        if (motivoErro != null) {
            documento.motivoErro = motivoErro
        }
        documento.dataValidacao = LocalDateTime.now()
        
        //return documentoRepository.save(documento)
        val documentoSalvo = documentoRepository.save(documento)

        // Se o documento foi aprovado, verifica se pode iniciar a pré-matrícula
        if (status == "aprovado") {
            // dispara a verificação de forma assíncrona para não bloquear a atualização do documento
            try {
                onDocumentoAprovadoAsync(documento.fkCandidato)
            } catch (e: Exception) {
                // Se async não estiver disponível por algum motivo, fallback para chamada síncrona
                println("[DocumentoService] Erro ao disparar verificação assíncrona: ${e.message}. Tentando síncrono.")
                matriculaService.verificarEAtualizarStatusMatricula(documento.fkCandidato)
            }
        }
        
        return documentoSalvo
    }

    @Async
    fun onDocumentoAprovadoAsync(fkCandidato: Int) {
        try {
            matriculaService.verificarEAtualizarStatusMatricula(fkCandidato)
        } catch (e: Exception) {
            println("[DocumentoService] Erro na verificação assíncrona da matrícula para candidato $fkCandidato: ${e.message}")
            e.printStackTrace()
        }
    }

    fun buscarDocumentoPorId(documentoId: Int): Documento {
        return documentoRepository.findById(documentoId)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Documento não encontrado") }
    }


    fun listarDocumentosDoCandidato(cpf: String): List<DocumentoResponseDTO> {
        val candidato = candidatoRepository.findByCpf(cpf)
            ?: throw ResponseStatusException(HttpStatus.NOT_FOUND, "Candidato não encontrado")

        val documentos = documentoRepository.findByFkCandidato(candidato.idCandidato)

        return documentos.map {
            DocumentoResponseDTO(
                id = it.id,
                tipo = it.fkDocumentoTipo.toString(),
                status = it.statusDocumento,
                dadosExtraidos = it.dadosExtraidos,
                motivoErro = it.motivoErro,
                dataUpload = it.dataUpload.toString()
            )
        }
    }
}