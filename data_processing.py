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

def nelin_regrese(filename,cesta_k_vysledku):
    df = pd.read_csv(filename, sep='\t', header=None)
    df = df.dropna(how='all')
    #bere první dva sloupečky, předpokládá x souřadnice a f(x)
    xko = np.array(df[0])
    yko = np.array(df[1])
    #získání koeficientů a,b,c,d
    popt, pcov = curve_fit(func, xko, yko)
    a, b, c, d = popt

    x_max = xko[-1]  # Poslední hodnota x
    integral_value = numericky(x_max, a, b, c, d)
    kontrola = analyticky(x_max, a, b, c, d)

    with open(cesta_k_vysledku, 'a', encoding='utf-8') as f:
        f.write(f"{Path(filename).name}\t{integral_value}\t{kontrola}\t{abs(integral_value - kontrola)}\n")

def temp_adresar(adresar):
    #zkontroluje a vytvori docasny adresar
    p = Path(adresar) / "temp"
    p.mkdir(exist_ok=True)
    if any(p.iterdir()):
        print("Adresář 'temp/' existuje a obsahuje soubory. Skript je ukončen.")
        exit()
    #zkopiruje do nej vsechny soubory z aktualniho adresare
    with os.scandir(adresar) as stromek:
        for listik in stromek:
            if listik.is_file():
                dest_path = os.path.join(p, listik.name)
                shutil.copy(listik.path, dest_path)
    return p

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
    #co actually chci dělat s daty o.o
    nelin_regrese(soubor_path, cesta_k_vysledku)

def prochazet_adresare(cesta_k_vysledku,adresar):
    with os.scandir(adresar) as stromek:
        for listek in stromek:
            if listek.is_file() and listek.name.endswith('.txt'):
                zpracovat_soubor(listek.path, cesta_k_vysledku)

#smaze adresar a vsechny polozky v nem
def uklizeci_ceta(adresar):
    os.chdir(adresar)
    with os.scandir(os.getcwd()) as stromek:
        for listik in stromek:
            if listik.is_file():
                os.remove(listik.name)
                print(f"soubor {listik.name} byl smazan")
    os.chdir('..')
    os.rmdir(adresar)
    print(f"adresar {adresar} byl smazan :> gg")

###################################
adresar = 'D:/dulezite_mimo_skolu/vupp_prougrami/17_7_0_nahrani'
os.chdir(adresar)
#vytvorime text soubor s vysledky
vysledky="vysledky.txt"
cesta_k_vysledku = os.path.join(adresar, vysledky)

#vytvoreni docasneho adresare, kde budeme upravovat data dle potreb, pokud neexistuje
p = temp_adresar(adresar)

prochazet_adresare(cesta_k_vysledku,p)

uklizeci_ceta(p)
