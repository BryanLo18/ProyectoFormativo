from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ambiente import AmbientCreate, AmbientUpdate
from app.schemas.users import UserOut
from core.database import get_db
from core.dependencies import get_current_user
from app.crud import ambiente as crud_ambiente
from sqlalchemy.exc import SQLAlchemyError
from typing import List



router = APIRouter()

@router.post("/create/ambiente", status_code=status.HTTP_201_CREATED)
def create_ambient(
    ambiente: AmbientCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)  # Dependencia para obtener el usuario actual autenticado
):
    """
        Debes usar id_rol que exista por ahora tenemos 1 superadmin, 2 admin y 3 instructor
    """
    if current_user.id_rol == 2:
        if current_user.id_rol == 1 or current_user.id_rol == 2:
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

    if current_user.id_rol == 3:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    try:
        ambiente_validate = crud_ambiente.get_ambiente_by_cod_centro(db, ambiente.cod_centro)
        # Verificar si el ambiente ya existe por cod_centro
        if ambiente_validate:
            raise HTTPException(status_code=400, detail="Ambiente ya registrado")

        crud_ambiente.create_ambiente(db, ambiente)
        return {"message": "Ambiente creado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-ambiente-by-id", response_model=AmbientCreate)
def get_ambiente_by_id(id_ambiente: int, db: Session = Depends(get_db)):
    try:
        user = crud_ambiente.get_ambiente_by_id(db, id_ambiente)
        if not user:
            raise HTTPException(status_code=404, detail="Ambiente no encontrado")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/update/{id_ambiente}")
def update_ambiente(
    id_ambiente: int, 
    ambiente: AmbientUpdate, 
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user) 
):  
    # Verificar permisos según el rol del usuario actual
    if current_user.id_usuario != 1:  # Si no es superadmin (id=1)
        if current_user.id_rol == 3:  # Si es instructor
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        if current_user.id_rol == 2:  # Si es admin
            ambiente_actual = crud_ambiente.get_ambiente_by_id(db, id_ambiente)
            if not ambiente_actual:
                raise HTTPException(status_code=404, detail="Ambiente no encontrado")
            if ambiente_actual.cod_centro != current_user.cod_centro:
                raise HTTPException(status_code=401, detail="No autorizado para modificar ambientes de otros centros")
                    
    try:
        # Verificar si el ambiente existe
        ambiente_actual = crud_ambiente.get_ambiente_by_id(db, id_ambiente)
        if not ambiente_actual:
            raise HTTPException(status_code=404, detail="Ambiente no encontrado")
        
        # Si se está actualizando el código del centro, verificar que no exista ya
        if ambiente.cod_centro is not None and ambiente.cod_centro != ambiente_actual.cod_centro:
            ambiente_existente = crud_ambiente.get_ambiente_by_cod_centro(db, ambiente.cod_centro)
            if ambiente_existente:
                raise HTTPException(status_code=400, detail="Ya existe un ambiente con ese código de centro")
        
        # Actualizar el ambiente
        success = crud_ambiente.update_ambiente(db, id_ambiente, ambiente)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el ambiente")
            
        return {"message": "Ambiente actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/modify-status/{id_ambiente}")
def modify_status_ambiente(
    id_ambiente: int, 
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
    ):
    
    if current_user.id_rol == 2:
        if current_user.id_rol == 1 or current_user.id_rol == 2:
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

    if current_user.id_rol == 3:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")
    
    try:
        ambiente_validate = crud_ambiente.get_ambiente_by_id(db, id_ambiente)
        if not ambiente_validate:
            raise HTTPException(status_code=404, detail="Ambiente no encontrado")

        crud_ambiente.modify_status_ambiente(db, id_ambiente)
            
        return {"message": "Ambiente actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/ambientes-activos/{cod_centro}", response_model=List[AmbientCreate])
def get_ambientes_activos_by_centro(
    cod_centro: int,
    db: Session = Depends(get_db)
):
    try:
        ambientes = crud_ambiente.get_ambientes_activos_by_centro(db, cod_centro)
        if not ambientes:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron ambientes activos para este centro"
            )
        return ambientes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))