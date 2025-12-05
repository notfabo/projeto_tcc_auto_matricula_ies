package rest_api.docflow.services

import org.springframework.security.core.userdetails.User
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.stereotype.Service
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.repositories.AdministradorRepository

@Service
class CustomUserDetailsService(
    private val candidatoRepository: CandidatoRepository,
    private val administradorRepository: AdministradorRepository
) : UserDetailsService {
    override fun loadUserByUsername(cpf: String): UserDetails {
        val admin = administradorRepository.findByCpf(cpf)
        if (admin != null) {
            return User.builder()
                .username(admin.cpf)
                .password(admin.senha)
                .roles("ADMIN")
                .build()
        }
        val candidato = candidatoRepository.findByCpf(cpf)
        if (candidato != null) {
            return User.builder()
                .username(candidato.cpf)
                .password(candidato.senha ?: "dummy")
                .roles("CANDIDATO")
                .build()
        }
        throw UsernameNotFoundException("Usuário com CPF $cpf não encontrado")
    }
}