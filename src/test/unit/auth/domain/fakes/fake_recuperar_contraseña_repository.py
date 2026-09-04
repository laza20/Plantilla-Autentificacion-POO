from src.auth.infrastructure.persistence.postgres.models.models_recover_password import RecoverPassword
from datetime import datetime

class FakeRecuperarContraseñaRepository:
    def __init__(self):
        self._tokens_eliminados = []
        self.tokens: dict[str, RecoverPassword] = {}
        self.fue_llamado: bool = False
        self.token_hash : str = ""
        self._next_recover_id= 1
        self.forzar_fallo_insercion = False

    def invalidar_tokens_anteriores(self, id_usuario: int) -> bool:
        self.fue_llamado = True

        tokens_a_invalidar = [
            token
            for token in self.tokens.values()
            if token.id_usuario == id_usuario and token.usado != True
        ]

        for token in tokens_a_invalidar:
            token.usado = True
            self._tokens_eliminados.append(token)


        return bool(tokens_a_invalidar)


    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str,
            expira_en:datetime )->bool:

        if self.forzar_fallo_insercion:
            return False

        recover_password = RecoverPassword(
            id_usuario=id_usuario,
            token_hash=token_hash,
            expira_en=expira_en
        )

        recover_password.id_recover_password = self._next_recover_id
        copia_recuperacion_contraseña = recover_password.model_copy()
        self.tokens[token_hash] = copia_recuperacion_contraseña
        self._next_recover_id += 1
        self.fue_llamado = True
        self.token_hash = token_hash
        return True

    def verificar_token(
            self,
            tiempo_actual:datetime,
            token_hash:str)->RecoverPassword | bool:

        token_retorno = None

        for token in self.tokens.values():
            if token_hash == token.token_hash and token.usado != True:
                token_retorno = token.model_copy()
                break

        if not token_retorno:
            return False

        if token_retorno.expira_en <= tiempo_actual:
            return False

        return token_retorno

    def desactivar_token_utilizado(self, id_usuario: int)->bool:
        resultado = self.invalidar_tokens_anteriores(id_usuario=id_usuario)
        return resultado