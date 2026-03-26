import { useEffect, useRef, useState } from "react";

import MarkdownPreview from "./components/MarkdownPreview";
import TaskStatus, { TaskState } from "./components/TaskStatus";
import UploadForm from "./components/UploadForm";

type UploadResponse = {
  task_id: string;
  access_token: string;
};

const TERMINAL_STATES = new Set(["success", "success_with_warnings", "failed"]);

export default function App() {
  const [busy, setBusy] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [task, setTask] = useState<TaskState | null>(null);
  const [pollError, setPollError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const canPoll = Boolean(taskId && accessToken);

  async function upload(file: File) {
    setBusy(true);
    setPollError(null);
    setTask(null);
    setDownloadUrl((current) => {
      if (current) {
        URL.revokeObjectURL(current);
      }
      return null;
    });
    try {
      const data = new FormData();
      data.append("file", file);

      const response = await fetch("/api/upload", {
        method: "POST",
        body: data
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? "Upload failed");
      }

      const payload = (await response.json()) as UploadResponse;
      setTaskId(payload.task_id);
      setAccessToken(payload.access_token);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    async function pollOnce() {
      if (!taskId || !accessToken) {
        return;
      }
      try {
        const response = await fetch(`/api/tasks/${taskId}`, {
          headers: {
            "X-Access-Token": accessToken
          }
        });
        if (!response.ok) {
          const payload = await response.json().catch(() => ({}));
          throw new Error(payload.detail ?? "Status polling failed");
        }
        const payload = (await response.json()) as TaskState;
        setTask(payload);
        setPollError(null);
        if (TERMINAL_STATES.has(payload.status) && intervalRef.current !== null) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "Status polling failed";
        setPollError(message);
      }
    }

    if (!canPoll) {
      return;
    }

    pollOnce();
    intervalRef.current = window.setInterval(pollOnce, 1500);

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [taskId, accessToken, canPoll]);

  useEffect(() => {
    if (!task?.markdown) {
      setDownloadUrl((current) => {
        if (current) {
          URL.revokeObjectURL(current);
        }
        return null;
      });
      return;
    }

    const blob = new Blob([task.markdown], { type: "text/markdown;charset=utf-8" });
    const nextUrl = URL.createObjectURL(blob);
    setDownloadUrl((current) => {
      if (current) {
        URL.revokeObjectURL(current);
      }
      return nextUrl;
    });
  }, [task?.markdown]);

  useEffect(() => {
    return () => {
      if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl);
      }
    };
  }, [downloadUrl]);

  return (
    <main className="app">
      <h1 style={{ marginBottom: 8 }}>File to Markdown</h1>
      <p className="label" style={{ marginTop: 0 }}>
        Upload a file, poll conversion status, and prepare for preview/download.
      </p>
      <UploadForm busy={busy} onUpload={upload} />
      <TaskStatus task={task} taskId={taskId} accessToken={accessToken} pollError={pollError} />
      <MarkdownPreview markdown={task?.markdown ?? null} downloadUrl={downloadUrl} />
    </main>
  );
}
