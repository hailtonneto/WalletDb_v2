from typing import Literal, List
from datetime import datetime
from pydantic import BaseModel, Field

class Carteira(BaseModel):
    endereco_carteira: str
    data_criacao: datetime
    status: Literal["ATIVA", "BLOQUEADA"] 

class CarteiraCriada(Carteira):
    chave_privada: str # Campo adicional que só é retornado na criação

class Saldo(BaseModel):
    saldo: float
    moeda_codigo: str
    moeda_nome: str

class SaldosCarteira(BaseModel):
    endereco: str
    saldos: List[Saldo]