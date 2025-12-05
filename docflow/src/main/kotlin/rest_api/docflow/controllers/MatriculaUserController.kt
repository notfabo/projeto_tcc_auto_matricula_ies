package rest_api.docflow.controllers

import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import rest_api.docflow.repositories.MatriculaRepository
import rest_api.docflow.services.CandidatoService
import rest_api.docflow.services.MatriculaService

@RestController
@RequestMapping("/api/matriculas")
class MatriculaUserController(
    private val candidatoService: CandidatoService,
    private val matriculaRepository: MatriculaRepository,
    private val matriculaService: MatriculaService
) {

    @GetMapping("/me")
    fun getMinhaMatricula(@RequestHeader("Authorization") token: String): ResponseEntity<Any> {
        val tokenClean = token.replace("Bearer ", "")
        val candidato = candidatoService.buscarDadosCandidatoPorToken(tokenClean)

        val matricula = matriculaRepository.findByCandidatoIdCandidato(candidato.id)
            ?: return ResponseEntity.notFound().build<Any>()

        val detalhes = matriculaService.buscarDetalhesMatricula(matricula.id)
        return ResponseEntity.ok(detalhes)
    }

}
