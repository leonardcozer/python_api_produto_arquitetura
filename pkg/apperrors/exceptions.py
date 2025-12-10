"""
Exceções personalizadas da aplicação
"""


class AppError(Exception):
    """Classe base para erros da aplicação"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """Erro quando um recurso não é encontrado"""
    
    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status_code=404)


class BadRequestError(AppError):
    """Erro quando a requisição é inválida"""
    
    def __init__(self, message: str = "Requisição inválida"):
        super().__init__(message, status_code=400)


class UnauthorizedError(AppError):
    """Erro quando a autenticação falha"""
    
    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppError):
    """Erro quando o acesso é negado"""
    
    def __init__(self, message: str = "Acesso negado"):
        super().__init__(message, status_code=403)


class ConflictError(AppError):
    """Erro quando há conflito (ex: recurso duplicado)"""
    
    def __init__(self, message: str = "Conflito"):
        super().__init__(message, status_code=409)


class InternalServerError(AppError):
    """Erro interno do servidor"""
    
    def __init__(self, message: str = "Erro interno do servidor"):
        super().__init__(message, status_code=500)
