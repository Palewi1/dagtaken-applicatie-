import json
from database_wrapper import Database

# --- database verbinding ---
db = Database(host="localhost", gebruiker="root", wachtwoord="WelkomVliegtuig@2025!", database="attractiepark")

# --- haal eerste personeelslid op ---
db.connect()
personeelslid_data = db.execute_query("SELECT * FROM personeelslid LIMIT 1")
db.close()
personeelslid = personeelslid_data[0]

# --- bereken maximale fysieke belasting ---
leeftijd = personeelslid["leeftijd"]
aangepast = personeelslid.get("verlaagde_fysieke_belasting")
if aangepast:
    max_belasting = aangepast
elif leeftijd <= 24:
    max_belasting = 25
elif leeftijd <= 50:
    max_belasting = 40
else:
    max_belasting = 20
personeelslid["max_fysieke_belasting"] = max_belasting

# --- haal onderhoudstaken op ---
db.connect()
taken = db.execute_query("SELECT * FROM onderhoudstaak")
db.close()

# --- filter geschikte taken ---
geschikte_taken = []
for taak in taken:
    if taak["beroepstype"] == personeelslid["beroepstype"]:
        if taak["bevoegdheid"] <= personeelslid["bevoegdheid"]:
            if taak["fysieke_belasting"] <= max_belasting:
                geschikte_taken.append(taak)

# --- maak JSON structuur ---
dagtakenlijst = {
    "personeelsgegevens": {
        "naam": personeelslid["naam"],
        "werktijd": personeelslid["werktijd"],
        "beroepstype": personeelslid["beroepstype"],
        "bevoegdheid": personeelslid["bevoegdheid"],
        "specialist_in_attracties": personeelslid["specialist_in_attracties"],
        "pauze_opsplitsen": personeelslid["pauze_opsplitsen"],
        "max_fysieke_belasting": max_belasting
    },
    "weergegevens": {
        "temperatuur": 20,
        "regen_kans": 30
    },
    "dagtaken": geschikte_taken,
    "totale_duur": sum([t["duur"] for t in geschikte_taken])
}

# --- schrijf JSON bestand ---
with open("dagtakenlijst_personeelslid_x.json", "w") as f:
    json.dump(dagtakenlijst, f, indent=4)

print("Klaar! JSON-bestand is aangemaakt.")
