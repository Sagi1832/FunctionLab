const TOKEN_KEY = "fl_token";

const isBrowser = () => typeof window !== "undefined";

export const saveToken = (token) => {
  if (!isBrowser()) return;
  const trimmed = token?.trim();
  if (trimmed) {
    window.localStorage.setItem(TOKEN_KEY, trimmed);
  } else {
    window.localStorage.removeItem(TOKEN_KEY);
  }
};

export const getToken = () => {
  if (!isBrowser()) return null;
  const value = window.localStorage.getItem(TOKEN_KEY) ?? "";
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

export const removeToken = () => {
  if (!isBrowser()) return;
  window.localStorage.removeItem(TOKEN_KEY);
};
