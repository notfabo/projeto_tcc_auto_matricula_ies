package rest_api.docflow.services

import org.springframework.stereotype.Service
import java.util.*
import java.util.concurrent.ConcurrentHashMap

enum class JobStatus { PENDING, PROCESSING, COMPLETED, FAILED }

data class JobStatusResponse(
    val status: JobStatus,
    val downloadUrl: String? = null,
    val message: String? = null
)

@Service
class JobStatusService {
    private val jobs = ConcurrentHashMap<String, JobStatusResponse>()

    fun createJob(): String {
        val jobId = UUID.randomUUID().toString()
        jobs[jobId] = JobStatusResponse(status = JobStatus.PENDING, message = "Job criado e aguardando na fila.")
        return jobId
    }

    fun updateJobStatus(jobId: String, status: JobStatus, message: String? = null, downloadUrl: String? = null) {
        jobs[jobId] = JobStatusResponse(status, downloadUrl, message)
    }

    fun getJobStatus(jobId: String): JobStatusResponse? {
        return jobs[jobId]
    }
}