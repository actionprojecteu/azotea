from typing import AsyncContextManager, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

class AsyncDatabase(Protocol):
    """application software use this interface as the dependency"""

    def session(self) -> AsyncContextManager[AsyncSession]: ...
