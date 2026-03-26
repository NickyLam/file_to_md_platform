type MarkdownPreviewProps = {
  markdown: string | null;
  downloadUrl: string | null;
};

export default function MarkdownPreview({ markdown, downloadUrl }: MarkdownPreviewProps) {
  return (
    <section className="card">
      <h2 style={{ marginTop: 0 }}>Preview</h2>
      {markdown ? (
        <pre className="preview-block">{markdown}</pre>
      ) : (
        <p>Markdown preview will appear here after conversion completes.</p>
      )}
      {downloadUrl ? (
        <a className="button-link" href={downloadUrl} download="result.md">
          Download Markdown
        </a>
      ) : (
        <button type="button" disabled>
          Download Unavailable
        </button>
      )}
    </section>
  );
}
