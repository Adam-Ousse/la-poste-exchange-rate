import requests
from bs4 import BeautifulSoup
import pickle as pkl
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
today = datetime.today().date()
url = "https://www.poste.tn/change.php"
addTodayData = False

         
try : 
    df= pd.read_csv("data.csv",parse_dates=["date"])
    print("Found data.csv")
    if any(df["date"].dt.date == today):
        print("Data already up to date")
        addTodayData = False
    else:
        print("Data not up to date")
        addTodayData = True
except:
    print("data.csv not found")
    df = pd.DataFrame(columns=["monnaie","sigle","unite","achat","vente","date"])
    addTodayData = True
df["unite"]=df["unite"].astype(int)
df["achat"]=df["achat"].astype(float)
df["vente"]=df["vente"].astype(float)
df["monnaie"] = df["monnaie"].astype("category")
df["sigle"] = df["sigle"].astype("category")
if addTodayData: 
    try :
        with open(f"{today.strftime("%d-%m-%Y")}.pkl", "rb") as f:
            soup = pkl.load(f)
        print(f"Found {today.strftime("%d-%m-%Y")}.pkl")
    except:
        print(f"{today.strftime("%d-%m-%Y")}.pkl not found proceeding to scrap from the internet")
        response = requests.get(url,verify=False)
        response.encoding="utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        with open(f"{today.strftime("%d-%m-%Y")}.pkl","wb") as f:
            pkl.dump(soup,f)   
        
    #<table cellspacing="1" cellpadding="0" border="0">
    table = soup.find("table",{"cellspacing":"1","cellpadding":"0","border":"0"})
    date=""
    new_data=[]
    for i, tr in enumerate(table.find_all("tr")):
        if i == 0:
            date = tr.find("td").text.split("le ")[-1]
        elif i > 1:
            tds = tr.find_all("td")
            monnaie, sigle, unite, achat, vente = [td.text for td in tds]
            if not achat:
                achat = None
            if not vente:
                vente = None
            new_data.append({"monnaie": monnaie, "sigle": sigle, "unite": unite, "achat": achat, "vente": vente, "date": date})

        
    new_df = pd.DataFrame(new_data)
    df["unite"]=df["unite"].astype(int)
    df["achat"]=df["achat"].astype(float)
    df["vente"]=df["vente"].astype(float)
    df["monnaie"] = df["monnaie"].astype("category")
    df["sigle"] = df["sigle"].astype("category")
    df["date"] = pd.to_datetime(df["date"])
    df = pd.concat([df, new_df], ignore_index=True)   
    df.to_csv("data.csv",index=False)

print(df)
print(df.dtypes)
df_melted = df.melt(id_vars=["monnaie", "unite"], value_vars=["achat", "vente"], 
                    var_name="type", value_name="value")
df_melted["normalized_value"] = df_melted["value"] / df_melted["unite"]
categories=df_melted.sort_values(by="normalized_value",ascending=True)["monnaie"].unique()
sns.set_theme(font_scale=.75)
g=sns.catplot(kind="bar", data=df_melted, x="monnaie", y=df_melted["normalized_value"],hue="type",order=categories)
plt.xticks(rotation=45)
g.set_axis_labels("Monnaie", "Valeur par Unité")
g.fig.suptitle(f"Valeur par Unité des Monnaies le {today}",y=1.03)
plt.show()
sns.catplot(kind="point",markers=True,x="date",y=df["achat"]/df["unite"],hue="monnaie",data=df)
plt.show()
