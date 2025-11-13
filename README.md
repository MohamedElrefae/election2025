# 🗳️ Election 2025 - Motobus District Data Management System

Complete election data management system for Motobus district, Kafr El-Sheikh Governorate, Egypt.

## 📊 Project Overview

- **Total Voters**: 188,871
- **Total Locations**: 33
- **Total Families**: ~3,500
- **Governorate**: كفر الشيخ (Kafr El-Sheikh)
- **District**: مطوبس (Motobus)

## 🚀 Quick Start

### Option 1: Using Batch File (Easiest)
```bash
# Double-click this file:
START_ELECTION_WEBAPP.bat
```

### Option 2: Manual Start
```bash
# Navigate to webapp folder
cd webapp

# Install dependencies (first time only)
npm install

# Start the application
npm run dev
```

The application will open at: **http://localhost:3000**

## 📁 Project Structure

```
Election-2025/
├── webapp/                      # React web application
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── index.css           # Styles
│   │   └── main.jsx            # Entry point
│   ├── package.json            # Node.js dependencies
│   └── vite.config.js          # Vite configuration
│
├── Data Files/
│   ├── motobus voter.csv       # Voter data (188,871 rows)
│   └── motobus  locations.csv  # Location data (33 rows)
│
├── Python Scripts/
│   ├── add_name_columns_and_split.py    # Split names into first/family
│   ├── clean_and_reupload_data.py       # Clean and upload data
│   ├── verify_correct_data.py           # Verify data integrity
│   └── force_clear_tables.py            # Clear database
│
├── Documentation/
│   ├── WEBAPP_GUIDE.md                  # Complete web app guide
│   ├── FAMILY_FEATURES_ADDED.md         # Family grouping features
│   ├── UI_UPDATES_GUIDE.md              # UI documentation
│   ├── QUICK_REFERENCE.md               # Quick commands
│   └── DATA_FIX_SUMMARY.md              # Data fixes applied
│
└── Configuration/
    ├── supabase_config.json             # Database credentials
    └── supabase_schema.sql              # Database schema
```

## ✨ Features

### Web Application
- 📍 **Locations Tab**: View all 33 election locations
- 👥 **Voters Tab**: Browse 188,871 voters with advanced filtering
- 👨‍👩‍👧‍👦 **Families Tab**: Group voters by family name (NEW!)
- 🔍 **Advanced Search**: Search by name, ID, location, or family
- 🔄 **Sorting**: Sort by any column (click headers)
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🌐 **RTL Support**: Full Arabic language support

### Data Management
- ✅ Name splitting (first name, family name, middle names)
- ✅ Family grouping and statistics
- ✅ Location-based filtering
- ✅ Real-time search
- ✅ Pagination (20 items per page)
- ✅ Data integrity verification

### Database
- **Supabase PostgreSQL** backend
- **Voters Table**: id, voter_id, full_name, first_name, family_name, middle_names, location_id
- **Locations Table**: location_id, location_number, location_name, location_address, total_voters
- **Indexes**: Optimized for fast queries on family_name and first_name

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Lucide React** - Icons
- **Custom CSS** - Styling

### Backend
- **Supabase** - Database and API
- **PostgreSQL** - Database engine

### Data Processing
- **Python 3** - Data scripts
- **Pandas** - Data manipulation
- **Supabase Python Client** - Database operations

## 📖 Usage Guide

### Viewing Locations
1. Click "المواقع الانتخابية" tab
2. Search or sort locations
3. View voter counts per location

### Viewing Voters
1. Click "الناخبين" tab
2. Use search to find specific voters
3. Filter by location or family
4. Sort by name, ID, or location

### Viewing Families
1. Click "العائلات" tab
2. See all families with member counts
3. Click "عرض الأفراد" to view family members
4. Sort by family size or name

### Filtering
- **By Location**: Select from location dropdown
- **By Family**: Select from family dropdown
- **By Search**: Type in search box (searches all fields)

### Sorting
- Click any column header to sort
- Click again to reverse sort order
- Look for arrows (↑/↓) to see current sort

## 🔧 Development

### Install Dependencies
```bash
cd webapp
npm install
```

### Start Development Server
```bash
cd webapp
npm run dev
```

### Build for Production
```bash
cd webapp
npm run build
```

### Preview Production Build
```bash
cd webapp
npm run preview
```

## 🗄️ Database Management

### Verify Data
```bash
python verify_correct_data.py
```

### Clear Database
```bash
python force_clear_tables.py
```

### Re-upload Data
```bash
python clean_and_reupload_data.py
```

### Split Names (if needed)
```bash
python add_name_columns_and_split.py
```

## 📊 Data Statistics

### Voters
- Total: 188,871
- Unique first names: ~500
- Unique family names: ~3,500
- Average voters per location: 5,723

### Top Families
1. ا - ~1,081 members
2. ابراهيم - ~795 members
3. ابوخليل - ~732 members
4. ابوحامد - ~554 members
5. ابواسماعيل - ~491 members

### Locations
- Total: 33
- Range: Location 76 to 108
- Largest: Location 87 (10,763 voters)
- Smallest: Location 91 (2,074 voters)

## 🔒 Security

- Supabase Row Level Security (RLS) enabled
- Read-only operations in web app
- Public anon key (safe for client-side use)
- No sensitive data exposed

## 📝 Configuration

### Supabase Configuration
Edit `supabase_config.json`:
```json
{
  "url": "https://gridbhusfotahmgulgdd.supabase.co",
  "key": "your-anon-key-here"
}
```

### Web App Configuration
Edit `webapp/vite.config.js` for port and other settings.

## 🐛 Troubleshooting

### Web App Won't Start
```bash
cd webapp
npm install
npm run dev
```

### Port Already in Use
Vite will automatically use the next available port.

### Data Not Loading
1. Check internet connection
2. Verify Supabase credentials in `supabase_config.json`
3. Check browser console (F12) for errors

### npm Error: ENOENT package.json
You're in the wrong directory. The Node.js project is in the `webapp` folder:
```bash
cd webapp
npm install
```

## 📚 Documentation

- **WEBAPP_GUIDE.md** - Complete web application guide
- **FAMILY_FEATURES_ADDED.md** - Family grouping features
- **UI_UPDATES_GUIDE.md** - UI updates and features
- **QUICK_REFERENCE.md** - Quick commands reference
- **DATA_FIX_SUMMARY.md** - Data integrity fixes
- **SORTING_FEATURE_GUIDE.md** - Sorting functionality

## 🎯 Future Enhancements

- [ ] Export to Excel/CSV
- [ ] Print-friendly reports
- [ ] Advanced analytics dashboard
- [ ] Multi-user authentication
- [ ] Data editing capabilities
- [ ] Bulk operations
- [ ] Map visualization
- [ ] Charts and graphs

## 📞 Support

For issues or questions:
1. Check documentation in the project root
2. Verify Supabase connection
3. Check browser console for errors (F12)
4. Ensure all dependencies are installed

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributors

- Mohamed Elrefae - Project Lead

## 🙏 Acknowledgments

- Supabase for database hosting
- React team for the framework
- Vite for the build tool

---

**Version**: 1.2.0  
**Last Updated**: November 13, 2025  
**Status**: ✅ Production Ready

## Quick Commands

```bash
# Start web app
cd webapp && npm run dev

# Verify data
python verify_correct_data.py

# Clear database
python force_clear_tables.py

# Re-upload data
python clean_and_reupload_data.py
```

**Access Application**: http://localhost:3000
