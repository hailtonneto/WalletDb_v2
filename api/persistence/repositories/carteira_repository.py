import os
import time
import secrets
import hashlib
import requests
from decimal import Decimal
from typing import Dict, Any, Optional, List

from sqlalchemy import text

from api.persistence.db import get_connection

class CarteiraRepository:

    def criar(self) -> Dict[str, Any]:
        # ADIÇÃO MÍNIMA: defaults caso env não exista
        private_key_size:int = int(os.getenv("PRIVATE_KEY_SIZE", "32"))
        public_key_size:int = int(os.getenv("PUBLIC_KEY_SIZE", "16"))

        chave_privada = secrets.token_hex(private_key_size)
        endereco = secrets.token_hex(public_key_size)
        hash_privada = hashlib.sha256(chave_privada.encode()).hexdigest()

        with get_connection() as conn:

            # ADIÇÃO MÍNIMA: incluir status = 'ATIVA'
            conn.execute(
                text("""
                    INSERT INTO carteira (endereco_carteira, hash_chave_privada, status)
                    VALUES (:endereco, :hash_privada, 'ATIVA')
                """),
                {"endereco": endereco, "hash_privada": hash_privada},
            )

            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco},
            ).mappings().first()
        self.popular_saldos(endereco)
        carteira = dict(row)
        carteira["chave_privada"] = chave_privada      
        return carteira


    def popular_saldos(self, endereco_carteira: str):
        with get_connection() as conn:
            conn.execute(
                text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda)
                    VALUES  (:endereco, 1), 
                            (:endereco, 2), 
                            (:endereco, 3),
                            (:endereco, 4),
                            (:endereco, 5);
                """),
                {"endereco": endereco_carteira},
            )
    

    def buscar_por_endereco(self, endereco_carteira: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira},
            ).mappings().first()

        return dict(row) if row else None


    def listar(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                """)
            ).mappings().all()

        return [dict(r) for r in rows]


    def atualizar_status(self, endereco_carteira: str, status: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE carteira
                       SET status = :status
                     WHERE endereco_carteira = :endereco
                """),
                {"status": status, "endereco": endereco_carteira},
            )

            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira},
            ).mappings().first()

        return dict(row) if row else None


    def listar_saldos(self, endereco: str):
            with get_connection() as conn:
                rows = conn.execute(
                    text("""
                        SELECT 
                            s.saldo,
                            m.codigo AS moeda_codigo,
                            m.nome AS moeda_nome
                        FROM saldo_carteira s
                        JOIN moeda m ON m.id_moeda = s.id_moeda
                        WHERE s.endereco_carteira = :endereco
                    """),
                    {"endereco": endereco},
                ).mappings().all()

            return [dict(r) for r in rows]


    def validar_chave(self, endereco, chave_privada):
        hash_input = hashlib.sha256(chave_privada.encode()).hexdigest()

        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT 1 
                    FROM carteira 
                    WHERE endereco_carteira = :endereco
                    AND hash_chave_privada = :hash
                """),
                {"endereco": endereco, "hash": hash_input}
            ).fetchone()

        return row is not None

    
    def depositar(self, endereco, moeda, valor, chave_privada):
        if not self.validar_chave(endereco, chave_privada):
            raise ValueError("Chave privada inválida")

        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                    SET saldo = saldo + :valor
                    WHERE endereco_carteira = :endereco 
                    AND id_moeda = :moeda
                """),
                {"valor": valor, "endereco": endereco, "moeda": moeda}
            )

            conn.execute(
                text("""
                    INSERT INTO deposito_saque 
                    (endereco_carteira, id_moeda, tipo, valor, taxa_valor, data_hora)
                    VALUES (:endereco, :moeda, 'DEPOSITO', :valor, 0, NOW())
                """),
                {"endereco": endereco, "valor": valor, "moeda": moeda}
            )

        return {"status": "OK", "novo_saldo": self.obter_saldo(endereco, moeda)}
    

    def sacar(self, endereco, moeda, valor, chave_privada):
        if not self.validar_chave(endereco, chave_privada):
            raise ValueError("Chave privada inválida")

        valor = Decimal(valor)
        taxa_valor = valor * Decimal("0.02")
        total = valor + taxa_valor

        saldo_atual = self.obter_saldo(endereco, moeda)
        if saldo_atual < total:
            raise ValueError("Saldo insuficiente")

        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                    SET saldo = saldo - :total
                    WHERE endereco_carteira = :endereco 
                    AND id_moeda = :moeda
                """),
                {"total": total, "endereco": endereco, "moeda": moeda}
            )

            conn.execute(
                text("""
                    INSERT INTO deposito_saque 
                    (endereco_carteira, id_moeda, tipo, valor, taxa_valor, data_hora)
                    VALUES (:endereco, :moeda, 'SAQUE', :valor, :taxa_valor, NOW())
                """),
                {"endereco": endereco, "valor": valor, "taxa_valor": taxa_valor, "moeda": moeda}
            )

        return {"status": "OK", "novo_saldo": saldo_atual - total}


    def obter_saldo(self, endereco, moeda):
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT saldo 
                    FROM saldo_carteira
                    WHERE endereco_carteira = :endereco
                    AND id_moeda = :moeda
                """),
                {"endereco": endereco, "moeda": moeda}
            ).mappings().first()

        return row["saldo"]
    

    def converter(self, endereco, id_moeda_origem, id_moeda_destino, valor_origem):
        from decimal import Decimal
        valor_origem = Decimal(valor_origem)

        saldo_origem = self.obter_saldo(endereco, id_moeda_origem)
        if saldo_origem < valor_origem:
            raise ValueError("Saldo insuficiente para conversão")

        codigo_origem = self.get_codigo_moeda(id_moeda_origem)
        codigo_destino = self.get_codigo_moeda(id_moeda_destino)

        resp = requests.get(f"https://api.coinbase.com/v2/exchange-rates?currency={codigo_origem}")
        if resp.status_code != 200:
            raise ValueError("Erro ao consultar cotação na Coinbase")
        data = resp.json()
        cotacao = Decimal(data["data"]["rates"][codigo_destino])

        valor_destino = valor_origem * cotacao
        taxa_percentual = Decimal("0.02")
        taxa_valor = valor_destino * taxa_percentual
        valor_destino_final = valor_destino - taxa_valor

        with get_connection() as conn:
            conn.execute(
                text("UPDATE saldo_carteira SET saldo = saldo - :valor WHERE endereco_carteira=:endereco AND id_moeda=:moeda"),
                {"valor": valor_origem, "endereco": endereco, "moeda": id_moeda_origem}
            )
            conn.execute(
                text("UPDATE saldo_carteira SET saldo = saldo + :valor WHERE endereco_carteira=:endereco AND id_moeda=:moeda"),
                {"valor": valor_destino_final, "endereco": endereco, "moeda": id_moeda_destino}
            )
            conn.execute(
                text("""
                    INSERT INTO conversao (endereco_carteira, id_moeda_origem, id_moeda_destino,
                                            valor_origem, valor_destino, taxa_percentual, taxa_valor, cotacao_utilizada)
                    VALUES (:endereco, :moeda_origem, :moeda_destino, :valor_origem, :valor_destino, :taxa_percentual, :taxa_valor, :cotacao)
                """),
                {
                    "endereco": endereco,
                    "moeda_origem": id_moeda_origem,
                    "moeda_destino": id_moeda_destino,
                    "valor_origem": valor_origem,
                    "valor_destino": valor_destino_final,
                    "taxa_percentual": taxa_percentual,
                    "taxa_valor": taxa_valor,
                    "cotacao": cotacao
                }
            )

        return {"status": "OK", "valor_convertido": str(valor_destino_final)}


    def get_codigo_moeda(self, id_moeda: int) -> str:
        with get_connection() as conn:
            row = conn.execute(
                text("SELECT codigo FROM moeda WHERE id_moeda = :id"),
                {"id": id_moeda}
            ).mappings().first()
        if not row:
            raise ValueError(f"Moeda com id {id_moeda} não encontrada")
        return row["codigo"]

    def transferir(self, endereco_origem, endereco_destino, id_moeda, valor, chave_privada):
        if not self.validar_chave(endereco_origem, chave_privada):
            raise ValueError("Chave privada inválida")

        valor = Decimal(valor)
        taxa_percentual = Decimal("0.02")
        taxa_valor = valor * taxa_percentual
        total = valor + taxa_valor

        saldo_origem = self.obter_saldo(endereco_origem, id_moeda)
        if saldo_origem < total:
            raise ValueError("Saldo insuficiente na origem")

        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                    SET saldo = saldo - :total
                    WHERE endereco_carteira = :endereco AND id_moeda = :moeda
                """),
                {"total": total, "endereco": endereco_origem, "moeda": id_moeda}
            )

            conn.execute(
                text("""
                    UPDATE saldo_carteira
                    SET saldo = saldo + :valor
                    WHERE endereco_carteira = :endereco AND id_moeda = :moeda
                """),
                {"valor": valor, "endereco": endereco_destino, "moeda": id_moeda}
            )

            conn.execute(
                text("""
                    INSERT INTO transferencia (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor, data_hora)
                    VALUES (:origem, :destino, :moeda, :valor, :taxa, NOW())
                """),
                {
                    "origem": endereco_origem,
                    "destino": endereco_destino,
                    "moeda": id_moeda,
                    "valor": valor,
                    "taxa": taxa_valor
                }
            )

        return {"status": "OK", "debito_origem": str(total), "credito_destino": str(valor)}
