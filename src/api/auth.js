import http from "../lib/http.js";

// Login endpoint: POST /auth/login
// Base URL is configured in src/lib/http.js from VITE_API_BASE_URL env variable
export const login = async ({ username, password }) => {
  const response = await http.post("/auth/login", { username, password });
  return response.data;
};

export const register = async ({ username, password }) => {
  const response = await http.post("/auth/register", { username, password });
  return response.data;
};

export const refresh = async () => {
  const response = await http.post("/auth/refresh");
  return response.data;
};
