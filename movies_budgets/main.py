
import pandas as pd

def clean_input_data():
    df = pd.read_csv('movie-budgets.csv')
    df['release_date']=pd.to_datetime(df['release_date'], format='%b %d, %Y')
    df = df.drop(columns=["Unnamed: 0"])
    df = df.sort_values(by='release_date')
    df['runtime'] = df['runtime'].str.replace(' minutes', '', regex=False)

    return df


def main():
    df = clean_input_data()
    print((df['runtime'].isna() & df['production_company'].isna()).sum())


if __name__ == "__main__":
    main()