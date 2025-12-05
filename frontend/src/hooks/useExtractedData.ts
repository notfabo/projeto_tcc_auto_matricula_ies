import { useState, useEffect, useCallback } from "react";
import { Document } from "../types/documento";
import { CandidatoAdicionalData, CandidatoLogado } from "../types/candidato";
import { getCandidatoLogado } from "../services/candidato";

const initialData = {
  Identificação: {
    "Nome Completo": "",
    Pai: "",
    Mãe: "",
    "Data de Nascimento": "",
    RG: "",
    CPF: "",
    Nacionalidade: "Brasil",
    "Estado Nasc.": "",
    "Cidade Nasc.": "",
  },
  Endereço: {
    CEP: "",
    "Rua/Logradouro": "",
    Número: "",
    Complemento: "",
    Bairro: "",
    Cidade: "",
    Estado: "",
  },
  "Formação Acadêmica": {
    "Nível de Escolaridade": "",
    "Instituição de Ensino": "",
    "Tempo Letivo": "",
  },
  "Informações adicionais": {
    Curso: "",
    Email: "",
    Whatsapp: "",
    "Nome social": "",
    "Estado civil": "",
    "Você se identifica com qual raça e/ou cor?": "",
    "Qual sua orientação sexual?": "",
    "Qual sua identidade de gênero?": "",
    "Você possui alguma deficiência?": "Não",
    "Informe o Número do CID apresentado no seu laudo médico": "",
  },
};

export type ExtractedData = typeof initialData;

export const useExtractedData = (
  documents: Document[],
  token: string | null
) => {
  const [extractedData, setExtractedData] =
    useState<ExtractedData>(initialData);
  const [candidatoApiData, setCandidatoApiData] = useState<
    (CandidatoLogado & CandidatoAdicionalData) | null
  >(null);

  useEffect(() => {
    const fetchCandidatoData = async () => {
      if (!token) {
        setCandidatoApiData(null);
        return;
      }
      try {
        const data = await getCandidatoLogado(token);
        setCandidatoApiData(data);
      } catch (error) {
        setCandidatoApiData(null);
      }
    };

    fetchCandidatoData();
  }, [token]);

  useEffect(() => {
    setExtractedData((prevData) => {
      const newData = JSON.parse(JSON.stringify(prevData));

    if (candidatoApiData) {
        newData["Informações adicionais"].Curso =
          candidatoApiData.nomeCurso || prevData["Informações adicionais"].Curso;
        newData["Informações adicionais"].Email =
          candidatoApiData.email || prevData["Informações adicionais"].Email;
        newData["Informações adicionais"].Whatsapp =
          candidatoApiData.telefone || prevData["Informações adicionais"].Whatsapp;
      newData["Informações adicionais"]["Nome social"] =
        candidatoApiData.nomeSocial || "";
      newData["Informações adicionais"]["Estado civil"] =
        candidatoApiData.estadoCivil || "";
      newData["Informações adicionais"][
        "Você se identifica com qual raça e/ou cor?"
      ] = candidatoApiData.racaCandidato || "";
      newData["Informações adicionais"]["Qual sua orientação sexual?"] =
        candidatoApiData.orientacaoSexual || "";
      newData["Informações adicionais"]["Qual sua identidade de gênero?"] =
        candidatoApiData.identidadeGenero || "";
      newData["Informações adicionais"]["Você possui alguma deficiência?"] =
        candidatoApiData.possuiDeficiencia || "Não";
      newData["Informações adicionais"][
        "Informe o Número do CID apresentado no seu laudo médico"
      ] = candidatoApiData.numeroCid || "";
    }

    documents.forEach((doc) => {
      if (doc.status === "aprovado" && doc.dadosExtraidos) {
        try {
          const parsedData = JSON.parse(doc.dadosExtraidos);

          const safeAssign = (
            section: string,
            field: string,
            value: string | undefined
          ) => {
            if (typeof value === "string" && value.trim() !== "") {
              const currentFieldValue = (newData as any)[section][field];
              if (!currentFieldValue) {
                (newData as any)[section][field] = value;
              }
            }
          };

          switch (doc.tipo) {
            case "1":
              safeAssign("Identificação", "Nome Completo", parsedData.nome);
              if (parsedData.filiacao) {
                safeAssign("Identificação", "Pai", parsedData.filiacao.pai);
                safeAssign("Identificação", "Mãe", parsedData.filiacao.mae);
              }
              safeAssign(
                "Identificação",
                "Data de Nascimento",
                parsedData.data_nascimento
              );
              safeAssign("Identificação", "RG", parsedData.registro_geral);
              safeAssign("Identificação", "CPF", parsedData.cpf);
              if (parsedData.naturalidade) {
                const [cidade, estado] = parsedData.naturalidade.split(" - ");
                safeAssign("Identificação", "Cidade Nasc.", cidade);
                safeAssign("Identificação", "Estado Nasc.", estado);
              }
              break;
            case "3":
              safeAssign(
                "Formação Acadêmica",
                "Nível de Escolaridade",
                parsedData.nivel_ensino
              );
              safeAssign(
                "Formação Acadêmica",
                "Instituição de Ensino",
                parsedData.instituicao_ensino
              );
              safeAssign(
                "Formação Acadêmica",
                "Tempo Letivo",
                parsedData.tempo_letivo
              );
              break;
            case "4":
              safeAssign("Endereço", "Rua/Logradouro", parsedData.rua_avenida);
              safeAssign("Endereço", "Número", parsedData.numero_endereco);
              safeAssign("Endereço", "Bairro", parsedData.bairro);
              safeAssign("Endereço", "Cidade", parsedData.cidade);
              safeAssign("Endereço", "Estado", parsedData.estado_uf);
              safeAssign("Endereço", "CEP", parsedData.cep);
              break;
            default:
              break;
          }
        } catch (error) {
          console.error(
            `Erro ao fazer parse dos dados extraídos para o documento tipo: ${doc.tipo}`,
            error
          );
        }
      }
    });
      return newData;
    });
  }, [candidatoApiData, documents]);

  const handleFieldChange = useCallback(
    (section: keyof ExtractedData, field: string, value: string) => {
      setExtractedData((prevData) => ({
        ...prevData,
        [section]: {
          ...prevData[section],
          [field]: value,
        },
      }));
    },
    []
  );

  return {
    extractedData,
    handleFieldChange,
  };
};
