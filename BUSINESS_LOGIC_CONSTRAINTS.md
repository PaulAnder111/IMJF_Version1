# Kontrent Metye (Business Logic Constraints)

Dokiman sa a dekri tout règ metye ak validasyon ki fòse nan sistèm IMJF la pou asire entegrite done ak lojikal aplikasyon an.

---

## 📋 Rezime Kontrèn yo

### A. Elèv (Inscriptions & Registro)

#### 1. **Yon elèv pa ka inskri plis pase yon fwa nan menm ane**
- **Kote**: `inscriptions/views.py` - `inscription_create()`, `inscription_update()`, `inscription_valider()`
- **Lojik**: Chèk `Inscription` ak kritè: `(nom, prenom, date_naissance, annee_scolaire)` eksakte
- **Mesaj Erè**: "Cet élève est déjà inscrit pour cette année scolaire."
- **Rejè**: Si doublon detekte, inscriptions pa pral pase.

#### 2. **Yon elèv pa ka nan plis pase yon klas nan menm ane**
- **Kote**: `inscriptions/views.py` - `inscription_create()`, `inscription_valider()`
- **Lojik**: Verifye `HistoriqueClasses` - si yon `Eleve` deja gen enrole pou ane a nan yon lòt klas, rejete nouvel inskripyon an.
- **Mesaj Erè**: "Cet élève est déjà assigné à une autre classe pour cette année scolaire."
- **Rejè**: Sistèm empeche transfè / double-enroleman nan differant klas menm ane.

#### 3. **Yon moun pa ka yon elèv E yon ensenyè anmenm tan**
- **Kote**: 
  - `inscriptions/views.py` - `inscription_create()`, `inscription_update()`, `inscription_valider()`, `eleves/views.py` - `ajouter_eleve()`
  - `enseignants/models.py` - `clean()` method
- **Lojik**: 
  - Lè kreye oswa valide yon inscripyon (Eleve create), chèk si moun sa egziste kòm `Enseignant` (menm nom, prenom, date nesans)
  - Lè kreye yon ensenyè, chèk si moun sa deja enrejitre kòm `Eleve`
- **Mesaj Erè**:
  - "Impossible de créer l'élève : cette personne est enregistrée comme enseignant."
  - "Impossible de valider l'inscription : cette personne est enregistrée comme enseignant."
  - "Une personne avec ces informations est déjà enregistrée comme élève." (nan enseignant model)
  - "Impossible d'ajouter : cette personne est déjà enregistrée comme enseignant." (nan eleves add view)
- **Rejè**: Sistèm bloke moun sa pa ka genyen de roles en de kat.

---

### B. Ensenyè (Registro)

#### 1. **Yon ensenyè pa ka inskri plis pase yon fwa**
- **Kote**: `enseignants/models.py` - `unique_together = ('nom', 'prenom')`
- **Lojik**: DB-level constraint plis model validation
- **Mesaj Erè**: "Ce matricule est déjà utilisé." oswa DB IntegrityError
- **Rejè**: Doublons ensenyè bloke otomatikman.

#### 2. **Ensenyè yo dwe gen laj minimom 18 an**
- **Kote**: `enseignants/models.py` - `clean()` method
- **Validasyon**: `age = (date.today() - date_naissance).days // 365; if age < 18: raise ValidationError`
- **Mesaj Erè**: "L'enseignant doit avoir au moins 18 ans."
- **Rejè**: Fòm rejete si laj < 18.

#### 3. **Date rekruteman pa ka dèyè lajour la**
- **Kote**: `enseignants/models.py` - `clean()` method
- **Validasyon**: `if date_recrutement > date.today(): raise ValidationError`
- **Mesaj Erè**: "La date de recrutement ne peut pas être dans le futur."
- **Rejè**: Fòm rejete si date > ajoude a.

---

### C. Email & Telefòn (Inikite Atravè Sistèm Lan)

#### 1. **Imel dwe inik atravè tout modèl yo**
- **Kote**: `core/validators.py` - `validate_unique_across_models('email', value, instance)`
- **Modèl Tcheke**: `utilisateurs.CustomUser`, `enseignants.Enseignant`, `inscriptions.Inscription`
- **Chan**:
  - `CustomUser.email`
  - `Enseignant.email`
  - `Inscription.email_responsable`
- **Mesaj Erè**: "Cette adresse e-mail est déjà utilisée dans le système (par {Model})."
- **Rejè**: Doublons imel bloke atravè tout aplikasyon an.

