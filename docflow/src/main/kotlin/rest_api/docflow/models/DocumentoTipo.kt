package rest_api.docflow.models

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "documento_tipo")
data class DocumentoTipo(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_documento_tipo")
    val id: Int = 0,

    @Column(name = "nome")
    val nome: String,

    @Column(name = "obrigatorio")
    val obrigatorio: Boolean = false,

    @Column(name = "data_criacao")
    val dataCriacao: LocalDateTime = LocalDateTime.now()
)