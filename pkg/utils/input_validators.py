"""
Validadores e sanitizadores de input para prevenir SQL injection e outros ataques
"""
import re
import logging
from typing import Optional
from pkg.apperrors.exceptions import BadRequestError

logger = logging.getLogger(__name__)

# Caracteres perigosos que devem ser removidos ou escapados
DANGEROUS_CHARS = [
    ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute',
    'union', 'select', 'insert', 'update', 'delete', 'drop',
    'create', 'alter', 'truncate', 'script', '<', '>'
]

# Tamanhos máximos permitidos
MAX_SEARCH_TERM_LENGTH = 100
MAX_CATEGORY_LENGTH = 50
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1
MAX_PAGE_NUMBER = 10000


def sanitize_search_term(term: str, max_length: int = MAX_SEARCH_TERM_LENGTH) -> str:
    """
    Sanitiza um termo de busca removendo caracteres perigosos
    
    Args:
        term: Termo de busca a ser sanitizado
        max_length: Tamanho máximo permitido
    
    Returns:
        str: Termo sanitizado
    
    Raises:
        BadRequestError: Se o termo for inválido ou muito longo
    """
    if not term or not isinstance(term, str):
        raise BadRequestError("Termo de busca inválido")
    
    # Remove espaços em branco no início e fim
    term = term.strip()
    
    if len(term) < 2:
        raise BadRequestError("Termo de busca deve ter pelo menos 2 caracteres")
    
    if len(term) > max_length:
        raise BadRequestError(f"Termo de busca muito longo (máximo {max_length} caracteres)")
    
    # Remove caracteres de controle
    term = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', term)
    
    # Verifica se contém caracteres perigosos (case insensitive)
    term_lower = term.lower()
    for dangerous in DANGEROUS_CHARS:
        if dangerous in term_lower:
            logger.warning(f"Tentativa de usar caractere perigoso em busca: {dangerous}")
            raise BadRequestError("Termo de busca contém caracteres inválidos")
    
    # Remove múltiplos espaços
    term = re.sub(r'\s+', ' ', term)
    
    return term


def sanitize_category(category: str, max_length: int = MAX_CATEGORY_LENGTH) -> str:
    """
    Sanitiza uma categoria
    
    Args:
        category: Categoria a ser sanitizada
        max_length: Tamanho máximo permitido
    
    Returns:
        str: Categoria sanitizada
    
    Raises:
        BadRequestError: Se a categoria for inválida
    """
    if not category or not isinstance(category, str):
        raise BadRequestError("Categoria inválida")
    
    category = category.strip()
    
    if len(category) == 0:
        raise BadRequestError("Categoria não pode ser vazia")
    
    if len(category) > max_length:
        raise BadRequestError(f"Categoria muito longa (máximo {max_length} caracteres)")
    
    # Remove caracteres de controle
    category = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', category)
    
    # Remove caracteres especiais perigosos
    category = re.sub(r'[<>;]', '', category)
    
    return category


def validate_page_params(page: int, page_size: int) -> tuple[int, int]:
    """
    Valida e normaliza parâmetros de paginação
    
    Args:
        page: Número da página
        page_size: Tamanho da página
    
    Returns:
        tuple: (page, page_size) validados
    
    Raises:
        BadRequestError: Se os parâmetros forem inválidos
    """
    if not isinstance(page, int) or page < 1:
        raise BadRequestError("Número da página deve ser um inteiro positivo")
    
    if page > MAX_PAGE_NUMBER:
        raise BadRequestError(f"Número da página muito grande (máximo {MAX_PAGE_NUMBER})")
    
    if not isinstance(page_size, int) or page_size < MIN_PAGE_SIZE:
        raise BadRequestError(f"Tamanho da página deve ser pelo menos {MIN_PAGE_SIZE}")
    
    if page_size > MAX_PAGE_SIZE:
        raise BadRequestError(f"Tamanho da página muito grande (máximo {MAX_PAGE_SIZE})")
    
    return page, page_size


def validate_id(id_value: int, field_name: str = "ID") -> int:
    """
    Valida um ID
    
    Args:
        id_value: Valor do ID
        field_name: Nome do campo para mensagem de erro
    
    Returns:
        int: ID validado
    
    Raises:
        BadRequestError: Se o ID for inválido
    """
    if not isinstance(id_value, int):
        raise BadRequestError(f"{field_name} deve ser um número inteiro")
    
    if id_value < 1:
        raise BadRequestError(f"{field_name} deve ser um número positivo")
    
    # Limite razoável para IDs (evita overflow)
    if id_value > 2**31 - 1:
        raise BadRequestError(f"{field_name} muito grande")
    
    return id_value


def sanitize_string(value: str, max_length: Optional[int] = None, allow_empty: bool = False) -> str:
    """
    Sanitiza uma string genérica
    
    Args:
        value: String a ser sanitizada
        max_length: Tamanho máximo (opcional)
        allow_empty: Se permite string vazia
    
    Returns:
        str: String sanitizada
    
    Raises:
        BadRequestError: Se a string for inválida
    """
    if not isinstance(value, str):
        raise BadRequestError("Valor deve ser uma string")
    
    value = value.strip()
    
    if not allow_empty and len(value) == 0:
        raise BadRequestError("String não pode ser vazia")
    
    if max_length and len(value) > max_length:
        raise BadRequestError(f"String muito longa (máximo {max_length} caracteres)")
    
    # Remove caracteres de controle
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    return value

