import { useMutation } from "@tanstack/react-query";
import { notifications } from "@mantine/notifications";
import { useNavigate } from "react-router-dom";

import { login } from "../../api/auth.js";
import { setAuthToken, clearAuthToken } from "../../lib/http.js";
import { saveToken } from "../../lib/storage.js";

const extractToken = (data) => data?.access_token ?? data?.token ?? null;

const useLogin = () => {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationKey: ["auth", "login"],
    mutationFn: login,
    onSuccess: (data, variables) => {
      const token = extractToken(data);

      if (token) {
        saveToken(token);
        setAuthToken(token);
      } else {
        clearAuthToken();
      }

      const username = variables?.username?.trim();
      notifications.show({
        title: "Welcome back",
        message: username ? `Signed in as ${username}` : "Signed in",
        color: "green",
      });

      navigate("/ask");
    },
    onError: (error) => {
      // Error message is already extracted by the axios interceptor
      // It will be the backend's detail string if available, or a network error message
      const message =
        error?.message ??
        (error?.response?.data?.detail ??
          `Login failed (status ${error?.response?.status ?? "unknown"})`);
      notifications.show({
        title: "Login failed",
        message,
        color: "red",
      });
    },
  });

  return {
    ...mutation,
    isLoading: mutation.isPending,
  };
};

export default useLogin;
