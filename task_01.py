'''
Скрипт, який читає всі файли у вказаній користувачем вихідній папці (source folder)
і розподіляє їх по підпапках у директорії призначення (output folder)
на основі розширення файлів. 
'''

import asyncio
import os
import sys
import argparse
import aioshutil
import aiofiles.os


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


async def read_files(src: str, dest: str):
    '''
    Функція приймає шляхи у файловій системі, обходить рекурсивно всі елементи
    за цим шляхом, і повертає список із повними шляхами до всіх файлів, які знайшлися. 
    '''
    res = []
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            res.extend(await read_files(item_path, dest))
        else:
            res.append(item_path)
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


async def main():
    args = parse_args()
    try:
        files = await read_files(args.source, args.output)
        await copy_file(files, args.output)
    except FileNotFoundError as e:
        print(f"Помилка: Шлях {e.filename} не існує")
    except Exception as e:
        print(f"Помилка при копіюванні файлів: {e}")
    else:
        print(f"Файли скопійовано у призначення {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
