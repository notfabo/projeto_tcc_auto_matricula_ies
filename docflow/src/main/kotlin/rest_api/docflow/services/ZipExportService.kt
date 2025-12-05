package rest_api.docflow.services

import org.apache.commons.io.output.ByteArrayOutputStream
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import rest_api.docflow.repositories.DocumentoRepository
import rest_api.docflow.repositories.MatriculaRepository
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

@Service
class ZipExportService(
    private val matriculaRepository: MatriculaRepository,
    private val documentoRepository: DocumentoRepository,
    private val documentoTipoRepository: rest_api.docflow.repositories.DocumentoTipoRepository,
    private val s3Service: S3Service,
    private val jobStatusService: JobStatusService
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Async
    fun gerarZipGeral(jobId: String) {
        try {
            jobStatusService.updateJobStatus(jobId, JobStatus.PROCESSING, "Iniciando busca de dados de todos os candidatos...")
            logger.info("[ZIP-GERAL] JobID $jobId - Iniciando geração de ZIP GERAL de todos os documentos.")

            val todasMatriculas = matriculaRepository.findAllWithDetails()
            if (todasMatriculas.isEmpty()) {
                logger.warn("[ZIP-GERAL] JobID $jobId - Nenhuma matrícula encontrada no sistema. Finalizando.")
                jobStatusService.updateJobStatus(jobId, JobStatus.COMPLETED, "Nenhum documento para exportar.", null)
                return
            }

            jobStatusService.updateJobStatus(jobId, JobStatus.PROCESSING, "Agrupando ${todasMatriculas.size} matrículas por turma...")

            val matriculasPorTurma = todasMatriculas.groupBy { it.turma!! }

            val byteArrayOutputStream = ByteArrayOutputStream()
            val zipOut = ZipOutputStream(byteArrayOutputStream)

            for ((turma, matriculasDaTurma) in matriculasPorTurma) {
                val turmaFolderName = "${turma.curso?.nomeCurso ?: "Curso"}_${turma.codigoTurma}".replace(Regex("[^a-zA-Z0-9_.-]"), "_")
                logger.info("[ZIP-GERAL] JobID $jobId - Processando turma: $turmaFolderName")

                for (matricula in matriculasDaTurma) {
                    val candidato = matricula.candidato ?: continue
                    val candidatoFolderName = "${candidato.nome} - ${candidato.cpf}"

                    val documentos = documentoRepository.findByFkCandidato(candidato.idCandidato)

                    for (documento in documentos) {
                        val fileBytes = s3Service.downloadFile(documento.caminhoArquivo)
                        if (fileBytes != null) {
                            val extension = documento.caminhoArquivo.substringAfterLast('.', "bin")
                            val tipoDoc = documentoTipoRepository.findById(documento.fkDocumentoTipo).orElse(null)
                            val tipoDocNome = tipoDoc?.nome?.replace(Regex("[^a-zA-Z0-9_.-]"), "_") ?: "documento"

                            val zipEntry = ZipEntry("$turmaFolderName/$candidatoFolderName/$tipoDocNome.$extension")

                            zipOut.putNextEntry(zipEntry)
                            zipOut.write(fileBytes)
                            zipOut.closeEntry()
                        }
                    }
                }
            }

            zipOut.close()

            jobStatusService.updateJobStatus(jobId, JobStatus.PROCESSING, "Fazendo upload do arquivo ZIP final...")

            val zipFileName = "export/geral/relatorio_geral_${jobId}.zip"
            val finalPath = s3Service.uploadFileFromBytes(byteArrayOutputStream.toByteArray(), zipFileName)

            val downloadUrl = s3Service.generatePresignedUrl(finalPath)
            jobStatusService.updateJobStatus(jobId, JobStatus.COMPLETED, "Arquivo ZIP pronto para download.", downloadUrl)
            logger.info("[ZIP-GERAL] JobID $jobId - SUCESSO! ZIP gerado e salvo em: $finalPath")

        } catch (e: Exception) {
            jobStatusService.updateJobStatus(jobId, JobStatus.FAILED, "Ocorreu um erro crítico durante a geração do arquivo.")
            logger.error("[ZIP-GERAL] JobID $jobId - FALHA CRÍTICA ao gerar ZIP geral: ${e.message}", e)
        }
    }
}
