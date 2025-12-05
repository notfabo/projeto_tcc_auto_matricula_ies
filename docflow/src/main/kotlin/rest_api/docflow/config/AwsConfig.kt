package rest_api.docflow.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.presigner.S3Presigner
import software.amazon.awssdk.services.textract.TextractClient
import software.amazon.awssdk.services.sqs.SqsClient

@Configuration
class AwsConfig {

    @Bean
    fun s3Client(): S3Client {
        return S3Client.builder()
            .region(Region.US_EAST_1)
            .credentialsProvider(DefaultCredentialsProvider.create())
            .build()
    }

    @Bean
    fun textractClient(): TextractClient {
        return TextractClient.builder()
            .region(Region.SA_EAST_1)
            .credentialsProvider(DefaultCredentialsProvider.create())
            .build()
    }

    @Bean
    fun sqsClient(): SqsClient {
        return SqsClient.builder()
            .region(Region.US_EAST_1)
            .credentialsProvider(DefaultCredentialsProvider.create())
            .build()
    }

    @Bean
    fun s3Presigner(): S3Presigner {
        return S3Presigner.builder()
            .region(Region.US_EAST_1)
            .credentialsProvider(DefaultCredentialsProvider.create())
            .build()
    }
}
