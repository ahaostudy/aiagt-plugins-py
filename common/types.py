from functools import wraps
from typing import Any, Dict, Optional, Type, TypeVar, Callable, Generic, Tuple

from flask import Response, jsonify, request

T = TypeVar('T')


class Req(Generic[T]):
    def __init__(
            self,
            plugin_id: int,
            tool_id: int,
            user_id: int,
            secrets: Dict[str, str],
            model_call_token: Optional[str],
            model_call_limit: int,
            body: Optional[T],
    ):
        self.plugin_id = plugin_id
        self.tool_id = tool_id
        self.user_id = user_id
        self.secrets = secrets
        self.model_call_token = model_call_token
        self.model_call_limit = model_call_limit
        self.body = body

    @staticmethod
    def parser(body_type: Optional[Type[T]] = None) -> Callable[..., Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    plugin_id = request.json.get('plugin_id')
                    if plugin_id is None:
                        raise ValueError('missing plugin id')

                    tool_id = request.json.get('tool_id')
                    if tool_id is None:
                        raise ValueError('missing tool id')

                    user_id = request.json.get('user_id')
                    if user_id is None:
                        raise ValueError('missing user id')

                    plugin_id = int(plugin_id)
                    tool_id = int(tool_id)
                    user_id = int(user_id)

                    secrets = request.json.get('secrets', {})
                    model_call_token = request.json.get('model_call_token', '')
                    model_call_limit = int(request.json.get('model_call_limit', 0))

                    body = request.json.get('body')
                    if body_type and body:
                        try:
                            if hasattr(body_type, "__annotations__"):
                                known_fields = body_type.__annotations__.keys()
                                filtered_body = {k: v for k, v in body.items() if k in known_fields}
                                body = body_type(**filtered_body)
                            else:
                                body = body_type(**body)
                        except TypeError as e:
                            error_message = str(e)
                            error_fields = error_message.split(":")[1].strip()
                            return Resp.error(
                                Resp.CodeBadRequest,
                                Exception(f"missing required fields: {error_fields}")
                            ).build()

                    req = Req(plugin_id, tool_id, user_id, secrets, model_call_token, model_call_limit, body)
                except Exception as e:
                    return Resp.error(Resp.CodeBadRequest, e).build()
                return func(req, *args, **kwargs)

            return wrapper

        return decorator


class Resp:
    CodeSuccess = 0
    CodeBadRequest = 400
    CodeServerInternal = 500

    CodeMsgs = {
        CodeSuccess: "success",
        CodeBadRequest: "bad request",
        CodeServerInternal: "server internal error",
    }

    def __init__(self, code: int, msg: str, data: Any = None):
        self.code = code
        self.msg = msg
        self.data = data

    def build(self) -> Response:
        return jsonify({"code": self.code, "msg": self.msg, "data": self.data})

    @staticmethod
    def err_msg(code: int, err: Exception) -> str:
        msg = Resp.CodeMsgs.get(code, Resp.CodeMsgs[Resp.CodeServerInternal])
        return f"{msg}: {type(err).__name__}: {err}"

    @staticmethod
    def error(code: int, err: Exception) -> "Resp":
        return Resp(code, Resp.err_msg(code, err))

    @staticmethod
    def internal_error(err: Exception) -> "Resp":
        return Resp(
            Resp.CodeServerInternal,
            Resp.err_msg(Resp.CodeServerInternal, err)
        )

    @staticmethod
    def status(code: int, msg: str) -> "Resp":
        return Resp(code, msg)

    @staticmethod
    def success(data: Any) -> "Resp":
        return Resp(
            Resp.CodeSuccess,
            Resp.CodeMsgs[Resp.CodeSuccess],
            data
        )
