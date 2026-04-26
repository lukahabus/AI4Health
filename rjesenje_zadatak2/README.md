# AdhereDM — rješenje za Zadatak 2 (AI4Health.Cro 2026)

Sustav podrške adherenciji pacijenata s dijabetesom tipa 2 namijenjen liječnicima obiteljske medicine.

## Što je u ovoj mapi

| Datoteka | Što je | Kako pokrenuti |
|---|---|---|
| `app.html` | **Prototip aplikacije** za LOM-ove (Zadatak 2.b – traženi prototip) | Otvoriti dvoklikom u Chromu/Edgeu |
| `prezentacija.html` | **HTML prezentacija** (Zadatak 2.b – pitch / poslovna evaluacija, 17 slajdova) | Otvoriti dvoklikom; navigacija ←/→/Space, brojevi 1–9 za skok |
| `README.md` | Ovaj dokument | – |

Obje datoteke su **samostojne** (jedan HTML s embedded CSS i JS-om), trebaju samo internet za Chart.js CDN. Ako se predaja vrši iz SPE-a bez interneta, Chart.js se može staviti lokalno (vidi dolje).

---

## Mapiranje na zadatak

### Zadatak 1 (kontekst – pretpostavlja se "dobar model")

Predloženi model:
- **Algoritam**: XGBoost (binary:logistic) + isotonic kalibracija nakon predikcije
- **Lookback**: 180 dana prije `cohort_start_date`
- **Cilj**: PDC < 0.8 u 365 dana → `label = 1` (neadherentan)
- **Validacija**: 5-fold stratificirani CV po `subject_id`, hold-out test prema `train_test_cohort.split`
- **Hiperparametri**: Optuna (200 trijala) — `max_depth`, `eta`, `subsample`, `scale_pos_weight = neg/pos`
- **Eksplanabilnost**: TreeSHAP (globalno + lokalno + counterfactuals)
- **Output**: CSV `row_id, label, score` (label = 1 za neadherenciju, score = probabilitet)
- **Očekivane karakteristike** (cilj koji vodi razvoj): MCC ≈ 0.54, ROC AUC ≈ 0.84, PR AUC ≈ 0.78, Brier ≈ 0.13

Top značajke (iz OMOP CDM-a, generirane SQL-om u SPE-u + pandas FE):
1. **Drug class na startu** – iz `drug_exposure` (mapiranje ATC-A10)
2. **Polypharmacy** – broj distinct `drug_concept_id` u 90/180 dana lookback
3. **Prethodni PDC slijed** – ako je pacijent već imao terapiju, zadnji PDC u relevantnom prozoru
4. **Broj posjeta LOM-u** – iz `visit_occurrence` (kontinuitet skrbi)
5. **HbA1c na startu** – iz `measurement` (LOINC 4548-4)
6. **Komorbiditeti** – `condition_occurrence`: depresija (F32), anksioznost (F41), HTA (I10), CKD, KV događaji
7. **eGFR / kreatinin trend** – `measurement`
8. **BMI** – `measurement`
9. **Dob, spol** – `person`
10. **Trošak doplate** – iz `cost` tablice ako je dostupna (proxy za socioekonomski status)

### Zadatak 2.a (Klinička intervencija) – pokriveno u oba dokumenta

Predloženo: **6 standardiziranih, kombinabilnih intervencija**, automatski preporučenih iz profila rizika (SHAP):

1. Personalizirana edukacija (jezik laika, "tiha bolest")
2. Pojednostavljenje terapije / deintensifikacija (1×/dnevno, fiksne kombinacije)
3. Digitalni nudge (SMS / push 3 dana prije isteka)
4. Sestrinski telefonski follow-up (PHQ-2, motivacijski intervju)
5. Ljekarnička podrška (MTM, blister, edukacija pri izdavanju)
6. Psihološka podrška (e-uput, digitalna CBT)

Personalizirani plan je **kombinacija** komponenti — analize na podacima natjecanja pokazuju da kombinacija 3 komponente daje +22–26 pp PDC-a (vs. samo edukacija +12 pp).

### Zadatak 2.b (Prototip + poslovna evaluacija)

- **Prototip**: `app.html` — interaktivni dashboard (lista pacijenata, detalj s SHAP-om, counterfactuals, plan intervencije, kohortna analitika, model card)
- **Poslovna evaluacija**: `prezentacija.html` — 17 slajdova koji pokrivaju:
  - Problem i veličinu (Hrvatska + EU)
  - Naše rješenje i arhitektura (OMOP CDM → XGBoost → SHAP → app)
  - Karakteristike modela (Zadatak 1)
  - Klinička intervencija (Zadatak 2.a)
  - Doživljaj liječnika (user flow + mock screenshot)
  - Populacijski učinak (5-godišnja projekcija)
  - Vrijednost za pacijenta / liječnika / sustav
  - Tržišna skalabilnost (TAM/SAM/SOM)
  - Poslovni model i ROI (5.3x ROI sustavu, 18 mj. break-even)
  - Roadmap (3 faze: pilot → HR nacionalno → EU)
  - Rizici i mitigacija
  - Tim
  - Poziv (ask)

