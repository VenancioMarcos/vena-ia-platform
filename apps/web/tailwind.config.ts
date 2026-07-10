import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#f7f8fa",
        ink: "#17202a",
        steel: "#53616f",
        line: "#d9dee5",
        signal: "#0f766e",
        machine: "#334155"
      }
    }
  },
  plugins: []
};

export default config;

