/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better error handling
  reactStrictMode: true,

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_APP_NAME: "TaxGenie AI",
  },

  // Image optimization
  images: {
    domains: ["localhost", "taxgenie.ai"],
    formats: ["image/avif", "image/webp"],
  },

  // Headers for security
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(self), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },

  // Rewrites for API proxy
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/api/:path*",
          destination: "/api/:path*",
        },
      ],
    };
  },

  // Redirects
  async redirects() {
    return [
      {
        source: "/home",
        destination: "/",
        permanent: true,
      },
    ];
  },

  // Performance optimizations
  swcMinify: true,
  compress: true,

  // Webpack optimization
  webpack: (config, { isServer }) => {
    // Optimize for client-side only
    if (!isServer) {
      config.optimization.runtimeChunk = "single";
      config.optimization.splitChunks = {
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            priority: 10,
          },
          common: {
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      };
    }

    return config;
  },

  // Experimental features
  experimental: {
    optimizePackageImports: ["framer-motion", "lucide-react"],
  },

  // Powering Next.js
  poweredByHeader: false,

  // Production source maps (can be disabled for security)
  productionBrowserSourceMaps: false,

  // API routes
  api: {
    responseLimit: "10mb",
  },
};

module.exports = nextConfig;