# Production Deployment Guide (Netlify + Supabase)

## 1. Supabase Setup
1. **Tables**: Run the SQL in `supabase-schema.sql` in the Supabase SQL Editor.
2. **Storage**: Create a bucket named `game-assets` and set it to **Public**.
3. **Authentication**: 
   - Go to Auth -> Settings.
   - (Optional) Disable "Confirm Email" if you want users to log in immediately upon signup.
   - Add your deployment URL (e.g., your Netlify URL) to the "Redirect URLs".

## 2. Netlify Setup
1. **Build Settings**:
   - Build Command: `npm run build`
   - Publish Directory: `dist`
2. **Environment Variables**:
   - Add `VITE_SUPABASE_URL`: Your Supabase Project URL.
   - Add `VITE_SUPABASE_ANON_KEY`: Your Supabase Anon Key.

## 3. Creating Admin
- After signing up in your app, go to Supabase SQL Editor and run:
  ```sql
  UPDATE profiles SET is_admin = true WHERE email = 'your-email@example.com';
  ```
