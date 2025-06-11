import pandas as pd
import nltk
import re
from nltk.corpus import wordnet

stopwords = set(nltk.corpus.stopwords.words("english"))
lemmatizer = nltk.WordNetLemmatizer()
regex_limpio = re.compile(r'https?://\S+|www\.\S+|\b\w\/\b|\'s\b|[^\w\s]|\d+')

def etiqueta_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('S'):
        return wordnet.ADJ_SAT
    else:
        return wordnet.NOUN

def obtener_corpus(file_path):
    df = pd.read_csv(file_path, usecols=['Title', 'Text'])
    corpus = df['Title'].dropna().tolist()
    corpus.extend(df['Text'].dropna().tolist())
    return corpus

def obtener_corpus_por_fecha(file_list):
    df_list = []
    for file in file_list:
        df = pd.read_csv(f'output_files\\{file}.csv', usecols=['Title', 'Text', 'Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Semester'] = df['Date'].apply(
            lambda x: f"{x.year}-S1" if x.month <= 6 else f"{x.year}-S2"
        )
        df_list.append(df)
    df_combinado = pd.concat(df_list, ignore_index=True)
    semestre_dfs = {
    semestre: grupo[['Title', 'Text']].reset_index(drop=True)
    for semestre, grupo in df_combinado.groupby('Semester')
    }
    semester_corpus = {}
    for semestre, df in semestre_dfs.items():
        corpus = df['Title'].dropna().tolist()
        corpus.extend(df['Text'].dropna().tolist())
        semester_corpus[semestre] = corpus

    return semester_corpus

def preprocesar(texto):
    texto = texto.lower()
    texto = regex_limpio.sub('', texto)
    tokens = nltk.word_tokenize(texto)
    tagged = nltk.pos_tag(tokens)
    return [
        lemmatizer.lemmatize(word, etiqueta_pos(tag))
        for word, tag in tagged
        if word not in stopwords
    ]

def obtener_palabras_comunes(corpus, numero_palabras = 5):
    lista_tokens = [token for texto in corpus for token in texto]
    frecuencia_palabras = nltk.FreqDist(lista_tokens)
    palabras_comunes = [word for word, _ in frecuencia_palabras.most_common(numero_palabras)]
    return palabras_comunes

def eliminar_palabras_frecuentes(texto, palabras_comunes):
    set_palabras_comunes = set(palabras_comunes)
    filtrado = [token for token in texto if token and token not in set_palabras_comunes]
    return filtrado if filtrado and filtrado != ['remove'] and filtrado != ['delete'] else None
