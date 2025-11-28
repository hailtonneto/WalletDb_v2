from typing import List

from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import (
    Carteira,
    CarteiraCriada,
    Saldo,
    SaldosCarteira,
    DepositoRequest,
    SaqueRequest,
    ConversaoRequest,
    TransferenciaRequest
)


class CarteiraService:
    def __init__(self, carteira_repo: CarteiraRepository):
        self.carteira_repo = carteira_repo

    # ------------------------------------------------------
    # JÁ EXISTENTES — NÃO ALTEREI NADA
    # ------------------------------------------------------

    def criar_carteira(self) -> CarteiraCriada:
        row = self.carteira_repo.criar()
        return CarteiraCriada(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
            chave_privada=row["chave_privada"],
        )

    def buscar_por_endereco(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )

    def listar(self) -> List[Carteira]:
        rows = self.carteira_repo.listar()
        return [
            Carteira(
                endereco_carteira=r["endereco_carteira"],
                data_criacao=r["data_criacao"],
                status=r["status"],
            )
            for r in rows
        ]

    def bloquear(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.atualizar_status(endereco_carteira, "BLOQUEADA")
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )

    # ------------------------------------------------------
    # ADIÇÕES — APENAS O NECESSÁRIO
    # ------------------------------------------------------

    def obter_saldos(self, endereco: str):
        carteira = self.carteira_repo.buscar_por_endereco(endereco)
        if not carteira:
            raise ValueError("Carteira não encontrada")

        saldos = self.carteira_repo.listar_saldos(endereco)
        return {
            "endereco": endereco,
            "saldos": saldos
        }

    def realizar_deposito(self, endereco_carteira: str, req: DepositoRequest):
        return self.carteira_repo.depositar(
            endereco_carteira,
            req.id_moeda,
            req.valor,
            req.chave_privada
        )

    def realizar_saque(self, endereco_carteira: str, req: SaqueRequest):
        return self.carteira_repo.sacar(
            endereco_carteira,
            req.id_moeda,
            req.valor, 
            req.chave_privada
        )

    def realizar_conversao(self, endereco_carteira: str, req: ConversaoRequest):
        """
        Converte uma moeda para outra.
        """
        return self.carteira_repo.converter(
            endereco_carteira,
            req.id_moeda_origem,
            req.id_moeda_destino,
            req.valor_origem
        )

    def realizar_transferencia(self, endereco_origem: str, req: TransferenciaRequest):
        """
        Transfere saldo entre carteiras.
        """
        return self.carteira_repo.transferir(
            endereco_origem,
            req.endereco_destino,
            req.moeda,
            req.valor
        )
        
    def realizar_transferencia(self, endereco_origem: str, req: TransferenciaRequest):
        return self.carteira_repo.transferir(
            endereco_origem,
            req.endereco_destino,
            req.id_moeda,
            req.valor,
            req.chave_privada
        )
