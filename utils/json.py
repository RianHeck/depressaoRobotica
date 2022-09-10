import json

def load_json(filename):
    """Carrega um json

    Args:
        filename: Caminho para o arquivo a ser carregado
    
    Returns:
        [list]: O conteúdo do arquivo, retorna uma lista vazia se o arquivo não existe
    """
    try:
        with open(filename, encoding='utf-8') as inF:
            arquivo = json.load(inF)
            return arquivo
    except ValueError:
        return []
    except FileNotFoundError:
        open(filename, 'w', encoding='utf-8')
        return []
        
def write_json(filename, content):
    """Escreve em um json

    Args:
        filename: Caminho para o arquivo a ser escrito
        content: O conteudo a ser adicionado ao fim do arquivo
    
    Returns:
        [None]: Nada
    """
    novo = load_json(filename)
    novo.append(content)
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(novo, outF, ensure_ascii=True, indent=4)


async def delete_item(filename, contentToDelete):
    """Deleta um elemento de um json

    Args:
        filename: Caminho para o arquivo a ser alterado
        content: O conteúdo a ser removido
    
    Returns:
        [None|-1]: Nada normalmente, -1 se o conteúdo não estiver no arquivo
    """
    content = load_json(filename)
    if contentToDelete in content:
        content.remove(contentToDelete)
    else:
        return -1
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(content, outF, ensure_ascii=True, indent=4)