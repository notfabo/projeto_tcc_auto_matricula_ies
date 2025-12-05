package rest_api.docflow.services

import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import rest_api.docflow.models.Administrador
import rest_api.docflow.repositories.AdministradorRepository
import rest_api.docflow.security.JwtUtil

@Service
class AdministradorService(
    private val administradorRepository: AdministradorRepository,
    private val jwtUtil: JwtUtil
) {

    fun buscarAdministradorPorCpf(cpf: String): Administrador? {
        return administradorRepository.findByCpf(cpf)
    }
}
