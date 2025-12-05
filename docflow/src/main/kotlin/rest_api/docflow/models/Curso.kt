package rest_api.docflow.models

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "curso")
class Curso {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_curso")
    var idCurso: Int = 0

    @Column(name = "nome_curso", nullable = false)
    var nomeCurso: String? = null

    @Column(name = "data_criacao")
    var dataCriacao: LocalDateTime? = null
}