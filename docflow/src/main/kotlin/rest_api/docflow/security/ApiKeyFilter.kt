package rest_api.docflow.security

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

@Component
class ApiKeyFilter(
    @Value("\${app.api.key:docflow-ai-key-2024}")
    private val apiKey: String
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        if (request.requestURI == "/api/documentos/atualizar-status" && request.method == "POST") {
            val providedApiKey = request.getHeader("X-API-Key")
            
            if (providedApiKey == null || providedApiKey != apiKey) {
                response.status = HttpServletResponse.SC_UNAUTHORIZED
                response.writer.write("{\"erro\": \"API Key inválida\"}")
                return
            }
        }
        
        filterChain.doFilter(request, response)
    }
} 