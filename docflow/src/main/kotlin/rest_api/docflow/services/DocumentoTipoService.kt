package rest_api.docflow.services

import org.springframework.stereotype.Service
import rest_api.docflow.models.DocumentoTipo
import rest_api.docflow.repositories.DocumentoTipoRepository

@Service
class DocumentoTipoService(
    private val documentoTipoRepository: DocumentoTipoRepository
) {

    fun listarTodos(): List<DocumentoTipo> = documentoTipoRepository.findAll()
}