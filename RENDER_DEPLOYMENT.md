# Deploying to Render.com

## Prerequisites
- GitHub account
- Render.com account (free tier available)
- Push your code to a GitHub repository

## Deployment Steps

### 1. Push Code to GitHub
```bash
cd /Users/sudhirsingh/forecasting
git init
git add .
git commit -m "Initial commit - WiFi Demand Forecasting System"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Render

#### Option A: Using render.yaml (Blueprint)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New" → "Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click **"Apply"** to deploy all services

#### Option B: Manual Service Creation
Deploy each service individually:

1. **Gateway Service**
   - New → Web Service
   - Connect repository
   - Name: `wifi-forecasting-gateway`
   - Root Directory: `gateway`
   - Environment: Docker
   - Dockerfile Path: `./Dockerfile`
   - Add environment variables:
     - `CLASSICAL_SERVICE_URL`: `https://wifi-forecasting-classical.onrender.com`
     - `ML_SERVICE_URL`: `https://wifi-forecasting-ml.onrender.com`
     - `DL_SERVICE_URL`: `https://wifi-forecasting-dl.onrender.com`

2. **Classical Service**
   - Root Directory: `classical-service`
   - Name: `wifi-forecasting-classical`

3. **ML Service**
   - Root Directory: `ml-service`
   - Name: `wifi-forecasting-ml`

4. **DL Service**
   - Root Directory: `dl-service`
   - Name: `wifi-forecasting-dl`

5. **Frontend Service**
   - Root Directory: `frontend-service`
   - Name: `wifi-forecasting-frontend`

### 3. Update Service URLs

After all services are deployed, update the Gateway's environment variables with the actual Render URLs:

```
CLASSICAL_SERVICE_URL=https://wifi-forecasting-classical.onrender.com
ML_SERVICE_URL=https://wifi-forecasting-ml.onrender.com
DL_SERVICE_URL=https://wifi-forecasting-dl.onrender.com
```

### 4. Access Your Application

- **Frontend**: `https://wifi-forecasting-frontend.onrender.com`
- **API Gateway**: `https://wifi-forecasting-gateway.onrender.com`

## Important Notes

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (enough for 1 service running 24/7)

### Production Recommendations
1. **Upgrade to Paid Plan** for:
   - Always-on services (no spin-down)
   - Better performance
   - Custom domains

2. **Database**: Consider using Render's PostgreSQL instead of SQLite for production

3. **Environment Variables**: Use Render's environment groups for shared configs

4. **Monitoring**: Enable Render's built-in monitoring and alerts

## Troubleshooting

### Services Not Connecting
- Verify all service URLs in Gateway environment variables
- Check service logs in Render dashboard
- Ensure all services are deployed and running

### Slow First Load
- Normal on free tier (cold start)
- Consider upgrading to paid plan for instant responses

### Build Failures
- Check Dockerfile paths in `render.yaml`
- Verify all dependencies in `requirements.txt`
- Review build logs in Render dashboard

## Cost Estimate

**Free Tier**: $0/month
- 5 services × 750 hours = 3,750 hours
- Limited to 750 hours total across all services

**Starter Plan**: ~$35/month
- All 5 services always-on
- No cold starts
- Better performance

## Alternative: Single Service Deployment

To reduce costs, you can combine all services into one:

1. Create a single Dockerfile that runs all services
2. Use a process manager like `supervisord`
3. Deploy as one web service

This reduces from 5 services to 1, fitting within free tier limits.
