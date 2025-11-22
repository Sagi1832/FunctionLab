import axios from "axios";
import { notifications } from "@mantine/notifications";
import { getToken, removeToken } from "./storage.js";

// Base URL configuration:
// 1. Read from VITE_API_BASE_URL environment variable (trimmed, trailing slashes removed)
// 2. Fallback: http://127.0.0.1:8000 for dev, /api for production
const raw = (import.meta.env?.VITE_API_BASE_URL ?? "").trim();
const normalized = raw.replace(/\/+$/, "");

const baseURL = normalized || (import.meta.env?.DEV ? "http://127.0.0.1:8000" : "/api");

let authToken = null;

const http = axios.create({
  baseURL,
  withCredentials: false,
  timeout: 15_000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// TODO: integrate token refresh against /auth/refresh when backend supports refresh tokens
let hasShown401Notification = false;

export const clearAuthToken = () => {
  authToken = null;
  delete http.defaults.headers.common.Authorization;
  removeToken();
  hasShown401Notification = false;
};

export const setAuthToken = (token) => {
  const trimmed = token?.trim();
  if (!trimmed) return clearAuthToken();
  authToken = trimmed;
  http.defaults.headers.common.Authorization = `Bearer ${trimmed}`;
  hasShown401Notification = false;
};

http.interceptors.request.use((config) => {
  const token = authToken ?? getToken();
  if (token && !(config.headers && "Authorization" in config.headers)) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (r) => r,
  (error) => {
    const status = error.response?.status ?? null;
    if (status === 401) {
      if (!hasShown401Notification) {
        hasShown401Notification = true;
        notifications.show({
          title: "Login expired",
          message: "Please sign in again to continue.",
          color: "yellow",
        });
      }
      clearAuthToken();
    }

    // Extract error message from response
    let message = "Request failed";
    if (error.response) {
      const data = error.response.data;
      if (typeof data?.detail === "string") {
        message = data.detail;
      } else if (typeof data?.message === "string") {
        message = data.message;
      } else if (typeof data?.error === "string") {
        message = data.error;
      } else if (status) {
        message = `Request failed (status ${status})`;
      }
    } else {
      // No response - true network error
      message = "Network error. Please check that the server is running.";
    }

    error.message = message;
    error.status = status;
    error.detail = error.response?.data?.detail ?? null;
    return Promise.reject(error);
  }
);

export default http;
