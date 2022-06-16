import json
import os

async def create_jsonDir():
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'json')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

async def load_json(filename):
    """Carrega um json

    Args:
        filename: Caminho para o arquivo a ser carregado
    
    Returns:
        [list]: O conteúdo do arquivo, retorna uma lista vazia se o arquivo não existe
    """
    try:
        # await create_jsonDir()
        with open(filename, encoding='utf-8') as inF:
            arquivo = json.load(inF)
            return arquivo
    except ValueError:
        return []
    except FileNotFoundError:
        open(filename, 'w', encoding='utf-8')
        return []
        
async def write_json(filename, content):
    """Escreve em um json

    Args:
        filename: Caminho para o arquivo a ser escrito
        content: O conteudo a ser adicionado ao fim do arquivo
    
    Returns:
        [None]: Nada
    """
    novo = await load_json(filename)
    novo.append(content)
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(novo, outF, ensure_ascii=True, indent=4)


async def delete_item(filename, content):
    """Deleta um elemento de um json

    Args:
        filename: Caminho para o arquivo a ser alterado
        content: O conteúdo a ser removido
    
    Returns:
        [None|-1]: Nada normalmente, -1 se o conteúdo não estiver no arquivo
    """
    content = await load_json(filename)
    if content in content:
        content.remove(content)
    else:
        return -1
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(content, outF, ensure_ascii=True, indent=4)