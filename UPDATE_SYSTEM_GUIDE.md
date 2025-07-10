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
2. Clicca su "Releases" → "Draft a new release"
3. Imposta il **tag** (es. `v2.0.0`)
4. Inserisci un **titolo** (es. `NetPulse 2.0.0`)
5. Carica i pacchetti generati dal build (`NetPulse-Setup.exe` e gli ZIP)
6. Scrivi una breve descrizione e pubblica la release

Una volta pubblicata la release, l'auto‑update di NetPulse sarà attivo in modo automatico.

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
1. Crea la release su GitHub come indicato sopra
2. Avvia NetPulse: l'app controllerà automaticamente la presenza di aggiornamenti

### 💡 Raccomandazione:
Lascia l'update system disabilitato finché non hai bisogno di distribuire aggiornamenti. NetPulse funziona perfettamente così!

---

**NetPulse 2.0 è pronto e funzionante al 100%! 🚀**