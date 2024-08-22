import re
import time
import requests
import sqlite3
import json

LOCAL_LANG = 'zh-Hans'
FIELDS = ['name', 'name_local', 'name_en', 'name_jp', 'genus', 'color', 'shape', 'forms_switchable', 'generation', 'growth_rate', 'habitat', 
        'has_gender_differences', 'hatch_counter', 'is_baby', 'is_legendary', 'is_mythical', 'base_happiness', 'capture_rate', 'gender_rate', 
        'sprite_default', 'sprite_home', 'egg_groups', 'flavor_texts_local', 'pal_park_encounters', 'pokedex_numbers', 'varieties', 'evolution_chain_id']

def get_species_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name_local = find_local_name(data['names'])
        name_en = find_local_name(data['names'], 'en')
        name_jp = find_local_name(data['names'], 'ja-Hrkt')
        genus = find_local_genus(data['genera'])
        varieties = [get_variety_data(variety['pokemon']['url']) for variety in data['varieties']]
        default_variety = next((v for v in varieties if v['is_default']), None)
        sprite_default = default_variety['sprites']['front_default'] if default_variety else None
        sprite_home = default_variety['sprites']['other']['home']['front_default'] if default_variety else None
        egg_groups = find_egg_groups(data['egg_groups'])
        flavor_texts_local = find_flavor_text(data['flavor_text_entries'])
        evolution_chain_id = extract_last_number(data['evolution_chain']['url'])
        pal_park_encounters = find_encounters(data['pal_park_encounters'])
        pokedex_numbers = find_pokedex_numbers(data['pokedex_numbers'])
        varieties = find_varieties(data['varieties'])

        return {
            # "order": data['order'],
            "name": data['name'],
            "name_local"  : name_local,
            "name_en"     : name_en,
            "name_jp"     : name_jp,
            "genus": genus,
            "color": data['color']['name'],
            "shape": data['shape']['name'],
            "forms_switchable": data['forms_switchable'],
            "generation": data['generation']['name'],
            "growth_rate": data['growth_rate']['name'],
            "habitat": data['habitat']['name'] if data['habitat'] else None,
            "has_gender_differences": data['has_gender_differences'],
            "hatch_counter": data['hatch_counter'],
            "is_baby": data['is_baby'],
            "is_legendary": data['is_legendary'],
            "is_mythical": data['is_mythical'],
            "base_happiness": data['base_happiness'],
            "capture_rate": data['capture_rate'],
            "gender_rate": data['gender_rate'],
            "sprite_default": sprite_default,
            "sprite_home": sprite_home,
            "egg_groups": json.dumps(egg_groups, ensure_ascii=False),
            "flavor_texts_local": json.dumps(flavor_texts_local, ensure_ascii=False),
            "pal_park_encounters": json.dumps(pal_park_encounters, ensure_ascii=False),
            "pokedex_numbers": json.dumps(pokedex_numbers, ensure_ascii=False),
            "varieties": json.dumps(varieties, ensure_ascii=False),
            "evolution_chain_id": evolution_chain_id
        }
    else:
        return None

def get_variety_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "is_default": data['is_default'],
            "height": data['height'],
            "weight": data['weight'],
            "sprites": data['sprites']
        }
    else:
        return None

def get_all_species(conn, cursor, is_append = False):
    response = requests.get('https://pokeapi.co/api/v2/pokemon-species?offset=0&limit=2000')
    if response.status_code == 200:
        data = response.json()
        species = data['results']
        for specie in species:
            cursor.execute('SELECT * FROM species WHERE name = ?', (specie['name'],))
            existing_species = cursor.fetchone()
            if existing_species is None:
                time.sleep(3)
                species_data = get_species_data(specie['url'])
                # print(species_data)
                if species_data:
                    insert_species(cursor, species_data, existing_species)
                    conn.commit()


