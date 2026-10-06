# RepairLens AI

## AI-Powered Repair Decision Assistant

RepairLens AI helps users understand possible device problems before deciding whether to repair or replace a device. Users provide a device category, brand, model, problem description, and an image. The application analyzes the available evidence and returns possible problems, possible causes, confidence, repair guidance, cost estimates, and safe next steps where supported by the current implementation.

RepairLens AI provides possible causes and estimates, not guaranteed technical diagnoses.

## Project Overview

Repair decisions can be difficult when users do not know:

- what might be wrong with a device;
- whether a repair is worthwhile;
- whether a technician quote is reasonable; or
- whether professional inspection is needed.

RepairLens AI is designed to provide useful context before a user makes a repair decision. It is an assistance tool, not a replacement for a qualified repair technician.

## Key Features

The current project includes:

- Device category, brand, model, and problem-description input
- JPG, JPEG, PNG, and WEBP image upload in the diagnosis flows
- Google Gemini analysis through the existing AI engine
- Local Demo Mode when Gemini is unavailable, the API key is missing, or an AI response cannot be used
- Evidence-aware analysis separating visible evidence, user-reported symptoms, and uncertainties
- Possible problem and possible-cause suggestions
- Confidence label and confidence percentage
- Repair-versus-replacement guidance
- Estimated repair time
- Safe troubleshooting guidance
- Safety warnings and professional-help recommendations
- SQLite diagnosis history using SQLAlchemy
- Streamlit dashboard statistics, recent diagnoses, and charts
- Streamlit Cost Estimator for comparing a technician quote with a broad device-aware estimate
- Streamlit Repair History table and complete-record selection
- Flask pages for the newer HTML/CSS/JavaScript frontend
- Flask diagnosis and cost-estimate JSON endpoints
- Responsive frontend styling with sidebar navigation

Real-time repair pricing and nearby repair-shop search are **not currently connected to verified external providers**. The application deliberately displays unavailable states instead of inventing prices, businesses, addresses, ratings, or contact details.

## How It Works

```text
User Input
    ↓
Device Details
    ↓
Problem Description + Image
    ↓
Evidence-Aware AI Analysis
    ↓
Possible Problem and Causes
    ↓
Confidence and Uncertainties
    ↓
Repair Guidance and Safe Troubleshooting
    ↓
Cost Estimate or Quote Comparison
    ↓
Diagnosis Saved to Local History
```

The Flask diagnosis endpoint requires a device category, brand, model, meaningful problem description, and a readable image. The Streamlit diagnosis page supports an optional image and can analyze a description without one. In both interfaces, results are estimates and may require professional confirmation.

## Application Pages

### Dashboard

The Streamlit dashboard reads saved diagnoses from SQLite and displays:

- total diagnoses;
- repair recommendations;
- replacement or professional-assessment recommendations;
- average stored estimated cost;
- recent diagnoses; and
- charts for recommendations, device categories, and estimated costs when enough data exists.

The Flask dashboard currently provides the redesigned dashboard presentation and navigation. Its metric and chart areas are placeholders until the Flask frontend is connected to database-backed dashboard data.

### Diagnose Problem

Users provide device details, describe symptoms, and may upload an image. The AI engine sends the available information to Google Gemini when configured, requests structured output, validates the response, and falls back to Demo Mode when necessary.

The result can include:

- possible problem;
- visible evidence;
- user-reported symptoms;
- uncertainties;
- possible causes;
- confidence;
- likely component;
- estimated repair time;
- repair-or-replace guidance;
- safe troubleshooting;
- safety warning; and
- professional-help recommendation.

Successful assessments are saved to the SQLite diagnosis history.

### Cost Estimator

The Streamlit Cost Estimator uses a device-category baseline range and adjusts it for terms such as screen, display, compressor, motor, software, slow performance, or settings. It compares that estimate with the technician quote and reports whether the quote is within, above, or below the expected range.

The Flask `/api/cost-estimate` endpoint provides the same type of broad estimate and quote assessment for the new frontend. It does not retrieve verified live market prices.

Repair costs are estimates only. Actual prices vary by device model, replacement parts, labor, location, service provider, and device condition.

### Repair History

The Streamlit Repair History page reads saved diagnosis records from SQLite, displays them in a table, and allows the user to select a record to view its complete details. An empty database is handled with a clear empty-state message.

The Flask history route currently displays the new frontend's empty-state presentation; database-backed history rendering remains a future Flask integration.

### About

The About page explains the purpose of RepairLens AI, what users can provide, what the assistant can return, and the limitations of AI-assisted repair guidance.

## AI Diagnosis

The AI engine uses Google Gemini through `google-genai` when `GEMINI_API_KEY` is configured. It requests structured JSON and normalizes the response before it is shown or saved.

