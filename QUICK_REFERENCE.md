# 📋 QUICK REFERENCE CARD - Système Suivi Utilisateurs

## 🎯 Mission
Mwen vle used utilisateur konekte nan system nan epi mwen vle konn le yo konekte epi dekonekte

## ✅ Livré
**Système complet de monitoring utilisateurs en temps réel**

---

## 🌐 URLs Important

| URL | Fonction |
|-----|----------|
| `/utilisateurs/dash_admin/` | Dashboard - Click "En Ligne" card |
| `/utilisateurs/active-users/` | Paj monitoring (Admin only) |
| `/utilisateurs/api/active-users/` | JSON API endpoint |

---

## 👥 Utilisateurs (16 Total)

### Admins (4)
- `Fedanoir` 
- `Anderson002`
- `admin_test`
- `admin001`

### Directeurs (4)
- `Wilbert001`
- `directeur_test`
- `directeur001`
- `directeur002`

### Secrétaires (4)
- `Hantz123`
- `secretaire_test`
- `secretaire001`
- `secretaire002`

### Archives (4)
- `Peterson002`
- `archives_test`
- `archives001`
- `archives002`

---

## 🛠️ Commandes Utiles

```bash
# Importer users depuis CSV
python manage.py add_users --file users_sample.csv

# Ajouter 5 directeurs automatiquement
python manage.py add_users --role directeur --count 5

# Mode interactif
python manage.py add_users --interactive

# Voir tous users + sessions
python manage.py shell
>>> from django.contrib.auth import get_user_model; from utilisateurs.models import UserSession
>>> User = get_user_model()
>>> User.objects.count()
>>> UserSession.objects.filter(is_active=True).count()
```

---

## 📊 Ce Que Vous Voyez sur Paj

### 1️⃣ Header Stats
```
En Ligne: 4        (Real-time count)
Total: 16          (All users)
```

### 2️⃣ Table: Tous les Utilisateurs
- Nom + Rôle (color-coded)
- Status: 🟢 En Ligne / ⚫ Hors Ligne / ❓ Jamais Connecté
- Dernière connexion timestamp
- IP address
- Heure déconnexion (ou "Toujours Connecté")

### 3️⃣ Table: Actuellement Connectés
- Utilisateurs avec `is_active=True`
- Durée: `2h 30m 45s` format
- 🟢 Actif avec pulse

### 4️⃣ Table: Déconnexions Récentes
- Dernières 20 déconnexions
- Durée session totale
- Auto-refresh 30 sec

---

## 🔄 Workflow Login/Logout

```
USER LOGIN
   ↓ [Browser]
APP MIDDLEWARE
   ↓ [Auto-detect authenticated user]
USERSESSION CREATED
   - login_time = NOW
   - is_active = True
   - ip_address = captured
   ↓ [Updated on each request]
MIDDLEWARE UPDATES SESSION
   - is_active stays True
   - Each request tracked
   ↓ [User makes action]
USER LOGOUT
   ↓ [Django session deleted]
SIGNAL FIRES
   ↓ [post_delete signal]
USERSESSION UPDATED
   - logout_time = NOW
   - is_active = False
   ↓ [Next time admin views page]
PAJE SHOWS "Hors Ligne" + timestamp
```

---

## 🎨 Color Coding

| Badge | Couleur | Signification |
|-------|---------|---------------|
| ADMIN | 🔴 Red | Administrateur |
| DIRECTEUR | 🔵 Blue | Directeur |
| SECRETAIRE | 🟡 Yellow | Secrétaire |
| ARCHIVES | ⚫ Gray | Archives |

---

## ⚙️ Configuration

### Settings (Django)
- ✅ RoleAccessMiddleware activé
- ✅ UserSession model enregistré
- ✅ Signal handlers activés
- ✅ @admin_required decorator fonctionnel

### Database
- ✅ Table `user_sessions` créée
- ✅ Indexes optimisés
- ✅ Migrations appliquées

### Cache (Optional)
```python
# Auto-refresh every 30 seconds on active_users.html
setTimeout(function() {
    location.reload();
}, 30000);
```

---

## 🔐 Permissions

```python
@admin_required  # Only admins can access
def active_users_list(request):
    # All admins see all users
    # No data restriction
```

---

## 📈 Stats Disponibles

```python
# Total users
User.objects.count()  # = 16

# Online users
UserSession.objects.filter(is_active=True).count()

# Total sessions (all time)
UserSession.objects.count()

# User's last session
UserSession.objects.filter(user=user).latest('login_time')

# Session duration
session.duration_display  # = "2h 30m 45s"

# Login time
session.login_time_display  # = "11/11/2025 14:32:15"

# Logout time
session.logout_time_display  # = "11/11/2025 15:00:22"
```

---

## 🚨 Troubleshooting

**Problem**: Users not appearing as "En Ligne"
- **Solution**: User must login through `/utilisateurs/login/`
- **Not work**: Last login column (old tracking method)
- **Now**: Middleware auto-creates UserSession

**Problem**: Can't access `/utilisateurs/active-users/`
- **Solution**: Must be admin (role='admin')
- **Check**: `@admin_required` decorator applied
- **Verify**: User role is lowercase 'admin'

**Problem**: IP address showing as None
- **Solution**: Middleware captures on each request
- **Check**: User made at least one request after login

---

## 📚 Documentation Files

```
/root/
├── USER_MANAGEMENT_GUIDE.md         ← Complete guide
├── IMPLEMENTATION_SUMMARY.md        ← What was built
├── QUICK_REFERENCE.md               ← This file
└── users_sample.csv                 ← Import template
```

---

## 🎯 Next Time You Need To

### Add more users
```bash
python manage.py add_users --file yourfile.csv
```

### Check who's online
```
Visit: /utilisateurs/active-users/
```

### Export user list
```python
# In Django shell
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
for u in users:
    print(f"{u.username},{u.email},{u.role}")
```

### Delete test users
```bash
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username__contains='test').delete()
```

---

## 💡 Pro Tips

1. **CSV Import** - Fastest way to add many users
2. **Role-based** - Quick for similar users
3. **Interactive** - Best for manual setup
4. **Always Check** - Verify users via shell after import
5. **Backup** - Export user list before bulk operations

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-11-11

---

*Pour assistance: Consultez USER_MANAGEMENT_GUIDE.md*
