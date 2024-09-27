'''
Python-скрипт, який завантажує текст із заданої URL "TEXT_URL",
визначає кількість включень слів у тексті за допомогою парадигми MapReduce
і візуалізує топ-N з найвищою частотою використання у тексті.
'''

import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt


def get_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(e)
        return None


def remove_punctuation(text):
    '''Функція для видалення знаків пунктуації'''
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def get_top_words(word_dict, n: int) -> dict:
    '''Функція приймає словник word_dict і вертає топ n найчастіших входжень'''
    sorted_words = sorted(
        word_dict.items(), key=lambda item: item[1], reverse=True)
    top_n_words = dict(sorted_words[:n])

    return top_n_words


def visualize_top_words(word_dict):
    '''
    Функція отримує словник, у якому містяться слова і їх кількість включень.
    На основі нього будує гістограму
    '''
    # Отримуємо окремі списки для слів і їхніх частот
    words = list(word_dict.keys())
    inclusions = list(word_dict.values())

    # Створюємо діаграму
    plt.figure(figsize=(10, 6))
    plt.barh(words, inclusions, color='skyblue')
    plt.gca().invert_yaxis()

    # Заголовки і підписи до осей
    plt.title("Гістограма частот слів", fontsize=14)
    plt.xlabel("Кількість входжень", fontsize=12)
    plt.ylabel("Слова", fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

    # Alice's Adventures in Wonderland
    TEXT_URL = "https://www.gutenberg.org/cache/epub/28885/pg28885.txt"
    # 1984
    # TEXT_URL = "https://gutenberg.net.au/ebooks01/0100021.txt"

    N = 10  # TOP-скільки слів буде візуалізовано

    text = get_text(TEXT_URL)
    if text:
        # Розкоментувати це, якщо треба шукати конкретні слова
        # search_words = ['war', 'peace', 'love']
        # result = map_reduce(text, search_words)

        word_dict = map_reduce(text)
        top_words_dict = get_top_words(word_dict, N)
        visualize_top_words(top_words_dict)
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
