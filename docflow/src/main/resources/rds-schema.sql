-- DROP DATABASE docflow;
-- CREATE DATABASE docflow;
USE docflow;
CREATE TABLE candidato (
                       id_candidato INT PRIMARY KEY AUTO_INCREMENT,
                       nome VARCHAR(60) NOT NULL,
                       cpf VARCHAR(11) NOT NULL,
                       email VARCHAR(45),
                       data_nascimento DATE,
                       telefone VARCHAR(11),
                       senha VARCHAR(255),
                       nome_social VARCHAR(60),
                       estado_civil VARCHAR(20),
                       raca_candidato VARCHAR(20),
                       orientacao_sexual VARCHAR(20),
                       identidade_genero VARCHAR(20),
                       possui_deficiencia VARCHAR(30),
                       numero_cid VARCHAR(60),
                       data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE administrador (
                           id_administrador INT PRIMARY KEY AUTO_INCREMENT,
                           nome VARCHAR(60) NOT NULL,
                           cpf VARCHAR(11) NOT NULL,
                           email VARCHAR(45),
                           telefone VARCHAR(11),
                           senha VARCHAR(255),
                           data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE documento_tipo (
                                id_documento_tipo INT PRIMARY KEY AUTO_INCREMENT,
                                nome VARCHAR(100) NOT NULL,
                                obrigatorio BOOLEAN DEFAULT FALSE,
                                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE documento (
                           id INT PRIMARY KEY AUTO_INCREMENT,
                           fk_candidato INT NOT NULL,
                           fk_documento_tipo INT NOT NULL,
                           caminho_arquivo VARCHAR(255) NOT NULL,
                           data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                           status_documento VARCHAR(20) DEFAULT 'revisao',
                           dados_extraidos JSON,
                           motivo_erro JSON,
                           subtipo VARCHAR(10),
                           data_validacao TIMESTAMP,
                           FOREIGN KEY (fk_candidato) REFERENCES candidato(id_candidato),
                           FOREIGN KEY (fk_documento_tipo) REFERENCES documento_tipo(id_documento_tipo)
);

CREATE TABLE curso (
    id_curso INT PRIMARY KEY AUTO_INCREMENT,
    nome_curso VARCHAR(100) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE turma (
    id_turma INT PRIMARY KEY AUTO_INCREMENT,
    fk_curso INT NOT NULL,
    codigo_turma VARCHAR(20) UNIQUE NOT NULL,
    ano_semestre VARCHAR(6) NOT NULL,
    periodo VARCHAR(20),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (fk_curso) REFERENCES curso(id_curso)
);

CREATE TABLE matricula (
                           id INT PRIMARY KEY AUTO_INCREMENT,
                           fk_candidato INT NOT NULL,
                           fk_turma INT NOT NULL,
                           status_matricula VARCHAR(20) DEFAULT 'pendente',
                           status_pre_matricula VARCHAR(20) DEFAULT 'pendente',
                           motivo_pre_matricula TEXT,
                           data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                           observacoes VARCHAR(95),
                           data_atualizacao TIMESTAMP,
                           FOREIGN KEY (fk_candidato) REFERENCES candidato(id_candidato),
                           FOREIGN KEY (fk_turma) REFERENCES turma(id_turma),
                           UNIQUE (fk_candidato, fk_turma)
);


select * from documento;
select * from candidato;
select * from administrador;