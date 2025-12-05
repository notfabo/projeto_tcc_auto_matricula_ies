package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import rest_api.docflow.models.Documento

@Repository
interface DocumentoRepository : JpaRepository<Documento, Int> {
    fun findByFkCandidato(fkCandidato: Int): List<Documento>

    fun findByFkCandidatoAndFkDocumentoTipo(fkCandidato: Int, fkDocumentoTipo: Int): Documento?

    // Retorna o documento mais recentemente validado (dataValidacao) com determinado status
    fun findTopByFkCandidatoAndStatusDocumentoOrderByDataValidacaoDesc(fkCandidato: Int, statusDocumento: String): Documento?
}