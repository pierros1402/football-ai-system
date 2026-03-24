import "./globals.css";
import { ThemeProvider } from "./providers/ThemeProvider";

export const metadata = {
  title: "Admin Dashboard",
  description: "Admin panel for managing users"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-black">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
