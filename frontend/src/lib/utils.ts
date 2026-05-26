export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export function formatDate(value?: string | null) {
  if (!value) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatRelativeNumber(value: number) {
  return new Intl.NumberFormat().format(value);
}

export function truncate(value: string, length = 24) {
  if (value.length <= length) {
    return value;
  }

  return `${value.slice(0, length)}...`;
}

export function maskSecret(value: string, visible = 6) {
  if (value.length <= visible) {
    return value;
  }

  return `${value.slice(0, visible)}${"•".repeat(10)}`;
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
