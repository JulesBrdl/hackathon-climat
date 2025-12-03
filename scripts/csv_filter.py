import pandas as pd

"""
NOM DES COLONES DU CSV

Année
Numéro
Département
Code INSEE
Nom de la commune
Date de première alerte
Surface parcourue (m2)
Surface forêt (m2)
Surface maquis garrigues (m2)
Autres surfaces naturelles hors forêt (m2)
Surfaces agricoles (m2)
Autres surfaces (m2)
Surface autres terres boisées (m2)
Surfaces non boisées naturelles (m2)
Surfaces non boisées artificialisées (m2)
Surfaces non boisées (m2)
Précision des surfaces
Type de peuplement
Nature
Décès ou bâtiments touchés
Nombre de décès
Nombre de bâtiments totalement détruits
Nombre de bâtiments partiellement détruits
Précision de la donnée
latitude
longitude

"""

df = pd.read_csv("./data/incendies/incendies_V2.csv")
print(df.columns)

percent_not_null = df.notnull().mean() * 100

print(percent_not_null)

cols_to_remove = ["Numéro", "Surface forêt (m2)", "Surface maquis garrigues (m2)", "Autres surfaces naturelles hors forêt (m2)",
                  "Surfaces agricoles (m2)", "Autres surfaces (m2)", "Surface autres terres boisées (m2)", "Surfaces non boisées naturelles (m2)",
                  "Surfaces non boisées artificialisées (m2)", "Surfaces non boisées (m2)", "Précision des surfaces", "Type de peuplement",
                  "Décès ou bâtiments touchés", "Nombre de décès", "Nombre de bâtiments totalement détruits", "Nombre de bâtiments partiellement détruits",
                  "Précision de la donnée"]

df = df[df["Année"] >= 2005]
df = df.sort_values(by=df.columns[5])

df_cleaned = df.drop(columns=cols_to_remove)

avg_size = df["Surface parcourue (m2)"].mean()
print(avg_size)

df_cleaned.to_csv("./data/incendies/incendies_V4.csv", index=False)