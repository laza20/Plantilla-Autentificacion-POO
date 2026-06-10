from sqlmodel import Session, select, update
from sqlalchemy.exc import IntegrityError
from src.auth.models import AuthUser
from fastapi import HTTPException, status
from src.database.enums.estado_entidad import EstadoEntidad

def insertar_y_retornar_registro(session:Session, objeto:AuthUser)-> AuthUser:
    """
    Función para insertar un registro en la base de datos y retornar el objeto actualizado.
    """
    try:
        session.add(objeto)
        session.commit()
        session.refresh(objeto)
        return objeto
    
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: Uno o más registros ya existen o violan restricciones."
        )

def obtener_user_por_id_sin_activar(session: Session, id_usuario: int) -> AuthUser:
    """
    Función para obtener un usuario por su ID.
    """
    statement = select(AuthUser).where(AuthUser.id_usuario == id_usuario)
    resultado = session.exec(statement).first()
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return resultado

def activar_usuario(session: Session, usuario: AuthUser) -> AuthUser:
    """
    Función para activar un usuario con update directo y sincronización.
    """
    statement = (
        update(AuthUser)
        .where(AuthUser.id_usuario == usuario.id_usuario)
        .values(estado=EstadoEntidad.ACTIVO, is_verified=True)
    )
    session.exec(statement) 
    session.commit()
    
    session.refresh(usuario) 
    
    return usuario


def buscar_y_retornar_user_por_mail_username(session: Session, mail_username: str) -> AuthUser:
    """
    Función para buscar un usuario por su correo electrónico o nombre de usuario.
    """
    statement = select(AuthUser).where(
        (AuthUser.email == mail_username and AuthUser.estado == EstadoEntidad.ACTIVO)
    )
    resultado = session.exec(statement).first()
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return resultado