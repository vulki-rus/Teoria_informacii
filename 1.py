import sqlite3
from collections import Counter, defaultdict

def init_database(db_file='markov_data.db'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS overall_prob (
            char TEXT PRIMARY KEY,
            probability REAL
        )
    ''')
    
    # Таблица переходов с индексами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markov_transitions (
            order_num INTEGER,
            history TEXT,
            next_char TEXT,
            probability REAL,
            PRIMARY KEY (order_num, history, next_char)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history ON markov_transitions(history)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_history ON markov_transitions(order_num, history)')
    
    conn.commit()
    conn.close()


def analyze_markov(text_file, max_order, db_file):
    init_database(db_file)
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read().lower()
    
    # Оставляем только нужные символы
    text = ''.join(c for c in text if c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,!?')
    
    # Общая вероятность
    total_chars = len(text)
    overall_prob = {char: text.count(char) / total_chars for char in set(text)}
    
    # Сохраняем вероятности
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM overall_prob')
    cursor.executemany('INSERT OR REPLACE INTO overall_prob (char, probability) VALUES (?, ?)',
                      [(char, prob) for char, prob in overall_prob.items()])
    
    for order in range(1, max_order + 1):
        transitions = defaultdict(Counter)
        for i in range(len(text) - order):
            history = text[i:i + order]
            next_char = text[i + order]
            transitions[history][next_char] += 1
        
        cursor.execute('DELETE FROM markov_transitions WHERE order_num = ?', (order,))
        for hist, counter in transitions.items():
            total = sum(counter.values())
            for next_c, count in counter.items():
                cursor.execute('INSERT OR REPLACE INTO markov_transitions (order_num, history, next_char, probability) VALUES (?, ?, ?, ?)',
                                (order, hist, next_c, count / total))
    
    conn.commit()
    conn.close()


analyze_markov("russian_wiki_copy.txt", 13, "markov_data.db")
print("Готово!")