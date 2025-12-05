package rest_api.docflow.models

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "matricula")
class Matricula {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    var id: Int = 0

    @ManyToOne
    @JoinColumn(name = "fk_candidato")
    var candidato: Candidato? = null

    @ManyToOne
    @JoinColumn(name = "fk_turma", nullable = false)
    var turma: Turma? = null

    @Column(name = "status_matricula", nullable = false)
    var statusMatricula: String = "pendente"

    @Column(name = "status_pre_matricula")
    var statusPreMatricula: String? = "pendente"

    @Column(name = "motivo_pre_matricula")
    var motivoPreMatricula: String? = null

    @Column(name = "data_inscricao")
    var dataInscricao: LocalDateTime? = null

    @Column(name = "observacoes")
    var observacoes: String? = null

    @Column(name = "data_atualizacao")
    var dataAtualizacao: LocalDateTime? = null
}


