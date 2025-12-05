package rest_api.docflow.config

import org.springframework.context.annotation.Configuration
import org.springframework.scheduling.annotation.EnableScheduling
import org.springframework.scheduling.annotation.EnableAsync

@Configuration
@EnableScheduling
@EnableAsync
class SchedulingConfig