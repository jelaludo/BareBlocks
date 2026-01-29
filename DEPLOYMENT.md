# Deployment Guide - BareBlocks Client-Side

## Quick Deploy to Cloudflare Pages

### Prerequisites
- Cloudflare account (free)
- `index.html` file

### Steps

1. **Go to Cloudflare Pages**
   - Visit: https://pages.cloudflare.com
   - Click "Create a project"

2. **Choose Deployment Method**
   
   **Option A: Direct Upload (Easiest)**
   - Click "Upload assets"
   - Drag and drop `index.html`
   - Click "Deploy site"
   - Done! You'll get a URL like `bareblocks.pages.dev`

   **Option B: Git Integration**
   - Connect your GitHub/GitLab repository
   - Select the repository
   - Build settings:
     - Build command: (leave empty)
     - Build output directory: `/`
   - Click "Save and Deploy"

3. **Custom Domain (Optional)**
   - Go to your project settings
   - Click "Custom domains"
   - Add: `metadata.jelaludo.com` or `tools.jelaludo.com`
   - Follow DNS instructions (add CNAME record)
   - Wait for SSL certificate (automatic, ~5 minutes)

4. **Test**
   - Visit your new URL
   - Upload a test image
   - Verify all features work

---

## Deploy to jelaludo.com Directly

### Prerequisites
- Access to jelaludo.com hosting (FTP, cPanel, or file manager)
- `index.html` file

### Steps

1. **Create Directory**
   - Log into your hosting control panel
   - Navigate to public_html (or www, or httpdocs)
   - Create new folder: `tools`

2. **Upload File**
   - Upload `index.html` to `/tools/` directory
   - Rename to `index.html` (if not already)

3. **Test**
   - Visit: `https://jelaludo.com/tools/`
   - Upload a test image
   - Verify all features work

4. **Add to Navigation**
   - Edit your site's menu/navigation
   - Add link: "Tools" → `https://jelaludo.com/tools/`

---

## Deploy to GitHub Pages

### Prerequisites
- GitHub account (free)
- Git installed locally

### Steps

1. **Create Repository**
   ```bash
   # Create new repository on GitHub: bareblocks
   
   # Clone it locally
   git clone https://github.com/yourusername/bareblocks.git
   cd bareblocks
   
   # Copy index.html
   cp /path/to/index.html .
   
   # Commit and push
   git add index.html
   git commit -m "Initial commit - client-side metadata inspector"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to repository settings
   - Scroll to "Pages" section
   - Source: Deploy from branch
   - Branch: `main` / `root`
   - Click "Save"

3. **Wait for Deployment**
   - GitHub will build and deploy (1-2 minutes)
   - Visit: `https://yourusername.github.io/bareblocks/`

4. **Custom Domain (Optional)**
   - In Pages settings, add custom domain: `metadata.jelaludo.com`
   - Add CNAME record in your DNS:
     ```
     metadata.jelaludo.com → yourusername.github.io
     ```

---

## Deploy to Netlify

### Prerequisites
- Netlify account (free)
- `index.html` file

### Steps

1. **Drag and Drop**
   - Visit: https://app.netlify.com/drop
   - Drag `index.html` onto the page
   - Done! You'll get a URL like `random-name.netlify.app`

2. **Rename Site (Optional)**
   - Click "Site settings"
   - Click "Change site name"
   - Enter: `bareblocks-metadata` (or whatever you want)
   - New URL: `bareblocks-metadata.netlify.app`

3. **Custom Domain (Optional)**
   - Click "Domain settings"
   - Click "Add custom domain"
   - Enter: `metadata.jelaludo.com`
   - Follow DNS instructions
   - SSL certificate: automatic

---

## DNS Configuration (For Custom Domains)

### For Cloudflare Pages
```
Type: CNAME
Name: metadata (or tools)
Target: bareblocks.pages.dev
Proxy: Yes (orange cloud)
```

### For GitHub Pages
```
Type: CNAME
Name: metadata (or tools)
Target: yourusername.github.io
```

### For Netlify
```
Type: CNAME
Name: metadata (or tools)
Target: bareblocks-metadata.netlify.app
```

---

## Adding to jelaludo.com Navigation

### If Using WordPress
1. Go to Appearance → Menus
2. Add Custom Link:
   - URL: `https://metadata.jelaludo.com`
   - Link Text: "Metadata Tools" or "Tools"
3. Save menu

### If Using HTML/Static Site
Add to your navigation menu:
```html
<nav>
  <a href="/">HOME</a>
  <a href="/gallery">GALLERY</a>
  <a href="/spark">SPARK</a>
  <a href="/jelaludo">JELALUDO</a>
  <a href="https://metadata.jelaludo.com">TOOLS</a>
</nav>
```

### If Using Wix/Squarespace
1. Go to site editor
2. Add menu item
3. Link to external URL: `https://metadata.jelaludo.com`

