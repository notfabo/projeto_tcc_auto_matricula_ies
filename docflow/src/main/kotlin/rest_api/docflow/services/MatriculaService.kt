package rest_api.docflow.services

import jakarta.transaction.Transactional
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.server.ResponseStatusException
import rest_api.docflow.dto.*
import rest_api.docflow.models.Matricula
import rest_api.docflow.repositories.AdministradorRepository
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.repositories.DocumentoRepository
import rest_api.docflow.repositories.DocumentoTipoRepository
import rest_api.docflow.repositories.MatriculaRepository
import java.time.LocalDateTime

@Service
class MatriculaService(
    private val matriculaRepository: MatriculaRepository,
    private val documentoRepository: DocumentoRepository,
    private val documentoTipoRepository: DocumentoTipoRepository,
    private val administradorRepository: AdministradorRepository,
    private val candidatoRepository: CandidatoRepository,
    private val preMatriculaService: PreMatriculaService,
    @Value("\${docflow.documento.tipo.identidade-id}")
    private val ID_TIPO_DOC_IDENTIDADE: Int,
    @Value("\${docflow.documento.tipo.historico-id}")
    private val ID_TIPO_DOC_HISTORICO: Int
    ,
    @Value("\${docflow.pre-matricula.retry-cooldown-seconds:3600}")
    private val preMatriculaRetryCooldownSeconds: Long
) {
    companion object {
        private const val STATUS_PENDENTE = "pendente"
        private const val STATUS_APROVADA = "aprovado"
    }

    fun listarMatriculasParaRevisao(status: String?): List<MatriculaResumoDTO> {
        val matriculas: List<Matricula>

        if (status.isNullOrBlank()) {
            matriculas = matriculaRepository.findByStatusPreMatricula(STATUS_APROVADA)
        } else {
            matriculas = matriculaRepository.findByStatusMatriculaAndStatusPreMatricula(
                status.uppercase(),
                STATUS_APROVADA
            )
        }

        return matriculas.map {
            MatriculaResumoDTO(
                idMatricula = it.id,
                nomeCandidato = it.candidato?.nome ?: "N/A",
                cpfCandidato = it.candidato?.cpf ?: "N/A",
                turma = it.turma?: throw ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Matrícula ID ${it.id} não possui turma associada."
                ),
                statusMatricula = it.statusMatricula,
                statusPreMatricula = it.statusPreMatricula,
                motivoPreMatricula = it.motivoPreMatricula,
                dataInscricao = it.dataInscricao
            )
        }
    }

    fun buscarDetalhesMatricula(id: Int): MatriculaDetalhesDTO {
        val matricula = matriculaRepository.findById(id)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Matrícula não encontrada") }

        val candidato = matricula.candidato
            ?: throw ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Matrícula ID $id não possui candidato associado.")

        val documentos = documentoRepository.findByFkCandidato(candidato.idCandidato)
        val todosTiposDocumento = documentoTipoRepository.findAll()
        
        // Tipos de documentos já enviados pelo candidato
        val tiposEnviados = documentos.map { it.fkDocumentoTipo }.toSet()
        
        // Criar documentos virtuais para tipos não enviados (pendentes)
        val documentosPendentes = todosTiposDocumento
            .filter { it.id !in tiposEnviados }
            .map { tipo ->
                DocumentoResponseDTO(
                    id = -tipo.id, // ID negativo para indicar que é um documento não enviado
                    tipo = tipo.id.toString(),
                    status = "pendente",
                    dadosExtraidos = null,
                    motivoErro = null,
                    dataUpload = "" // Documento não enviado ainda
                )
            }

        val candidatoDTO = CandidatoResponse(
            id = candidato.idCandidato,
            nome = candidato.nome,
            cpf = candidato.cpf,
            email = candidato.email,
            dataNascimento = candidato.dataNascimento,
            telefone = candidato.telefone,
            nomeSocial = candidato.nomeSocial,
            estadoCivil = candidato.estadoCivil,
            racaCandidato = candidato.racaCandidato,
            orientacaoSexual = candidato.orientacaoSexual,
            identidadeGenero = candidato.identidadeGenero,
            possuiDeficiencia = candidato.possuiDeficiencia,
            numeroCid = candidato.numeroCid,
            nomeCurso = matricula.turma?.curso?.nomeCurso ?: "N/A"
        )

        val documentosEnviadosDTO = documentos.map { doc ->
            DocumentoResponseDTO(
                id = doc.id,
                tipo = doc.fkDocumentoTipo.toString(),
                status = doc.statusDocumento,
                dadosExtraidos = doc.dadosExtraidos,
                motivoErro = doc.motivoErro,
                dataUpload = doc.dataUpload.toString(),
                caminhoArquivo = doc.caminhoArquivo
            )
        }
        
        // Combinar documentos enviados com documentos pendentes
        val documentosDTO = documentosEnviadosDTO + documentosPendentes

        return MatriculaDetalhesDTO(
            idMatricula = matricula.id,
            statusMatricula = matricula.statusMatricula,
            statusPreMatricula = matricula.statusPreMatricula,
            motivoPreMatricula = matricula.motivoPreMatricula,
            candidato = candidatoDTO,
            turma = matricula.turma,
            documentos = documentosDTO,
            observacoes = matricula.observacoes,
            dataAtualizacao = matricula.dataAtualizacao
        )
    }

    @Transactional
    fun aprovarMatricula(id: Int, request: AprovarMatriculaRequest): Matricula {
        val matricula = matriculaRepository.findById(id)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Matrícula não encontrada") }

        if (matricula.statusMatricula != STATUS_PENDENTE) {
            throw ResponseStatusException(HttpStatus.BAD_REQUEST, "Esta matrícula não pode ser aprovada pois não está pendente de revisão.")
        }

        matricula.apply {
            statusMatricula = STATUS_APROVADA
            observacoes = request.observacoes
        }

        return matriculaRepository.save(matricula)
    }

    @Transactional
    fun reprovarMatricula(id: Int, request: ReprovarMatriculaRequest): Matricula {
        val matricula = matriculaRepository.findById(id)
            .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND, "Matrícula não encontrada") }

        if (matricula.statusMatricula != STATUS_PENDENTE) {
            throw ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "Esta matrícula não pode ser reprovada pois seu status é '${matricula.statusMatricula}'."
            )
        }

        if (request.observacoes.isBlank()) {
            throw ResponseStatusException(HttpStatus.BAD_REQUEST, "O motivo da reprovação (observação) é obrigatório.")
        }

        matricula.apply {
            statusMatricula = STATUS_PENDENTE
            statusPreMatricula = STATUS_PENDENTE
            observacoes = request.observacoes
            dataAtualizacao = LocalDateTime.now()
        }

        return matriculaRepository.save(matricula)
    }

    @Transactional
    fun verificarEAtualizarStatusMatricula(candidatoId: Int) {
        println("[MatriculaService] Verificando status para candidato ID: $candidatoId")

        // Buscando documentos e verificando pré-requisitos
        val documentos = documentoRepository.findByFkCandidato(candidatoId)
        println("[MatriculaService] Documentos encontrados: ${documentos.size}")

        val temIdentidadeAprovada = documentos.any {
            it.fkDocumentoTipo == ID_TIPO_DOC_IDENTIDADE && it.statusDocumento == "aprovado"
        }
        val temHistoricoAprovado = documentos.any {
            it.fkDocumentoTipo == ID_TIPO_DOC_HISTORICO && it.statusDocumento == "aprovado"
        }

        if (!temIdentidadeAprovada || !temHistoricoAprovado) {
            println("[MatriculaService] ⚠️  Documentos obrigatórios NÃO atendidos: RG aprovado? $temIdentidadeAprovada, Histórico aprovado? $temHistoricoAprovado")
            return
        }

        println("[MatriculaService] ✓ Ambos os documentos obrigatórios aprovados (RG e Histórico)")

        // Busca/Cria matrícula
        val matriculaExistente = matriculaRepository.findByCandidatoIdCandidato(candidatoId)
        val matricula = if (matriculaExistente == null) {
            val candidato = candidatoRepository.findById(candidatoId)
                .orElseThrow {
                    ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Candidato com ID $candidatoId não encontrado para criar a matrícula."
                    )
                }

            val novaMatricula = Matricula().apply {
                this.candidato = candidato
                this.statusMatricula = STATUS_PENDENTE
                this.statusPreMatricula = STATUS_PENDENTE
                this.dataInscricao = LocalDateTime.now()
            }

            matriculaRepository.save(novaMatricula)
        } else {
            matriculaExistente
        }

        // Checa se existe novo documento aprovado desde a última validação
        val ultimoDocAprovado = documentoRepository.findTopByFkCandidatoAndStatusDocumentoOrderByDataValidacaoDesc(candidatoId, "aprovado")
        val lastApprovedAt = ultimoDocAprovado?.dataValidacao
        val lastValidationAt = matricula.dataAtualizacao

        if (lastApprovedAt != null && lastValidationAt != null && !lastApprovedAt.isAfter(lastValidationAt)) {
            println("[MatriculaService] 🔁 Último documento aprovado em $lastApprovedAt não é mais recente que a última validação em $lastValidationAt. Pulando revalidação.")
            return
        }

        // Se já estiver em processamento no DB, pule (proteção entre instâncias)
        if (matricula.statusPreMatricula == "processando") {
            println("[MatriculaService] ⏳ Matrícula ${matricula.id} já está marcada como 'processando' no DB. Pulando.")
            return
        }

        // Marca como processando e persiste antes da chamada externa (visibilidade)
        matricula.statusPreMatricula = "processando"
        matricula.dataAtualizacao = LocalDateTime.now()
        matriculaRepository.save(matricula)

        // Chama o verify_docs (mesma lógica anterior)
        println("[MatriculaService] → ACIONANDO verificação automática via verify_docs")
        println("[MatriculaService] Matrícula ID: ${matricula.id} | Candidato: ${matricula.candidato?.nome} | Candidato ID: $candidatoId")

        try {
            val verifyDocsUrl = System.getenv("VERIFY_DOCS_URL") ?: "http://localhost:5000/verify-docs"
            val payload = mapOf("matricula_id" to matricula.id)

            val client = java.net.http.HttpClient.newBuilder()
                .connectTimeout(java.time.Duration.ofSeconds(30))
                .build()

            val payloadJson = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper().writeValueAsString(payload)
            val request = java.net.http.HttpRequest.newBuilder()
                .uri(java.net.URI.create(verifyDocsUrl))
                .header("Content-Type", "application/json")
                .timeout(java.time.Duration.ofSeconds(30))
                .POST(java.net.http.HttpRequest.BodyPublishers.ofString(payloadJson))
                .build()

            val response = client.send(request, java.net.http.HttpResponse.BodyHandlers.ofString())

            if (response.statusCode() != 200) {
                throw Exception("HTTP Status ${response.statusCode()}: ${response.body()}")
            }

            val mapper = com.fasterxml.jackson.module.kotlin.jacksonObjectMapper()
            val result = mapper.readTree(response.body())
            val status = result.get("status")?.asText() ?: "pendente"
            val observacao = result.get("observacao")?.asText() ?: ""

            // Atualiza a matrícula com o resultado
            matricula.statusPreMatricula = status
            matricula.motivoPreMatricula = observacao
            matricula.dataAtualizacao = LocalDateTime.now()
            matriculaRepository.save(matricula)

            println("[MatriculaService] ✓ Matrícula ${matricula.id} ATUALIZADA com status pré-matrícula: '$status'")
            if (observacao.isNotEmpty()) println("[MatriculaService] Observação: $observacao")

        } catch (e: java.net.http.HttpTimeoutException) {
            println("[MatriculaService] ❌ ERRO: Timeout ao conectar com verify_docs")
            e.printStackTrace()
            matricula.statusPreMatricula = STATUS_PENDENTE
            matricula.motivoPreMatricula = "Erro: Timeout ao conectar com serviço de validação. Verifique se o servidor Python está rodando."
            matriculaRepository.save(matricula)
        } catch (e: java.net.ConnectException) {
            println("[MatriculaService] ❌ ERRO: Não foi possível conectar com verify_docs")
            e.printStackTrace()
            matricula.statusPreMatricula = STATUS_PENDENTE
            matricula.motivoPreMatricula = "Erro: Não foi possível conectar com serviço de validação. Verifique se o servidor Python está rodando."
            matriculaRepository.save(matricula)
        } catch (e: Exception) {
            println("[MatriculaService] ❌ ERRO ao validar dados via verify_docs: ${e.message}")
            e.printStackTrace()
            matricula.statusPreMatricula = STATUS_PENDENTE
            matricula.motivoPreMatricula = "Erro na validação automática: ${e.javaClass.simpleName} - ${e.message ?: "Erro desconhecido"}"
            matriculaRepository.save(matricula)
            println("[MatriculaService] Matrícula marcada como PENDENTE devido ao erro")
        }
    }

    @Transactional
    fun processarMatriculasPendentes(): Int {
        println("[MatriculaService] Iniciando processamento de matrículas pendentes...")
        
        // Busca todas as matrículas com status_pre_matricula = 'pendente'
        val matriculasPendentes = matriculaRepository.findByStatusPreMatricula(STATUS_PENDENTE)
        println("[MatriculaService] Matrículas pendentes encontradas: ${matriculasPendentes.size}")
        
        var processadas = 0
        val cutoff = java.time.LocalDateTime.now().minusSeconds(preMatriculaRetryCooldownSeconds)
        for (matricula in matriculasPendentes) {
            try {
                // Se já tentamos processar essa pré-matrícula recentemente, pule para evitar loops
                val lastAttempt = matricula.dataAtualizacao
                if (lastAttempt != null && lastAttempt.isAfter(cutoff)) {
                    println("[MatriculaService] ⏭️ Pulando matrícula ${matricula.id} - última tentativa em $lastAttempt (cooldown: ${preMatriculaRetryCooldownSeconds}s)")
                    continue
                }
                val candidatoId = matricula.candidato?.idCandidato
                if (candidatoId != null) {
                    println("[MatriculaService] Processando matrícula ID: ${matricula.id}, Candidato ID: $candidatoId")
                    verificarEAtualizarStatusMatricula(candidatoId)
                    processadas++
                }
            } catch (e: Exception) {
                println("[MatriculaService] Erro ao processar matrícula ${matricula.id}: ${e.message}")
            }
        }
        
        println("[MatriculaService] Processamento concluído. Matrículas processadas: $processadas")
        return processadas
    }
}