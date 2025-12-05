package rest_api.docflow.services

import jakarta.mail.MessagingException
import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.mail.javamail.MimeMessageHelper
import org.springframework.stereotype.Service

@Service
class EmailService(private val javaMailSender: JavaMailSender) {

        fun enviarSenhaPorEmail(emailCandidato: String, cpf: String, senha: String) {
            val mensagem = javaMailSender.createMimeMessage()
            val helper = MimeMessageHelper(mensagem, true, "UTF-8")

            try {
                helper.setTo(emailCandidato)
                helper.setSubject("[Matriculando] Sua senha de acesso ao sistema de matrículas")
                helper.setText(
                    """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background-color: #155dfc; color: white; padding: 10px; text-align: center; }
                            .content { padding: 20px; }
                            .dados { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }
                            .footer { margin-top: 20px; font-size: 12px; text-align: center; color: #777; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>Boas vindas à Matriculando!</h1>
                            </div>
                            <div class="content">
                                <p>Olá,</p>
                                <p>Sua matrícula está quase pronta! Aqui estão seus dados de acesso:</p>
                                
                                <div class="dados">
                                    <p><strong>Plataforma:</strong> <a href="https://matriculando.com.br">matriculando.com.br</a></p>
                                    <p><strong>Usuário (CPF):</strong> $cpf</p>
                                    <p><strong>Senha:</strong> $senha</p>
                                </div>
                                
                                <p>Entre em nossa plataforma para enviar seus dados e completar sua mátricula na RecordTech</p>
                                <p>Se tiver dúvidas, responda este e-mail ou entre em contato com suporte@matriculando.com.</p>
                            </div>
                            <div class="footer">
                                <p>© 2025 Matriculando - Todos os direitos reservados</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """.trimIndent(),
                    true // Habilita HTML
                )

                javaMailSender.send(mensagem)
            } catch (e: MessagingException) {
                throw RuntimeException("Falha ao enviar e-mail: ${e.message}")
            }
        }

    fun enviarSenhaPorEmailAdm(emailAdministrador: String, cpf: String, senha: String) {
        val mensagem = javaMailSender.createMimeMessage()
        val helper = MimeMessageHelper(mensagem, true, "UTF-8")

        try {
            helper.setTo(emailAdministrador)
            helper.setSubject("[Matriculando] Sua senha de acesso ao sistema de matrículas")
            helper.setText(
                """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background-color: #155dfc; color: white; padding: 10px; text-align: center; }
                            .content { padding: 20px; }
                            .dados { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }
                            .footer { margin-top: 20px; font-size: 12px; text-align: center; color: #777; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>Boas vindas à Matriculando!</h1>
                            </div>
                            <div class="content">
                                <p>Olá,</p>
                                <p>Aqui estão seus dados de acesso:</p>
                                
                                <div class="dados">
                                    <p><strong>Plataforma:</strong> <a href="https://matriculando.com.br">matriculando.com.br</a></p>
                                    <p><strong>Usuário (CPF):</strong> $cpf</p>
                                    <p><strong>Senha:</strong> $senha</p>
                                </div>
                                
                                <p>Entre em nossa plataforma para acessar os dados das candidaturas!</p>
                                <p>Se tiver dúvidas, responda este e-mail ou entre em contato com suporte@matriculando.com.</p>
                            </div>
                            <div class="footer">
                                <p>© 2025 Matriculando - Todos os direitos reservados</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """.trimIndent(),
                true // Habilita HTML
            )

            javaMailSender.send(mensagem)
        } catch (e: MessagingException) {
            throw RuntimeException("Falha ao enviar e-mail: ${e.message}")
        }
    }
}