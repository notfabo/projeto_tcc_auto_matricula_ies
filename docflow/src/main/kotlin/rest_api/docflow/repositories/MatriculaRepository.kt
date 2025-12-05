package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import rest_api.docflow.models.Matricula

interface MatriculaRepository : JpaRepository<Matricula, Int> {
    fun findByStatusMatricula(statusMatricula: String): List<Matricula>
    
    @Query("SELECT m FROM Matricula m WHERE m.candidato.idCandidato = :candidatoId ORDER BY m.dataInscricao DESC")
    fun findByCandidatoIdCandidato(candidatoId: Int): Matricula?
    
    fun findByStatusMatriculaAndStatusPreMatricula(statusMatricula: String, statusPreMatricula: String): List<Matricula>
    fun findByStatusPreMatricula(statusPreMatricula: String): List<Matricula>
    fun findByTurmaIdTurma(turmaId: Int): List<Matricula>

    @Query("""
        SELECT m FROM Matricula m
        JOIN FETCH m.candidato c
        JOIN FETCH m.turma t
        JOIN FETCH t.curso
    """)
    fun findAllWithDetails(): List<Matricula>
}
