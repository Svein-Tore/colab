# FOPDT Interaktiv Notatbok – Undervisning

Dette repoet inneholder en interaktiv Jupyter/Colab-notatbok for å lære FOPDT-modellering og PID-tuning.

Notatboken lar elevene:

- Laste opp måledata fra LabVIEW (stegrespons)
- Justere FOPDT-parametre A (amplitude), T (tidskonstant), L (dødtid) og y0 (startnivå) med sliders
- Se rød modellkurve mot blå måledata
- Se statiske standardverdier for referanse
- Få veiledning til å beregne PID-parametre (K, Ti, Td) manuelt
- Lagre figuren som PNG

## Åpne i Google Colab

Klikk på knappen under for å åpne notatboken direkte i Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Svein-Tore/colab/blob/main/FOPDT_Interaktiv_Notatbok_undervisning.ipynb)

> Elevene trenger ikke GitHub-konto eller Google Drive for å åpne notebooken.

## Bruk

1. Åpne notebooken via Colab
2. Last opp måledatafilen fra LabVIEW (f.eks. `pid_test.txt`)
3. Juster sliders til modellen passer måledataene visuelt
4. Noter avleste standardverdier om du ønsker en referanse
5. Bruk informasjonen til å beregne PID-parametre selv
6. Lagre figuren som PNG om ønskelig

## Filstruktur

- `FOPDT_Interaktiv_Notatbok_undervisning.ipynb` – hovednotatbok med interaktiv FOPDT-modell
- `pid_test.txt` – eksempel på stegresponsdata (valgfritt)

---

**Tips for lærere:**  
Denne notatboken fungerer perfekt med små lab-tanker, for eksempel nivåtanker i LabVIEW-laboratorier, hvor Ziegler-Nichols ofte ikke er praktisk på grunn av trege responser.
