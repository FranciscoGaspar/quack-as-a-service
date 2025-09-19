import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { AppProviders } from "@/components/AppProviders";
import { Toaster } from "@/components/ui/sonner";
import { cn } from "@/lib/utils";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "QaaS",
};

type RootLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

const RootLayout = ({ children }: RootLayoutProps) => {
  return (
    <html lang="en">
      <body className={cn(inter.className, "antialiased")}>
        <AppProviders>{children}</AppProviders>
        <Toaster richColors />
      </body>
    </html>
  );
};

export default RootLayout;
