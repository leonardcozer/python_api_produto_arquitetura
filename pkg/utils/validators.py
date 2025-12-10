"""Validadores utilitários para a aplicação"""

import re


def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF (Cadastro de Pessoas Físicas)
    
    Args:
        cpf: String contendo o CPF (com ou sem formatação)
    
    Returns:
        True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 > 9 else digito1
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 > 9 else digito2
    
    return cpf[9] == str(digito1) and cpf[10] == str(digito2)


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF para o padrão XXX.XXX.XXX-XX
    
    Args:
        cpf: String contendo o CPF (com ou sem formatação)
    
    Returns:
        CPF formatado
    """
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        raise ValueError("CPF deve conter 11 dígitos")
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def validar_email(email: str) -> bool:
    """
    Valida um endereço de email
    
    Args:
        email: String contendo o email
    
    Returns:
        True se o email é válido, False caso contrário
    """
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None


def validar_telefone(telefone: str) -> bool:
    """
    Valida um número de telefone brasileiro
    
    Args:
        telefone: String contendo o telefone
    
    Returns:
        True se o telefone é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    telefone = re.sub(r'\D', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (com ou sem 9° dígito)
    return len(telefone) in [10, 11]


def formatar_telefone(telefone: str) -> str:
    """
    Formata um telefone para o padrão (XX) XXXXX-XXXX
    
    Args:
        telefone: String contendo o telefone
    
    Returns:
        Telefone formatado
    """
    telefone = re.sub(r'\D', '', telefone)
    
    if len(telefone) == 10:
        return f"({telefone[0:2]}) {telefone[2:6]}-{telefone[6:10]}"
    elif len(telefone) == 11:
        return f"({telefone[0:2]}) {telefone[2:7]}-{telefone[7:11]}"
    else:
        raise ValueError("Telefone deve conter 10 ou 11 dígitos")


def formatar_moeda(valor: float) -> str:
    """
    Formata um valor para o padrão de moeda brasileira
    
    Args:
        valor: Valor a formatar
    
    Returns:
        Valor formatado em reais
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar_string(texto: str) -> str:
    """
    Normaliza uma string removendo espaços em branco extras
    
    Args:
        texto: String a normalizar
    
    Returns:
        String normalizada
    """
    return " ".join(texto.split())


def slug(texto: str) -> str:
    """
    Converte uma string em slug (URL-safe)
    
    Args:
        texto: String a converter
    
    Returns:
        Slug gerado
    """
    texto = normalizar_string(texto).lower()
    # Remove acentos (simplificado)
    acentos = 'áàâãäéèêëíìîïóòôõöúùûüçñ'
    sem_acentos = 'aaaaaaeeeeiiiiooooouuuucn'
    traduzir = str.maketrans(acentos, sem_acentos)
    texto = texto.translate(traduzir)
    # Remove caracteres especiais
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    # Remove hífens no início e final
    return texto.strip('-')