---

## Testing After Deployment

### Checklist
- [ ] Page loads without errors
- [ ] Can upload image by clicking
- [ ] Can upload image by drag-and-drop
- [ ] EXIF data displays correctly
- [ ] GPS coordinates show and copy works
- [ ] Chunks tab shows file structure
- [ ] JSON export downloads file
- [ ] Works on mobile (test on phone)
- [ ] HTTPS is enabled (padlock in browser)
- [ ] Custom domain works (if configured)

### Test Images
Use these to verify functionality:
1. **JPEG with EXIF** - Any photo from your camera
2. **PNG with text chunks** - AI-generated image
3. **Image with GPS** - Photo taken with phone location on

---

## Troubleshooting

### "exifr is not defined" Error
**Problem**: CDN failed to load exifr library
**Solution**: 
- Check internet connection
- Try different CDN: Replace in `index.html`:
  ```html
  <!-- Change from -->
  <script src="https://cdn.jsdelivr.net/npm/exifr@latest/dist/full.umd.js"></script>
  
  <!-- To -->
  <script src="https://unpkg.com/exifr@latest/dist/full.umd.js"></script>
  ```

### Clipboard Copy Not Working
**Problem**: Clipboard API requires HTTPS
**Solution**: 
- Ensure site is accessed via HTTPS (not HTTP)
- All hosting options above provide free HTTPS

### File Upload Not Working on Mobile
**Problem**: File input not triggering
**Solution**: 
- Already handled in code - tap anywhere in upload zone
- Ensure browser supports File API (all modern browsers do)

### Page Loads But Nothing Happens
**Problem**: JavaScript error
**Solution**: 
- Open browser console (F12)
- Look for red error messages
- Common causes:
  - exifr library didn't load
  - Browser too old (update browser)
  - JavaScript disabled (enable it)

---

## Performance Optimization (Optional)

### 1. Minify HTML
Use online tool to minify `index.html`:
- https://www.willpeavy.com/tools/minifier/
- Reduces file size by ~30%

### 2. Self-Host exifr Library
Instead of CDN, download and host exifr:
```bash
# Download exifr
wget https://cdn.jsdelivr.net/npm/exifr@latest/dist/full.umd.js -O exifr.min.js

# Update index.html
<script src="./exifr.min.js"></script>
```

**Pros**: Faster (no external request), works offline
**Cons**: Slightly larger deployment

### 3. Add Service Worker (PWA)
Make it installable and work offline:
```javascript
// Add to index.html
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

---

## Monitoring (Optional)

### Add Google Analytics
Add before `</head>` in `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Add Cloudflare Analytics
Automatic if using Cloudflare Pages - check dashboard.

---

## Updating After Deployment

### Cloudflare Pages (Direct Upload)
1. Make changes to `index.html`
2. Go to Cloudflare Pages dashboard
3. Click "Create deployment"
4. Upload new `index.html`

### Cloudflare Pages (Git)
1. Make changes to `index.html`
2. Commit and push:
   ```bash
   git add index.html
   git commit -m "Update metadata inspector"
   git push origin main
   ```
3. Cloudflare auto-deploys

### GitHub Pages
1. Make changes
2. Commit and push (same as above)
3. GitHub auto-deploys

### Direct Upload (jelaludo.com)
1. Make changes to `index.html`
2. Re-upload via FTP/cPanel
3. May need to clear browser cache

---

## Cost Summary

| Platform | Monthly Cost | Custom Domain | SSL | CDN |
|----------|-------------|---------------|-----|-----|
| **Cloudflare Pages** | $0 | ✅ Free | ✅ Free | ✅ Free |
| **GitHub Pages** | $0 | ✅ Free | ✅ Free | ✅ Free |
| **Netlify** | $0 | ✅ Free | ✅ Free | ✅ Free |
| **jelaludo.com hosting** | $0* | ✅ Included | ✅ Included | Depends |

*Uses existing hosting, no additional cost

---

## Recommended: Cloudflare Pages

**Why**:
1. Your site is already on Cloudflare
2. Fastest CDN
3. Easiest custom domain setup
4. Best integration with existing site
5. Excellent analytics dashboard

**Deploy now**: https://pages.cloudflare.com

---

## Questions?

### How do I update the styling?
Edit the `<style>` section in `index.html`

### Can I add more features?
Yes! It's just HTML/JavaScript. Edit `index.html`

### Can I use my own domain?
Yes! Follow "Custom Domain" steps for your hosting platform

### Is it really free?
Yes! All hosting options listed are free tier, sufficient for this use case

### What about bandwidth limits?
- Cloudflare Pages: Unlimited
- GitHub Pages: 100GB/month (more than enough)
- Netlify: 100GB/month (more than enough)

---

**Ready to deploy? Pick a platform above and follow the steps. Takes less than 10 minutes.**

