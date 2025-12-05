import React, { useState } from 'react';
import { Save, ChevronDown, ChevronUp } from 'lucide-react';
import { ExtractedData } from '../../hooks/useExtractedData';
import { toast } from 'react-hot-toast';


const ORIENTACAO_SEXUAL_OPTIONS = ["Selecione", "Heterossexual", "Homossexual (gay/lésbica)", "Bissexual", "Pansexual", "Assexual", "Demissexual", "Queer", "Outro", "Prefiro não responder"];
const IDENTIDADE_GENERO_OPTIONS = ["Selecione", "Homem cisgênero", "Mulher cisgênero", "Homem transgênero", "Mulher transgênero", "Pessoa não-binária", "Pessoa gênero fluido", "Pessoa agênero", "Outro", "Prefiro não responder"];
const ESTADO_CIVIL_OPTIONS = ["Selecione", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"];
const RACA_OPTIONS = ["Selecione", "Branca", "Preta", "Parda", "Amarela", "Indígena", "Prefiro não declarar"];
const DEFICIENCIA_OPTIONS = ["Não", "Sim", "Prefiro não informar"];

interface DataSheetProps {
  data: ExtractedData;
  onFieldChange: (section: keyof ExtractedData, field: string, value: string) => void,
  onSaveChanges: (data: any) => void;
}

export const DataSheet: React.FC<DataSheetProps> = ({ data, onFieldChange, onSaveChanges }) => {
  const handleSaveClick = () => {
    const additionalInfo = data["Informações adicionais"];
    onSaveChanges(additionalInfo);
    toast.success("Informações adicionais salvas com sucesso!");
  };

  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const renderField = (sectionTitle: keyof ExtractedData, fieldLabel: string, value: string) => {
    if (sectionTitle !== "Informações adicionais") {
      return <div className="text-gray-900 bg-gray-100 px-3 py-2 rounded-lg w-full min-h-[42px]">{value || "-"}</div>;
    }

    const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      onFieldChange(sectionTitle, fieldLabel, e.target.value);
    };

    switch (fieldLabel) {
      case "Email":
      case "Whatsapp":
      case "Curso":
        return <div className="text-gray-900 bg-gray-100 px-3 py-2 rounded-lg w-full min-h-[42px]">{value || "-"}</div>;
      case "Nome social":
        return <input type="text" value={value} onChange={onChange} placeholder="Como você prefere ser chamado(a)" className="w-full px-3 py-2 border border-gray-300 rounded-lg" />;
      case "Estado civil":
        return (
          <select value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {ESTADO_CIVIL_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      case "Você se identifica com qual raça e/ou cor?":
        return (
          <select value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {RACA_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      case "Qual sua orientação sexual?":
        return (
          <select value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {ORIENTACAO_SEXUAL_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      case "Qual sua identidade de gênero?":
        return (
          <select value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {IDENTIDADE_GENERO_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      case "Você possui alguma deficiência?":
        return (
          <select value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {DEFICIENCIA_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      case "Informe o Número do CID apresentado no seu laudo médico":
        return null;
      default:
        return <input type="text" value={value} onChange={onChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="p-6 space-y-4">
        {Object.entries(data).map(([sectionTitle, fields]) => (
          <div key={sectionTitle} className="border border-gray-200 rounded-lg p-6">
            <button
              onClick={() => toggleSection(sectionTitle)}
              className="w-full flex justify-between items-center p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
            >
              <h3 className="text-xl font-semibold text-gray-800">{sectionTitle}</h3>
              {expandedSections[sectionTitle] ? (
                <ChevronUp className="h-6 w-6 text-gray-500" />
              ) : (
                <ChevronDown className="h-6 w-6 text-gray-500" />
              )}
            </button>
            {expandedSections[sectionTitle] && (
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(fields).map(([fieldLabel, value]) => {
                    const fieldComponent = renderField(sectionTitle as keyof ExtractedData, fieldLabel, value as string);
                    if (!fieldComponent) return null;

                    return (
                      <div key={fieldLabel}>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{fieldLabel}</label>
                        {fieldComponent}
                      </div>
                    );
                  })}

                  {sectionTitle === "Informações adicionais" && data["Informações adicionais"]["Você possui alguma deficiência?"] === "Sim" && (
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Número do CID (se aplicável)</label>
                      <input
                        type="text"
                        value={data["Informações adicionais"]["Informe o Número do CID apresentado no seu laudo médico"]}
                        onChange={(e) => onFieldChange("Informações adicionais", "Informe o Número do CID apresentado no seu laudo médico", e.target.value)}
                        placeholder="Informe o número do CID"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  )}
                </div>

                {sectionTitle === "Informações adicionais" && (
                  <div className="mt-8 text-right">
                    <button
                      onClick={handleSaveClick}
                      className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors"
                    >
                      <Save size={18} />
                      Salvar Informações Adicionais
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};