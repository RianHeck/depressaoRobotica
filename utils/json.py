import json
import os

async def create_jsonDir():
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'json')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

async def load_json(filename):
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
    novo = await load_json(filename)
    novo.append(content)
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(novo, outF, ensure_ascii=True, indent=4)


async def delete_item(filename, item):
    content = await load_json(filename)
    if item in content:
        content.remove(item)
    else:
        return -1
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(content, outF, ensure_ascii=True, indent=4)