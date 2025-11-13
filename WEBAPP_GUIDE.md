# 🗳️ Election Data Manager - User Guide

## Overview

A modern, responsive web application for managing Motobus election data stored in Supabase.

## ✨ Features

### 📊 Dashboard
- Real-time statistics display
- Total locations count
- Total voters count  
- Average voters per location

### 📍 Location Management
- View all 33 election locations
- Search by location name, address, or number
- See voter count for each location
- Sortable and filterable table

### 👥 Voter Database
- Browse all 377,742 voters
- Search by voter name or ID
- Filter by specific location
- Linked to location information
- Paginated results (20 per page)

### 🔍 Advanced Filtering
- Real-time search across all fields
- Location-based filtering for voters
- Instant results with no page reload

### 🔄 Column Sorting (NEW!)
- Click any column header to sort
- Toggle between ascending/descending order
- Visual indicators (↑/↓) show sort direction
- Works with all columns in both tables
- Maintains sort while filtering/searching

### 📱 Responsive Design
- Works on desktop, tablet, and mobile
- RTL (Right-to-Left) support for Arabic
- Modern, clean interface
- Smooth animations and transitions

## 🚀 Quick Start

### Option 1: Using Batch File (Easiest)
```bash
# Double-click this file:
START_ELECTION_WEBAPP.bat
```

### Option 2: Manual Start
```bash
cd webapp
npm install
npm run dev
```

The app will automatically open at: **http://localhost:3000**

## 📖 How to Use

### Viewing Locations
1. Click on "المواقع الانتخابية" (Election Locations) tab
2. Use the search box to filter locations
3. View location details including voter counts
4. Navigate through pages using pagination controls

### Viewing Voters
1. Click on "الناخبين" (Voters) tab
2. Use the search box to find specific voters
3. Filter by location using the dropdown menu
4. Click column headers to sort (name, ID, location)
5. Browse through paginated results

### Sorting Data
1. Click any column header to sort by that column
2. Click again to reverse the sort order
3. Look for arrows (↑/↓) to see current sort direction
4. Sorting works on:
   - Location numbers and names
   - Voter IDs and names
   - Voter counts
   - All text fields

### Search Tips
- Search works in real-time as you type
- You can search by:
  - Location name or address
  - Location number
  - Voter name
  - Voter ID
- Search is case-insensitive

## 🛠️ Technical Details

### Technology Stack
- **Frontend**: React 18 with Vite
- **Database**: Supabase (PostgreSQL)
- **Styling**: Custom CSS with modern design
- **Icons**: Lucide React
- **Language**: Arabic (RTL support)

### Database Connection
- URL: `https://gridbhusfotahmgulgdd.supabase.co`
- Tables: `locations`, `voters`
- Relationship: `voters.location_id` → `locations.location_id`

### Performance
- Pagination: 20 items per page
- Voter queries limited to 1000 records for performance
- Real-time filtering without API calls
- Optimized for large datasets

## 📁 Project Structure

```
webapp/
├── src/
│   ├── App.jsx          # Main application component
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── START_WEBAPP.bat     # Quick start script
```

## 🔧 Development

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🎨 Customization

### Changing Colors
Edit `webapp/src/index.css` and modify the color values:
- Primary color: `#667eea`
- Secondary color: `#764ba2`
- Background gradient can be customized in the `body` selector

### Adjusting Pagination
In `webapp/src/App.jsx`, change:
```javascript
const itemsPerPage = 20  // Change this number
```

### Modifying Search Behavior
Search logic is in the `filteredLocations` and `filteredVoters` functions in `App.jsx`

## 🔒 Security Notes

- The Supabase anon key is included in the code (safe for public use)
- Row Level Security (RLS) is enabled on Supabase
- All operations use read-only queries
- No sensitive data is exposed

## 📊 Data Statistics

- **Total Locations**: 33
- **Total Voters**: 377,742
- **Governorate**: كفر الشيخ (Kafr El-Sheikh)
- **District**: مطوبس (Motobus)

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is busy, Vite will automatically use the next available port.

### Dependencies Not Installing
```bash
# Clear npm cache
npm cache clean --force
npm install
```

### App Not Loading Data
1. Check internet connection
2. Verify Supabase URL and key in `App.jsx`
3. Check browser console for errors (F12)

## 📞 Support

For issues or questions:
1. Check the browser console (F12) for errors
2. Verify Supabase connection
3. Ensure all dependencies are installed

## 🎯 Future Enhancements

Potential features to add:
- Export data to Excel/CSV
- Advanced analytics and charts
- Voter registration management
- Location map visualization
- Multi-user authentication
- Data editing capabilities
- Bulk operations
- Print-friendly reports

---

**Version**: 1.1.0  
**Last Updated**: November 2025  
**New in 1.1.0**: Column sorting feature  
**License**: MIT
