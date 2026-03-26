import { FormEvent, useState } from "react";

type UploadFormProps = {
  busy: boolean;
  onUpload: (file: File) => Promise<void>;
};

export default function UploadForm({ busy, onUpload }: UploadFormProps) {
  const [selected, setSelected] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!selected) {
      setError("Please choose a file first.");
      return;
    }

    try {
      await onUpload(selected);
    } catch (uploadError) {
      const message = uploadError instanceof Error ? uploadError.message : "Upload failed";
      setError(message);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2 style={{ marginTop: 0 }}>Upload</h2>
      <p className="label">Supported: docx, pdf, xlsx</p>
      <div className="row">
        <input
          type="file"
          accept=".docx,.pdf,.xlsx"
          onChange={(event) => setSelected(event.target.files?.[0] ?? null)}
          disabled={busy}
        />
        <button type="submit" disabled={busy || !selected}>
          {busy ? "Uploading..." : "Upload File"}
        </button>
      </div>
      {error ? (
        <p style={{ color: "#a61b1b", marginBottom: 0 }} role="alert">
          {error}
        </p>
      ) : null}
    </form>
  );
}

