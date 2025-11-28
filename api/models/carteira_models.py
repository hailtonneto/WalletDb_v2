from typing import Literal, List
from datetime import datetime
from pydantic import BaseModel

class Carteira(BaseModel):
    endereco_carteira: str
    data_criacao: datetime
    status: Literal["ATIVA", "BLOQUEADA"] 

class CarteiraCriada(Carteira):
    chave_privada: str

class Saldo(BaseModel):
    saldo: float
    moeda_codigo: str
    moeda_nome: str

class SaldosCarteira(BaseModel):
    endereco: str
    saldos: List[Saldo]

class DepositoRequest(BaseModel):
    id_moeda: int
    valor: float
    chave_privada: str

class SaqueRequest(BaseModel):
    id_moeda: int
    valor: float
    chave_privada: str

class ConversaoRequest(BaseModel):
    id_moeda_origem: int
    id_moeda_destino: int
    valor_origem: float

class TransferenciaRequest(BaseModel):
    endereco_destino: str
    id_moeda: int
    valor: float
    chave_privada: str