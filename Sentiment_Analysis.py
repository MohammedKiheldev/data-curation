# Importation des bibliothèques nécessaires
import re  # Module pour les expressions régulières
import nltk  # Bibliothèque de traitement du langage naturel
import pandas as pd  # Bibliothèque pour la manipulation de données tabulaires
from nltk.corpus import stopwords  # Liste de mots vides en anglais
from nltk.tokenize import word_tokenize  # Fonction de tokenization de NLTK
from nltk.stem import PorterStemmer  # Algorithme de racinisation (stemming) de NLTK
from textblob import TextBlob  # Bibliothèque pour l'analyse de sentiments
from wordcloud import WordCloud, STOPWORDS  # Création de nuages de mots
import matplotlib.pyplot as plt  # Bibliothèque de visualisation de données
import plotly.express as px  # Bibliothèque de visualisation interactive
import tkinter as tk  # Bibliothèque pour créer des interfaces graphiques
from tkinter import ttk  # Widgets de thèmes pour Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Intégration de graphiques Matplotlib dans Tkinter
import numpy as np  # Bibliothèque pour les opérations mathématiques


# Téléchargement des ressources NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Fonction pour nettoyer les données textuelles
def cleanText(text):
    # Convertir le texte en minuscules pour assurer la cohérence
    text = text.lower()
    
    # Supprimer les mentions d'utilisateurs (@username)
    text = re.sub(r'(@[A-Za-z0-9_]+)', '', text)
    
    # Supprimer les liens URL
    text = re.sub(r'http://\S+|https://\S+', '', text)
    
    # Supprimer les caractères non alphabétiques (sauf les espaces)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenize le texte en mots pour le traitement ultérieur
    text_tokens = word_tokenize(text)
    
    # Supprimer les mots vides (stopwords) et STOPWORDS supplémentaires
    text = [word for word in text_tokens if word not in stopwords.words() and word not in STOPWORDS]
    
    # Rejoindre les mots pour former une chaîne de texte propre
    text = ' '.join(text)
    
    # Retourner le texte nettoyé
    return text

# Fonction pour raciner le texte
def stem(text):
    porter = PorterStemmer()
    token_words = word_tokenize(text)
    stem_sentence = [porter.stem(word) for word in token_words]
    return " ".join(stem_sentence)

# Fonction pour l'analyse de sentiment
def sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    return 'positif' if polarity > 0 else ('négatif' if polarity < 0 else 'neutre')

# Fonction générique pour le traitement et l'analyse des données
def process_and_analyze(file_path, header_names):
    df = pd.read_csv(file_path, encoding='latin-1', header=None, names=header_names, low_memory=False)
    df = df.head(10)
    df['clean_tweets'] = df['text'].apply(cleanText)
    df['stemmed_tweets'] = df['clean_tweets'].apply(stem)
    df['sentiment'] = df['stemmed_tweets'].apply(sentiment)
    ptweets = df[df['sentiment'] == 'positif']
    p_perc = 100 * len(ptweets) / len(df)
    ntweets = df[df['sentiment'] == 'négatif']
    n_perc = 100 * len(ntweets) / len(df)
    print(f'Tweets positifs: {round(p_perc, 2)}%')
    print(f'Tweets neutres: {round(100 - p_perc - n_perc, 2)}%')
    print(f'Tweets négatifs: {round(n_perc, 2)}%')

# Chemins des fichiers
file_paths = [
    'C:\\Users\\kihel\\Documents\\dataSets\\Sentiment140.csv',
    'C:\\Users\\kihel\\Documents\\dataSets\\covid19_tweets.csv',
    'C:\\Users\\kihel\\Documents\\dataSets\\twitter_training.csv',
    'C:\\Users\\kihel\\Documents\\dataSets\\twitter_validation.csv'
]

# Liste des noms de colonnes pour chaque fichier
header_names = [
    ["target", "ids", "date", "flag", "user", "text"],
    ["user_name", "user_location", "user_description", "user_created", "user_followers", "user_friends", "user_favourites", "user_verified", "date", "text", "hashtags", "source", "is_retweet"],
    ["id", "platform", "text"],
    ["id", "platform", "text"]
]

# Charger les données de chaque fichier dans une liste de dataframes
dfs = [pd.read_csv(file_path, encoding='latin-1', header=None, names=header_names[i], low_memory=False).head(10) for i, file_path in enumerate(file_paths)]

