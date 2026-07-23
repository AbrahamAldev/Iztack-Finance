/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,

  // Public env vars exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },

  async rewrites() {
    // Internal API proxy for local/docker development.
    // In production (Cloudflare/nginx) the public domain is used directly.
    const backendHost = process.env.BACKEND_HOST || 'sf-backend:8000';
    return [
      {
        source: '/api/:path*',
        destination: `http://${backendHost}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
