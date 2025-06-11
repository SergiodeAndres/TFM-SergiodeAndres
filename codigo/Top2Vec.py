from top2vec import Top2Vec
import preprocessing_file
import pandas as pd
import dataframe_image as dfi

def realizar_analisis(corpus, topic, analisis, num_temas=5, num_palabras=10):
        corpus_preprocesado = [preprocessing_file.preprocesar(texto) for texto in corpus]
        palabras_comunes = preprocessing_file.obtener_palabras_comunes(corpus_preprocesado,5)
        corpus_preprocesado = [preprocessing_file.eliminar_palabras_frecuentes(texto, palabras_comunes) for texto in corpus_preprocesado]
        corpus_preprocesado = [texto for texto in corpus_preprocesado if texto is not None]

        lista_corpus = [' '.join(text) for text in corpus_preprocesado]

        Top2Vec_model = Top2Vec(lista_corpus, min_count=15, workers=4)

        temas_totales = min(Top2Vec_model.get_num_topics(), num_temas)
        palabras_temas, pesos_palabras, _ = Top2Vec_model.get_topics(temas_totales)
        lista_dfs = []
        for i in range(len(palabras_temas)):
            df = pd.DataFrame(zip(palabras_temas[i][:num_palabras], pesos_palabras[i][:num_palabras]), columns=[f"tema {i+1}", f"peso {i+1}"])
            lista_dfs.append(df)
        df_combinado = pd.concat(lista_dfs, axis = 1)
        dfi.export(df_combinado, f'result_files\\Top2Vec\\Top2Vec_{topic}_{analisis}_{len(corpus_preprocesado)}.png')



print("Tema a analizar (1. Elon Musk, 2:SpaceX): ")
tema = input()
print("Tipo de análisis (1. Cuerpo completo, 2. Cuerpo completo por semestre, 3. Cuerpo por subreddit): ")
tipo_analisis = input()

if tema == "1":
    subreddits = ['posts_politics', 'posts_elonmusk', 'posts_enoughMuskSpam', 'posts_technology_elonMusk']
    if tipo_analisis == "1":
        corpus = preprocessing_file.obtener_corpus('output_files\\posts_politics.csv')
        corpus += preprocessing_file.obtener_corpus('output_files\\posts_elonmusk.csv')
        corpus += preprocessing_file.obtener_corpus('output_files\\posts_enoughMuskSpam.csv')
        corpus += preprocessing_file.obtener_corpus('output_files\\posts_technology_elonMusk.csv')
        realizar_analisis(corpus, "ElonMusk", "cuerpo_completo")
    elif tipo_analisis == "2":
        full_corpus = preprocessing_file.obtener_corpus_por_fecha(subreddits)
        for semestre, docs_semestre in full_corpus.items():
            realizar_analisis(docs_semestre, "ElonMusk", "semestre_" + semestre)
    elif tipo_analisis == "3":
         for subreddit in subreddits:
            corpus = preprocessing_file.obtener_corpus(f'output_files\\{subreddit}.csv')
            realizar_analisis(corpus, "ElonMusk", "subreddit_" + subreddit)
    else:
         print("Tipo de análisis no válido. Por favor, elige una opción válida.")
elif tema == "2":    
    subreddits = ['posts_space', 'posts_spacex', 'posts_technology_spaceX']
    if tipo_analisis == "1":
        corpus = preprocessing_file.obtener_corpus('output_files\\posts_space.csv')
        corpus += preprocessing_file.obtener_corpus('output_files\\posts_spacex.csv')
        corpus += preprocessing_file.obtener_corpus('output_files\\posts_technology_spaceX.csv')
        realizar_analisis(corpus, "SpaceX", "cuerpo_completo")
    elif tipo_analisis == "2":
        full_corpus = preprocessing_file.obtener_corpus_por_fecha(subreddits)
        for semestre, docs_semestre in full_corpus.items():
             realizar_analisis(docs_semestre, "SpaceX", "semestre_" + semestre)
    elif tipo_analisis == "3":
         for subreddit in subreddits:
            corpus = preprocessing_file.obtener_corpus(f'output_files\\{subreddit}.csv')
            realizar_analisis(corpus, "SpaceX", "subreddit_" + subreddit)
    else:
         "Tipo de análisis no válido. Por favor, elige una opción válida."
else:
    print("Tema no válido. Por favor, elige una opción válida.")