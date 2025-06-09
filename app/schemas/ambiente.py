from typing import Optional
from pydantic import BaseModel, Field


class AmbientBase(BaseModel):
    nombre_ambiente: str = Field(min_length=6, max_length=12)
    num_max_aprendices: int
    municipio: str = Field(min_length=3, max_length=50)
    ubicacion: str = Field(min_length=3, max_length=100)
    cod_centro: int
    estado: bool

class AmbientUpdate(BaseModel):
    nombre_ambiente: Optional[str] = Field(default=None, min_length=6, max_length=12)
    num_max_aprendices: Optional[int] = Field(default=None)
    municipio: Optional[str] = Field(default=None, min_length=3, max_length=50)
    ubicacion: Optional[str] = Field(default=None, min_length=3, max_length=100)
    cod_centro: Optional[int] = Field(default=None)
    estado: Optional[bool] = None

class AmbientCreate(AmbientBase):
    id_ambiente: int