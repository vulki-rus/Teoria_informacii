import sqlite3
import random

def load_markov_from_db(db_file):
    conn = sqlite3.connect(db_file)
    
    # Загружаем общие вероятности
    cursor = conn.cursor()
    cursor.execute("SELECT char, probability FROM overall_prob")
    overall_prob = dict(cursor.fetchall())
    
    conn.close()
    return overall_prob, db_file


def get_candidates(cursor, order, history):
    cursor.execute('SELECT next_char, probability FROM markov_transitions WHERE order_num = ? AND history = ?',
                    (order, history))
    return cursor.fetchall()


def generate_text_from_db(db_file, seed, length, max_order):
    current = seed.lower()
    result = current
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    for _ in range(length):
        next_char = None
        
        # Используем Марковские цепи от высшего к низшему
        for order in range(min(max_order, len(current)), 0, -1):
            history = current[-order:]
            candidates = get_candidates(cursor, order, history)
            
            if candidates:
                chars, probs = zip(*candidates)
                next_char = random.choices(chars, weights=probs)[0]
                break
        
        if next_char is None:
            chars = list(overall_prob.keys())
            probs = list(overall_prob.values())
            next_char = random.choices(chars, probs)[0]
        
        result += next_char
        current += next_char
        
        if len(current) > max_order:
            current = current[-max_order:]
    
    conn.close()
    return result

overall_prob, db_file = load_markov_from_db("markov_data.db")
print(generate_text_from_db(db_file, "я думаю что", 300, 8))