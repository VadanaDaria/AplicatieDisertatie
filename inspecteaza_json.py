import json
import os

# Cale absolută către fișierul JSON
cale_fisier = r"C:\Users\vadan\Desktop\Disertatie\Aplicatie\Homo_F508_1.json"

# Citim fișierul
with open(cale_fisier, "r", encoding="utf-8") as f:
    data = json.load(f)

# Afișăm toate cheile principale (nivelul 1)
print("🔑 Câmpuri principale în JSON:")
for cheie in data.keys():
    print("-", cheie)

# Afișăm conținutul parțial
print("\n📖 Conținut parțial:")
for cheie in data:
    valoare = data[cheie]
    print(f"\n🔹 {cheie}:")
    if isinstance(valoare, dict):
        print(f"  - Sub-chei: {list(valoare.keys())[:5]}")
    elif isinstance(valoare, list):
        print(f"  - Tip listă, {len(valoare)} elemente")
        if len(valoare) > 0:
            print(f"    - Exemplu: {str(valoare[0])[:300]}")
    else:
        print(f"  - Valoare: {str(valoare)[:300]}")
