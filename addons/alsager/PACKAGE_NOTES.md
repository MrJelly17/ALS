# Alsager — Package Notes (do instalacji na Home Assistant)

Wersja: **0.3.0** (MVA-1 + MVA-2 + MVA-3: szkielet, listing encji, ingestion do SQLite).

## Co ten pakiet potrafi
- Lista encji HA (automatycznie z Twojego HA przez Supervisor token, lub mock lokalnie).
- Wybór encji do monitorowania (UI → `config/alsager/monitored.json`).
- **Ingestion** stanów do lokalnej bazy SQLite (`/data/ingestion.db`):
  - **Push**: HA automatyzacja wysyła stan przez `POST /api/ingestion/event`.
  - **Pull**: background polling encji co `poll_interval` s (domyślnie 5).
- Web UI (ingress): Status (Start/Stop ingestion), Entities, Data preview.

## Jak zainstalować na HA (Samba / lokalne repo)
1. W HA włącz add-on **Samba share** (jeśli nie masz) i zamontuj `\\ha-ip\config`.
2. Skopiuj **cały folder `addons/alsager/`** z tego projektu do:
   `\\ha-ip\config\addons\local\alsager`
   (czyli `/config/addons/local/alsager` na hoście HA). Musi zawierać:
   `config.json`, `Dockerfile`, `run.sh`, `requirements.txt`, `src/`, `ui/`, `.dockerignore`.
3. W HA: **Ustawienia → Dodatki → Sklep z dodatkami → ⋮ → Repozytoria → Dodaj** → wpisz `local`.
   Alsager pojawi się w sekcji "Lokalne dodatki".
4. Kliknij **Alsager → Zainstaluj**. Supervisor sam zbuduje obraz z `Dockerfile`
   (nie potrzebujesz Dockera na swoim komputerze).
5. **Uruchom** dodatek. Logi widoczne na stronie dodatku. UI otwórz z paska bocznego HA.

## Połączenie z HA
- W kontenerze dodatku Supervisor automatycznie wstrzykuje `SUPERVISOR_TOKEN`
  i `SUPERVISOR_URL`. Add-on łączy się z HA przez `${SUPERVISOR_URL}/core/api`.
  **Nie trzeba nic konfigurować.**
- Opcjonalnie (zaawansowane) w opcjach dodatku: `ha_base_url`, `ha_token`, `poll_interval`.

## Jak testować ingestion (push)
W HA → Automatyzacja (np. przy zmianie `sensor.accelerometer_x`), akcja "Wyślij zapytanie
do dodatku / webhook" do:
`http://localhost:PORT/api/ingestion/event` z JSON-em:
```json
{
  "entity_id": "sensor.accelerometer_x",
  "new_state": { "state": "{{ states('sensor.accelerometer_x') }}",
                 "attributes": {}, "last_updated": "{{ now() }}" }
}
```
(albo prościej: w UI kliknij "Start ingestion" — wtedy pull co 5s sam zacznie zbierać
zaznaczone encje).

## Ograniczenia / co dalej (MVA-4+)
- Brak jeszcze: eksportu do Parquet, treningu modelu, feedbacku do automatyzacji.
- WebSocket zamiast poll (niższe opóźnienie) — do dodania później.
- UI jest minimalne (dark theme, funkcjonalne).

## Weryfikacja przed wysyłką
- 10/10 pytest (izolowany venv) PASS.
- Live smoke test (uvicorn): health, status, entities(mock), ingestion event→SQLite→data, start/stop — PASS.
- `run.sh` poprawny składniowo; app importuje bez błędów; wszystkie route'y zarejestrowane.
- **Nie zweryfikowano**: samego builda obrazu Docker (na tym hoście nie ma Dockera —
  robi to HA Supervisor przy instalacji). Jeśli build się wywali, sprawdź logi dodatku.
