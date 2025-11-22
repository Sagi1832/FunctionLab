import { Anchor, Button, Paper, PasswordInput, Stack, Text, TextInput, Title } from "@mantine/core";
import { useForm } from "@mantine/form";
import { Link } from "react-router-dom";

import useLogin from "../features/auth/useLogin.js";

const LoginPage = () => {
  const login = useLogin();

  const form = useForm({
    initialValues: {
      username: "",
      password: "",
    },
    validate: {
      // Backend policy: password must be at least 6 characters (no max length)
      password: (value) =>
        value.trim().length >= 6 ? null : "Password must be at least 6 characters",
    },
  });

  const handleSubmit = form.onSubmit((values) => {
    const payload = {
      username: values.username.trim(),
      password: values.password.trim(),
    };
    login.mutate(payload);
  });

  const isSubmitting = login.isLoading;

  return (
    <main role="main">
      <Stack align="center" justify="center" mih="100vh" px="md">
        <Paper withBorder shadow="sm" p="xl" radius="md" w="100%" maw={420}>
          <Stack>
            <Title order={2}>Sign in</Title>
            <form onSubmit={handleSubmit}>
              <Stack>
                <TextInput
                  label="Username"
                  placeholder="Your username"
                  autoFocus
                  {...form.getInputProps("username")}
                  disabled={isSubmitting}
                  required
                />
                <PasswordInput
                  label="Password"
                  placeholder="Your password"
                  description="Minimum 6 characters"
                  {...form.getInputProps("password")}
                  disabled={isSubmitting}
                  required
                />
                <Button type="submit" loading={isSubmitting}>
                  Sign in
                </Button>
              </Stack>
            </form>
            {login.error ? (
              <Text c="red" size="sm">
                {login.error.message}
              </Text>
            ) : null}
            <div aria-live="polite" style={{ position: "absolute", left: -9999 }}>
              {login.error ? login.error.message : ""}
            </div>
            <Text size="sm" ta="center">
              Need an account?{" "}
              <Anchor component={Link} to="/register">
                Create account
              </Anchor>
            </Text>
          </Stack>
        </Paper>
      </Stack>
    </main>
  );
};

export default LoginPage;
