from collections.abc import Callable

from fastapi.responses import StreamingResponse

from services.chat_service import ChatService


class ChatController:
    async def process_message(self, message: str, on_success: Callable[[], None] | None = None) -> StreamingResponse:
        chat_service = ChatService()
        source_stream = chat_service.process_context_with_llm(message)

        async def tracked_stream():
            has_content = False
            async for chunk in source_stream:
                if chunk and chunk.strip():
                    has_content = True
                yield chunk

            if has_content and on_success:
                on_success()

        return StreamingResponse(tracked_stream(), media_type="text/plain")