def insert_species(cursor, data, existing_species = None):
    print('Inserting species:', data['name_local'])
    try:
        if existing_species:
            update_fields = []
            update_values = []
            # 获取列名
            cursor.execute('PRAGMA table_info(species)')
            columns = [column[1] for column in cursor.fetchall()]
            
            for field in FIELDS:
                if field in columns:
                    index = columns.index(field)
                    if not existing_species[index] and data[field]:
                        update_fields.append(f"{field} = ?")
                        update_values.append(data[field])

            if update_fields:
                update_values.append(data['name'])
                update_query = f"UPDATE species SET {', '.join(update_fields)} WHERE name = ?"
                cursor.execute(update_query, update_values)
                
        else:  
            cursor.execute('''
                INSERT INTO species (name, name_local, name_en, name_jp, genus, color, shape, forms_switchable, generation, growth_rate, habitat, has_gender_differences, hatch_counter, is_baby, is_legendary, is_mythical, base_happiness, capture_rate, gender_rate, sprite_default, sprite_home, egg_groups, flavor_texts_local, pal_park_encounters, pokedex_numbers, varieties, evolution_chain_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'], data['name_local'], data['name_en'], data['name_jp'], data['genus'], data['color'], data['shape'], data['forms_switchable'], data['generation'], data['growth_rate'], data['habitat'], data['has_gender_differences'], data['hatch_counter'], data['is_baby'], data['is_legendary'], data['is_mythical'], data['base_happiness'], data['capture_rate'], data['gender_rate'], data['sprite_default'], data['sprite_home'], json.dumps(data['egg_groups']), json.dumps(data['flavor_texts_local']), json.dumps(data['pal_park_encounters']), json.dumps(data['pokedex_numbers']), json.dumps(data['varieties']), data['evolution_chain_id']
            ))
    
    except Exception as e:
        print('Error inserting species:', e)

def find_pokedex_numbers(pokedex_numbers):
    result = []
    for pokedex_number in pokedex_numbers:
        result.append({
            "pokedex": pokedex_number['pokedex']['name'],
            "entry_number": pokedex_number['entry_number']
        })
    return result

def find_varieties(varieties):
    result = []
    for variety in varieties:
        result.append({
            "is_default": variety['is_default'],
            "pokemon": variety['pokemon']['name'],
        })
    return result

def find_egg_groups(egg_groups):
    egg_groups = [egg_group['name'] for egg_group in egg_groups]
    return egg_groups

def find_local_name(names, lang = LOCAL_LANG):
    name = next((n for n in names if n['language']['name'] == lang), None)
    return name['name'] if name else None

def find_local_genus(genera, lang = LOCAL_LANG):
    genus = next((g for g in genera if g['language']['name'] == lang), None)
    return genus['genus'] if genus else None

def find_flavor_text(flavor_texts, lang = LOCAL_LANG):
    texts = []
    for text in flavor_texts:
        if text['language']['name'] == lang:
            text= {
                "flavor_text": text['flavor_text'],
                "version": text['version']['name']
            }
            texts.append(text)
    return texts

def find_encounters(encounters):
    result = []
    for encounter in encounters:
        result.append({
            "area": encounter['area']['name'],
            "base_score": encounter['base_score'],
            "rate": encounter['rate']
        })
    return result

def extract_last_number(url):
    match = re.search(r'/(\d+)/?$', url)
    if match:
        return int(match.group(1))
    return None

def run():
    conn = sqlite3.connect('poke.db')
    cursor = conn.cursor()

    # create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            name_local TEXT,
            name_en TEXT,
            name_jp TEXT,
            genus TEXT,
            color TEXT,
            shape TEXT,
            forms_switchable BOOLEAN,
            generation TEXT,
            growth_rate TEXT,
            habitat TEXT,
            has_gender_differences BOOLEAN,
            hatch_counter INTEGER,
            is_baby BOOLEAN,
            is_legendary BOOLEAN,
            is_mythical BOOLEAN,
            base_happiness INTEGER,
            capture_rate INTEGER,
            gender_rate INTEGER,
            sprite_default TEXT,
            sprite_home TEXT,
            egg_groups TEXT,
            flavor_texts_local TEXT,
            pal_park_encounters TEXT,
            pokedex_numbers TEXT,
            varieties TEXT,
            evolution_chain_id INTEGER
        )
        ''')

    get_all_species(conn, cursor, True)

    conn.close()

run()