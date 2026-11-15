```
barberbot/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── logging_setup.py
│   ├── db/            models.py, session.py, migrations/
│   ├── handlers/      common.py, branches.py, booking.py, bonuses.py, admin.py, master.py
│   ├── keyboards/     menu.py, booking.py, admin.py
│   ├── states/        onboarding.py, booking.py, admin.py
│   ├── services/      slots.py, booking.py, bonuses.py, reminders.py, stats.py
│   ├── middlewares/   db.py, i18n.py, throttle.py
│   └── locales/       uk.json, en.json
├── tests/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```