INSERT INTO candidato (nome, cpf, email, data_nascimento, telefone)
VALUES ('João Silva', '12345678901', 'fabomoledo12@gmail.com', '1990-05-15', '11987654321'),
       ('Marco Campos', '98765432109', 'marco.camposjr@sptech.school', '1995-08-22', '21988776655');

INSERT INTO administrador (nome, cpf, email, data_nascimento, telefone)
VALUES ('Julia Araripe', '38719735057', 'julia.araripe@sptech.school', '1990-05-15', '18728527842'),
       ('Maria Oliveira', '74836559090', 'marcocjr2082@gmail.com', '1995-08-22', '27933322077');

-- Tipos de documento
INSERT INTO documento_tipo (nome, obrigatorio) VALUES
('Documento de Identidade (CIN ou RG)', TRUE),
('Declaração ou Certificado de Conclusão de Ensino Médio', FALSE),
('Histórico Escolar', FALSE),
('Comprovante de Residência', FALSE),
('Documento do Responsável', FALSE),
('Certificado de Reservista (Obrigatório para homens)', FALSE),
('Certidão de Nascimento ou Casamento', FALSE),
('Boletim do ENEM (Obrigatório para alunos que entram pelo Sisu ou pela nota do Enem)', FALSE);

-- Documentos dos candidatos
INSERT INTO documento (fk_candidato, fk_documento_tipo, caminho_arquivo, status_documento)
VALUES
(2, 1, 'docs/marco_rg.pdf', 'pendente'),
(2, 3, 'docs/marco_residencia.pdf', 'aprovado');

-- Matrículas
INSERT INTO matricula (fk_candidato, status_matricula, observacoes)
VALUES
(2, 'aprovado', 'Aguardando RG');
