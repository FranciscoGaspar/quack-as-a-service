import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      new URL(
        "https://quack-as-a-service-bucket.s3.us-east-1.amazonaws.com/**",
      ),
    ],
  },
};

export default nextConfig;
