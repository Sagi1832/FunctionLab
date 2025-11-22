import { useMutation } from "@tanstack/react-query";
import { notifications } from "@mantine/notifications";
import { useNavigate } from "react-router-dom";

import { register as registerRequest } from "../../api/auth.js";
import { setAuthToken, clearAuthToken } from "../../lib/http.js";
import { saveToken } from "../../lib/storage.js";

const extractToken = (data) => data?.access_token ?? data?.token ?? null;

const useRegister = () => {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationKey: ["auth", "register"],
    mutationFn: registerRequest,
    onSuccess: (data, variables) => {
      const token = extractToken(data);
      const username = variables?.username?.trim();

      if (token) {
        saveToken(token);
        setAuthToken(token);
        notifications.show({
          title: "Account ready",
          message: username ? `Welcome, ${username}` : "Account created",
          color: "green",
        });
        navigate("/ask");
      } else {
        clearAuthToken();
        notifications.show({
          title: "Account created",
          message: "You can now sign in",
          color: "green",
        });
        navigate("/login");
      }
    },
    onError: (error) => {
      // Error message is already extracted by the axios interceptor
      // It will be the backend's detail string if available, or a network error message
      const message =
        error?.message ??
        (error?.response?.data?.detail ??
          `Registration failed (status ${error?.response?.status ?? "unknown"})`);
      notifications.show({
        title: "Registration failed",
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

export default useRegister;