# Afficher les résultats pour chaque fichier avant la fusion
for i, df in enumerate(dfs):
    print(f'\nRésultats pour le fichier {file_paths[i]} avant la fusion :')
    df['clean_tweets'] = df['text'].apply(cleanText)
    df['stemmed_tweets'] = df['clean_tweets'].apply(stem)
    df['sentiment'] = df['stemmed_tweets'].apply(sentiment)
    ptweets = df[df['sentiment'] == 'positif']
    p_perc = 100 * len(ptweets) / len(df)
    ntweets = df[df['sentiment'] == 'négatif']
    n_perc = 100 * len(ntweets) / len(df)
    print(f'Tweets positifs: {round(p_perc, 2)}%')
    print(f'Tweets neutres: {round(100 - p_perc - n_perc, 2)}%')
    print(f'Tweets négatifs: {round(n_perc, 2)}%')

# Fusionner les dataframes en utilisant la colonne 'text'
merged_df = pd.concat(dfs, ignore_index=True)

# Appliquer le reste du traitement et de l'analyse sur le dataframe fusionné
merged_df['clean_tweets'] = merged_df['text'].apply(cleanText)
merged_df['stemmed_tweets'] = merged_df['clean_tweets'].apply(stem)
merged_df['sentiment'] = merged_df['stemmed_tweets'].apply(sentiment)

# Afficher les résultats après la fusion
print('\nRésultats après la fusion :')
ptweets = merged_df[merged_df['sentiment'] == 'positif']
p_perc = 100 * len(ptweets) / len(merged_df)
ntweets = merged_df[merged_df['sentiment'] == 'négatif']
n_perc = 100 * len(ntweets) / len(merged_df)
print(f'Tweets positifs: {round(p_perc, 2)}%')
print(f'Tweets neutres: {round(100 - p_perc - n_perc, 2)}%')
print(f'Tweets négatifs: {round(n_perc, 2)}%')

# Réduction de données : Sélectionner uniquement les tweets avec un sentiment positif
positive_tweets_reduced = merged_df[merged_df['sentiment'] == 'positif']

# Afficher le pourcentage de tweets positifs après la réduction
p_perc_reduced = 100 * len(positive_tweets_reduced) / len(merged_df)
print(f'Tweets positifs après réduction : {round(p_perc_reduced, 2)}%')

# Affichage de chaque tweet avec son sentiment prédit
print('\nDétails des tweets avec leurs sentiments :')
table_data = []
for index, row in merged_df.iterrows():
    table_data.append([index + 1, row["text"], row["clean_tweets"], row["sentiment"]])

# Création d'un dataframe pour afficher le tableau
table_df = pd.DataFrame(table_data, columns=['Tweet #', 'Texte original', 'Texte après nettoyage', 'Sentiment prédit'])

# Création de la fenêtre principale
root = tk.Tk()
root.title('Analyse de Sentiment')

# Frame pour le tableau
table_frame = ttk.Frame(root)
table_frame.grid(row=0, column=0, padx=10, pady=10, rowspan=2)

# Création du tableau
tree = ttk.Treeview(table_frame, columns=['Tweet #', 'Texte après nettoyage', 'Sentiment prédit'])
tree.heading('#0', text='', anchor='center')
tree.heading('#1', text='Numéro', anchor='center')
tree.heading('#2', text='Texte', anchor='center')
tree.heading('#3', text='Sentiment prédit', anchor='center')

# Affichage des données dans le tableau
for index, row in table_df.iterrows():
    tree.insert('', 'end', values=[row['Tweet #'], row['Texte après nettoyage'], row['Sentiment prédit']])

# Scrollbar pour le tableau
tree_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
tree.configure(yscroll=tree_scroll.set)
tree_scroll.grid(row=0, column=1, sticky='ns')

# Ajout du tableau à la fenêtre
tree.grid(row=0, column=0)

# Frame pour le Pi Chart
chart_frame = ttk.Frame(root)
chart_frame.grid(row=1, column=1, padx=10, pady=10)

# Création du Pi Chart
sentiment_counts = merged_df['sentiment'].value_counts()
labels = sentiment_counts.index
sizes = sentiment_counts.values
colors = ['green', 'gray', 'red']  # Couleurs pour les sentiments positifs, neutres et négatifs
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax.axis('equal')  # Assure une représentation circulaire
chart_canvas = FigureCanvasTkAgg(fig, chart_frame)
chart_canvas.get_tk_widget().pack()
chart_canvas.draw()

# Lancement de la boucle principale
root.mainloop()