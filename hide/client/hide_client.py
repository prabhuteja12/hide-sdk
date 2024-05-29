from typing import Optional
from pydantic import BaseModel, Field
import requests


class Project(BaseModel):
    id: str = Field(..., description="The ID of the project.")

class TaskResult(BaseModel):
    stdOut: str = Field(..., description="The standard output of the command.")
    stdErr: str = Field(..., description="The standard error of the command.")
    exitCode: int = Field(..., description="The exit code of the command.")

class Task(BaseModel):
    alias: str = Field(..., description="The alias of the task.")
    command: str = Field(..., description="The shell command to run the task.")

class File(BaseModel):
    path: str = Field(..., description="The path of the file.")
    content: str = Field(..., description="The content of the file.")

class FileInfo(BaseModel):
    path: str = Field(..., description="The path of the file.")

class HideClient:

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def create_project(self, url: str) -> Project:
        response = requests.post(f"{self.base_url}/projects", json={"repoUrl": url})
        response.raise_for_status()
        return Project.model_validate(response.json())

    def get_tasks(self, project_id: str) -> list[Task]:
        response = requests.get(f"{self.base_url}/projects/{project_id}/tasks")
        response.raise_for_status()
        return [Task.model_validate(task) for task in response.json()]

    def run_task(
        self,
        project_id: str,
        command: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> TaskResult:
        if not command and not alias:
            raise ValueError("Either 'command' or 'alias' must be provided")

        if command and alias:
            raise ValueError("Cannot provide both 'command' and 'alias'")

        payload = {}
        if command:
            payload["command"] = command
        if alias:
            payload["alias"] = alias

        response = requests.post(f"{self.base_url}/projects/{project_id}/tasks", json=payload)
        if not response.ok:
            raise HideClientError(response.text)
        return TaskResult.model_validate(response.json())

    def create_file(self, project_id: str, path: str, content: str) -> File:
        response = requests.post(f"{self.base_url}/projects/{project_id}/files", json={"path": path, "content": content})
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def get_file(self, project_id: str, path: str) -> File:
        response = requests.get(f"{self.base_url}/projects/{project_id}/files/{path}")
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def update_file(self, project_id: str, path: str, content: str) -> File:
        print(f"Updating file {path} in project {project_id}")
        print(content)
        response = requests.put(f"{self.base_url}/projects/{project_id}/files/{path}", json={"content": content})
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def delete_file(self, project_id: str, path: str) -> bool:
        response = requests.delete(f"{self.base_url}/projects/{project_id}/files/{path}")
        if not response.ok:
            raise HideClientError(response.text)
        return response.status_code == 200

    def list_files(self, project_id: str) -> list[FileInfo]:
        response = requests.get(f"{self.base_url}/projects/{project_id}/files")
        if not response.ok:
            raise HideClientError(response.text)
        return [FileInfo.model_validate(file) for file in response.json()]


class HideClientError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
