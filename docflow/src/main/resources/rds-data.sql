INSERT INTO candidato (nome, cpf, email, data_nascimento, telefone)
VALUES ('Jose Felipe Dias', '38328401842', 'fabomoledo12@gmail.com', '2000-05-15', '11987654321'),
       ('Marco Campos', '98765432109', 'marco.camposjr@sptech.school', '2000-08-22', '21988776655'),
       ('Ana Pereira', '11122233344', 'ana.pereira@gmail.com', '2000-03-10', '11911223344'),
       ('Carlos Souza', '55566677788', 'carlos.souza@gmail.com', '2000-11-25', '11955667788'),
       ('Beatriz Oliveira', '99988877766', 'beatriz.oliveira@gmail.com', '2000-07-01', '21999887766'),
       ('Lucas Ferreira', '44455566677', 'lucas.f@gmail.com', '2000-01-30', '31944556677'),
       ('Juliana Costa', '22233344455', 'juliana.costa@gmail.com', '2000-09-18', '41922334455'),
       ('Livia Araripe Lopes', '44335197828', 'fabiomoledo12@gmail.com', '2003-02-08', '11999887766');

-- Tipos de documento
INSERT INTO documento_tipo (nome, obrigatorio) VALUES
('Documento de Identidade (RG)', TRUE),
('Declaração ou Certificado de Conclusão de Ensino Médio ', FALSE),
('Histórico Escolar', TRUE),
('Comprovante de Residência', TRUE),
('Documento do Responsável ', FALSE),
('Certificado de Reservista', FALSE),
('Certidão de Nascimento ou Casamento', TRUE),
('Boletim do ENEM (Obrigatório para candidatos que entram pelo Sisu ou pela nota do Enem)', FALSE);

INSERT INTO documento (fk_candidato, fk_documento_tipo, caminho_arquivo, status_documento, dados_extraidos, subtipo, data_validacao)
VALUES 
(2, 1, 'documentos/2/rg.png', 'aprovado', '{"cpf": "98765432109", "nome": "Marco Campos", "filiacao": {"mae": "Maria Campos", "pai": "Joao Campos"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "10/05/2018", "registro_geral": "28.123.456-7", "data_nascimento": "22/08/2000"}', 'rg', NOW()),
(2, 3, 'documentos/2/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Marco Campos", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Pedro II", "certificacao_conclusao": true}', NULL, NOW()),

(3, 1, 'documentos/3/rg.png', 'aprovado', '{"cpf": "11122233344", "nome": "Ana Pereira", "filiacao": {"mae": "Lucia Pereira", "pai": "Carlos Pereira"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "15/02/2018", "registro_geral": "33.456.789-1", "data_nascimento": "10/03/2000"}', 'rg', NOW()),
(3, 3, 'documentos/3/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Ana Pereira", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Bandeirantes", "certificacao_conclusao": true}', NULL, NOW()),

(4, 1, 'documentos/4/rg.png', 'aprovado', '{"cpf": "55566677788", "nome": "Carlos Souza", "filiacao": {"mae": "Sofia Souza", "pai": "Roberto Souza"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "20/11/2018", "registro_geral": "44.567.890-2", "data_nascimento": "25/11/2000"}', 'rg', NOW()),
(4, 3, 'documentos/4/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Carlos Souza", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Santo Agostinho", "certificacao_conclusao": true}', NULL, NOW()),

(5, 1, 'documentos/5/rg.png', 'aprovado', '{"cpf": "99988877766", "nome": "Beatriz Oliveira", "filiacao": {"mae": "Fernanda Oliveira", "pai": "Ricardo Oliveira"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "05/06/2018", "registro_geral": "55.678.901-3", "data_nascimento": "01/07/2000"}', 'rg', NOW()),
(5, 3, 'documentos/5/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Beatriz Oliveira", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Anchieta", "certificacao_conclusao": true}', NULL, NOW()),

(6, 1, 'documentos/6/rg.png', 'aprovado', '{"cpf": "44455566677", "nome": "Lucas Ferreira", "filiacao": {"mae": "Sandra Ferreira", "pai": "Marcos Ferreira"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "12/01/2018", "registro_geral": "66.789.012-4", "data_nascimento": "30/01/2000"}', 'rg', NOW()),
(6, 3, 'documentos/6/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Lucas Ferreira", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Farroupilha", "certificacao_conclusao": true}', NULL, NOW()),

(7, 1, 'documentos/7/rg.png', 'aprovado', '{"cpf": "22233344455", "nome": "Juliana Costa", "filiacao": {"mae": "Vera Costa", "pai": "Paulo Costa"}, "naturalidade": "S.PAULO - SP", "data_expedicao": "30/08/2018", "registro_geral": "77.890.123-5", "data_nascimento": "18/09/2000"}', 'rg', NOW()),
(7, 3, 'documentos/7/historico_escolar.png', 'aprovado', '{"cidade": "SÃO PAULO", "estado": "SP", "nome_aluno": "Juliana Costa", "nivel_ensino": "Ensino Médio", "tempo_letivo": "2015 - 2017", "instituicao_ensino": "Colégio Positivo", "certificacao_conclusao": true}', NULL, NOW());

INSERT INTO curso (nome_curso) VALUES
('Ciencia da Computacao'),
('Sistemas de Informacao');

INSERT INTO turma (fk_curso, codigo_turma, ano_semestre, periodo) VALUES
(1, 'CCO2025-1-A', '2025.1', 'Noite'),   
(2, 'SIS2025-1-A', '2025.1', 'Noite');

INSERT INTO matricula (fk_candidato, fk_turma, status_matricula, status_pre_matricula, motivo_pre_matricula, data_inscricao)
VALUES
(1, 1, 'pendente', 'pendente', NULL, '2025-01-05 10:15:00'),          
(2, 1, 'pendente', 'aprovado', NULL, '2025-01-08 14:30:00'),          
(3, 1, 'pendente', 'aprovado', NULL, '2025-01-11 09:00:00'),          
(4, 2, 'pendente', 'aprovado', NULL, '2025-01-12 11:25:00'),          
(5, 2, 'pendente', 'aprovado', NULL, '2025-01-15 17:45:00'),          
(6, 1, 'pendente', 'aprovado', NULL, '2025-01-19 18:10:00'),          
(7, 2, 'aprovado', 'aprovado', NULL, '2025-01-21 12:00:00'),
(8, 1, 'pendente', 'pendente', NULL, '2025-01-23 16:20:00');

select * from documento;
select * from administrador;
select * from matricula;
select * from candidato;


