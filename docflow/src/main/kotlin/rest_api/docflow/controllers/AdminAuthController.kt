package rest_api.docflow.controllers

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.BadCredentialsException
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.*
import rest_api.docflow.dto.AuthRequest
import rest_api.docflow.dto.AuthResponse
import rest_api.docflow.repositories.AdministradorRepository
import rest_api.docflow.security.JwtUtil
import rest_api.docflow.services.AdministradorService

@RestController
@RequestMapping("/api/admin/auth")
class AdminAuthController(
    private val authenticationManager: AuthenticationManager,
    private val jwtUtil: JwtUtil,
) {
    @PostMapping("/login")
    fun login(@RequestBody request: AuthRequest): ResponseEntity<AuthResponse> {
        return try {
            val authentication = authenticationManager.authenticate(
                UsernamePasswordAuthenticationToken(request.cpf, request.senha)
            )
            val token = jwtUtil.generateToken(request.cpf)
            ResponseEntity.ok(AuthResponse(token))
        } catch (e: BadCredentialsException) {
            ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(null)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null)
        }
    }

    @PostMapping("/logout")
    fun logout(): ResponseEntity<String> {
        SecurityContextHolder.clearContext()
        return ResponseEntity.ok("Logout efetuado com sucesso")
    }

}
