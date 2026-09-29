import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Reservas Parquei",
  description: "Sistema de reservas de laboratorios del Parque i, ITM",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
