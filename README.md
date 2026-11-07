# Bedside Drug Guide

A searchable nursing drug reference in a single HTML file. It works offline, with nothing to install and no account needed.

**Open it:** https://darkness-alone.github.io/Nurses-Drug-Guide/

Content current as of October 2026.

> **Quick reference only.** This guide is for nurses and nursing students. It doesn't replace current prescribing information, your pharmacist, clinical judgment, or your institution's policies and protocols. Doses are typical adult doses unless an entry says otherwise. Verify the dose, route and rate before giving any medication.

## What's in it

- **289 drug entries** covering dosing, administration, checks before giving, nursing considerations, monitoring, adverse effects, contraindications, interactions, dose adjustments, pregnancy and lactation, patient teaching, and overdose and antidotes
- **22 reference tables**, including high-alert medications, do-not-use abbreviations, look-alike and sound-alike names, antidotes, therapeutic drug levels, IV fluids and lab values
- **12 calculators** that show their math, including infusion dose and rate, weight-based dose and creatinine clearance

## Features

- Search by generic or brand name, drug class, use, or any text in an entry. Common abbreviations such as afib, DVT, PPI and TXA work, and misspelled names get "Did you mean" suggestions.
- Filter by category or by flag (high-alert, boxed warning, controlled, look-alike names, pediatric dosing, updated), or jump through the A–Z index.
- Safety marks: Tall Man lettering for look-alike names, ISMP high-alert and FDA boxed-warning flags, DEA schedules, and anesthesia syringe-label colors by drug class.
- Star drugs, add notes to any entry, and add drugs your unit uses. These are saved in your browser on that device only. To keep a copy, use **Saved → Download backup file**.
- Move your stars, notes and drug entries to another phone or computer with **Saved → Move to another device**: scan the QR code with the other device's camera, or send yourself the link. The items travel inside the link itself, so nothing is uploaded anywhere. Anyone with the link can read your notes, so send it only to yourself.
- Dark mode, adjustable text size and print-friendly pages.
- Keyboard shortcuts: `/` to search, `Enter` to open the top result, `↑` `↓` to move through results, `Esc` to clear the search or go back.

## On a phone

Open the link above in your phone's browser. On iPhone and iPad, use Safari: HTML files opened from Mail, Gmail or the Files app open in a preview that can't run the guide.

To keep it on your home screen, open the link in Safari, tap Share, then **Add to Home Screen**.

The Home Screen guide keeps its own stars and notes, separate from Safari's. To copy them in, make a link under **Saved → Move to another device**, copy it, then in the Home Screen guide go to **Saved → Paste a link from another device**.

## Offline

Download `index.html` from this repository and open it in a browser on a computer, such as Chrome, Edge, Firefox or Safari. Everything is in that one file.

## Sources consulted

- FDA prescribing information and safety communications, via [DailyMed](https://dailymed.nlm.nih.gov/)
- ISMP List of High-Alert Medications in Acute Care Settings (2024), ISMP List of Error-Prone Abbreviations, and FDA and ISMP Tall Man lettering lists
- The Joint Commission "Do Not Use" list
- American Heart Association 2025 CPR and ECC guidelines; 2026 AHA/ASA acute ischemic stroke guideline
- American Geriatrics Society 2023 Beers Criteria
- CDC 2022 Clinical Practice Guideline for Prescribing Opioids for Pain
- NIH [LactMed](https://www.ncbi.nlm.nih.gov/books/NBK501922/) for lactation questions

Every entry was written for this guide. Nothing is copied from a published drug handbook.

## Report a problem

Found a wrong dose or another error? [Open an issue](https://github.com/Darkness-Alone/Nurses-Drug-Guide/issues/new) with the drug, the section, what it should say and a source. Don't include patient information. To report a security problem privately, see [SECURITY.md](SECURITY.md).

## Editing the page

`index.html` has a security policy that lets only its own script run and blocks it from loading or sending anything over the network. The policy holds a fingerprint of that script. After any change to the script, update the fingerprint, or the page will load but won't work:

```
python3 scripts/check_csp.py --fix
```

A check runs on every push and pull request and fails if the fingerprint is out of date.
