package rest_api.docflow.services

import org.springframework.security.core.userdetails.User
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.stereotype.Service
import rest_api.docflow.repositories.AdministradorRepository

@Service
class AdminUserDetailsService(
    private val administradorRepository: AdministradorRepository
) : UserDetailsService {
    override fun loadUserByUsername(cpf: String): UserDetails {
        val admin = administradorRepository.findByCpf(cpf)
            ?: throw UsernameNotFoundException("Administrador com CPF $cpf não encontrado")
        return User.builder()
            .username(admin.cpf)
            .password(admin.senha)
            .roles("ADMIN")
            .build()
    }
}
