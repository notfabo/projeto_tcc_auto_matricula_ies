package rest_api.docflow.controllers

import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.web.bind.annotation.*
import rest_api.docflow.dto.CandidatoAdicionalDTO
import rest_api.docflow.dto.CandidatoResponse
import rest_api.docflow.models.Candidato
import rest_api.docflow.security.JwtUtil
import rest_api.docflow.services.CandidatoService

@RestController
@RequestMapping("/api/candidatos")
class CandidatoController(
    private val candidatoService: CandidatoService,
    private val jwtUtil: JwtUtil
) {

    @GetMapping("/listar")
    fun getCandidatos() : List<Candidato>{
        return candidatoService.listarTodos()
    }

    @GetMapping("/me")
    fun getCandidatoLogado(@RequestHeader("Authorization") token: String): ResponseEntity<CandidatoResponse> {
        val tokenClean = token.replace("Bearer ", "")
        val candidato = candidatoService.buscarDadosCandidatoPorToken(tokenClean)
        return ResponseEntity.ok(candidato)
    }

    @PatchMapping("/me/additional-info")
    fun updateAdditionalInfo(
        @AuthenticationPrincipal userDetails: UserDetails,
        @RequestBody dadosAdicionais: CandidatoAdicionalDTO
    ): ResponseEntity<CandidatoResponse> {
        val cpf = userDetails.username
        val candidatoAtualizado = candidatoService.atualizarInformacoesAdicionais(cpf, dadosAdicionais)

        val novoToken = jwtUtil.generateToken(candidatoAtualizado.cpf!!)
        val responseDto = candidatoService.buscarDadosCandidatoPorToken(novoToken)

        return ResponseEntity.ok(responseDto)
    }

}