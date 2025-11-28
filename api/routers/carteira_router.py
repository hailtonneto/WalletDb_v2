from fastapi import APIRouter, HTTPException, Depends
from typing import List

from api.services.carteira_service import CarteiraService
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import (
    Carteira,
    CarteiraCriada,
    DepositoRequest,
    SaqueRequest,
    ConversaoRequest,
    TransferenciaRequest,
    SaldosCarteira
)

router = APIRouter(prefix="/carteiras", tags=["carteiras"])


def get_carteira_service() -> CarteiraService:
    repo = CarteiraRepository()
    return CarteiraService(repo)


@router.post("", response_model=CarteiraCriada, status_code=201)
def criar_carteira(service: CarteiraService = Depends(get_carteira_service)) -> CarteiraCriada:
    try:
        return service.criar_carteira()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Carteira])
def listar_carteiras(service: CarteiraService = Depends(get_carteira_service)):
    return service.listar()


@router.get("/{endereco_carteira}", response_model=Carteira)
def buscar_carteira(
    endereco_carteira: str,
    service: CarteiraService = Depends(get_carteira_service),
):
    try:
        return service.buscar_por_endereco(endereco_carteira)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{endereco_carteira}", response_model=Carteira)
def bloquear_carteira(
    endereco_carteira: str,
    service: CarteiraService = Depends(get_carteira_service),
):
    try:
        return service.bloquear(endereco_carteira)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{endereco_carteira}/saldos", response_model=SaldosCarteira)
def listar_saldos(
    endereco_carteira: str,
    service: CarteiraService = Depends(get_carteira_service),
):
    try:
        return service.obter_saldos(endereco_carteira)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{endereco_carteira}/depositos")
def depositar(endereco_carteira: str, req: DepositoRequest, service: CarteiraService = Depends(get_carteira_service)):
    try:
        return service.realizar_deposito(endereco_carteira, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{endereco_carteira}/saques")
def sacar(endereco_carteira: str, req: SaqueRequest, service: CarteiraService = Depends(get_carteira_service)):
    try:
        return service.realizar_saque(endereco_carteira, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{endereco_carteira}/conversoes")
def converter(
    endereco_carteira: str,
    req: ConversaoRequest,
    service: CarteiraService = Depends(get_carteira_service),
):
    try:
        return service.realizar_conversao(endereco_carteira, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{endereco_origem}/transferencias")
def transferir(
    endereco_origem: str,
    req: TransferenciaRequest,
    service: CarteiraService = Depends(get_carteira_service),
):
    try:
        return service.realizar_transferencia(endereco_origem, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
