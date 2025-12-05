package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import rest_api.docflow.models.Turma

interface TurmaRepository : JpaRepository<Turma, Int> {
}