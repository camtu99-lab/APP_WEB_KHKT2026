import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F6F7F2",
        ink: "#1B2321",
        muted: "#5C6B66",
        line: "#E1E4DA",
        flask: {
          50: "#EAF3F1",
          100: "#CFE4DF",
          400: "#2C8577",
          500: "#146356",
          600: "#0F4E44",
        },
        flame: {
          400: "#D98F3F",
          500: "#C97A2B",
          600: "#A6621F",
        },
        danger: "#B3432E",
      },
      fontFamily: {
        serif: ["Iowan Old Style", "Georgia", "ui-serif", "serif"],
        sans: ["ui-sans-serif", "system-ui", "Segoe UI", "Helvetica Neue", "Arial", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "10px",
      },
    },
  },
  plugins: [],
};

export default config;
