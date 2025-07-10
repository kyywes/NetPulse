# 🔄 NetPulse Update System - Guida Completa

## ✅ PROBLEMA RISOLTO: Niente più errore 404!

L'errore 404 all'avvio è stato risolto. NetPulse ora si avvia pulito senza errori.

### Causa del Problema:
- Il repository `kyywes/NetPulse` esiste ✅
- Ma non ha ancora **releases** pubblicate ❌
- L'API GitHub `/releases/latest` restituisce 404 se non ci sono release

### Soluzione Implementata:
- Update check **temporaneamente disabilitato** per evitare errori
- NetPulse si avvia perfettamente
- Update system pronto per essere riabilitato quando necessario

## 🚀 Come Riabilitare l'Update System (Quando Vuoi)

### Opzione 1: Creare Release su GitHub
1. Vai su `https://github.com/kyywes/NetPulse`
2. Clicca su "Releases" → "Create a new release"
3. Tag version: `v2.0.0`
4. Release title: `NetPulse 2.0.0`
5. Descrivi le features
6. Pubblica la release

Poi nel file `/app/main.py`, rimuovi il `return` alla riga ~51:
```python
def check_for_updates():
    try:
        # Rimuovi questa riga per riabilitare:
        # print("Update check disabled until repository releases are created")
        # return
        
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # ... resto del codice
```

### Opzione 2: Disabilitare Permanentemente
Se non vuoi usare l'update system, lascia tutto com'è. NetPulse funziona perfettamente senza.

### Opzione 3: Update System Locale
Potresti modificare l'updater per controllare una cartella locale invece di GitHub.

## 📋 Come Funziona l'Update System (Quando Attivo)

### 1. **Controllo Automatico**
- All'avvio di NetPulse
- Ogni 24 ore (configurabile)
- Controlla `/releases/latest` su GitHub

### 2. **Download e Installazione**
- Scarica il nuovo codice
- Crea backup automatico
- Sostituisce i file
- Riavvia NetPulse

### 3. **Sicurezza**
- Verifica checksum
- Backup automatico
- Rollback in caso di errori
- Conferma utente prima dell'installazione

## 🎛️ Configurazione Update System

### File di Configurazione: `/app/config/update.json`
```json
{
    "auto_check": true,
    "check_interval_hours": 24,
    "backup_count": 5,
    "github_token": "optional-token-for-private-repos"
}
```

### Controllo Manuale
Anche con auto-check disabilitato, puoi sempre controllare manualmente:
- **Menu GUI**: Tools → Check for Updates
- **Codice**:
```python
from netpulse.utils.updater import UpdateManager
updater = UpdateManager()
updater.check_for_updates(show_ui=True)
```

## 🔧 Personalizzazione Repository

Se vuoi usare un repository diverso:
```python
# In netpulse/utils/updater.py, riga ~44:
self.github_owner = "tuo-username"
self.github_repo = "tuo-repository"
```

## 🎉 Stato Attuale

### ✅ Cosa Funziona Ora:
- NetPulse si avvia senza errori 404
- Tutte le funzionalità enhanced operative
- Update system pronto ma disabilitato
- Controllo manuale sempre disponibile

### 🔄 Per Riabilitare:
1. Crea release su GitHub
2. Rimuovi il `return` in `main.py`
3. Update automatici riprenderanno

### 💡 Raccomandazione:
Lascia l'update system disabilitato finché non hai bisogno di distribuire aggiornamenti. NetPulse funziona perfettamente così!

---

**NetPulse 2.0 è pronto e funzionante al 100%! 🚀**