#### 2. **Telefòn dwe inik atravè tout modèl yo**
- **Kote**: `core/validators.py` - `validate_unique_across_models('telephone', value, instance)` 
- **Modèl Tcheke**: `utilisateurs.CustomUser`, `enseignants.Enseignant`, `inscriptions.Inscription`
- **Chan**:
  - `CustomUser.telephone`
  - `Enseignant.telephone`
  - `Inscription.telephone_responsable`
- **Normalizasyon**: Nimewo telefòn normalize (retire espas, tirets, elatriye) pou konparasyon
- **Mesaj Erè**: "Ce numéro de téléphone est déjà utilisé dans le système (par {Model})."
- **Rejè**: Doublons telefòn bloke atravè tout aplikasyon an.

#### 3. **Telefòn dwe gen prefiks ki akcepte (Digicel/Natcom)**
- **Kote**: `core/validators.py` - `validate_phone_prefix(value)`
- **Validasyon**: Nimewo normalize, dekoupe prefiks, tchekerèn si prefiks egziste nan `settings.PHONE_ALLOWED_PREFIXES`
- **Default Prefiks**: `['34', '35', '36', '37', '38', '39']` (Digicel/Natcom Haiti)
- **Mesaj Erè**: "Le numéro de téléphone doit commencer par un préfixe Digicel ou Natcom valide (ex: 34, 35, 36, 37, 38, 39)."
- **Rejè**: Nimewo ki komanse pa youn nan prefiks yo rejete.
- **Konfigirasyon**: Mete `PHONE_ALLOWED_PREFIXES` nan `settings.py` pou modifye prefiks yo.

---

## 📊 Tablo Rezime Validasyon

| Kontrent | Modèl | Validasyon | Nivwo | Mesaj Erè |
|---|---|---|---|---|
| Inskripyon Inik (ane) | Inscription | 4-tuple: nom, prenom, date_naissance, annee_scolaire | Forms/Views | "Cet élève est déjà inscrit..." |
| Yon Klas (ane) | HistoriqueClasses | eleve + annee_scolaire + classe | Views | "Cet élève est déjà assigné..." |
| Elève ≠ Enseignant | Eleve/Enseignant | nom, prenom, date_naissance | Models/Views | "Impossible de créer..." |
| Enseignant Inik | Enseignant | unique_together(nom, prenom) | DB/Model | IntegrityError ou custom |
| Laj Minimum (18 an) | Enseignant | age >= 18 | Model.clean() | "L'enseignant doit avoir..." |
| Date Rekrut Valide | Enseignant | date_recrutement <= today | Model.clean() | "La date de recrutement..." |
| Imel Atravè Sistèm | CustomUser, Enseignant, Inscription | email unique | Forms/Validator | "Cette adresse e-mail..." |
| Telefòn Atravè Sistèm | CustomUser, Enseignant, Inscription | telephone unique (normalize) | Forms/Validator | "Ce numéro de téléphone..." |
| Prefiks Telefòn | CustomUser, Enseignant, Inscription | telefòn start w/ allowed prefix | Forms/Validator | "Le numéro de téléphone..." |

---

## 🔍 Detay Teknik pou Dev

### Kote Validasyon Fèt

#### **Forms Level** (Django Forms)
- `utilisateurs/forms.py`:
  - `CustomUserCreationForm.clean_email()` - chèk atravè modèl yo
  - `CustomUserUpdateForm.clean_telephone()` - validasyon prefiks + inikite atravè sistèm

- `enseignants/forms.py`:
  - `EnseignantForm.clean_email()` - chèk atravè modèl yo
  - `EnseignantForm.clean_telephone()` - validasyon prefiks + inikite atravè sistèm
  - `EnseignantForm.clean_matricule()` - chèk inikite

- `inscriptions/forms.py`:
  - `InscriptionForm.clean()` - validasyon prefiks telefòn responsab + inikite atravè sistèm pou imel & telefòn

#### **Model Level** (Django Models)
- `utilisateurs/models.py`:
  - `Inscription.unique_together` - ('nom', 'prenom', 'date_naissance', 'annee_scolaire')

- `enseignants/models.py`:
  - `Enseignant.clean()` - laj >= 18, date_recrutement <= today, eleve ≠ enseignant check
  - `Enseignant.unique_together` - ('nom', 'prenom')

#### **Views Level** (Django Views)
- `inscriptions/views.py`:
  - `inscription_create()` - chèk inikite inscripyon, klas inik, eleve ≠ enseignant
  - `inscription_update()` - menm chèk ak create
  - `inscription_valider()` - chèk eleve ≠ enseignant, klas inik anvan create eleve

- `eleves/views.py`:
  - `ajouter_eleve()` - chèk eleve ≠ enseignant anvan create

