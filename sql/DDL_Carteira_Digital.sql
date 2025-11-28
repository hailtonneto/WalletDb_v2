-- =========================================================
--  Script de criação da base, usuário,
--  Projeto: Carteira Digital
--  Banco:   MySQL 8+
-- =========================================================

-- 1) Criação da base de homologação
CREATE DATABASE IF NOT EXISTS wallet_homolog
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 2) Criação do usuário restrito para a API
--    (ajuste a senha conforme necessário)
CREATE USER IF NOT EXISTS 'wallet_api_homolog'@'%'
    IDENTIFIED BY 'api123';

-- 3) Grants: apenas DML (sem CREATE/DROP/ALTER)
GRANT SELECT, INSERT, UPDATE, DELETE
    ON wallet_homolog.*
    TO 'wallet_api_homolog'@'%';

FLUSH PRIVILEGES;

-- 4) Usar a base
USE wallet_homolog;

-- =========================================================
--  Tabelas (Aluno deve fazer o modelo)
-- =========================================================

CREATE TABLE CARTEIRA (
    endereco_carteira VARCHAR(255) NOT NULL,
    hash_chave_privada VARCHAR(255) NOT NULL,
    MODIFY data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVA','BLOQUEADA') NOT NULL DEFAULT 'ATIVA',
    PRIMARY KEY (endereco_carteira)
);

CREATE TABLE MOEDA (
    id_moeda SMALLINT NOT NULL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('Cripto', 'Fiduciária') NOT NULL
);

CREATE TABLE SALDO_CARTEIRA (
    endereco_carteira VARCHAR(255) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    saldo DECIMAL(18, 8) NOT NULL, -- Assumindo precisão alta para moedas
    data_atualizacao DATETIME NOT NULL,
    PRIMARY KEY (endereco_carteira, id_moeda),
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE DEPOSITO_SAQUE (
    id_movimento BIGINT NOT NULL,
    endereco_carteira VARCHAR(255) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    tipo ENUM('DEPOSITO', 'SAQUE') NOT NULL,
    valor DECIMAL(18, 8) NOT NULL,
    taxa_valor DECIMAL(18, 8) NOT NULL,
    data_hora DATETIME NOT NULL,
    PRIMARY KEY (id_movimento),
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE CONVERSAO (
    id_conversao BIGINT NOT NULL,
    endereco_carteira VARCHAR(255) NOT NULL,
    id_moeda_origem SMALLINT NOT NULL,
    id_moeda_destino SMALLINT NOT NULL,
    valor_origem DECIMAL(18, 8) NOT NULL,
    valor_destino DECIMAL(18, 8) NOT NULL,
    taxa_percentual DECIMAL(5, 2) NOT NULL,
    taxa_valor DECIMAL(18, 8) NOT NULL,
    cotacao_utilizada DECIMAL(18, 8) NOT NULL,
    data_hora DATETIME NOT NULL,
    PRIMARY KEY (id_conversao),
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    -- Referência a MOEDA para a moeda de origem
    FOREIGN KEY (id_moeda_origem) REFERENCES MOEDA(id_moeda),
    -- Referência a MOEDA para a moeda de destino
    FOREIGN KEY (id_moeda_destino) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE TRANSFERENCIA (
    id_transferencia BIGINT NOT NULL,
    endereco_origem VARCHAR(255) NOT NULL,
    endereco_destino VARCHAR(255) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    valor DECIMAL(18, 8) NOT NULL,
    taxa_valor DECIMAL(18, 8) NOT NULL,
    data_hora DATETIME NOT NULL,
    PRIMARY KEY (id_transferencia),
    -- Referência à CARTEIRA de origem
    FOREIGN KEY (endereco_origem) REFERENCES CARTEIRA(endereco_carteira),
    -- Referência à CARTEIRA de destino
    FOREIGN KEY (endereco_destino) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);

INSERT INTO MOEDA (id_moeda, codigo, nome, tipo) VALUES
(1, 'BTC', 'Bitcoin', 'Cripto'),
(2, 'ETH', 'Ethereum', 'Cripto'),
(3, 'SOL', 'Solana', 'Cripto'),
(4, 'USD', 'Dólar Americano', 'Fiduciária'),
(5, 'BRL', 'Real Brasileiro', 'Fiduciária');

-- O tipo 'Cripto' e 'Fiduciária' são exemplos. Ajuste conforme necessário.

-- ALTER TABLE carteira
--     MODIFY data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     MODIFY status ENUM('ATIVA','BLOQUEADA') NOT NULL DEFAULT 'ATIVA';