package rest_api.docflow.models

import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime

@Entity
@Table(name = "administrador")
class Administrador {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_administrador")
    var idAdministrador: Int = 0

    @Column(name = "nome")
    var nome: String? = null

    @Column(name = "cpf", length = 11)
    var cpf: String? = null

    @Column(name = "email")
    var email: String? = null

    @Column(name = "telefone", length = 11)
    var telefone: String? = null

    @Column(nullable = false)
    var senha: String? = null

    @Column(name = "data_criacao")
    var dataCriacao: LocalDateTime? = null
}
