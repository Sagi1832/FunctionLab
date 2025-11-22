import { useState } from "react";
import { Button } from "@mantine/core";
import { notifications } from "@mantine/notifications";

const CopyButton = ({ value, label = "Copy" }) => {
  const [isCopying, setIsCopying] = useState(false);

  const handleCopy = async () => {
    if (isCopying) return;
    try {
      setIsCopying(true);
      await navigator.clipboard.writeText(value);
      notifications.show({
        title: "Copied",
        message: "JSON copied to clipboard",
        color: "green",
      });
    } catch (error) {
      notifications.show({
        title: "Copy failed",
        message: error?.message ?? "Unable to copy",
        color: "red",
      });
    } finally {
      setIsCopying(false);
    }
  };

  return (
    <Button size="xs" variant="light" type="button" onClick={handleCopy} loading={isCopying}>
      {label}
    </Button>
  );
};

export default CopyButton;
