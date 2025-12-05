DROP TABLE IF EXISTS documento_tipo;
DROP TABLE IF EXISTS matricula;
DROP TABLE IF EXISTS documento;
DROP TABLE IF EXISTS candidato;
DROP TABLE IF EXISTS administrador;

CREATE TABLE candidato (
                       id_candidato INT PRIMARY KEY AUTO_INCREMENT,
                       nome VARCHAR(60) NOT NULL,
                       cpf CHAR(11) NOT NULL,
                       email VARCHAR(45),
                       data_nascimento DATE,
                       telefone VARCHAR(11),
                       senha VARCHAR(255),
                       info_add JSON,
                       data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE administrador (
                           id_administrador INT PRIMARY KEY AUTO_INCREMENT,
                           nome VARCHAR(60) NOT NULL,
                           cpf CHAR(11) NOT NULL,
                           email VARCHAR(45),
                           data_nascimento DATE,
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
                           caminho_arquivo VARCHAR(80) NOT NULL,
                           data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                           status_documento VARCHAR(20) DEFAULT 'pendente',
                           dados_extraidos JSON, -- substitui JSON
                           motivo_erro JSON,
                           subtipo VARCHAR(10),
                           data_validacao TIMESTAMP,
                           FOREIGN KEY (fk_candidato) REFERENCES candidato(id_candidato),
                           FOREIGN KEY (fk_documento_tipo) REFERENCES documento_tipo(id_documento_tipo)
);

CREATE TABLE matricula (
                           id INT PRIMARY KEY AUTO_INCREMENT,
                           fk_candidato INT NOT NULL,
                           status_matricula VARCHAR(20) DEFAULT 'pendente',
                           data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                           observacoes VARCHAR(95),
                           data_atualizacao TIMESTAMP,
                           FOREIGN KEY (fk_candidato) REFERENCES candidato(id_candidato)
);