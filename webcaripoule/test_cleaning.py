import time

import pandas as pd
from pandas.errors import EmptyDataError
import warnings as wn

wn.filterwarnings('ignore')


def datacleaning():
    """
    Permet le nettoyage et la remise en forme des données
    scrapées sous forme de dataframe pandas
    """
    # scraped datas file cleaning using pandas
    try:
        df = pd.read_csv('final_scraping.csv')

        # pour enlever les espaces en début et fin de ligne
        for column in df.columns:
            df[column] = df[column].astype(str).str.strip()

        # Remplacer des caractères 'parasites' à la colonne 'niveau de difficulté'
        df['niveau de difficulté'] = df['niveau de difficulté'].str.lower()
        df.drop(df[df['niveau de difficulté'] == 'niveau de difficulté'].index, inplace=True)
        df = df.reset_index(drop=True)

        # pour uniformiser le format des avis etc en un compte
        toreplace = ['Recettes', 'avis', 'commentaires', '', 'nan',' ']
        remplacement = ['', '', '', 0, 0,'']

        d = dict(zip(toreplace, remplacement))

        df['Nbre vote, avis ou commentaires'] = df['Nbre vote, avis ou commentaires'].replace(d, regex=True)

        # we replace the missing values:
        numerical_col = ['note', 'Nbre vote, avis ou commentaires', 'temps de préparation (en min)',
                         'temps de cuisson (en min)']

        for column in numerical_col:
            df[column] = df[column].fillna(0)

        str_col = []

        for col in df.columns:
            if col not in numerical_col:
                str_col.append(col)

        for cols in str_col:
            df[cols] = df[cols].fillna('Non_renseigné')

        df['Nbre vote, avis ou commentaires'] = df['Nbre vote, avis ou commentaires'].replace('', 0)
        df['Nbre vote, avis ou commentaires'] = df['Nbre vote, avis ou commentaires'].replace('nan', 0)

        df['note'] = df['note'].replace('', 0)
        df['note'] = df['note'].replace('nan', 0)
        df['note'] = df['note'].astype(float)

        temps_to_change = ['temps de cuisson (en min)', 'temps de préparation (en min)']
        for value in temps_to_change:
            for i in range(len(df)):
                df[value][i] = "".join(str(df[value][i]).split())

        # on remplace 'mn' par 'min'
        toreplace = ['mn', 'min', ' ', '-', '1j', 'nan']
        remplacement = ['', '', '', 0, 24, 0]
        d = dict(zip(toreplace, remplacement))

        for value in temps_to_change:
            df[value] = df[value].replace(d, regex=True)

        for col in temps_to_change:
            df[col] = df[col].astype(str)
            for i in range(len(df)):
                for value in df[col]:
                    if value != 0:
                        if len(value) == 5:
                            if (value[1:2] == 'j') and (value[4] == 'h'):
                                new_value = str((int(value[0]) * 24 * 60) + int(value[2:4]) * 60)
                                df[col][i] = df[col][i].replace(value, new_value)

                            elif value[1:2] == 'j':
                                new_value = str((int(value[0]) * 24 * 60) + int(value[3:5]))
                                df[col][i] = df[col][i].replace(value, new_value)

                            elif value[1:2] == 'h':
                                new_value = str((int(value[0]) * 60) + int(value[3:5]))
                                df[col][i] = df[col][i].replace(value, new_value)
                            else:
                                new_value = str((int(value[0:2]) * 60) + int(value[3:5]))
                                df[col][i] = df[col][i].replace(value, new_value)
                        elif len(value) == 4:
                            if value[1:2] == 'h':
                                new_value = str((int(value[0:1]) * 60) + int(value[2:4]))
                                df[col][i] = df[col][i].replace(value, new_value)
                            else:
                                new_value = str((int(value[0:2]) * 60) + int(value[3:4]))
                                df[col][i] = df[col][i].replace(value, new_value)
                        elif len(value) == 3:
                            if value[2:3] == 'h':
                                new_value = str(int(value[0:2]) * 60)
                                df[col][i] = df[col][i].replace(value, new_value)
                            else:
                                new_value = str((int(value[0:1]) * 60 + int(value[2:3])))
                                df[col][i] = df[col][i].replace(value, new_value)

                        elif len(value) == 2:
                            if value[1:2] == 'j':
                                new_value = str((int(value[0]) * 60 * 24))
                                df[col][i] = df[col][i].replace(value, new_value)

                            elif value[1:2] == 'h':
                                new_value = str((int(value[0]) * 60))
                                df[col][i] = df[col][i].replace(value, new_value)


        df['niveau de difficulté'] = df['niveau de difficulté'].replace(
            {'intermédiaire': 'moyen', 'moyenne': 'moyen', 'nan': 'Non_renseigné'})
        # saving the cleaned file as a .csv
        df.to_csv('fichier_clean.csv')

    except EmptyDataError:
        time.sleep(10)
    except FileNotFoundError:
        time.sleep(10)

def main():
    datacleaning()
    help(datacleaning)


# pour lancer le test de la fonction dans ce module
if __name__ == '__main__':
    main()
