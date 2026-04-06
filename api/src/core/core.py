from core.chat.api.routes import ChatRouter
from core.chat.application.service import ChatService
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from core.document.api.routes import DocumentRouter
from core.document.application.service import DocumentService
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from core.message.api.routes import MessageRouter
from core.message.application.service import MessageService
from core.message.infrastructure.repository_impl import MessageRepositoryImpl
from core.run.api.routes import RunRouter
from core.run.application.service import RunService
from core.run.infrastructure.repository_impl import RunRepositoryImpl
from core.workspace.api.routes import WorkspaceRouter
from core.workspace.application.service import WorkspaceService
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from fastapi import FastAPI


class Core:
    app = FastAPI(title="Open Document Manager Core")

    def __init__(self):
        self._set_repositories()
        self._set_services()
        self._set_routers()
        self._include_routers_on_app()

    def _set_repositories(self):
        self.workspace_repository_impl = WorkspaceRepositoryImpl
        self.document_repository_impl = DocumentRepositoryImpl
        self.chat_repository_impl = ChatRepositoryImpl
        self.message_repository_impl = MessageRepositoryImpl
        self.run_repository_impl = RunRepositoryImpl

    def _set_services(self):
        self.workspace_service = WorkspaceService(workspace_repository_impl=self.workspace_repository_impl)
        self.document_service = DocumentService(document_repository_impl=self.document_repository_impl)
        self.chat_service = ChatService(chat_repository_impl=self.chat_repository_impl)
        self.message_service = MessageService(message_repository_impl=self.message_repository_impl)
        self.run_service = RunService(run_repository_impl=self.run_repository_impl)

    def _set_routers(self):
        self.workspace_router = WorkspaceRouter(workspace_service=self.workspace_service)
        self.document_router = DocumentRouter(document_service=self.document_service)
        self.chat_router = ChatRouter(chat_service=self.chat_service)
        self.message_router = MessageRouter(message_service=self.message_service)
        self.run_router = RunRouter(run_service=self.run_service)

    def _include_routers_on_app(self):
        self.app.include_router(self.workspace_router.router, prefix="/workspaces", tags=["Workspaces"])
        self.app.include_router(self.document_router.router, prefix="/documents", tags=["Documents"])
        self.app.include_router(self.chat_router.router, prefix="/chats", tags=["Chats"])
        self.app.include_router(self.message_router.router, prefix="/messages", tags=["Messages"])
        self.app.include_router(self.run_router.router, prefix="/runs", tags=["Runs"])