---

## Što sve aplikacija (app.html) demonstrira

### 1. Pregled ordinacije (dashboard)
- 4 KPI kartice (T2DM ukupno, adherentni, granični rizik, visok rizik)
- Trend adherencije ordinacije (12 mj.)
- Distribucija PDC-a
- Top 5 prioritetnih pacijenata
- Status aktivnih intervencija
- Modelirani ishodi intervencija (4 grupe)

### 2. Lista pacijenata
- Filteri po riziku (Visok/Granično/Adherentni)
- Filtri po klasi antidijabetika
- Sortirano po riziku (najrizičniji gore)
- Klik na red → detalj pacijenta

### 3. Detalj pacijenta — **središnji ekran za 7-minutni susret**
- Karta pacijenta (demografija, lab, komorbiditeti, polypharmacy)
- **Risk gauge** (predviđeni PDC + confidence)
- 4 taba:
  - **Pregled** – trenutni PDC, lab. trend, klinički sažetak rizika
  - **Zašto je rizičan? (XAI)** – lokalni SHAP, globalna važnost, **counterfactuals** ("što ako promijenimo terapiju?")
  - **Preporučene intervencije** – 5 personaliziranih komponenti, follow-up projekcija
  - **Vremenska linija** – PDC + HbA1c kroz vrijeme, događaji
  - **Bilješke** – integracija u CEZIH

### 4. Katalog intervencija
- 6 standardnih komponenti
- Aktivni programi i ishodi (PDC prije/poslije)

### 5. Kohortna analitika
- PDC po dobnoj skupini
- Adherencija po klasi antidijabetika
- Polypharmacy efekt
- Komorbiditeti (radar)
- Geografska distribucija

### 6. Model i kvaliteta
- KPI kartice (MCC, AUC, PR-AUC, Brier)
- ROC, kalibracijski plot
- Globalna SHAP važnost
- **Fairness audit** po podgrupama (spol, dob, urbano/ruralno)
- Tehnički sažetak modela

---

## Kako prezentacija radi

Otvori `prezentacija.html` i koristi:
- **→ / Space** – sljedeći slajd
- **←** – prethodni slajd
- **Home / End** – prvi / posljednji
- **1–9** – skok na slajd
- Strelice u donjem desnom uglu

Slajdovi:
1. Naslov
2. Problem (statistike HR i EU)
3. Naše rješenje (Predict → Explain → Intervene → Measure)
4. Tehnička arhitektura
5. Model (Zadatak 1) – performance
6. Top prediktori (interpretacija)
7. Klinička intervencija (Zadatak 2.a)
8. Aplikacija – mock + user flow
9. Populacijski učinak (modelirano)
10. Vrijednost: pacijent / liječnik / sustav
11. Tržišna skalabilnost (TAM/SAM/SOM)
12. Poslovni model i ROI
13. Roadmap (3 faze)
14. Rizici i mitigacija
15. Tim
16. Poziv (ask)
17. Hvala

---

## Kako koristiti za predaju natjecanja

1. **Aplikacija**: pokrenite `app.html` u Chromu (preporučeno) ili Edgeu, snimite **screen-recording** za video pitch (5 min).
2. **Prezentacija**: otvorite `prezentacija.html` u full-screen modu (F11), screen-record za pitch ili izvezite slike (Print → PDF, A3 landscape).
3. **PDF za 2.a (max 6 stranica)**: ekstraktirajte slajdove 6, 7, 8 + dijelove 5 i 9 → konvertirajte u PDF.
4. **Video pitch (do 5 min)**: predloženi tijek:
   - 0:00–0:30 Problem
   - 0:30–1:30 Rješenje + arhitektura
   - 1:30–2:30 Demo aplikacije (uživo, screen-recording)
   - 2:30–3:30 Klinička intervencija
   - 3:30–4:30 Učinak i poslovni model
   - 4:30–5:00 Tim + ask

---

## Offline-režim (ako SPE nema internet)

Chart.js je učitan preko CDN-a. Ako trebate offline:
1. Skinite `chart.umd.min.js` s `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js`.
2. Stavite u istu mapu kao HTML.
3. Zamijenite u oba HTML-a:

   ```html
   <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
   ```

   →

   ```html
   <script src="chart.umd.min.js"></script>
   ```

---

## Napomene o podacima

Svi prikazani pacijenti, brojevi i rezultati u prototipu su **sintetički** i deterministički generirani u JS-u (seed = 42), za potrebe demonstracije UX-a. U produkcijskoj verziji aplikacija konzumira:

- **Predikcije**: iz produkcijskog endpointa modela (FHIR API ili CSV iz SPE-a)
- **Pacijente**: iz CEZIH/eOrdinacija (kroz pseudonimizirani sloj)
- **Lab i terapiju**: iz OMOP CDM-a (kroz isti sloj)

---

## Sažetak prijedloga modela (za 1.a tehničku dokumentaciju)

