package rest_api.docflow.controllers

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.*
import rest_api.docflow.dto.AuthRequest
import rest_api.docflow.dto.AuthResponse
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.security.JwtUtil
import rest_api.docflow.services.CandidatoService

@RestController
@RequestMapping("/api/auth")
class AuthController(
    private val authenticationManager: AuthenticationManager,
    private val jwtUtil: JwtUtil,
    private val candidatoRepository: CandidatoRepository,
    private val candidatoService: CandidatoService
) {

    @PostMapping("/login")
    fun login(@RequestBody request: AuthRequest): ResponseEntity<AuthResponse> {
        try {
            val candidato = candidatoRepository.findByCpf(request.cpf)
            if (candidato == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build()
            }
            val auth = UsernamePasswordAuthenticationToken(request.cpf, request.senha)
            authenticationManager.authenticate(auth)
            val token = jwtUtil.generateToken(request.cpf)
            return ResponseEntity.ok(AuthResponse(token))
        } catch (e: Exception) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build()
        }
    }

    @PostMapping("/logout")
    fun logout(): ResponseEntity<String> {
        SecurityContextHolder.clearContext()
        return ResponseEntity.ok("Logout efetuado com sucesso")
    }


    @PostMapping("/enviar-senha/{cpf}")
    fun enviarSenha(@PathVariable cpf: String): ResponseEntity<String> {
        return try {
            val senha = candidatoService.gerarSenhaEAtribuirPorCpf(cpf)
            ResponseEntity.ok("Senha enviada para o e-mail cadastrado. Verifique sua caixa de entrada (e spam).")
        } catch (e: IllegalArgumentException) {
            ResponseEntity.badRequest().body("Erro: ${e.message}")
        } catch (e: Exception) {
            ResponseEntity.internalServerError().body("Falha ao enviar e-mail. Tente novamente mais tarde.")
        }
    }
}
