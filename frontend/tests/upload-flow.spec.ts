import { expect, test } from "@playwright/test";

test("user can upload and see a task", async ({ page }) => {
  let pollCount = 0;

  await page.route("**/api/upload", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-123",
        access_token: "token-abc",
      }),
    });
  });

  await page.route("**/api/tasks/task-123", async (route) => {
    pollCount += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-123",
        status: pollCount === 1 ? "running" : "success",
        file_name: "sample.docx",
        file_type: "docx",
        file_size: 128,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        markdown: pollCount === 1 ? undefined : "# Converted\n\nHello markdown.",
      }),
    });
  });

  await page.goto("/");
  await page.setInputFiles('input[type="file"]', {
    name: "sample.docx",
    mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    buffer: Buffer.from("sample"),
  });
  await page.getByRole("button", { name: "Upload File" }).click();

  await expect(page.getByText("task-123")).toBeVisible();
  await expect(page.getByText("token-abc")).toBeVisible();
  await expect(page.getByText(/running|success/i)).toBeVisible();
  await expect(page.getByText("# Converted")).toBeVisible();
  await expect(page.getByText("Hello markdown.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Download Markdown" })).toBeVisible();
});
