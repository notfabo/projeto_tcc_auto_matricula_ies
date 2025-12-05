package rest_api.docflow.controllers

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.opencsv.CSVWriter
import org.apache.poi.xssf.usermodel.XSSFWorkbook
import org.springframework.core.io.ByteArrayResource
import org.springframework.http.HttpHeaders
import org.springframework.http.ResponseEntity
import rest_api.docflow.dto.CandidatoAprovadoExportDTO

import rest_api.docflow.services.CsvExportService
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.*
import rest_api.docflow.services.JobStatusResponse
import rest_api.docflow.services.JobStatusService
import rest_api.docflow.services.ZipExportService
import java.io.ByteArrayOutputStream
import java.io.StringWriter


@RestController
@RequestMapping("/api/admin/export")
class AdminExportController(
    private val exportService: CsvExportService,
    private val zipExportService: ZipExportService,
    private val jobStatusService: JobStatusService,
) {
    private val objectMapper = jacksonObjectMapper().writerWithDefaultPrettyPrinter()

    @GetMapping("/aprovados-para-erp")
    fun exportAprovadosParaErps(@RequestParam(defaultValue = "csv") format: String): ResponseEntity<*> {
        val dados = exportService.getDadosCandidatosAprovados()
        return gerarArquivoResposta(dados, format, "candidatos_aprovados")
    }

    @GetMapping("/geral")
    fun exportGeral(@RequestParam(defaultValue = "csv") format: String): ResponseEntity<*> {
        val dados = exportService.getDadosTodosCandidatos()
        return gerarArquivoResposta(dados, format, "relatorio_geral_candidatos")
    }


    private fun gerarArquivoResposta(
        dados: List<CandidatoAprovadoExportDTO>,
        format: String,
        filenameBase: String
    ): ResponseEntity<*> {
        val headers = arrayOf(
            "ID Candidato", "Nome Completo", "CPF", "Email", "Telefone", "Data Nascimento", "Data Inscrição", "Status Matricula",
            "Nome Mãe", "Nome Pai", "RG", "Data Emissão RG", "Naturalidade",
            "Escola Ensino Médio", "Ano Conclusão", "Cidade Escola", "Estado Escola",
            "Endereço Rua", "Endereço Número", "Endereço Bairro", "Endereço Cidade", "Endereço Estado", "Endereço CEP"
        )

        val resource: ByteArrayResource
        val fileName: String
        val contentType: String

        when (format.lowercase()) {
            "json" -> {
                fileName = "candidatos_aprovados.json"
                contentType = "application/json"

                val jsonString = objectMapper.writeValueAsString(dados)
                resource = ByteArrayResource(jsonString.toByteArray(Charsets.UTF_8))
            }
            "csv" -> {
                fileName = "candidatos_aprovados.csv"
                contentType = "text/csv"
                val stringWriter = StringWriter()
                CSVWriter(stringWriter).use { csvWriter ->
                    csvWriter.writeNext(headers)
                    dados.forEach { dto ->
                        csvWriter.writeNext(arrayOf(
                            dto.idCandidato.toString(), dto.nomeCompleto ?: "", dto.cpf ?: "", dto.email ?: "", dto.telefone ?: "",
                            dto.dataNascimentoCandidato?.toString() ?: "", dto.dataInscricao?.toString() ?: "", dto.statusMatricula ?: "" ,dto.nomeMae ?: "",
                            dto.nomePai ?: "", dto.rg ?: "", dto.dataEmissaoRg ?: "", dto.naturalidade ?: "",
                            dto.escolaEnsinoMedio ?: "", dto.anoConclusaoEnsinoMedio ?: "", dto.cidadeEscola ?: "",
                            dto.estadoEscola ?: "", dto.enderecoRua ?: "", dto.enderecoNumero ?: "", dto.enderecoBairro ?: "",
                            dto.enderecoCidade ?: "", dto.enderecoEstado ?: "", dto.enderecoCep ?: ""
                        ))
                    }
                }
                resource = ByteArrayResource(stringWriter.toString().toByteArray(Charsets.UTF_8))
            }
            "excel" -> {
                fileName = "candidatos_aprovados.xlsx"
                contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ByteArrayOutputStream().use { outputStream ->
                    XSSFWorkbook().use { workbook ->
                        val sheet = workbook.createSheet("Candidatos Aprovados")
                        val headerRow = sheet.createRow(0)
                        headers.forEachIndexed { index, headerText ->
                            headerRow.createCell(index).setCellValue(headerText)
                        }

                        dados.forEachIndexed { index, dto ->
                            val row = sheet.createRow(index + 1)
                            // Map cells exactly following the `headers` array indices
                            row.createCell(0).setCellValue(dto.idCandidato.toDouble())
                            row.createCell(1).setCellValue(dto.nomeCompleto ?: "")
                            row.createCell(2).setCellValue(dto.cpf ?: "")
                            row.createCell(3).setCellValue(dto.email ?: "")
                            row.createCell(4).setCellValue(dto.telefone ?: "")
                            row.createCell(5).setCellValue(dto.dataNascimentoCandidato?.toString() ?: "")
                            row.createCell(6).setCellValue(dto.dataInscricao?.toString() ?: "")
                            row.createCell(7).setCellValue(dto.statusMatricula ?: "")
                            row.createCell(8).setCellValue(dto.nomeMae ?: "")
                            row.createCell(9).setCellValue(dto.nomePai ?: "")
                            row.createCell(10).setCellValue(dto.rg ?: "")
                            row.createCell(11).setCellValue(dto.dataEmissaoRg ?: "")
                            row.createCell(12).setCellValue(dto.naturalidade ?: "")
                            row.createCell(13).setCellValue(dto.escolaEnsinoMedio ?: "")
                            row.createCell(14).setCellValue(dto.anoConclusaoEnsinoMedio ?: "")
                            row.createCell(15).setCellValue(dto.cidadeEscola ?: "")
                            row.createCell(16).setCellValue(dto.estadoEscola ?: "")
                            row.createCell(17).setCellValue(dto.enderecoRua ?: "")
                            row.createCell(18).setCellValue(dto.enderecoNumero ?: "")
                            row.createCell(19).setCellValue(dto.enderecoBairro ?: "")
                            row.createCell(20).setCellValue(dto.enderecoCidade ?: "")
                            row.createCell(21).setCellValue(dto.enderecoEstado ?: "")
                            row.createCell(22).setCellValue(dto.enderecoCep ?: "")
                        }
                        workbook.write(outputStream)
                    }
                    resource = ByteArrayResource(outputStream.toByteArray())
                }
            }
            else -> {
                return ResponseEntity.badRequest().body("Formato de arquivo inválido. Use 'csv' ou 'excel'.")
            }
        }

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(contentType))
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"$fileName\"")
            .body(resource)
    }

    @PostMapping("/documentos-zip/geral")
    fun exportDocumentosGeralZip(): ResponseEntity<Map<String, String>> {
        val jobId = jobStatusService.createJob()
        zipExportService.gerarZipGeral(jobId)

        val response = mapOf(
            "message" to "Solicitação recebida.",
            "jobId" to jobId
        )
        return ResponseEntity.accepted().body(response)
    }

    @GetMapping("/status/{jobId}")
    fun getExportStatus(@PathVariable jobId: String): ResponseEntity<JobStatusResponse> {
        val status = jobStatusService.getJobStatus(jobId)
        return if (status != null) {
            ResponseEntity.ok(status)
        } else {
            ResponseEntity.notFound().build()
        }
    }
}
