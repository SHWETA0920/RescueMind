const BASE_URL = "http://localhost:8000/api";

export async function fetchCards() {
  const res = await fetch(`${BASE_URL}/dashboard/cards`);
  if (!res.ok) throw new Error("Failed to fetch dispatch cards");
  return res.json();
}

export async function submitSms(message) {
  const res = await fetch(`${BASE_URL}/sms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Failed to submit SMS");
  return res.json();
}

export async function submitAudio(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/audio`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Failed to submit audio");
  return res.json();
}

export async function submitPhoto(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/photo`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Failed to submit photo");
  return res.json();
}
