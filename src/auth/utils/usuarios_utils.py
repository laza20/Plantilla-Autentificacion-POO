from typing import List, Dict
from src.auth.models import AuthUser, AuthUserNoImage, UsuarioLogeado, UserRegisterDTO
from pydantic import ValidationError
from src.exceptions.domain import LongitudExcedida, ContraseñaNoSegura
import re


class UserMapper:
    def __init__(
        self
    ):
        pass

    def orquestador_carga(self, usuario:UserRegisterDTO)->AuthUser:
        objeto_usuario = self.normalizar_registro_a_cargar(usuario)
        verificacion_pass = self.validar_contraseña(objeto_usuario.password)
        if not verificacion_pass:
            raise ContraseñaNoSegura()
        
        return objeto_usuario


    def normalizar_registro_a_cargar(self, usuario: UserRegisterDTO) -> AuthUser:
        """
        Funcion encargada de normalizar los datos del usuario antes de ser insertados en la base de datos.
        - Datos limpios debe utilizarse para los datos str con una longitud maxima definida.
        - Valida que la imagen no exceda el tamaño máximo permitido.
        """
        try:

            datos_limpios = {"email": usuario.email.strip().lower(),
                             "password":usuario.password}
            usuario_orm = AuthUser(**datos_limpios)
            
            return usuario_orm

        except ValidationError as e:
            error_detalle = e.errors()[0]
            campo_afectado = error_detalle.get("loc", ["campo"])[0]
            
            if error_detalle.get("type") == "string_too_long":
                raise LongitudExcedida(
                    message=f"El campo '{campo_afectado}' excede el tamaño máximo permitido."
                )
            raise e


    def validar_contraseña(self, contraseña: str) -> bool:
        """
        Valida que la contraseña cumpla con los requisitos de seguridad.
        Requisitos:
        - Al menos 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        
        if len(contraseña) < 8:
            return False
        if not re.search(r'[A-Z]', contraseña):
            return False
        if not re.search(r'[a-z]', contraseña):
            return False
        if not re.search(r'[0-9]', contraseña):
            return False
        if not re.search(r'[^a-zA-Z0-9]', contraseña):
            return False
        
        return True


    def retornar_usuario_publico(self, usuario:AuthUser)-> UsuarioLogeado:
        return UsuarioLogeado(
            email= usuario.email,
            imagen_url= usuario.imagen_url
        )


def get_user_mapper() -> UserMapper:
    return UserMapper()