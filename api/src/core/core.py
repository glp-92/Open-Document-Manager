from core.chat.api.routes import ChatRouter
from core.chat.application.service import ChatService
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from core.document.api.routes import DocumentRouter
from core.document.application.service import DocumentService
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from core.message.api.routes import MessageRouter
from core.message.application.service import MessageService
from core.message.infrastructure.repository_impl import MessageRepositoryImpl
from core.workspace.api.routes import WorkspaceRouter
from core.workspace.application.service import WorkspaceService
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from fastapi import FastAPI


class Core:
    app = FastAPI(title="FAIR Application Server")

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

    def _set_services(self):
        self.workspace_service = WorkspaceService(workspace_repository_impl=self.workspace_repository_impl)
        self.document_service = DocumentService(document_repository_impl=self.document_repository_impl)
        self.chat_service = ChatService(chat_repository_impl=self.chat_repository_impl)
        self.message_service = MessageService(message_repository_impl=self.message_repository_impl)

    def _set_routers(self):
        self.workspace_router = WorkspaceRouter(workspace_service=self.workspace_service)
        self.document_router = DocumentRouter(document_service=self.document_service)
        self.chat_router = ChatRouter(chat_service=self.chat_service)
        self.message_router = MessageRouter(message_service=self.message_service)

    def _include_routers_on_app(self):
        self.app.include_router(self.workspace_router.router, prefix="/workspaces", tags=["Workspaces"])
        self.app.include_router(self.document_router.router, prefix="/documents", tags=["Documents"])
        self.app.include_router(self.chat_router.router, prefix="/chats", tags=["Chats"])
        self.app.include_router(self.message_router.router, prefix="/messages", tags=["Messages"])
