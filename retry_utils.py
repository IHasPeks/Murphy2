"""
Retry utilities for handling API failures with exponential backoff.
"""
import asyncio
import logging
import random
from typing import TypeVar, Callable, Optional
from functools import wraps
import aiohttp

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions


async def retry_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> T:
    """
    Execute a function with exponential backoff retry logic.

    Args:
        func: The async function to execute
        config: Retry configuration
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The result of the function call

    Raises:
        The last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()

    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except config.exceptions as e:
            last_exception = e

            if attempt == config.max_attempts - 1:
                logger.error("All %d attempts failed for %s", config.max_attempts, func.__name__)
                raise

            # Calculate delay with exponential backoff
            delay = min(
                config.initial_delay * (config.exponential_base ** attempt),
                config.max_delay
            )

            # Add jitter to prevent thundering herd
            if config.jitter:
                delay *= (0.5 + random.random())

            logger.warning(
                "Attempt %d/%d failed for %s: %s. Retrying in %.2f seconds...",
                attempt + 1, config.max_attempts, func.__name__, str(e), delay
            )

            await asyncio.sleep(delay)

    raise last_exception


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to async functions.

    Usage:
        @with_retry(RetryConfig(max_attempts=5))
        async def my_api_call():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(func, config, *args, **kwargs)
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute a function through the circuit breaker.
        """
        if self.state == 'open':
            if self.last_failure_time and \
               (asyncio.get_event_loop().time() - self.last_failure_time) > self.recovery_timeout:
                self.state = 'half-open'
                logger.info("Circuit breaker entering half-open state for %s", func.__name__)
            else:
                raise Exception(f"Circuit breaker is open for {func.__name__}")

        try:
            result = await func(*args, **kwargs)

            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
                logger.info("Circuit breaker closed for %s", func.__name__)

            return result

        except self.expected_exception:
            self.failure_count += 1
            self.last_failure_time = asyncio.get_event_loop().time()

            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                logger.error(
                    "Circuit breaker opened for %s after %d failures",
                    func.__name__, self.failure_count
                )

            raise


# Pre-configured retry configs for common use cases
OPENAI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exceptions=(
        aiohttp.ClientError,
        asyncio.TimeoutError,
        ConnectionError,
    )
)

TWITCH_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=30.0,
    exceptions=(
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
    )
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=0.5,
    max_delay=5.0,
    exceptions=(
        aiohttp.ClientError,
        asyncio.TimeoutError,
        ConnectionError,
    )
)
