package rest_api.docflow.services

import jakarta.persistence.EntityNotFoundException
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import rest_api.docflow.dto.CandidatoAdicionalDTO
import rest_api.docflow.dto.CandidatoResponse
import rest_api.docflow.models.Candidato
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.security.JwtUtil

@Service
class CandidatoService(
    private val candidatoRepository: CandidatoRepository,
    private val emailService: EmailService,
    private val passwordEncoder: PasswordEncoder,
    private val jwtUtil: JwtUtil
) {

    fun listarTodos(): List<Candidato> {
        return candidatoRepository.findAll()
    }

    fun gerarSenhaEAtribuirPorCpf(cpf: String): String {
        val candidato = candidatoRepository.findByCpf(cpf)
            ?: throw IllegalArgumentException("Candidato com CPF $cpf não encontrado")

        val senhaGerada = gerarSenhaAleatoria()
        candidato.senha = passwordEncoder.encode(senhaGerada)
        candidatoRepository.save(candidato)

        emailService.enviarSenhaPorEmail(
            emailCandidato = candidato.email ?: throw IllegalArgumentException("E-mail do candidato não cadastrado"),
            cpf = cpf,
            senha = senhaGerada
        )

        return senhaGerada
    }

    private fun gerarSenhaAleatoria(): String {
        val chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return (1..10).map { chars.random() }.joinToString("")
    }

    fun buscarDadosCandidatoPorToken(token: String): CandidatoResponse {
        val cpf = jwtUtil.extractCpf(token) ?:
        throw IllegalArgumentException("Token inválido ou CPF não encontrado")

        val candidato = candidatoRepository.findByCpf(cpf) ?:
        throw IllegalArgumentException("Candidato não encontrado")

        return candidatoRepository.findCandidatoComCursoByCpf(cpf)
            ?: throw IllegalArgumentException("Candidato com CPF $cpf não encontrado ou não matriculado")
    }

    fun buscarCandidatoPorEmail(email: String): Candidato? {
        return candidatoRepository.findByEmail(email)
    }

    fun atualizarInformacoesAdicionais(cpf: String, dadosAdicionais: CandidatoAdicionalDTO): Candidato {
        val candidato = candidatoRepository.findByCpf(cpf)
            ?: throw EntityNotFoundException("Candidato com CPF $cpf não encontrado.")

        dadosAdicionais.nomeSocial?.let { candidato.nomeSocial = it }
        dadosAdicionais.estadoCivil?.let { candidato.estadoCivil = it }
        dadosAdicionais.racaCandidato?.let { candidato.racaCandidato = it }
        dadosAdicionais.orientacaoSexual?.let { candidato.orientacaoSexual = it }
        dadosAdicionais.identidadeGenero?.let { candidato.identidadeGenero = it }
        dadosAdicionais.possuiDeficiencia?.let { candidato.possuiDeficiencia = it }

        if (dadosAdicionais.possuiDeficiencia == "Sim") {
            candidato.numeroCid = dadosAdicionais.numeroCid
        } else {
            candidato.numeroCid = null
        }

        return candidatoRepository.save(candidato)
    }

}