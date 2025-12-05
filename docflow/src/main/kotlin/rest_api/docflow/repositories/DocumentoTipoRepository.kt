package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import rest_api.docflow.models.DocumentoTipo

interface DocumentoTipoRepository : JpaRepository<DocumentoTipo, Int> {
    fun findByNome(nome: String): DocumentoTipo?
}