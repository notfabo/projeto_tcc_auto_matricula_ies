package rest_api.docflow

import org.springframework.boot.CommandLineRunner
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.scheduling.annotation.EnableAsync
import org.springframework.security.crypto.password.PasswordEncoder
import rest_api.docflow.models.Administrador
import rest_api.docflow.repositories.AdministradorRepository
import java.time.LocalDateTime

@SpringBootApplication
@EnableAsync
class DocflowApplication {

	@Bean
	fun initDatabase(
		repository: AdministradorRepository,
		encoder: PasswordEncoder
	) = CommandLineRunner {
		val adminCpf = "38719735057"

		if (repository.findByCpf(adminCpf) == null) {
			println("--- CRIANDO USUÁRIO ADMIN DE TESTE ---")
			val admin = Administrador().apply {
				nome = "Julia Araripe"
				cpf = adminCpf
				email = "julia.araripe@sptech.school"
				//universidade = "SPTECH"
				telefone = "18728527842"
				senha = encoder.encode("senha123")
				dataCriacao = LocalDateTime.now()
			}
			repository.save(admin)
			println("Usuário criado -> CPF: $adminCpf | Senha (texto puro): senha123")
		}
	}
}

fun main(args: Array<String>) {
	runApplication<DocflowApplication>(*args)
}
