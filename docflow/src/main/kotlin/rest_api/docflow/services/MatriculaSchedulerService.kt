package rest_api.docflow.services

import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service

@Service
class MatriculaSchedulerService(
    private val matriculaService: MatriculaService
) {
    @Scheduled(fixedDelay = 10000) // executa a cada 10 segundos
    fun processarMatriculasPendentesScheduled() {
        try {
            println("[MatriculaSchedulerService] Iniciando verificação agendada de matrículas pendentes...")
            val processadas = matriculaService.processarMatriculasPendentes()
            println("[MatriculaSchedulerService] Verificação agendada concluída. Matrículas processadas: $processadas")
        } catch (e: Exception) {
            println("[MatriculaSchedulerService] Erro ao processar matrículas pendentes: ${e.message}")
            e.printStackTrace()
        }
    }
}