package rest_api.docflow.services

import org.springframework.stereotype.Service
import software.amazon.awssdk.services.sqs.SqsClient
import software.amazon.awssdk.services.sqs.model.SendMessageRequest

@Service
class SqsService(
    private val sqsClient: SqsClient
) {

    private val queueUrl = "https://sqs.us-east-1.amazonaws.com/658995536017/document-processing"

    fun sendMessage(documentPayload: String) {
        println("Enviando mensagem para SQS: $documentPayload")
        val request = SendMessageRequest.builder()
            .queueUrl(queueUrl)
            .messageBody(documentPayload)
            .build()

        sqsClient.sendMessage(request)
    }
}
