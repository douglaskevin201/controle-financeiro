from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.pocket import Pocket, PocketTransaction
from backend.app.schemas.pocket import (
    PocketCreate,
    PocketUpdate,
    PocketResponse,
    PocketTransferRequest,
    PocketTransactionResponse
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/pockets", tags=["Caixinhas"])

def build_pocket_response(pocket: Pocket) -> PocketResponse:
    progress = None
    if pocket.target_amount and pocket.target_amount > 0:
        progress = round(min(100.0, (pocket.current_amount / pocket.target_amount) * 100), 1)
    
    return PocketResponse(
        id=pocket.id,
        user_id=pocket.user_id,
        name=pocket.name,
        target_amount=pocket.target_amount,
        current_amount=round(pocket.current_amount, 2),
        color=pocket.color,
        icon=pocket.icon,
        progress_percentage=progress,
        created_at=pocket.created_at
    )

@router.get("", response_model=List[PocketResponse])
def list_pockets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pockets = db.query(Pocket).filter(Pocket.user_id == current_user.id).order_by(Pocket.id.asc()).all()
    return [build_pocket_response(p) for p in pockets]

@router.post("", response_model=PocketResponse, status_code=status.HTTP_201_CREATED)
def create_pocket(
    pocket_in: PocketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_pocket = Pocket(
        user_id=current_user.id,
        name=pocket_in.name.strip(),
        target_amount=pocket_in.target_amount,
        current_amount=0.0,
        color=pocket_in.color or "#10B981",
        icon=pocket_in.icon or "piggy-bank"
    )
    db.add(new_pocket)
    db.flush()

    if pocket_in.initial_deposit and pocket_in.initial_deposit > 0:
        new_pocket.current_amount = pocket_in.initial_deposit
        ptx = PocketTransaction(
            pocket_id=new_pocket.id,
            user_id=current_user.id,
            type="deposit",
            amount=pocket_in.initial_deposit,
            description="Depósito Inicial",
            transaction_date=date.today()
        )
        db.add(ptx)

    db.commit()
    db.refresh(new_pocket)
    return build_pocket_response(new_pocket)

@router.get("/{pocket_id}", response_model=PocketResponse)
def get_pocket(
    pocket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pocket = db.query(Pocket).with_for_update().filter(
        Pocket.id == pocket_id,
        Pocket.user_id == current_user.id
    ).first()
    if not pocket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixinha não encontrada.")
    return build_pocket_response(pocket)

@router.post("/{pocket_id}/transfer", response_model=PocketResponse)
def transfer_pocket_funds(
    pocket_id: int,
    transfer_in: PocketTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer funds into or out of a pocket.

    Uses optimistic locking (Pocket.version) with a small retry loop to handle concurrent updates.
    When running on Postgres, .with_for_update() will acquire a row lock; on SQLite it is ignored.
    """
    from sqlalchemy.exc import StaleDataError

    tx_date = transfer_in.transaction_date or date.today()
    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        try:
            # Try to acquire row lock when supported by the DB - harmless noop on SQLite
            pocket = db.query(Pocket).with_for_update().filter(
                Pocket.id == pocket_id,
                Pocket.user_id == current_user.id
            ).first()

            if not pocket:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixinha não encontrada.")

            if transfer_in.type == "deposit":
                pocket.current_amount += transfer_in.amount
                desc = transfer_in.description or f"Guardado na caixinha {pocket.name}"
            elif transfer_in.type == "withdraw":
                if pocket.current_amount < transfer_in.amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Saldo insuficiente na caixinha. Saldo atual: R$ {pocket.current_amount:.2f}"
                    )
                pocket.current_amount -= transfer_in.amount
                desc = transfer_in.description or f"Resgate da caixinha {pocket.name}"
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de transferência inválido.")

            ptx = PocketTransaction(
                pocket_id=pocket.id,
                user_id=current_user.id,
                type=transfer_in.type,
                amount=transfer_in.amount,
                description=desc,
                transaction_date=tx_date
            )
            db.add(ptx)
            # commit will attempt the update; if version changed concurrently, SQLAlchemy raises StaleDataError
            db.commit()
            db.refresh(pocket)
            return build_pocket_response(pocket)

        except StaleDataError:
            # Concurrent update detected: rollback and retry
            db.rollback()
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflito de concorrência ao atualizar a caixinha. Tente novamente.")
            # otherwise loop to retry

    # Should not reach here
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao processar transferência")

@router.get("/{pocket_id}/transactions", response_model=List[PocketTransactionResponse])
def list_pocket_transactions(
    pocket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pocket = db.query(Pocket).filter(
        Pocket.id == pocket_id,
        Pocket.user_id == current_user.id
    ).first()
    if not pocket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixinha não encontrada.")

    txs = db.query(PocketTransaction).filter(
        PocketTransaction.pocket_id == pocket_id,
        PocketTransaction.user_id == current_user.id
    ).order_by(PocketTransaction.transaction_date.desc(), PocketTransaction.id.desc()).all()

    return txs

@router.put("/{pocket_id}", response_model=PocketResponse)
def update_pocket(
    pocket_id: int,
    pocket_in: PocketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pocket = db.query(Pocket).filter(
        Pocket.id == pocket_id,
        Pocket.user_id == current_user.id
    ).first()
    if not pocket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixinha não encontrada.")

    if pocket_in.name is not None:
        pocket.name = pocket_in.name.strip()
    if pocket_in.target_amount is not None:
        pocket.target_amount = pocket_in.target_amount
    if pocket_in.color is not None:
        pocket.color = pocket_in.color
    if pocket_in.icon is not None:
        pocket.icon = pocket_in.icon

    db.commit()
    db.refresh(pocket)
    return build_pocket_response(pocket)

@router.delete("/{pocket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pocket(
    pocket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pocket = db.query(Pocket).filter(
        Pocket.id == pocket_id,
        Pocket.user_id == current_user.id
    ).first()
    if not pocket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixinha não encontrada.")

    db.delete(pocket)
    db.commit()
    return None

