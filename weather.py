# Import des bibliothèques
import tkinter as tk  # Bibliothèque pour l'interface graphique
from tkinter import ttk, messagebox  # Widgets supplémentaires pour tkinter et boîtes de dialogue
import requests  # Pour effectuer des requêtes HTTP
from datetime import datetime, timedelta, timezone  # Pour manipuler les dates et heures
import pandas as pd  # Bibliothèque pour la manipulation de données en tableau
import matplotlib.pyplot as plt  # Bibliothèque pour créer des graphiques
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Utilisé pour intégrer des graphiques dans tkinter
from fuzzywuzzy import process  # Pour la recherche de correspondances floues

# Clé API pour OpenWeatherMap
api_key = 'XXXXXX'

# Liste des villes marocaines
cities = [
    'Casablanca', 'Casablanca','Marrakech', 'Marrakech', 
    'Tanger', 'Agadir', 'Essaouira', 'Ouarzazate', 'Chefchaouen', 'Meknès', 
    'Fès', 'Kenitra', 'Oujda', 'Safi', 'Mohammedia', 'Khouribga', 'Beni Mellal', 
    'El Jadida', 'Taza', 'Nador', 'Settat', 'Tétouan', 'Khémisset', 'Guelmim', 
    'Béni Mellal', 'Ksar El Kebir', 'Targuist', 'Larache', 'Dakhla', 'Tiznit', 
    'Tiflet', 'Berrechid', 'Taourirt', 'Taroudant', 'Sidi Slimane', 'Fquih Ben Salah', 
    'Errachidia', 'Essaouira', 'Tiznit', 'Lqliaa', 'Khenifra', 'Midelt', 'Azrou', 
    'Skhirat', 'Bouznika', 'Sidi Kacem', 'El Kelaa des Sraghna', 'Tan-Tan', 'Lahraouyine', 
    'Sidi Bennour', 'El Aioun', 'Sidi Ifni', 'Meknès', 'Settat', 'Guelmim', 'Oujda-Angad', 
    'Mohammedia', 'Laâyoune', 'Nouaceur', 'Khouribga', 'Taza', 'Fès', 'Khémisset'
]

# Initialisation d'un ensemble pour stocker les noms de ville uniques
unique_cities = set(cities)

# Initialisation d'une liste pour stocker les données météorologiques
weather_data = []

# Définir la période de 5 jours à partir d'aujourd'hui
start_date = datetime.now(timezone.utc)
end_date = start_date + timedelta(days=5)

# Itération sur les villes uniques
for city in unique_cities:
    # URL API pour chaque ville
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'

    # Effectuer la requête API
    response = requests.get(url)
    data = response.json()

    # Assurer que la clé 'list' est présente dans la réponse
    if 'list' in data:
        # Itération sur la liste de prévisions pour chaque ville
        for forecast in data['list']:
            # Convertir le timestamp en objet datetime
            date_obj = datetime.fromtimestamp(forecast['dt'], timezone.utc)

            # Vérifier si la date est dans la période de 5 jours
            if start_date <= date_obj <= end_date:
                # Ajouter les données à la liste
                weather_data.append({
                    'ville': city,
                    'heure': date_obj.strftime('%H:%M'),
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'temperature': forecast['main']['temp'],
                    'temp_max': forecast['main']['temp_max'],
                    'temp_min': forecast['main']['temp_min'],
                    'humidity': forecast['main']['humidity'],
                    'speed': forecast['wind']['speed'],
                    'description': forecast['weather'][0]['description']
                })
    else:
        print(f"Aucune donnée de prévision trouvée pour {city}")

# Création d'un DataFrame à partir de la liste de données
df = pd.DataFrame(weather_data)

# Fonction de nettoyage des données
def clean_data(data_frame):
    # Supprimer les doublons dans la liste des villes
    data_frame['ville'] = data_frame['ville'].apply(lambda x: x.strip().capitalize())
    data_frame = data_frame.drop_duplicates(subset=['ville', 'date', 'heure'], keep='first')

    # Supprimer les lignes avec des valeurs manquantes
    data_frame = data_frame.dropna()
    
    # Convertir la température de Kelvin à Celsius
    #data_frame['temperature'] = data_frame['temperature'] - 273.15
    
    # Supprimer les valeurs aberrantes dans la colonne 'temperature'
    #data_frame = data_frame[(data_frame['temperature'] >= -10) & (data_frame['temperature'] <= 40)]
    
    # Renommer la colonne 'speed' en 'wind_speed'
    data_frame = data_frame.rename(columns={'speed': 'wind_speed'})
    
    # Convertir la colonne 'date' en format datetime
    data_frame['date'] = pd.to_datetime(data_frame['date'])

    return data_frame

# Utiliser la fonction clean_data
df = clean_data(df)

