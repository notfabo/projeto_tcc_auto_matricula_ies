package rest_api.docflow.models

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "turma")
class Turma {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_turma")
    var idTurma: Int = 0

    @ManyToOne
    @JoinColumn(name = "fk_curso", nullable = false)
    var curso: Curso? = null

    @Column(name = "codigo_turma", unique = true, nullable = false)
    var codigoTurma: String? = null

    @Column(name = "ano_semestre", nullable = false)
    var anoSemestre: String? = null

    @Column(name = "periodo")
    var periodo: String? = null

    @Column(name = "data_criacao")
    var dataCriacao: LocalDateTime? = null
}