If Gemini cannot be used, the application uses a local Demo Mode assessment. This can happen when:

- `GEMINI_API_KEY` is missing;
- the Gemini request fails;
- the response is malformed; or
- image processing fails.

The AI prompt explicitly avoids dangerous instructions involving high voltage, exposed wiring, batteries, gas appliances, refrigerants, dangerous chemicals, unsafe disassembly, and complex vehicle repairs. Dangerous or uncertain situations should be referred to a qualified professional.

## Cost Estimation

The current estimator is a broad rule-based estimate and quote comparison. It is not a live pricing service and should not be interpreted as a guaranteed repair price.

The estimate can vary according to:

- device category, brand, and model;
- problem description;
- replacement parts;
- labor;
- location;
- service provider; and
- device condition.

## Technology Stack

Technologies used directly by the current application include:

- Python
- Streamlit
- Flask
- Jinja templates
- HTML, CSS, and JavaScript
- Google Gemini via `google-genai`
- `python-dotenv`
- SQLAlchemy
- SQLite
- pandas
- Matplotlib

The dependency file also declares NumPy, scikit-learn, Seaborn, Requests, LangChain, and LangChain Community for the project's supported environment and planned extensions.

## Project Structure

```text
RepairLens AI/
├── app.py                  # Complete Streamlit application
├── server.py               # Flask pages and JSON API endpoints
├── ai_engine.py            # Gemini integration and Demo Mode
├── database.py             # SQLAlchemy model, SQLite setup, and sessions
├── utils.py                # Streamlit formatting and custom styling
├── price_service.py        # Honest unavailable-state price provider scaffold
├── places_service.py       # Honest unavailable-state places provider scaffold
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Local secrets, databases, and virtual environments
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── diagnose.html
│   ├── cost_estimator.html
│   ├── history.html
│   └── about.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

`repairlens.db` is created locally when the database module initializes and is ignored by Git.

## Requirements

The project is developed and tested with Python 3.13. The supported dependency ranges are listed in `requirements.txt`.

## Installation

Windows PowerShell:

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd "RepairLens AI"
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If the repository is already downloaded, start at the `cd` and virtual-environment steps.

## Environment Variables

Copy the example file to `.env`:

```powershell
Copy-Item .env.example .env
```

Set your own Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional provider placeholders are also documented in `.env.example`:

```env
REPAIR_PRICE_API_URL=
PLACES_API_URL=
```

These optional values do not currently activate a provider adapter. Leave them blank to retain the explicit unavailable states. Never commit `.env` or expose an API key in source code.

## Run the Project

### Streamlit application

The complete original application runs with:

```powershell
streamlit run app.py
```

### Flask application

The newer HTML/CSS/JavaScript frontend runs with:

```powershell
py server.py
```

Open the Flask application at:

```text
http://127.0.0.1:5000
```

The Flask frontend shares the existing AI engine and database. Its diagnosis and cost-estimate requests are submitted asynchronously through JavaScript to `/api/diagnose` and `/api/cost-estimate`.

## Database

SQLite and SQLAlchemy are used for local persistence. The database is created automatically as `repairlens.db` beside the application files.

Saved diagnosis records include the date, device details, problem description, possible problem, confidence, estimated cost value where available, recommendation, likely component, price-confidence state, reasoning, and analysis basis.

## Safety and Limitations

RepairLens AI is an assistance tool and does not replace a qualified repair technician.

- AI-generated results are possible causes and estimates.
- An image cannot reveal every internal fault.
- Confidence is an estimate, not scientific certainty.
- Repair costs vary by location, parts, labor, model, and provider.
- Professional inspection may be required.
- Users should seek professional assistance for dangerous, uncertain, or complex repairs.
- The application is designed not to provide unsafe instructions for high-voltage equipment, exposed wiring, batteries, gas, refrigerants, dangerous chemicals, unsafe disassembly, or complex vehicle repairs.

## Real-World Data Limitations

Real-time repair pricing and nearby repair-business information may require external service/API integration and are not represented as verified data unless explicitly provided by a connected service.

The current `price_service.py` and `places_service.py` files are integration scaffolds. They return honest unavailable states and do not fabricate provider results.

## Future Improvements

Potential future work includes:

- verified real-time repair-price providers;
- nearby repair-shop and authorized service-center search;
- richer image-based diagnosis;
- broader device and symptom coverage;
- improved repair-versus-replace analysis;
- database-backed dashboard and history pages in the Flask frontend;
- user accounts and cloud deployment; and
- exportable diagnosis reports.

## Contributing

Improvements, bug fixes, documentation updates, and feature suggestions are welcome. Please keep changes focused, avoid committing secrets or local databases, and describe how changes were tested.

## License

License information will be added.

## Author / Project

Developed as an academic/project initiative.
