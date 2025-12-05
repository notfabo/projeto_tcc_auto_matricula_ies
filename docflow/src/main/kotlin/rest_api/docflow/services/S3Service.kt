package rest_api.docflow.services

import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import software.amazon.awssdk.core.ResponseBytes
import software.amazon.awssdk.core.sync.RequestBody
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest
import software.amazon.awssdk.services.s3.model.GetObjectRequest
import software.amazon.awssdk.services.s3.model.GetObjectResponse
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.s3.presigner.S3Presigner
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest
import java.net.URI
import java.nio.file.Files
import java.time.Duration
import java.util.UUID

@Service
class S3Service(
    private val s3Client: S3Client,
    private val s3Presigner: S3Presigner,
) {
    private val bucketName = "docflow-candidatos-2"

    @Value("\${aws.s3.presigned-url.expiration-minutes:15}") // Pega do properties, com 15 min de padrão
    private lateinit var expirationMinutes: String

    fun uploadFile(file: MultipartFile, folder: String = ""): String {
        val extension = file.originalFilename?.substringAfterLast('.', "") ?: "bin"
        val folderPath = if (folder.isNotBlank()) folder.trimEnd('/') + "/" else ""
        val fileName = "$folderPath${UUID.randomUUID()}.$extension"

        val tempFile = Files.createTempFile("upload-", ".$extension").toFile()
        file.inputStream.use { input ->
            tempFile.outputStream().use { output -> input.copyTo(output) }
        }

        val request = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(fileName)
            .build()

        s3Client.putObject(request, tempFile.toPath())
        tempFile.delete()

        return fileName
    }

    // Helper para extrair a key do objeto mesmo quando receber uma URL completa
    private fun extractObjectKey(fileKeyOrUrl: String): String {
        var key = fileKeyOrUrl
        try {
            if (key.startsWith("http", ignoreCase = true)) {
                val uri = URI(key)
                val path = uri.path // geralmente '/bucketName/path/to/object'
                // tenta extrair após o nome do bucket se presente
                val bucketIndex = path.indexOf("/$bucketName/")
                key = if (bucketIndex >= 0) {
                    path.substring(bucketIndex + bucketName.length + 2) // pula '/' + bucketName + '/'
                } else {
                    // se não encontrou bucket no path, remove a primeira '/' e usa o restante
                    path.trimStart('/')
                }
            } else if (key.contains(bucketName)) {
                key = key.substringAfter("$bucketName/").trimStart('/')
            } else if (key.contains(".amazonaws.com/")) {
                key = key.substringAfter(".amazonaws.com/").trimStart('/')
            }
        } catch (e: Exception) {
            System.err.println("Aviso: não foi possível parsear a chave/URL do S3: $fileKeyOrUrl. Usando valor original. Erro: ${e.message}")
            key = fileKeyOrUrl
        }
        return key
    }

    fun deleteFile(fileKey: String) {
        val normalizedKey = extractObjectKey(fileKey)
        println("Tentando deletar o arquivo: $normalizedKey do bucket: $bucketName")
        try {
            val deleteObjectRequest = DeleteObjectRequest.builder()
                .bucket(bucketName)
                .key(normalizedKey)
                .build()

            s3Client.deleteObject(deleteObjectRequest)
            println("Arquivo $normalizedKey deletado com sucesso.")

        } catch (e: Exception) {
            System.err.println("Erro ao deletar o arquivo $normalizedKey do S3: ${e.message}")
            // Não relança exceção: falha ao deletar arquivo antigo não deve impedir o fluxo principal.
        }
    }

    fun downloadFile(fileKey: String): ByteArray? {
        return try {
            val getObjectRequest = GetObjectRequest.builder()
                .bucket(bucketName)
                .key(fileKey)
                .build()

            val responseBytes: ResponseBytes<GetObjectResponse> = s3Client.getObjectAsBytes(getObjectRequest)
            responseBytes.asByteArray()
        } catch (e: Exception) {
            System.err.println("Erro ao baixar o arquivo $fileKey do S3: ${e.message}")
            null
        }
    }

    fun uploadFileFromBytes(fileBytes: ByteArray, fileName: String): String {
        val request = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(fileName)
            .build()

        s3Client.putObject(request, RequestBody.fromBytes(fileBytes))
        return fileName
    }

    fun generatePresignedUrl(objectKey: String): String {
        val getObjectRequest = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(objectKey)
            .build()

        val presignRequest = GetObjectPresignRequest.builder()
            .signatureDuration(Duration.ofMinutes(expirationMinutes.toLong()))
            .getObjectRequest(getObjectRequest)
            .build()

        val presignedRequest = s3Presigner.presignGetObject(presignRequest)
        return presignedRequest.url().toString()
    }

}
