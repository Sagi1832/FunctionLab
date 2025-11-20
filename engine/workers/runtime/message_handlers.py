from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable, Dict, Tuple

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import ValidationError

from engine.kafka.config import KafkaSettings
from engine.kafka.serializers import to_bytes
from engine.schemas.messages import EngineRequest, EngineResponse
from engine.workers.runtime.actions.asymptotes_holes import _handle_asymptotes_and_holes
from engine.workers.runtime.actions.derivative import _handle_derivative
from engine.workers.runtime.actions.domain import _handle_domain
from engine.workers.runtime.actions.extrema_mono import _handle_extrema_and_monotonic
from engine.workers.runtime.actions.x_intercepts import _handle_x_intercepts
from engine.workers.runtime.actions.y_intercepts import _handle_y_intercepts
from engine.workers.runtime.actions.analyze_and_present import _handle_analyze_and_present

logger = logging.getLogger(__name__)

# Valid mathematical actions (excluding "analyze_and_present" which is a Kafka operation name)
VALID_MATH_ACTIONS = {
    "domain",
    "derivative",
    "asymptotes_and_holes",
    "x_intercepts",
    "y_intercepts",
    "extrema_and_monotonic",
}

HANDLERS: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {
    "domain": _handle_domain,
    "derivative": _handle_derivative,
    "asymptotes_and_holes": _handle_asymptotes_and_holes,
    "x_intercepts": _handle_x_intercepts,
    "y_intercepts": _handle_y_intercepts,
    "extrema_and_monotonic": _handle_extrema_and_monotonic,
    "analyze_and_present": _handle_analyze_and_present,
}





async def build_response_for_request(
    request: EngineRequest,
    settings: KafkaSettings,
    handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
) -> Tuple[EngineResponse, str]:
    """Build an EngineResponse for the given request and return it with the reply topic.

    This contains business-logic dispatching; it does not perform any Kafka I/O.
    """
    logger.info(
        "Processing request: action=%s, correlation_id=%s",
        request.action,
        request.correlation_id,
    )
    reply_topic = request.reply_to or settings.response_topic
    ts = int(time.time())

    handler = handlers.get(request.action)

    if handler is None:
        logger.warning("Unsupported action received: %s", request.action)
        response = EngineResponse(
            correlation_id=request.correlation_id,
            ok=False,
            data=None,
            error={"message": f"unsupported action '{request.action}'"},
            ts=ts,
        )
    else:
        try:
            # Pass handlers to analyze_and_present handler to avoid circular import
            if request.action == "analyze_and_present":
                from engine.workers.runtime.actions.analyze_and_present import _handle_analyze_and_present
                data = await _handle_analyze_and_present(request.payload, handlers)
            else:
                data = await handler(request.payload)
            response = EngineResponse(
                correlation_id=request.correlation_id,
                ok=True,
                data=data,
                error=None,
                ts=ts,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Handler failed for action %s", request.action)
            response = EngineResponse(
                correlation_id=request.correlation_id,
                ok=False,
                data=None,
                error={"message": str(exc)},
                ts=ts,
            )

    return response, reply_topic


async def _process_message(
    request: EngineRequest,
    producer: AIOKafkaProducer,
    settings: KafkaSettings,
) -> None:
    """Process an incoming engine request."""
    response, reply_topic = await build_response_for_request(request, settings)
    await producer.send_and_wait(reply_topic, to_bytes(response.model_dump()))



async def _consume_loop(
    consumer: AIOKafkaConsumer,
    producer: AIOKafkaProducer,
    settings: KafkaSettings,
) -> None:
    """Consume messages from Kafka and dispatch them to handlers."""
    async for message in consumer:
        try:
            request = EngineRequest.model_validate_json(message.value)
        except ValidationError as exc:
            logger.error("Received invalid request payload: %s", exc)
            continue

        try:
            await _process_message(request, producer, settings)
        except Exception:
            logger.exception("Unhandled error while processing message")


def build_kafka_client_kwargs(settings: KafkaSettings) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Construct keyword arguments for Kafka producer and consumer."""
    producer_kwargs: Dict[str, Any] = {
        "bootstrap_servers": settings.broker_url,
        "client_id": settings.client_id,
    }
    consumer_kwargs: Dict[str, Any] = {
        "bootstrap_servers": settings.broker_url,
        "client_id": settings.client_id,
        "group_id": settings.group_id,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
    }

    if settings.security_protocol:
        producer_kwargs["security_protocol"] = settings.security_protocol
        consumer_kwargs["security_protocol"] = settings.security_protocol
    if settings.sasl_mechanism:
        producer_kwargs["sasl_mechanism"] = settings.sasl_mechanism
        consumer_kwargs["sasl_mechanism"] = settings.sasl_mechanism
    if settings.sasl_username and settings.sasl_password:
        producer_kwargs["sasl_plain_username"] = settings.sasl_username
        producer_kwargs["sasl_plain_password"] = settings.sasl_password
        consumer_kwargs["sasl_plain_username"] = settings.sasl_username
        consumer_kwargs["sasl_plain_password"] = settings.sasl_password

    return producer_kwargs, consumer_kwargs
