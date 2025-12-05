package rest_api.docflow.services

import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import org.springframework.web.server.ResponseStatusException
import rest_api.docflow.repositories.DocumentoRepository
import rest_api.docflow.repositories.MatriculaRepository
import java.time.LocalDateTime

@Service
class PreMatriculaService(
    private val matriculaRepository: MatriculaRepository,
    private val documentoRepository: DocumentoRepository,
    @Value("\${docflow.python-api.url}")
    private val pythonApiUrl: String
) {
    private val restTemplate = RestTemplate()

    fun verificarEAtualizarPreMatricula(matriculaId: Int) {
        println("[PreMatriculaService] Iniciando verificação da pré-matrícula ID: $matriculaId")
        val matricula = matriculaRepository.findById(matriculaId)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Matrícula não encontrada") }

        // Chama a API Python para verificar os documentos
        try {
            val verifyDocsUrl = pythonApiUrl + "/verify-docs"
            println("[PreMatriculaService] Chamando verify_docs em: $verifyDocsUrl")

            val client = java.net.http.HttpClient.newBuilder().build()
            val request = java.net.http.HttpRequest.newBuilder()
                .uri(java.net.URI.create(verifyDocsUrl))
                .header("Content-Type", "application/json")
                .POST(java.net.http.HttpRequest.BodyPublishers.ofString(
                    com.fasterxml.jackson.module.kotlin.jacksonObjectMapper().writeValueAsString(
                        mapOf("matricula_id" to matriculaId)
                    )
                ))
                .build()

            val response = client.send(request, java.net.http.HttpResponse.BodyHandlers.ofString())
            println("[PreMatriculaService] Resposta recebida: ${response.body()}")

            val mapper = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper()
            val result = mapper.readTree(response.body())
            val status = result.get("status")?.asText() ?: "pendente"
            val observacao = result.get("observacao")?.asText()

            println("[PreMatriculaService] Status: $status, Observação: $observacao")

            // Atualiza a matrícula com o resultado da verificação
            matricula.apply {
                statusPreMatricula = status
                motivoPreMatricula = observacao
                dataAtualizacao = LocalDateTime.now()
            }

            val matriculaSalva = matriculaRepository.save(matricula)
            println("[PreMatriculaService] Matrícula atualizada com sucesso. Novo status: ${matriculaSalva.statusPreMatricula}")

        } catch (e: Exception) {
            println("[PreMatriculaService] Erro ao verificar documentos: ${e.message}")
            e.printStackTrace()
            throw ResponseStatusException(
                HttpStatus.INTERNAL_SERVER_ERROR,
                "Erro ao verificar documentos: ${e.message}"
            )
        }
    }
}