import { Anchor, Button, Group, Paper, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { Link, useNavigate } from "react-router-dom";

import { clearAuthToken } from "../../lib/http.js";

const HeaderBar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuthToken();
    notifications.show({
      title: "Signed out",
      message: "You have been logged out",
      color: "blue",
    });
    navigate("/login");
  };

  return (
    <Paper withBorder shadow="xs" px="md" py="sm" radius={0}>
      <Group justify="space-between">
        <Text fw={600}>
          <Anchor component={Link} to="/ask" underline="never">
            FunctionLab
          </Anchor>
        </Text>
        <Button
          variant="light"
          type="button"
          aria-label="Logout"
          withFocusRing
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Group>
    </Paper>
  );
};

export default HeaderBar;
