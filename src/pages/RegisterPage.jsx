import { Anchor, Button, Paper, PasswordInput, Stack, Text, TextInput, Title } from "@mantine/core";
import { useForm } from "@mantine/form";
import { Link } from "react-router-dom";

import useRegister from "../features/auth/useRegister.js";

const RegisterPage = () => {
  const register = useRegister();

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
    register.mutate(payload);
  });

  const isSubmitting = register.isLoading;

  return (
    <main role="main">
      <Stack align="center" justify="center" mih="100vh" px="md">
        <Paper withBorder shadow="sm" p="xl" radius="md" w="100%" maw={420}>
          <Stack>
            <Title order={2}>Create account</Title>
            <form onSubmit={handleSubmit}>
              <Stack>
                <TextInput
                  label="Username"
                  placeholder="Choose a username"
                  autoFocus
                  {...form.getInputProps("username")}
                  disabled={isSubmitting}
                  required
                />
                <PasswordInput
                  label="Password"
                  placeholder="Create a password"
                  description="Minimum 6 characters"
                  {...form.getInputProps("password")}
                  disabled={isSubmitting}
                  required
                />
                <Button type="submit" loading={isSubmitting}>
                  Create account
                </Button>
              </Stack>
            </form>
            {register.error ? (
              <Text c="red" size="sm">
                {register.error.message}
              </Text>
            ) : null}
            <div aria-live="polite" style={{ position: "absolute", left: -9999 }}>
              {register.error ? register.error.message : ""}
            </div>
            <Text size="sm" ta="center">
              Already have an account?{" "}
              <Anchor component={Link} to="/login">
                Back to login
              </Anchor>
            </Text>
          </Stack>
        </Paper>
      </Stack>
    </main>
  );
};

export default RegisterPage;
