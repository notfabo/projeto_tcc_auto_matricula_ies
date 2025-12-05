package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import rest_api.docflow.models.Administrador

interface AdministradorRepository: JpaRepository<Administrador, Int> {
    fun findByCpf(cpf: String): Administrador?
    fun findByEmail(email: String): Administrador?
}
