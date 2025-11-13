# 🚀 Vercel Deployment Guide

## Quick Fix for 404 Error

The 404 error occurs because Vercel needs to know where your app is located. Follow these steps:

## Option 1: Deploy from webapp folder (Recommended)

### Step 1: Update Vercel Project Settings

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **General**
4. Update these settings:

```
Root Directory: webapp
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### Step 2: Redeploy

1. Go to **Deployments** tab
2. Click the three dots (...) on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

## Option 2: Use Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to webapp folder
cd webapp

# Deploy
vercel --prod
```

## Option 3: Deploy via Git (Automatic)

### Update vercel.json in root

The `vercel.json` file has been created with the correct configuration:

```json
{
  "buildCommand": "cd webapp && npm install && npm run build",
  "outputDirectory": "webapp/dist",
  "devCommand": "cd webapp && npm run dev",
  "installCommand": "cd webapp && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Push to GitHub

```bash
git add vercel.json webapp/vercel.json
git commit -m "Add Vercel deployment configuration"
git push origin main
```

Vercel will automatically redeploy with the new configuration.

## Verifying Deployment

After deployment, check:

1. ✅ Homepage loads without 404
2. ✅ All three tabs work (Locations, Voters, Families)
3. ✅ Search and filters work
4. ✅ Data loads from Supabase
5. ✅ No console errors

## Common Issues & Solutions

### Issue 1: 404 on Page Refresh
**Solution**: The `vercel.json` rewrites configuration handles this. Make sure it's deployed.

### Issue 2: Build Fails
**Solution**: Check that:
- `webapp/package.json` exists
- All dependencies are listed
- Build command is correct: `npm run build`

### Issue 3: Blank Page
**Solution**: Check browser console (F12) for errors. Usually means:
- Supabase credentials are correct
- API calls are working
- No JavaScript errors

### Issue 4: Environment Variables
If you need environment variables:

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add:
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key

Then update `webapp/src/App.jsx`:
```javascript
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://gridbhusfotahmgulgdd.supabase.co'
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-key-here'
```

## Project Structure for Vercel

```
election2025/                    ← Root (Vercel looks here)
├── vercel.json                  ← Tells Vercel where to build
├── webapp/                      ← Your React app
│   ├── package.json            ← Dependencies
│   ├── vite.config.js          ← Vite config
│   ├── index.html              ← Entry HTML
│   ├── src/
│   │   ├── App.jsx             ← Main component
│   │   ├── main.jsx            ← React entry
│   │   └── index.css           ← Styles
│   └── dist/                   ← Build output (created by Vite)
└── [other files]
```

## Deployment Checklist

Before deploying:
- [ ] `vercel.json` exists in root
- [ ] `webapp/vercel.json` exists
- [ ] All changes committed to Git
- [ ] Pushed to GitHub
- [ ] Vercel project settings updated
- [ ] Build command points to webapp folder
- [ ] Output directory is `webapp/dist`

## Testing Locally Before Deploy

```bash
# Build the app
cd webapp
npm run build

# Preview the build
npm run preview
```

Visit http://localhost:4173 to test the production build locally.

## Vercel Dashboard Settings

### Framework Preset
- Select: **Vite**

### Build & Development Settings
```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Development Command: npm run dev
```

### Root Directory
```
Root Directory: webapp
```

## Alternative: Deploy Only webapp Folder

If you want to deploy only the webapp folder:

1. Create a new Vercel project
2. Connect to GitHub
3. Select the repository
4. Set Root Directory to `webapp`
5. Vercel will auto-detect Vite
6. Deploy!

## Support

If you still see 404:
1. Check Vercel build logs
2. Verify all files are in the correct location
3. Make sure `webapp/dist` folder is created during build
4. Check that `index.html` exists in the output

---

**Need Help?** Check the Vercel documentation: https://vercel.com/docs
