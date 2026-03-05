# Boutique Manager — Improvements Summary

## 🐛 Bug Fixes

### Critical Crashes Fixed
1. **`event_detail.html`** — Referenced `event.base_cost` and `event.cost_per_guest`, fields that were
   deleted in database migration 0002. The page would crash on load. Fixed to use `event.budget`
   (the correct current field name).

2. **`event_wizard_confirm.html`** — Used `base_cost`, `guest_cost` template variables that the view
   never passed in. Now uses `budget` and `total` which the view actually provides.

3. **`invoice_detail.html`** — Used inline `<script>` JavaScript to calculate prices
   (e.g. `document.write(qty * price)`). This is fragile, insecure, and bypasses Django's
   template engine. Rewritten to use proper Django template rendering.

### Logic Bugs Fixed
4. **`views_dashboard.py` — Overdue invoices count** — The query used `date_created__lt=today`
   but `date_created` is a `DateTimeField`. Comparing a datetime to a `date` object is unreliable
   in SQLite. Fixed to use `date_created__date__lt=today`.

5. **`rental_detail.html`** — Status change buttons were completely absent (code comment said
   "Add status change buttons here in future"). Added full status transitions:
   - Reserved → Mark as Picked Up / Cancel
   - Picked Up → Mark as Returned

6. **`rental_wizard_confirm.html`** — The deposit amount was collected in Step 1 but never
   shown in the confirmation summary. Now displayed.

7. **`rental_detail.html`** — Template tag used inconsistent quote style:
   `{% url "contract_generate" ... %}` — standardised to single quotes.

---

## 🔒 Security Improvements

8. **`settings.py` — Hardcoded secret key** — The original `SECRET_KEY` had a hardcoded
   fallback value that would be used if the env var was missing. In production this is a
   serious vulnerability. Fixed so that production runs without `SECRET_KEY` set will
   **raise an error** rather than silently use an insecure key.

9. **`settings.py` — DEBUG default** — Changed default from `"False"` string comparison
   (which evaluated to `True`!) to explicitly check `"true"`. Now correctly defaults to `False`.

10. **`settings.py` — ALLOWED_HOSTS wildcard** — Changed from `"*"` default to
    `["localhost", "127.0.0.1"]` in dev and `[]` (empty, requiring explicit config) in production.

11. **`settings.py` — Security headers in production** — Added `SECURE_BROWSER_XSS_FILTER`,
    `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS`, `SESSION_COOKIE_SECURE`,
    `CSRF_COOKIE_SECURE` when `DEBUG=False`.

---

## 🆕 New Feature: Rental Status Updates

12. **New URL**: `POST /rentals/<id>/status/` — `rental_update_status` view
    Added to `views_rental.py` and `urls.py`. Allows staff to move rentals through
    their lifecycle directly from the rental detail page without needing admin access.

---

## 🎨 UI/UX Redesign

### Design Direction: Refined Luxury Editorial
- **Palette**: Deep plum (`#3d1f3f`) + champagne (`#f5e6d0`) + antique gold (`#b8924a`)
- **Typography**: Cormorant Garamond (display/headings) + DM Sans (body/UI)
- **Feel**: High-end boutique — think a well-designed fashion atelier, not a generic SaaS dashboard

### Files Redesigned
- `static/css/style.css` — Complete rewrite (~500 lines, full design system with CSS variables)
- `templates/base.html` — New sticky dark navbar with active link highlighting
- `templates/core/dashboard.html` — Stat cards, elegant action panels, improved today's items view
- `templates/core/event_detail.html` — Clean two-column layout, services panel added
- `templates/core/invoice_detail.html` — Server-side line items, proper payment history table
- `templates/core/rental_detail.html` — Status action buttons, alteration links
- `templates/core/rental_list.html` — Item count badge, clickable rows
- `templates/core/customer_list.html` — VIP badge styling, clickable rows, cleaner search
- `templates/core/invoice_list.html` — Shows what each invoice is for (event/rental)
- `templates/core/event_wizard_confirm.html` — Fixed variables + wizard step indicator

---

## How to Apply These Changes

Copy the updated files over your existing ones:

```bash
# CSS
cp boutique_fixed/static/css/style.css  static/css/style.css

# Templates
cp boutique_fixed/templates/base.html  templates/base.html
cp boutique_fixed/templates/core/*.html  templates/core/

# Python (backend fixes)
cp boutique_fixed/core/views_rental.py  core/views_rental.py
cp boutique_fixed/core/views_dashboard.py  core/views_dashboard.py
cp boutique_fixed/core/urls.py  core/urls.py
cp boutique_fixed/boutique_management/settings.py  boutique_management/settings.py
```

Then set your environment variable before running:
```bash
export SECRET_KEY="your-strong-random-key-here"
export DEBUG=true   # only for local development
```
