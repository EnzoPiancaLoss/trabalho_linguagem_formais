import re

# 1. Tabela de Especificação dos Tokens (SpreadScript)
TOKEN_SPEC = [
    ('TOKEN_PREFIX',     r'='),
    ('TOKEN_SEMI',       r';'),
    ('TOKEN_CELL_REF',   r'[A-Z]+[0-9]+'),
    ('TOKEN_NUM',        r'\d+(\.\d+)?'),
    ('TOKEN_OP_MUL_DIV', r'[\*/\%]'),
    ('TOKEN_OP_ADD_SUB', r'[\+\-]'),
    ('TOKEN_LPAREN',     r'\('),
    ('TOKEN_RPAREN',     r'\)'),
    ('TOKEN_SKIP',       r'[ \t\n]+'),
    ('TOKEN_UNKNOWN',    r'.'),
]

def cell_ref_to_indices(ref):
    """
    Converte referências de células da planilha (ex: "A1", "B2", "AA10")
    em coordenadas matriciais [linha][coluna] de uma matriz 2D 0-indexed.
    """
    match = re.match(r"^([A-Z]+)([0-9]+)$", ref)
    if not match:
        return None
    
    col_str, row_str = match.groups()
    
    col_index = 0
    for char in col_str:
        col_index = col_index * 26 + (ord(char) - ord('A') + 1)
    col_index -= 1
    
    row_index = int(row_str) - 1
    
    return {"row": row_index, "col": col_index}

def scanner_spreadscript(input_code):
    """
    Analisador Léxico (Scanner) para a linguagem SpreadScript
    """
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPEC)
    tokens = []
    
    for match in re.finditer(tok_regex, input_code):
        kind = match.lastgroup
        value = match.group()
        
        if kind == 'TOKEN_SKIP':
            continue
        elif kind == 'TOKEN_UNKNOWN':
            tokens.append({'type': kind, 'lexeme': value, 'error': True})
        else:
            token_data = {'type': kind, 'lexeme': value}
            if kind == 'TOKEN_CELL_REF':
                token_data['coords'] = cell_ref_to_indices(value)
            tokens.append(token_data)
            
    return tokens

def avaliador_spreadscript(tokens, planilha):
    """
    Valida a sintaxe e avalia o resultado final da instrução SpreadScript.
    """
    if not tokens:
        print("[ERRO SINTÁTICO] Instrução vazia.")
        return None

    # 1. Validação de Prefixo '='
    if tokens[0]['type'] != 'TOKEN_PREFIX':
        print("[ERRO SINTÁTICO] A instrução deve começar obrigatoriamente com '='.")
        return None

    # 2. Validação de Delimitador ';'
    if tokens[-1]['type'] != 'TOKEN_SEMI':
        print("[ERRO SINTÁTICO] A instrução deve ser encerrada obrigatoriamente com ';'.")
        return None

    expressao_str = ""
    corpo_tokens = tokens[1:-1]
    
    if not corpo_tokens:
        print("[ERRO SINTÁTICO] Corpo da expressão vazio.")
        return None

    for tok in corpo_tokens:
        if tok.get('error'):
            print(f"[ERRO LÉXICO] Caractere inválido '{tok['lexeme']}' encontrado.")
            return None
        
        if tok['type'] == 'TOKEN_CELL_REF':
            r = tok['coords']['row']
            c = tok['coords']['col']
            
            if r < 0 or r >= len(planilha) or c < 0 or c >= len(planilha[0]):
                print(f"[ERRO SEMÂNTICO] Célula {tok['lexeme']} fora dos limites da planilha.")
                return None
            
            valor = planilha[r][c]
            expressao_str += str(valor)
        else:
            expressao_str += tok['lexeme']
            
    try:
        resultado = eval(expressao_str)
        return resultado
    except Exception as e:
        print(f"[ERRO SINTÁTICO / EXECUÇÃO] Expressão inválida '{expressao_str}': {e}")
        return None


# ==========================================
# Planilha para Teste (4x3)
# ==========================================
spreadsheet = [
    [10,  20, 30], # Linha 0 (A1=10, B1=20, C1=30)
    [5,   15, 25], # Linha 1 (A2=5,  B2=15, C2=25)
    [100, 2,  4],  # Linha 2 (A3=100, B3=2, C3=4)
    [110, 45, 65]  # Linha 3 (A4=110, B4=45, C4=65)
]


# ==========================================
# Execução
# ==========================================

# 1. Caso Válido
c1 = "= A1 * 3;"
t1 = scanner_spreadscript(c1)
res1 = avaliador_spreadscript(t1, spreadsheet)
print(f"Entrada: '{c1}' -> Resultado: {res1}\n")
