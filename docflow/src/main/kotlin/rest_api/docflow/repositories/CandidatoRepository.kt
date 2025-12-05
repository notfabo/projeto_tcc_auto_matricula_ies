package rest_api.docflow.repositories

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import rest_api.docflow.dto.CandidatoAprovadoExportDTO
import rest_api.docflow.dto.CandidatoResponse
import rest_api.docflow.models.Candidato

interface CandidatoRepository: JpaRepository<Candidato, Int> {
    fun findByCpf(cpf: String): Candidato?
    fun findByEmail(email: String): Candidato?

    @Query("""
        SELECT new rest_api.docflow.dto.CandidatoAprovadoExportDTO(
            c.idCandidato,
            c.nome,
            c.cpf,
            c.email,
            c.telefone,
            c.dataNascimento,
            c.nomeSocial,
            c.estadoCivil,
            c.racaCandidato,
            c.orientacaoSexual,
            c.identidadeGenero,
            c.possuiDeficiencia,
            c.numeroCid,
            m.dataInscricao,
            m.statusMatricula
        )
        FROM Matricula m JOIN m.candidato c
        WHERE m.statusMatricula = 'aprovado'
    """)
    fun findCandidatosAprovadosParaExport(): List<CandidatoAprovadoExportDTO>

    @Query("""
        SELECT new rest_api.docflow.dto.CandidatoAprovadoExportDTO(
            c.idCandidato, 
            c.nome, 
            c.cpf, 
            c.email, 
            c.telefone,
            c.dataNascimento, 
            c.nomeSocial, 
            c.estadoCivil,            
            c.racaCandidato,
            c.orientacaoSexual,
            c.identidadeGenero,
            c.possuiDeficiencia,
            c.numeroCid,m.dataInscricao, m.statusMatricula
        )
        FROM Matricula m JOIN m.candidato c
    """)
    fun findAllCandidatosParaExport(): List<CandidatoAprovadoExportDTO>

    @Query("""
    SELECT new rest_api.docflow.dto.CandidatoResponse(
        c.idCandidato,
        c.nome,
        c.cpf,
        c.email,
        c.telefone,
        c.dataNascimento,
        c.nomeSocial,
        c.estadoCivil,
        c.racaCandidato,
        c.orientacaoSexual,
        c.identidadeGenero,
        c.possuiDeficiencia,
        c.numeroCid,
        k.nomeCurso
    )
    FROM Candidato c
    JOIN Matricula m ON c.idCandidato = m.candidato.idCandidato
    JOIN Turma t ON m.turma.idTurma = t.idTurma
    JOIN Curso k ON t.curso.idCurso = k.idCurso
    WHERE c.cpf = :cpf
""")
    fun findCandidatoComCursoByCpf(cpf: String): CandidatoResponse?
}