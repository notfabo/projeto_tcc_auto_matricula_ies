package rest_api.docflow.models

import jakarta.persistence.*
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.time.LocalDate
import java.time.LocalDateTime

@Entity
@Table(name = "candidato")
class Candidato {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_candidato")
    var idCandidato: Int = 0

    @Column(name = "nome")
    var nome: String? = null

    @Column(name = "cpf")
    var cpf: String? = null

    @Column(name = "email")
    var email: String? = null

    @Column(name = "telefone", length = 11)
    var telefone: String? = null

    @Column(name = "data_nascimento")
    var dataNascimento: LocalDate? = null

    @Column(name = "data_criacao")
    var dataCriacao: LocalDateTime? = null

    @Column(nullable = false)
    var senha: String? = null

    @Column(name = "nome_social")
    var nomeSocial: String? = null

    @Column(name = "estado_civil")
    var estadoCivil: String? = null

    @Column(name = "raca_candidato")
    var racaCandidato: String? = null

    @Column(name = "orientacao_sexual")
    var orientacaoSexual: String? = null

    @Column(name = "identidade_genero")
    var identidadeGenero: String? = null

    @Column(name = "possui_deficiencia")
    var possuiDeficiencia: String? = null

    @Column(name = "numero_cid")
    var numeroCid: String? = null
}