#### **Validator Module** (`core/validators.py`)
- `validate_phone_prefix(value)` - chèk prefiks
- `validate_unique_across_models(field, value, instance)` - chèk inikite atravè modèl
- `CONTACT_FIELD_MAP` - map modèl pou verifye imel & telefòn

---

## ⚙️ Konfigirasyon

### Modifye Prefiks Telefòn Accepte
Mete nan `imjfpro2025/settings.py`:
```python
# Prefiks telefòn ki pèmèt (Digicel/Natcom Haiti pa default)
PHONE_ALLOWED_PREFIXES = ['34', '35', '36', '37', '38', '39']

# Oswa si w vle diferan prefiks:
PHONE_ALLOWED_PREFIXES = ['30', '31', '32']  # Egzanp
```

### Ajoute Nouvo Modèl nan Verifye Atravè Sistèm
1. Modifye `core/validators.py` - `CONTACT_FIELD_MAP`:
```python
CONTACT_FIELD_MAP = {
    'utilisateurs.CustomUser': {'email': 'email', 'telephone': 'telephone'},
    'enseignants.Enseignant': {'email': 'email', 'telephone': 'telephone'},
    'inscriptions.Inscription': {'email': 'email_responsable', 'telephone': 'telephone_responsable'},
    'mon_app.MonModel': {'email': 'email_field_name', 'telephone': 'telephone_field_name'},  # ← NOUVO
}
```

---

## 🧪 Tès Kontrent

### Egzanp Tès Manual

1. **Tès: Elève inskri 2x menm ane**
   ```
   1. Kreye Inscription: "Jean Doe" (2025-2026) en Classe 6A
   2. Eseye kreye Inscription: "Jean Doe" (2025-2026) en Classe 6B
   → Erè: "Cet élève est déjà inscrit pour cette année scolaire."
   ```

2. **Tès: Moun elève E enseignant**
   ```
   1. Kreye Eleve: "Marie Smith" (1990-05-15)
   2. Eseye kreye Enseignant: "Marie Smith" (1990-05-15)
   → Erè: "Une personne avec ces informations est déjà enregistrée comme élève."
   ```

3. **Tès: Telefòn inik**
   ```
   1. Kreye Enseignant: telefòn = "50934123456" (Enseignant A)
   2. Eseye kreye Inscripyon: telefòn_responsable = "50934123456"
   → Erè: "Ce numéro de téléphone est déjà utilisé dans le système (par Enseignants)."
   ```

4. **Tès: Prefiks Telefòn**
   ```
   1. Eseye kreye Enseignant: telefòn = "50988123456" (88 pa Valid)
   → Erè: "Le numéro de téléphone doit commencer par un préfixe Digicel ou Natcom valide..."
   ```

---

## 📝 Limit & Nòt Teknik

### Konnen Limit
- **Inikite Email/Telefòn**: Validasyon fèt nan nivo aplikasyon (forms/views), pa db-level constraint atravè tab (pa gen foreign key santral). 
  - Solisyon: Si vle garanti DB-level, kreye `Contact` tab santral ke tout modèl fè ForeignKey sou.
- **Normalizasyon Telefòn**: Nimewo normalize pa retire non-digit, men yo AP stoke ak format orijen li (espas, tirets elatriye), sa pouvwa lakòz fò pozitif.
  - Rekòmande: Store telefòn normalize an DB oswa ajoute trigè pou normalize antre.

### Pwochain Amelyorasyon
1. **Signal pre_save** - Repeate validasyon a nivo modèl pou extra proteksyon
2. **Central Contact Model** - Kreye `Contact` tab pou garantir DB-level uniqueness atravè tab
3. **Audit Logging** - Swiv chak rejeye/validasyon pou ek & admin
4. **API Valdation** - Repete validasyon pou REST API sou mèm regles

---

## ✅ Sumeri Implementation

✅ **Komplète**:
- Yon elèv pa ka inskri 2x menm ane
- Yon elèv pa ka nan 2 klas menm ane
- Elève ≠ Enseignant check
- Enseignant inik (nom, prenom)
- Laj minimum 18 an pou enseignant
- Date rekruteman valide
- Email inik atravè sistèm
- Telefòn inik atravè sistèm
- Prefiks telefòn valide (Digicel/Natcom)

❌ **Pa Komplète**:
- DB-level unique constraint atravè tab (volontèrman aktuelman)
- Signal pre_save pou dobl-chèk
- Central Contact model

---

**Dèniye Update**: 2025-11-10  
**Status**: OPERATIONAL ✅
