export type TaskState = {
  task_id: string;
  status: string;
  file_name: string;
  file_type: string;
  file_size: number;
  created_at: string;
  updated_at: string;
  markdown?: string;
};

type TaskStatusProps = {
  task: TaskState | null;
  taskId: string | null;
  accessToken: string | null;
  pollError: string | null;
};

export default function TaskStatus({ task, taskId, accessToken, pollError }: TaskStatusProps) {
  return (
    <section className="card">
      <h2 style={{ marginTop: 0 }}>Task Status</h2>
      <div className="row">
        <span className="pill">Task ID</span>
        <span className="mono">{taskId ?? "-"}</span>
      </div>
      <div className="row" style={{ marginTop: 8 }}>
        <span className="pill">Access Token</span>
        <span className="mono">{accessToken ?? "-"}</span>
      </div>
      <div className="row" style={{ marginTop: 16 }}>
        <strong>Status:</strong>
        <span>{task?.status ?? "waiting_for_upload"}</span>
      </div>
      <p className="label" style={{ marginBottom: 0 }}>
        Last update: {task?.updated_at ?? "-"}
      </p>
      {pollError ? (
        <p style={{ color: "#a61b1b", marginBottom: 0 }} role="alert">
          {pollError}
        </p>
      ) : null}
    </section>
  );
}
