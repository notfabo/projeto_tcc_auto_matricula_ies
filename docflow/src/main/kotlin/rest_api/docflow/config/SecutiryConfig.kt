package rest_api.docflow.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpMethod
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.AuthenticationProvider
import org.springframework.security.authentication.dao.DaoAuthenticationProvider
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter
import org.springframework.web.cors.CorsConfigurationSource
import rest_api.docflow.services.CustomUserDetailsService
import rest_api.docflow.security.JwtAuthFilter
import rest_api.docflow.security.ApiKeyFilter

@Configuration
@EnableMethodSecurity
class SecurityConfig(
    private val jwtAuthFilter: JwtAuthFilter,
    private val apiKeyFilter: ApiKeyFilter,
    private val userDetailsService: CustomUserDetailsService
) {

    @Bean
    fun securityFilterChain(http: HttpSecurity, corsConfigurationSource: CorsConfigurationSource): SecurityFilterChain {
        return http
            .csrf { it.disable() }
            .cors { it.configurationSource(corsConfigurationSource) }
            .headers { it.frameOptions { frame -> frame.disable() } }
            .authorizeHttpRequests {
                it
                    .requestMatchers("/api/auth/**").permitAll()
                    .requestMatchers("/api/admin/auth/**").permitAll()
                    .requestMatchers("/api/admin/export/**").permitAll()
                    .requestMatchers("/api/candidatos/**").permitAll()
                    .requestMatchers("/api/documentos/**").permitAll()
                    .requestMatchers("/api/matriculas/**").permitAll()
                    .requestMatchers(HttpMethod.GET, "/api/candidatos/me").authenticated()
                    .requestMatchers(HttpMethod.GET, "/api/documentos/me").authenticated()
                    .requestMatchers(HttpMethod.GET, "/api/matriculas/me").permitAll()
                    .requestMatchers(HttpMethod.GET, "/api/candidatos/listar").authenticated()
                    .requestMatchers(HttpMethod.PATCH, "/api/candidatos/me/additional-info").permitAll()
                    .requestMatchers(HttpMethod.POST, "/api/auth/enviar-senha/**").permitAll()
                    .requestMatchers(HttpMethod.POST, "/api/documentos/atualizar-status").permitAll()
                    .requestMatchers(HttpMethod.POST, "/api/admin/matriculas/processar-pendentes").permitAll()
                    .requestMatchers("/h2-console/**").permitAll()
                    .anyRequest().authenticated()
            }
            .sessionManagement {
                it.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            }
            .authenticationProvider(authenticationProvider())
            .addFilterBefore(apiKeyFilter, UsernamePasswordAuthenticationFilter::class.java)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter::class.java)
            .build()
    }

    @Bean
    fun authenticationProvider(): AuthenticationProvider {
        val provider = DaoAuthenticationProvider()
        provider.setUserDetailsService(userDetailsService)
        provider.setPasswordEncoder(passwordEncoder())
        return provider
    }

    @Bean
    fun passwordEncoder(): PasswordEncoder = BCryptPasswordEncoder()

    @Bean
    fun authenticationManager(auth: AuthenticationConfiguration): AuthenticationManager {
        return auth.authenticationManager
    }
}