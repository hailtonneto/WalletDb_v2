from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Saldo(BaseModel):
    moeda: str
    quantidade: float

class OperacaoValor(BaseModel):
    valor: float
    moeda: str

class Conversao(BaseModel):
    moeda_origem: str
    moeda_destino: str
    valor: float

class Transferencia(BaseModel):
    destino: str
    valor: float
    moeda: str

class Carteira(BaseModel):
    endereco: str
    data_criacao: datetime
    status: str

class CarteiraCriada(BaseModel):
    endereco: str
    chave_privada: str
