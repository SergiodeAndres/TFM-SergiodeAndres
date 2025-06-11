from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
import preprocessing_file
import pandas as pd
import dataframe_image as dfi

def realizar_analisis(corpus, topic, analisis, num_temas=5, num_palabras=10):
        corpus_preprocesado = [preprocessing_file.preprocesar(texto) for texto in corpus]
        palabras_comunes = preprocessing_file.obtener_palabras_comunes(corpus_preprocesado,5)
        corpus_preprocesado = [preprocessing_file.eliminar_palabras_frecuentes(texto, palabras_comunes) for texto in corpus_preprocesado]
        corpus_preprocesado = [texto for texto in corpus_preprocesado if texto is not None]

        lista_corpus = [' '.join(text) for text in corpus_preprocesado]
        
        Tf_idf_vectorizer = TfidfVectorizer()
        Tf_idf_score = Tf_idf_vectorizer.fit_transform(lista_corpus)

        nmf_model = NMF(n_components=num_temas, random_state=1)
        nmf_model.fit_transform(Tf_idf_score)

        vocabulario = Tf_idf_vectorizer.get_feature_names_out()
        lista_dfs = []
        for i, componentes in enumerate(nmf_model.components_):
            tupla_componente_palabra = zip(vocabulario, componentes)
            palabras_ordenadas = sorted(tupla_componente_palabra, key = lambda x:x[1], reverse=True)[:num_palabras]
            df = pd.DataFrame(palabras_ordenadas, columns=[f"tema {i+1}", f"peso {i+1}"])
            lista_dfs.append(df)
        combined_df = pd.concat(lista_dfs, axis = 1)
        dfi.export(combined_df, f'result_files\\ScikitLearn_NMF\\ScikitLearn_NMF_{topic}_{analisis}_{len(corpus_preprocesado)}.png')



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