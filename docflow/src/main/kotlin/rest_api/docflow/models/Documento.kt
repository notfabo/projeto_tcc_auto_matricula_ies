package rest_api.docflow.models

import jakarta.persistence.*
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.time.LocalDateTime

@Entity
@Table(name = "documento")
data class Documento(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "fk_candidato", nullable = false)
    val fkCandidato: Int,

    @Column(name = "fk_documento_tipo", nullable = false)
    val fkDocumentoTipo: Int,

    @Column(name = "caminho_arquivo")
    var caminhoArquivo: String,

    @Column(name = "data_upload")
    var dataUpload: LocalDateTime = LocalDateTime.now(),

    @Column(name = "status_documento")
    var statusDocumento: String = "pendente",

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "dados_extraidos")
    var dadosExtraidos: String? = null,

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "motivo_erro")
    var motivoErro: String? = null,

    @Column(name = "subtipo")
    var subtipo: String? = null,

    @Column(name = "data_validacao")
    var dataValidacao: LocalDateTime? = null
)
