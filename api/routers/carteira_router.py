from fastapi import APIRouter, HTTPException, Depends
from typing import List

from api.services.carteira_service import CarteiraService
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import Carteira, CarteiraCriada


router = APIRouter(prefix="/carteiras", tags=["carteiras"])


def get_carteira_service() -> CarteiraService:
    repo = CarteiraRepository()
    return CarteiraService(repo)


@router.post("", response_model=CarteiraCriada, status_code=201)
def criar_carteira(
    service: CarteiraService = Depends(get_carteira_service),
)->CarteiraCriada:
    """
    Cria uma nova carteira. O body é opcional .
    Retorna endereço e chave privada (apenas nesta resposta).
    """
    try:
        return service.criar_carteira()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Carteira])
def listar_carteiras(service: CarteiraService = Depends(get_carteira_service)):
    return service.listar()


@router.get("/{endereco_carteira}/saldos")
def listar_saldos(
    endereco_carteira: str,
    service: CarteiraService = Depends(get_carteira_service)
):
    try:
        return service.listar_saldos(endereco_carteira)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{endereco_carteira}/depositos")
def depositar(
    endereco_carteira: str,
    dados: OperacaoValor,
    service: CarteiraService = Depends(get_carteira_service)
):
    return service.depositar(endereco_carteira, dados.valor, dados.moeda)


@router.post("/{endereco_carteira}/saques")
def sacar(
    endereco_carteira: str,
    dados: OperacaoValor,
    service: CarteiraService = Depends(get_carteira_service)
):
    return service.sacar(endereco_carteira, dados.valor, dados.moeda)


@router.post("/{endereco_carteira}/conversoes")
def converter(
    endereco_carteira: str,
    dados: Conversao,
    service: CarteiraService = Depends(get_carteira_service)
):
    return service.converter(
        endereco_carteira,
        dados.moeda_origem,
        dados.moeda_destino,
        dados.valor,
    )


@router.post("/{endereco_origem}/transferencias")
def transferir(
    endereco_origem: str,
    dados: Transferencia,
    service: CarteiraService = Depends(get_carteira_service)
):
    return service.transferir(
        endereco_origem,
        dados.destino,
        dados.valor,
        dados.moeda,
    )
