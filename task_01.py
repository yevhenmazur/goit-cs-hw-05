'''
Скрипт, який читає всі файли у вказаній користувачем вихідній папці (source folder)
і розподіляє їх по підпапках у директорії призначення (output folder)
на основі розширення файлів. 
'''

import asyncio
import os
import sys
import logging
import argparse
import aioshutil
import aiofiles.os

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def parse_args():
    '''Функція парсить аргументи командного рядка і вертає Namespace із ними'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-s", "--source", type=str, default=".",
                        help="Шлях до директорії звідки копіювати")
    parser.add_argument("-o", "--output", type=str, default="out",
                        help="Шлях до директорії куди копіювати")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()


async def read_folder(src: str, dest: str):
    '''
    Функція приймає шляхи у файловій системі, обходить рекурсивно всі елементи
    за цим шляхом, і повертає список із повними шляхами до всіх файлів, які знайшлися. 
    '''
    res = []
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            res.extend(await read_folder(item_path, dest))
        else:
            res.append(item_path)
            logger.debug("Зчитано файл %s", item_path)
    return res

async def copy_file(list_of_files, dest):
    '''
    Функція приймає список файлів і копіює їх, у директорії,
    віжповідно до їх розширень, що будуть створені за шляхом dest.
    '''
    for item in list_of_files:
        extention = os.path.splitext(item)[1][1:]
        if extention:
            dir_path = os.path.join(dest, extention)
            await aiofiles.os.makedirs(dir_path, exist_ok=True)
            await aioshutil.copy(item, dir_path)
            logger.debug("Скопійовано файл %s у %s", item, dir_path)


async def main():
    args = parse_args()
    try:
        files = await read_folder(args.source, args.output)
        await copy_file(files, args.output)
    except FileNotFoundError as e:
        logger.error("Помилка: шлях %s не існує", e.filename)
    except Exception as e:
        logger.error("Помилка при копіюванні файлів: %s", e)
    else:
        logger.info("Файли скопійовано у призначення %s", args.output)


if __name__ == "__main__":
    asyncio.run(main())
