from tkinter import *
import requests
import requests.auth
import threading
import preprocessing_file
import html
from flair.data import Sentence
from flair.nn import Classifier
import seaborn as sns
import matplotlib.pyplot as plt
from bertopic import BERTopic
import pandas as pd
import dataframe_image as dfi

def obtener_token():
    with open('api_credentials/password.txt', 'r') as f:
        password = f.read()
    with open('api_credentials/user.txt', 'r') as f:
        user = f.read().strip()
    with open('api_credentials/client_id.txt', 'r') as f:
        client_id = f.read().strip()
    with open('api_credentials/client_secret.txt', 'r') as f:
        client_secret = f.read().strip()

    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {
        'grant_type': 'password',
        'username': user,
        'password': password
    }
    headers = {'User-Agent': 'datosPostsTFM/0.1'}

    response = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        auth=client_auth,
        data=post_data,
        headers=headers
    )
    token = response.json()['access_token']
    return token

def generar_peticion(token, url):
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "datosPostsTFM/0.1"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        token = obtener_token()
        return generar_peticion(token, url)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def obtener_posts_2025_texto(token, subreddit, query):
    token = obtener_token()
    base_url = f"https://oauth.reddit.com/r/{subreddit}/search?limit=100&sort=new&q={query}&restrict_sr=1"
    posts_totales = []
    after = None

    while True:
        url = base_url + (f"&after={after}" if after else "")
        resultado = generar_peticion(token, url)

        if 'data' not in resultado or 'children' not in resultado['data']:
            break 

        posts = resultado['data']['children']

        for post in posts:
            posts_totales.append(post)

        after = resultado['data'].get('after')
        if not after:
            break

    return posts_totales

def realizar_analisis_temas(corpus, topic, analisis, num_temas=5, num_palabras=10):
        corpus_preprocesado = [preprocessing_file.preprocesar(texto) for texto in corpus]
        palabras_comunes = preprocessing_file.obtener_palabras_comunes(corpus_preprocesado,5)
        corpus_preprocesado = [preprocessing_file.eliminar_palabras_frecuentes(texto, palabras_comunes) for texto in corpus_preprocesado]
        corpus_preprocesado = [texto for texto in corpus_preprocesado if texto is not None]
        
        lista_corpus = [' '.join(text) for text in corpus_preprocesado]

        BERTopic_model = BERTopic(verbose=True)
        BERTopic_model.fit_transform(lista_corpus)

        lista_dfs = []
        temas_totales = min(len(BERTopic_model.get_topics()) - 1, num_temas)
        for i in range(0, temas_totales):
            df = pd.DataFrame(BERTopic_model.get_topic(i)[:num_palabras], columns=[f"tema {i+1}", f"peso {i+1}"])
            lista_dfs.append(df)
        df_combinado = pd.concat(lista_dfs, axis = 1)
        dfi.export(df_combinado, f'analisis_temas_{topic}_{analisis}.png')

def realizar_analisis_sentimientos(corpus, topic, analisis):
        corpus_preprocesado = [preprocessing_file.preprocesar(texto) for texto in corpus]
        palabras_comunes = preprocessing_file.obtener_palabras_comunes(corpus_preprocesado,5)
        corpus_preprocesado = [preprocessing_file.eliminar_palabras_frecuentes(texto, palabras_comunes) for texto in corpus_preprocesado]
        corpus_preprocesado = [texto for texto in corpus_preprocesado if texto is not None]

        lista_corpus = [' '.join(text) for text in corpus_preprocesado]
        
        lista_sentimientos = []
        tagger = Classifier.load('sentiment-fast')
        for text in lista_corpus:
            sentence = Sentence(text)
            tagger.predict(sentence)
            if sentence.labels:
                if sentence.labels[0].value == 'NEGATIVE':
                    lista_sentimientos.append(-sentence.labels[0].score)
                else:
                    lista_sentimientos.append(sentence.labels[0].score)

        sns.displot(lista_sentimientos, kind='kde')
        plt.savefig(f'analisis_sentimientos{topic}_{analisis}.png')
        plt.close()

def analizar_elon_musk(subreddit_name, info_label):
    threading.Thread(target=analizar_elon_musk_hilo, args=(subreddit_name, info_label)).start()

def analizar_elon_musk_hilo(subreddit_name, info_label):
    info_label.after(0, lambda: info_label.config(text=f"Obteniendo posts de subreddit: {subreddit_name} para Elon Musk"))
    posts = obtener_posts_2025_texto(obtener_token(), subreddit_name, "Elon Musk")  
    if not posts:
        info_label.after(0, lambda: info_label.config(text="No se encontraron posts relevantes."))
        return
    else:
        info_label.config(text=f"Se encontraron {len(posts)} posts relevantes sobre Elon Musk en {subreddit_name}.")
        data = []
        for post in posts:
            data.append(post['data']['title'])
            data.append(html.unescape(post['data']['selftext'].replace('\n', ' ')))
        data = [s for s in data if s != ""]
        info_label.config(text=f"Obteniendo análisis de temas")
        realizar_analisis_temas(data, "ElonMusk", subreddit_name)
        info_label.config(text=f"Obteniendo análisis de sentimientos")
        realizar_analisis_sentimientos(data, "ElonMusk", subreddit_name)
        info_label.config(text=f"Operación completada.")
        return

def analizar_space_x(subreddit_name, info_label):
    threading.Thread(target=analizar_space_x_hilo, args=(subreddit_name, info_label)).start()

def analizar_space_x_hilo(subreddit_name, info_label):
    info_label.after(0, lambda: info_label.config(text=f"Obteniendo posts de subreddit: {subreddit_name} para SpaceX"))
    posts = obtener_posts_2025_texto(obtener_token(), subreddit_name, "SpaceX")  
    if not posts:
        info_label.after(0, lambda: info_label.config(text="No se encontraron posts relevantes."))
        return
    else:
        info_label.config(text=f"Se encontraron {len(posts)} posts relevantes sobre SpaceX en {subreddit_name}.")
        data = []
        for post in posts:
            data.append(post['data']['title'])
            data.append(html.unescape(post['data']['selftext'].replace('\n', ' ')))
        data = [s for s in data if s != ""]
        info_label.config(text=f"Obteniendo análisis de temas")
        realizar_analisis_temas(data, "SpaceX", subreddit_name)
        info_label.config(text=f"Obteniendo análisis de sentimientos")
        realizar_analisis_sentimientos(data, "SpaceX", subreddit_name)
        info_label.config(text=f"Operación completada.")
        return

if __name__ == "__main__": 
    gui = Tk()
    gui.title("Reddit Topic and Sentiment Analysis")
    gui.geometry("400x300")
    nombre_subreddit_var = StringVar()
    nombre_subreddit = Entry(gui, textvariable = nombre_subreddit_var)
    nombre_subreddit.grid(row=0, column=1, padx=10, pady=10)
    nombre_subreddit_label = Label(gui, text="Nombre del subreddit:")
    nombre_subreddit_label.grid(row=0, column=0, padx=10, pady=10)
    button_elon_musk = Button(gui, text="Elon Musk", command=lambda: analizar_elon_musk(nombre_subreddit_var.get(), info_label))
    button_elon_musk.grid(row=1, column=0, padx=10, pady=10)
    button_space_x = Button(gui, text="SpaceX", command=lambda: analizar_space_x(nombre_subreddit_var.get(), info_label))
    button_space_x.grid(row=1, column=1, padx=10, pady=10)
    info_label = Label(gui, text="Selecciona un subreddit y un tema para analizar.")
    info_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    gui.mainloop()