# Classe d'application Tkinter
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prévisions météorologiques par ville")

        # Créer un Frame pour organiser les widgets
        input_frame = ttk.Frame(root)
        input_frame.pack(pady=10)

        # Ajouter une Entry pour la recherche de ville
        self.search_entry = ttk.Entry(input_frame)
        self.search_entry.grid(row=0, column=0, padx=5)

        # Bouton pour déclencher la recherche
        search_button = ttk.Button(input_frame, text="Rechercher", command=self.perform_search)
        search_button.grid(row=0, column=1, padx=5)

        # Bouton pour ajouter une nouvelle ville
        add_city_button = ttk.Button(input_frame, text="Ajouter Ville", command=self.add_city)
        add_city_button.grid(row=0, column=2, padx=5)
        
        # Bouton pour mettre à jour les données
        update_button = ttk.Button(input_frame, text="Mettre à jour", command=self.update_data)
        update_button.grid(row=0, column=3, padx=5)

        # Créer un Treeview pour afficher les données avec une barre de défilement
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = tuple(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(pady=10)

        # Ajouter des données au Treeview
        for index, row in df.iterrows():
            self.tree.insert("", index, values=tuple(row))

        # Bouton pour quitter l'application
        quit_button = ttk.Button(root, text="Quitter", command=root.destroy)
        quit_button.pack(pady=10)

        # Initialiser une variable pour stocker la référence à la figure du graphique
        self.plot_figure = None

    def add_city(self):
        new_city = self.search_entry.get().capitalize()
        if new_city and new_city not in unique_cities:
            unique_cities.add(new_city)
            messagebox.showinfo("Ville ajoutée", f"La ville {new_city} a été ajoutée à la liste.")
        else:
            messagebox.showinfo("Ville existante", "La ville existe déjà dans la liste.")

    def update_data(self):
        global df
        weather_data = []

        for city in unique_cities:
            # URL API pour chaque ville
            url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'

            # Effectuer la requête API
            response = requests.get(url)
            data = response.json()

            # Assurer que la clé 'list' est présente dans la réponse
            if 'list' in data:
                # Itération sur la liste de prévisions pour chaque ville
                for forecast in data['list']:
                    # Convertir le timestamp en objet datetime
                    date_obj = datetime.fromtimestamp(forecast['dt'], timezone.utc)

                    # Vérifier si la date est dans la période de 5 jours
                    if start_date <= date_obj <= end_date:
                        # Ajouter les données à la liste
                        weather_data.append({
                            'ville': city,
                            'heure': date_obj.strftime('%H:%M'),
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'temperature': forecast['main']['temp'],
                            'temp_max': forecast['main']['temp_max'],
                            'temp_min': forecast['main']['temp_min'],
                            'humidity': forecast['main']['humidity'],
                            'wind_speed': forecast['wind']['speed'],
                            'description': forecast['weather'][0]['description']
                        })
            else:
                print(f"Aucune donnée de prévision trouvée pour {city}")

        # Mettre à jour le DataFrame
        df = pd.DataFrame(weather_data)
        df = clean_data(df)

        # Mettre à jour le Treeview
        self.update_treeview(df)
        
        # Afficher la boîte de dialogue de mise à jour réussie
        messagebox.showinfo("Mise à jour réussie", "Les données ont été mises à jour avec succès.")

    def update_treeview(self, updated_df):
        # Effacer l'ancien Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les nouvelles données au Treeview
        for index, row in updated_df.iterrows():
            self.tree.insert("", index, values=tuple(row))

    def perform_search(self):
        search_text = self.search_entry.get().capitalize()
        best_match, similarity = process.extractOne(search_text, unique_cities)

        if similarity >= 80:
            for item in self.tree.get_children():
                self.tree.delete(item)

            filtered_df = df[df['ville'] == best_match]

            for index, row in filtered_df.iterrows():
                self.tree.insert("", index, values=tuple(row))

            self.update_temperature_curve(filtered_df)
        else:
            messagebox.showinfo("Aucune correspondance", f"Aucune correspondance trouvée pour {search_text}")

    def update_temperature_curve(self, filtered_df):
        if filtered_df.empty:
            return

        if self.plot_figure:
            self.plot_figure.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(10, 6))

        filtered_df.loc[:, 'date'] = pd.to_datetime(filtered_df['date'])  # Utilisation de .loc pour éviter l'avertissement
        daily_avg_temp = filtered_df.groupby('date')['temperature'].mean()

        ax.plot(daily_avg_temp.index, daily_avg_temp.values, marker='o', linestyle='-', color='b')

        ax.set_xlabel('Date')
        ax.set_ylabel('Température moyenne (°C)')
        ax.set_title(f"Courbe de température pour {filtered_df['ville'].iloc[0]}")

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        self.plot_figure = canvas

# Script principal
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
