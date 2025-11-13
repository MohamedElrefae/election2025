# 🚀 Quick Reference - Election Data Manager

## Current Status: ✅ All Systems Operational

### Database Statistics
- **Locations**: 33
- **Voters**: 188,871
- **Status**: ✅ Correct, No Duplicates
- **Last Updated**: November 13, 2025

---

## Web Application

### Access
- **URL**: http://localhost:3000
- **Status**: Running
- **Features**: Locations, Voters, Search, Filter, Sort

### Start/Stop
```bash
# Start
START_ELECTION_WEBAPP.bat

# Or manually
cd webapp
npm run dev
```

---

## Data Management Scripts

### Verify Data
```bash
python verify_correct_data.py
```
Shows current statistics and checks for duplicates.

### Clear All Data
```bash
python force_clear_tables.py
```
Removes all data from Supabase (use with caution!).

### Re-upload Data
```bash
python clean_and_reupload_data.py
```
Clears and re-uploads data from CSV files with proper conversion.

### Analyze CSV
```bash
python fix_arabic_numbers.py
```
Analyzes CSV files for data integrity issues.

---

## Important Notes

### Voter ID Structure
- ⚠️ Voter IDs are **NOT globally unique**
- ✅ Voter IDs restart at 1 for each location
- ✅ Combination of (location_id + voter_id) is unique
- Example:
  - Location 76: Voters 1-6059
  - Location 77: Voters 1-6209 (starts at 1 again)

### Data Format
- ✅ Voter numbers: English integers (1, 2, 3...)
- ✅ Names: Arabic text (UTF-8)
- ✅ Location IDs: 76-108

---

## Troubleshooting

### Web App Not Loading
1. Check if server is running: http://localhost:3000
2. Restart: `cd webapp && npm run dev`
3. Check browser console (F12) for errors

### Wrong Data Showing
1. Refresh browser (Ctrl+F5)
2. Verify database: `python verify_correct_data.py`
3. Re-upload if needed: `python clean_and_reupload_data.py`

### Database Issues
1. Check Supabase connection
2. Verify config: `supabase_config.json`
3. Clear and re-upload: `python force_clear_tables.py` then `python clean_and_reupload_data.py`

---

## File Locations

### Web Application
- `webapp/` - React application
- `webapp/src/App.jsx` - Main component
- `webapp/src/index.css` - Styles

### Data Files
- `motobus voter.csv` - Voter data (188,877 rows)
- `motobus  locations.csv` - Location data (33 rows)
- `supabase_config.json` - Database credentials

### Scripts
- `clean_and_reupload_data.py` - Main upload script
- `verify_correct_data.py` - Verification script
- `force_clear_tables.py` - Clear database
- `fix_arabic_numbers.py` - Data analysis

### Documentation
- `WEBAPP_GUIDE.md` - Complete web app guide
- `DATA_FIX_SUMMARY.md` - Technical fix details
- `ISSUE_RESOLVED.md` - Problem resolution summary
- `QUICK_REFERENCE.md` - This file

---

## Quick Commands

```bash
# Start web app
START_ELECTION_WEBAPP.bat

# Verify data
python verify_correct_data.py

# Clear database
python force_clear_tables.py

# Upload fresh data
python clean_and_reupload_data.py

# Analyze CSV
python fix_arabic_numbers.py
```

---

## Support

### Common Issues
1. **Duplicates**: Run `clean_and_reupload_data.py`
2. **Wrong counts**: Refresh browser, verify with `verify_correct_data.py`
3. **Arabic numerals**: Already fixed in upload script
4. **Web app not starting**: Check Node.js installed, run `npm install` in webapp folder

### Data Integrity
- ✅ All data matches CSV source files
- ✅ No duplicates in database
- ✅ Voter counts accurate per location
- ✅ All relationships preserved

---

**Last Updated**: November 13, 2025  
**Version**: 1.1.0  
**Status**: ✅ Production Ready
