# Vercel Deployment Guide

## Quick Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository

3. **Configure Project**
   - **Root Directory**: Leave empty (or set to `frontend` if you want)
   - **Framework Preset**: Create React App
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `cd frontend && npm install`

4. **Environment Variables** (Optional)
   - `REACT_APP_API_URL`: Your backend URL (or leave empty for mock data)
   - `REACT_APP_DEMO_MODE`: Set to `true` to enable demo mode

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live!

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

4. **Follow prompts**
   - Link to existing project or create new
   - Confirm settings
   - Deploy!

### Option 3: Use vercel.json (Recommended)

The `vercel.json` file is already configured. Just:

1. Push to GitHub
2. Import to Vercel
3. Vercel will automatically use `vercel.json` settings

---

## Configuration Details

### Build Settings

The `vercel.json` file configures:
- **Build Command**: Installs dependencies and builds React app
- **Output Directory**: Points to `frontend/build`
- **Rewrites**: All routes go to `index.html` (for React Router)
- **Headers**: Cache static assets for performance

### Environment Variables

Set these in Vercel Dashboard → Project Settings → Environment Variables:

- `REACT_APP_API_URL`: Backend API URL (optional, leave empty for mock data)
- `REACT_APP_DEMO_MODE`: Set to `true` to force demo mode

### Demo Mode

If `REACT_APP_API_URL` is not set or empty, the app will automatically use mock data.

You can also enable demo mode in the app by setting:
```javascript
localStorage.setItem('demoMode', 'true');
```

---

## Troubleshooting

### Build Fails

**Error**: "Cannot find module"
- **Solution**: Make sure `package.json` is in the `frontend` directory
- Check that all dependencies are listed in `package.json`

**Error**: "Build command failed"
- **Solution**: Check build logs in Vercel dashboard
- Try building locally: `cd frontend && npm run build`

### Routes Not Working

**Issue**: 404 on page refresh
- **Solution**: The `vercel.json` rewrites should fix this
- Make sure `rewrites` section is in `vercel.json`

### API Calls Failing

**Issue**: CORS errors or API not found
- **Solution**: Use mock data mode (set `REACT_APP_DEMO_MODE=true`)
- Or deploy backend separately and set `REACT_APP_API_URL`

---

## Post-Deployment

### 1. Update README

Add deployment badge and live demo link:
```markdown
[![Deployed with Vercel](https://vercel.com/button)](https://your-app.vercel.app)

🌐 Live Demo: [https://your-app.vercel.app](https://your-app.vercel.app)
```

### 2. Custom Domain (Optional)

1. Go to Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### 3. Monitor Performance

- Check Vercel Analytics (if enabled)
- Monitor build times
- Check error logs

---

## Free Tier Limits

Vercel Free Tier includes:
- ✅ 100GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Automatic SSL
- ✅ Global CDN
- ✅ Preview deployments for PRs

**Note**: Free tier is perfect for portfolio projects!

---

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Test all pages work
3. ✅ Add demo link to README
4. ✅ Share your portfolio!

---

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Discord](https://vercel.com/discord)
- [GitHub Issues](https://github.com/vercel/vercel/issues)

