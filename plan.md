# Express.js + SQLite Rebuild Plan

## Tech Stack
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: SQLite via better-sqlite3 (synchronous, fast, no ORM overhead)
- **Templating**: EJS (similar to Django templates, server-rendered)
- **Auth**: express-session + bcrypt (session-based like Django)
- **CSS**: Keep existing Bootstrap (reuse static/css/style.css)
- **QR Codes**: qrcode package
- **Email**: nodemailer (console transport for dev)

## Directory Structure
```
express-app/
├── package.json
├── server.js                  # Entry point
├── db/
│   ├── schema.sql             # SQLite schema (all 10+ tables)
│   ├── seed.js                # Setup roles + initial data
│   └── connection.js          # better-sqlite3 connection
├── middleware/
│   ├── auth.js                # requireLogin, requireRole
│   └── locals.js              # Template locals (user, flash messages)
├── routes/
│   ├── auth.js                # Login/logout
│   ├── dashboard.js           # Dashboard, calendar, reports
│   ├── customers.js           # CRUD
│   ├── inventory.js           # CRUD + QR labels
│   ├── rentals.js             # CRUD + wizard (4 steps)
│   ├── seamstress.js          # CRUD + status updates
│   ├── events.js              # CRUD + wizard (4 steps)
│   └── invoices.js            # List, detail, payments, print
├── services/
│   ├── availability.js        # get_available_quantity logic
│   ├── invoicing.js           # create/calculate invoice totals
│   └── email.js               # Async email notifications
├── views/                     # EJS templates (port from Django)
│   ├── layout.ejs             # Base layout (navbar, sidebar)
│   ├── login.ejs
│   ├── dashboard/
│   │   ├── index.ejs
│   │   ├── calendar.ejs
│   │   └── reports.ejs
│   ├── customers/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   └── form.ejs
│   ├── inventory/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   ├── form.ejs
│   │   └── labels.ejs
│   ├── rentals/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   ├── contract.ejs
│   │   ├── wizard_step1.ejs
│   │   ├── wizard_step2.ejs
│   │   ├── wizard_step3.ejs
│   │   └── wizard_confirm.ejs
│   ├── seamstress/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   └── form.ejs
│   ├── events/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   ├── wizard_step1.ejs
│   │   ├── wizard_step2.ejs
│   │   ├── wizard_step3.ejs
│   │   └── wizard_confirm.ejs
│   ├── invoices/
│   │   ├── list.ejs
│   │   ├── detail.ejs
│   │   └── print.ejs
│   ├── emails/
│   │   ├── rental_confirm.ejs
│   │   ├── event_confirm.ejs
│   │   ├── job_ready.ejs
│   │   └── reminder.ejs
│   └── partials/
│       └── pagination.ejs
├── public/                    # Static files
│   └── css/
│       └── style.css          # Port existing styles
├── Procfile                   # Railway: web: node server.js
├── railway.toml
├── Dockerfile
└── .env.example
```

## Implementation Steps

### Phase 1: Foundation
1. Initialize npm project, install deps
2. Create SQLite schema (all tables matching Django models)
3. Create db connection module
4. Create server.js with Express setup (sessions, static files, EJS)
5. Create auth middleware (requireLogin)
6. Create base layout template

### Phase 2: Auth & Dashboard
7. Login/logout routes
8. Dashboard route + template
9. Calendar view
10. Reports view (Chart.js data)

### Phase 3: CRUD Modules
11. Customer routes (list, detail, create, edit) + templates
12. Inventory routes + QR code generation + templates
13. Seamstress routes + status updates + templates
14. Invoice routes + payment recording + templates

### Phase 4: Wizards
15. Rental wizard (4 steps, session-based) + templates
16. Event wizard (4 steps, session-based) + templates

### Phase 5: Services & Email
17. Availability checking service
18. Invoice calculation & creation service
19. Email notification service
20. Reminder command (can be a script or route)

### Phase 6: Deployment
21. Procfile, railway.toml, Dockerfile
22. Health check endpoint
23. Environment variable handling

## Key Decisions
- **better-sqlite3** over Sequelize/Knex — no ORM, raw SQL, fastest SQLite driver
- **EJS** over Handlebars — supports JS expressions, closer to Django template logic
- **Session-based auth** — matches Django behavior, no JWT complexity
- **Server-rendered** — keeps the same UX, no SPA overhead
- **Same URL structure** — drop-in replacement, bookmarks still work
