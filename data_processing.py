import os
import shutil
from pathlib import Path
import pandas as pd
from scipy.optimize import curve_fit
import numpy as np
from scipy.integrate import quad

def func(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

def numericky(x_max, a, b, c, d):
    return quad(func, 0, x_max, args=(a, b, c, d))[0]

def analyticky(x_max,a,b,c,d):
    return d*x_max+c*(x_max**2)/2+b*(x_max**3)/3+a*(x_max**4)/4

def nelin_regrese(df):
    df = df.dropna(how='all')
    #bere první dva sloupečky, předpokládá x souřadnice a f(x)
    xko = np.array(df[0])
    yko = np.array(df[1])
    #získání koeficientů a,b,c,d
    popt, pcov = curve_fit(func, xko, yko)
    a, b, c, d = popt

    x_max = xko[-1]  # Poslední hodnota x
    #integralka = numericky(x_max, a, b, c, d)
    return analyticky(x_max, a, b, c, d)
def num_int(df):
    df = df.dropna(how='all')
    xko = np.array(pd.to_numeric(df[0], errors='coerce'))
    yko = np.array(pd.to_numeric(df[1], errors='coerce'))
    vysl=0
    for i in range(1,len(xko)):
        o=(xko[i]-xko[i-1])*yko[i-1]
        vysl+=o
    return vysl

def novy_adresar(jmeno, adresar):
    #zkontroluje a vytvori adresar
    p = Path(adresar) / jmeno
    p.mkdir(exist_ok=True)
    if any(p.iterdir()):
        print("Adresář 'temp/' existuje a obsahuje soubory. Skript je ukončen.")
        exit()
    return p

def kopirovani(puvodni, adresar):
    with os.scandir(puvodni) as stromek:
        for listek in stromek:
            if listek.is_file():
                tam=os.path.join(adresar,listek.name)
                shutil.copy(listek.path,tam)

#se kterými sloupci souboru chci pracovat
def vyjmout_sloupecky(df):
    return df[[2, 3]]

#pokud mám soubor, ktery má desetinne carky, je treba zaměnit za desetinne tecky
def nahradit_carky_za_tecky(df):
    #return df.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)
    return df.map(lambda x: x.replace(',', '.') if isinstance(x, str) else x)

def zpracovat_soubor(soubor_path, cesta_k_vysledku):
    df = pd.read_csv(soubor_path, sep='\t', header=None, encoding='utf-8')
    df = vyjmout_sloupecky(df)
    df = nahradit_carky_za_tecky(df)
    df.to_csv(soubor_path, sep='\t', index=False, header=False, encoding='utf-8')
    #nelin_regrese(soubor_path, cesta_k_vysledku)
    df = pd.read_csv(soubor_path, sep='\t', header=None, encoding='utf-8')
    vysl=num_int(df)
    vysl2=nelin_regrese(df)
    with open(cesta_k_vysledku, 'a', encoding='utf-8') as f:
        f.write(f"{Path(soubor_path).name}\t{vysl}\t{vysl2}\t{abs(vysl-vysl2)}\n")

def prochazet_adresare(cesta_k_vysledku,adresar):
    with os.scandir(adresar) as stromek:
        for listek in stromek:
            if listek.is_file() and listek.name.endswith('.txt'):
                zpracovat_soubor(listek.path, cesta_k_vysledku)

#smaze adresar a vsechny polozky v nem
def uklizeci_ceta(adresar):
    os.chdir(adresar)
    with os.scandir(os.getcwd()) as stromek:
        for listecek in stromek:
            if listecek.is_file():
                os.remove(listecek.name)
                print(f"soubor {listecek.name} byl smazan")
    os.chdir('..')
    os.rmdir(adresar)
    print(f"adresar {adresar} byl smazan :> gg")

###################################
adresar = 'D:/dulezite_mimo_skolu/vupp_prougrami/17_7_0_nahrani'
os.chdir(adresar)

vysledkovy_adresar=novy_adresar("vysledkovy_adresar",adresar)
vysledky="vysledky1.txt"
cesta_k_vysledku = os.path.join(vysledkovy_adresar, vysledky)
p = novy_adresar("temp",adresar)
kopirovani(adresar,p)
prochazet_adresare(cesta_k_vysledku, p)

uklizeci_ceta(p)
