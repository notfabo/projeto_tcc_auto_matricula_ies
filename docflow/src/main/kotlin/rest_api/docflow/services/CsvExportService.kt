package rest_api.docflow.services

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import org.springframework.stereotype.Service
import rest_api.docflow.dto.CandidatoAprovadoExportDTO
import rest_api.docflow.dto.DadosComprovanteResidenciaDTO
import rest_api.docflow.dto.DadosHistoricoDTO
import rest_api.docflow.dto.DadosRgDTO
import rest_api.docflow.repositories.CandidatoRepository
import rest_api.docflow.repositories.DocumentoRepository
import rest_api.docflow.repositories.MatriculaRepository

@Service
class CsvExportService(
    private val candidatoRepository: CandidatoRepository,
    private val documentoRepository: DocumentoRepository,
) {
    private val objectMapper = jacksonObjectMapper()

    fun getDadosCandidatosAprovados(): List<CandidatoAprovadoExportDTO> {
        val candidatosExportList = candidatoRepository.findCandidatosAprovadosParaExport()
        candidatosExportList.forEach { enriquecerDadosCandidato(it) }
        return candidatosExportList
    }

    fun getDadosTodosCandidatos(): List<CandidatoAprovadoExportDTO> {
        val candidatosExportList = candidatoRepository.findAllCandidatosParaExport()
        candidatosExportList.forEach { enriquecerDadosCandidato(it) }
        return candidatosExportList
    }

    private fun enriquecerDadosCandidato(candidatoDTO: CandidatoAprovadoExportDTO) {
        val documentos = documentoRepository.findByFkCandidato(candidatoDTO.idCandidato)

        documentos.find { it.subtipo == "rg" && it.dadosExtraidos != null }?.let { docRg ->
            try {
                val dadosRg: DadosRgDTO = objectMapper.readValue(docRg.dadosExtraidos!!)
                candidatoDTO.nomeMae = dadosRg.filiacao?.mae
                candidatoDTO.nomePai = dadosRg.filiacao?.pai
                candidatoDTO.rg = dadosRg.registroGeral
                candidatoDTO.dataEmissaoRg = dadosRg.dataExpedicao
                candidatoDTO.naturalidade = dadosRg.naturalidade
            } catch (e: Exception) {
                println("ERRO: Falha ao processar JSON do RG para o candidato ID ${candidatoDTO.idCandidato}: ${e.message}")
            }
        }
        documentos.find { it.fkDocumentoTipo == 3 && it.dadosExtraidos != null }?.let { docHistorico ->
            try {
                val dadosHistorico: DadosHistoricoDTO = objectMapper.readValue(docHistorico.dadosExtraidos!!)
                candidatoDTO.escolaEnsinoMedio = dadosHistorico.instituicaoEnsino
                candidatoDTO.anoConclusaoEnsinoMedio = dadosHistorico.tempoLetivo?.split(" - ")?.lastOrNull()?.trim()
                candidatoDTO.cidadeEscola = dadosHistorico.cidade
                candidatoDTO.estadoEscola = dadosHistorico.estado
            } catch (e: Exception) {
                println("ERRO: Falha ao processar JSON do Histórico para o candidato ID ${candidatoDTO.idCandidato}: ${e.message}")
            }
        }

        documentos.find { it.fkDocumentoTipo == 4 && it.dadosExtraidos != null }?.let { docResidencia ->
            try {
                val dadosResidencia: DadosComprovanteResidenciaDTO = objectMapper.readValue(docResidencia.dadosExtraidos!!)
                candidatoDTO.enderecoRua = dadosResidencia.ruaAvenida
                candidatoDTO.enderecoNumero = dadosResidencia.numeroEndereco
                candidatoDTO.enderecoBairro = dadosResidencia.bairro
                candidatoDTO.enderecoCidade = dadosResidencia.cidade
                candidatoDTO.enderecoEstado = dadosResidencia.estadoUf
                candidatoDTO.enderecoCep = dadosResidencia.cep
            } catch (e: Exception) {
                println("ERRO: Falha ao processar JSON de Residência para o candidato ID ${candidatoDTO.idCandidato}: ${e.message}")
            }
        }
    }


}