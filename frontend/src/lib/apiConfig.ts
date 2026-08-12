const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!configuredBaseUrl) {
  throw new Error(
    "VITE_API_BASE_URL is required. Define it in the frontend environment."
  );
}

export const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");
