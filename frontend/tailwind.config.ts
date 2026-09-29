import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        text: "var(--color-text)",
        muted: "var(--color-muted)",
        border: "var(--color-border)",
        sky: "var(--color-sky)",
        gray: "var(--color-gray)",
        disabled: {
          bg: "var(--color-disabled-bg)",
          text: "var(--color-disabled-text)",
        },
        primary: {
          1: "var(--color-primary-1)",
          2: "var(--color-primary-2)",
          hover1: "var(--color-primary-hover-1)",
          hover2: "var(--color-primary-hover-2)",
          pressed: "var(--color-primary-pressed)",
          tint: "var(--color-primary-tint)",
        },
        success: {
          1: "var(--color-success-1)",
          2: "var(--color-success-2)",
          hover2: "var(--color-success-hover-2)",
          pressed: "var(--color-success-pressed)",
        },
        error: {
          1: "var(--color-error-1)",
          2: "var(--color-error-2)",
          hover2: "var(--color-error-hover-2)",
          pressed: "var(--color-error-pressed)",
        },
        warning: {
          1: "var(--color-warning-1)",
          2: "var(--color-warning-2)",
          hover2: "var(--color-warning-hover-2)",
          pressed: "var(--color-warning-pressed)",
        },
      },
      borderRadius: {
        control: "var(--radius)",
      },
      boxShadow: {
        default: "var(--shadow-default)",
        hover: "var(--shadow-hover)",
        pressed: "var(--shadow-pressed)",
        focus: "var(--shadow-focus)",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
      },
      fontSize: {
        sm: "var(--fs-sm)",
        base: "var(--fs-base)",
        xl: "var(--fs-xl)",
        "2xl": "var(--fs-2xl)",
        "3xl": "var(--fs-3xl)",
        "4xl": "var(--fs-4xl)",
        "5xl": "var(--fs-5xl)",
      },
      fontWeight: {
        normal: "var(--fw-normal)",
        bold: "var(--fw-bold)",
      },
    },
  },
  plugins: [],
};
export default config;
