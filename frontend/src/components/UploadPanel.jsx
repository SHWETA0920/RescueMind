import { useState } from "react";
import { submitAudio, submitPhoto, submitSms } from "../api.js";

export default function UploadPanel({ onNewCard }) {
  const [smsText, setSmsText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleSmsSubmit(e) {
    e.preventDefault();
    if (!smsText.trim()) {
      setError("Type a message first.");
      return;
    }
    setError("");
    setBusy(true);
    try {
      const card = await submitSms(smsText);
      onNewCard(card);
      setSmsText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleFileChange(e, kind) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setBusy(true);
    try {
      const card = kind === "audio" ? await submitAudio(file) : await submitPhoto(file);
      onNewCard(card);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  return (
    <div className="panel">
      <h2>Simulate an incoming report</h2>

      <form onSubmit={handleSmsSubmit} className="sms-form">
        <label htmlFor="sms-input">SMS text</label>
        <textarea
          id="sms-input"
          rows={3}
          value={smsText}
          onChange={(e) => setSmsText(e.target.value)}
          placeholder="e.g. There's a fire near the old warehouse on 5th street..."
        />
        <button type="submit" disabled={busy}>
          Submit SMS
        </button>
      </form>

      <div className="upload-row">
        <label className="upload-btn">
          Upload audio call
          <input type="file" accept="audio/*" hidden onChange={(e) => handleFileChange(e, "audio")} />
        </label>
        <label className="upload-btn">
          Upload scene photo
          <input type="file" accept="image/*" hidden onChange={(e) => handleFileChange(e, "photo")} />
        </label>
      </div>

      {error && <p className="error">{error}</p>}
      {busy && <p className="status">Processing...</p>}
    </div>
  );
}