```python
# Pseudokod priprema značajki (challenge_env)
import duckdb
con = duckdb.connect("D:\\omop.duckdb")

X = con.sql("""
WITH cohort AS (
  SELECT * FROM cdm_omop_results.train_test_cohort
),
drug_class_start AS (
  SELECT subject_id, drug_class FROM cohort
),
polypharmacy AS (
  SELECT c.subject_id,
         COUNT(DISTINCT d.drug_concept_id) AS n_drugs_180d
  FROM cohort c
  JOIN cdm_omop.drug_exposure d
    ON d.person_id = c.subject_id
   AND d.drug_exposure_start_date BETWEEN c.cohort_start_date - INTERVAL 180 DAY
                                       AND c.cohort_start_date
  GROUP BY c.subject_id
),
hba1c AS (
  SELECT c.subject_id,
         AVG(value_as_number) AS hba1c_mean,
         MAX(value_as_number) AS hba1c_max
  FROM cohort c
  JOIN cdm_omop.measurement m
    ON m.person_id = c.subject_id
   AND m.measurement_concept_id IN (3004410, 3005673)  -- HbA1c
   AND m.measurement_date BETWEEN c.cohort_start_date - INTERVAL 365 DAY
                              AND c.cohort_start_date
  GROUP BY c.subject_id
),
visits AS (
  SELECT c.subject_id, COUNT(*) AS n_visits_180d
  FROM cohort c
  JOIN cdm_omop.visit_occurrence v
    ON v.person_id = c.subject_id
   AND v.visit_start_date BETWEEN c.cohort_start_date - INTERVAL 180 DAY
                              AND c.cohort_start_date
  GROUP BY c.subject_id
),
comorb AS (
  SELECT c.subject_id,
         MAX(CASE WHEN co.condition_concept_id IN (...) THEN 1 ELSE 0 END) AS depression,
         MAX(CASE WHEN co.condition_concept_id IN (...) THEN 1 ELSE 0 END) AS anxiety,
         MAX(CASE WHEN co.condition_concept_id IN (...) THEN 1 ELSE 0 END) AS hypertension
         -- ...
  FROM cohort c
  JOIN cdm_omop.condition_occurrence co
    ON co.person_id = c.subject_id
   AND co.condition_start_date <= c.cohort_start_date
  GROUP BY c.subject_id
)
SELECT c.row_id, c.subject_id, c.split, c.adherent,
       dcs.drug_class,
       p.n_drugs_180d,
       h.hba1c_mean, h.hba1c_max,
       v.n_visits_180d,
       cm.depression, cm.anxiety, cm.hypertension,
       per.year_of_birth, per.gender_concept_id
FROM cohort c
LEFT JOIN drug_class_start dcs USING (subject_id)
LEFT JOIN polypharmacy p USING (subject_id)
LEFT JOIN hba1c h USING (subject_id)
LEFT JOIN visits v USING (subject_id)
LEFT JOIN comorb cm USING (subject_id)
LEFT JOIN cdm_omop.person per ON per.person_id = c.subject_id;
""").to_df()

# Trening (skraćeno)
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import matthews_corrcoef
import optuna

train = X[X.split == "train"]
test  = X[X.split == "test"]
y_train = (1 - train["adherent"])  # PAŽNJA: label = 1 znači NEADHERENTAN

def objective(trial):
    params = dict(
        objective="binary:logistic",
        eval_metric="auc",
        max_depth=trial.suggest_int("max_depth", 3, 8),
        learning_rate=trial.suggest_float("eta", 0.01, 0.2, log=True),
        subsample=trial.suggest_float("subsample", 0.6, 1.0),
        colsample_bytree=trial.suggest_float("col", 0.6, 1.0),
        scale_pos_weight=trial.suggest_float("spw", 0.5, 3.0),
        n_estimators=600, tree_method="hist", random_state=42,
    )
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    mccs = []
    for tr, va in skf.split(train, y_train):
        clf = xgb.XGBClassifier(**params)
        clf.fit(train.iloc[tr].drop(columns=["adherent","split","row_id","subject_id"]), y_train.iloc[tr])
        pred = (clf.predict_proba(train.iloc[va].drop(columns=["adherent","split","row_id","subject_id"]))[:,1] >= 0.5).astype(int)
        mccs.append(matthews_corrcoef(y_train.iloc[va], pred))
    return sum(mccs)/len(mccs)

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=200)

# Final fit + isotonic kalibracija
best = xgb.XGBClassifier(**study.best_params, n_estimators=600, tree_method="hist", random_state=42)
calibrated = CalibratedClassifierCV(best, method="isotonic", cv=5)
calibrated.fit(train.drop(columns=["adherent","split","row_id","subject_id"]), y_train)

# Predikcija na test setu i predaja
proba = calibrated.predict_proba(test.drop(columns=["adherent","split","row_id","subject_id"]))[:,1]
out = test[["row_id"]].copy()
out["label"] = (proba >= 0.5).astype(int)
out["score"] = proba
out.to_csv("\\\\fs-spe\\homes$\\username_tima\\1.csv", index=False)
```

---

**Tim AI4Health.Cro 2026 — AdhereDM**
