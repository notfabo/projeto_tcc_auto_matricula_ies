package rest_api.docflow.dto

data class AuthRequest(
    val cpf: String,
    val senha: String
)