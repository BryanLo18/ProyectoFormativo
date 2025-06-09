import logging
from sqlalchemy import text
from fastapi import logger
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.ambiente import AmbientCreate, AmbientUpdate 


logger = logging.getLogger(__name__)

def create_ambiente(db: Session, ambiente: AmbientCreate) -> Optional[bool]:
    try:
       
        query = text("""
            INSERT INTO ambiente_formacion (
                nombre_ambiente, num_max_aprendices,
                municipio, ubicacion, cod_centro, estado
            ) VALUES (
                :nombre_ambiente, :num_max_aprendices,
                :municipio, :ubicacion, :cod_centro, :estado
            )
        """)
        db.execute(query)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear ambiente: {e}")
        raise Exception("Error de base de datos al crear el ambiente")



def get_ambiente_by_id(db: Session, id_ambiente: int):
    try:
        query = text(""" SELECT  id_ambiente,nombre_ambiente, num_max_aprendices,
                    municipio, ubicacion, cod_centro, estado
                     FROM ambiente_formacion 
                     WHERE id_ambiente = :id_ambiente """)
        result = db.execute(query, {"id_ambiente": id_ambiente}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por id: {e}")
        raise Exception("Error de base de datos al obtener el usuario")
    

def modify_status_ambiente(db: Session, id_ambiente: int):
    try:
        query = text( """
                     UPDATE ambiente_formacion SET estado = IF(estado, FALSE, TRUE)
                     WHERE id_ambiente = :id_ambiente
                    """ )
        db.execute(query, {"id_ambiente": id_ambiente})
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al modificar el estado del ambiente: {e}")
        raise Exception("Error de base de datos al modificar estado del ambiente")


def update_ambiente(db: Session, id_ambiente: int, ambiente_update: AmbientUpdate) -> bool:
    try:
        fields = ambiente_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["id_ambiente"] = id_ambiente

        query = text(f"UPDATE ambiente_formacion SET {set_clause} WHERE id_ambiente = :id_ambiente")
        db.execute(query, fields)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar ambiente: {e}")
        raise Exception("Error de base de datos al actualizar el ambiente")


def get_ambientes_activos_by_centro(db: Session, cod_centro: int):
    try:
        query = text("""
            SELECT id_ambiente, nombre_ambiente, num_max_aprendices,
                   municipio, ubicacion, cod_centro, estado
            FROM ambiente_formacion
            WHERE cod_centro = :cod_centro AND estado = TRUE
        """)
        result = db.execute(query, {"cod_centro": cod_centro}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ambientes activos por centro: {e}")
        raise Exception("Error de base de datos al obtener los ambientes")